"""
NetSage AI rule checker
-----------------------
Runs a small set of deterministic checks on a lab network snapshot.
These checks do not call an AI model. The same input always produces
the same findings.

Expected JSON shape is documented in data/sample_network_state.json.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SEVERITY_ORDER = {"INFO": 0, "WARNING": 1, "ERROR": 2}


@dataclass
class Finding:
    level: str
    code: str
    message: str
    detail: str = ""

    def as_dict(self) -> dict[str, str]:
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "detail": self.detail,
        }


def _ip(value: str) -> ipaddress.IPv4Address:
    return ipaddress.IPv4Address(value)


def _network(ip_addr: str, mask: str) -> ipaddress.IPv4Network:
    return ipaddress.IPv4Network(f"{ip_addr}/{mask}", strict=False)


def check_duplicate_ips(state: dict[str, Any]) -> list[Finding]:
    """Two hosts (or a host and a router interface) must not share an IPv4 address."""
    findings: list[Finding] = []
    seen: dict[str, list[str]] = {}

    for device in state.get("devices", []):
        ip_addr = device.get("ip_address")
        if not ip_addr:
            continue
        seen.setdefault(ip_addr, []).append(device.get("name", "unknown-host"))

    for router in state.get("routers", []):
        rname = router.get("name", "unknown-router")
        for iface in router.get("interfaces", []):
            ip_addr = iface.get("ip_address")
            if not ip_addr:
                continue
            label = f"{rname} {iface.get('name', 'iface')}"
            seen.setdefault(ip_addr, []).append(label)

    for ip_addr, owners in seen.items():
        unique_owners = sorted(set(owners))
        if len(unique_owners) > 1:
            findings.append(
                Finding(
                    level="ERROR",
                    code="DUPLICATE_IP",
                    message="Duplicate IP detected",
                    detail=f"{ip_addr} is used by: {', '.join(unique_owners)}",
                )
            )
    return findings


def check_subnet_masks(state: dict[str, Any]) -> list[Finding]:
    """Host mask must match the mask on the gateway interface in the same VLAN/LAN."""
    findings: list[Finding] = []
    gateway_masks: dict[str, str] = {}

    for router in state.get("routers", []):
        for iface in router.get("interfaces", []):
            ip_addr = iface.get("ip_address")
            mask = iface.get("subnet_mask")
            if ip_addr and mask:
                gateway_masks[ip_addr] = mask

    for device in state.get("devices", []):
        gw = device.get("gateway")
        host_mask = device.get("subnet_mask")
        name = device.get("name", "host")
        if not gw or not host_mask:
            continue
        expected = gateway_masks.get(gw)
        if expected and expected != host_mask:
            findings.append(
                Finding(
                    level="ERROR",
                    code="MASK_MISMATCH",
                    message="Incorrect subnet mask",
                    detail=(
                        f"{name} uses {host_mask} while gateway {gw} uses {expected}"
                    ),
                )
            )
    return findings


def check_gateway_mismatch(state: dict[str, Any]) -> list[Finding]:
    """Default gateway must sit on the same IPv4 network as the host."""
    findings: list[Finding] = []
    known_gateway_ips: set[str] = set()

    for router in state.get("routers", []):
        for iface in router.get("interfaces", []):
            ip_addr = iface.get("ip_address")
            if ip_addr:
                known_gateway_ips.add(ip_addr)

    for device in state.get("devices", []):
        name = device.get("name", "host")
        ip_addr = device.get("ip_address")
        mask = device.get("subnet_mask")
        gw = device.get("gateway")
        if not ip_addr or not mask or not gw:
            continue

        try:
            host_net = _network(ip_addr, mask)
            gw_addr = _ip(gw)
        except ValueError as exc:
            findings.append(
                Finding(
                    level="ERROR",
                    code="GATEWAY_MISMATCH",
                    message="Gateway mismatch",
                    detail=f"{name} has an unreadable IP or gateway ({exc})",
                )
            )
            continue

        if gw_addr not in host_net:
            findings.append(
                Finding(
                    level="ERROR",
                    code="GATEWAY_MISMATCH",
                    message="Gateway mismatch",
                    detail=(
                        f"{name} {ip_addr}/{mask} points at gateway {gw}, "
                        "which is not on the same subnet"
                    ),
                )
            )
        elif gw not in known_gateway_ips:
            findings.append(
                Finding(
                    level="WARNING",
                    code="GATEWAY_MISMATCH",
                    message="Gateway mismatch",
                    detail=(
                        f"{name} uses gateway {gw}, but that address is not "
                        "present on any router interface in this snapshot"
                    ),
                )
            )
    return findings


def check_interfaces_down(state: dict[str, Any]) -> list[Finding]:
    """Flag router interfaces that are administratively down or protocol down."""
    findings: list[Finding] = []
    for router in state.get("routers", []):
        rname = router.get("name", "router")
        for iface in router.get("interfaces", []):
            iname = iface.get("name", "interface")
            status = str(iface.get("status", "")).lower()
            protocol = str(iface.get("protocol", "")).lower()
            if "administratively down" in status or status == "down":
                findings.append(
                    Finding(
                        level="WARNING",
                        code="INTERFACE_DOWN",
                        message="Interface is down",
                        detail=f"{rname} {iname} status={iface.get('status')} protocol={iface.get('protocol')}",
                    )
                )
            elif protocol == "down":
                findings.append(
                    Finding(
                        level="WARNING",
                        code="INTERFACE_DOWN",
                        message="Interface is down",
                        detail=f"{rname} {iname} line protocol is down",
                    )
                )
    return findings


def check_missing_vlans(state: dict[str, Any]) -> list[Finding]:
    """Access ports and hosts must not reference a VLAN that is missing from the switch."""
    findings: list[Finding] = []
    for switch in state.get("switches", []):
        sname = switch.get("name", "switch")
        configured = set(switch.get("vlans", []))
        for port in switch.get("access_ports", []):
            vlan = port.get("vlan")
            if vlan is None:
                continue
            if vlan not in configured:
                findings.append(
                    Finding(
                        level="ERROR",
                        code="MISSING_VLAN",
                        message="Missing VLAN",
                        detail=(
                            f"{sname} port {port.get('port')} is in VLAN {vlan}, "
                            f"but that VLAN is not created on {sname}"
                        ),
                    )
                )

    switch_vlans: dict[str, set[int]] = {
        sw.get("name"): set(sw.get("vlans", [])) for sw in state.get("switches", [])
    }
    for device in state.get("devices", []):
        vlan = device.get("vlan")
        conn = str(device.get("connected_interface", ""))
        if vlan is None or not conn:
            continue
        for sname, vlans in switch_vlans.items():
            if conn.upper().startswith(sname.upper()):
                if vlan not in vlans:
                    findings.append(
                        Finding(
                            level="ERROR",
                            code="MISSING_VLAN",
                            message="Missing VLAN",
                            detail=(
                                f"{device.get('name')} expects VLAN {vlan} on {sname}, "
                                "but the VLAN is not in the switch VLAN list"
                            ),
                        )
                    )
    return findings


def check_missing_routes(state: dict[str, Any]) -> list[Finding]:
    """Compare expected_routes with the routes actually present on each router."""
    findings: list[Finding] = []
    tables: dict[str, set[tuple[str, int]]] = {}
    for router in state.get("routers", []):
        rname = router.get("name", "router")
        present: set[tuple[str, int]] = set()
        for route in router.get("routes", []):
            network = route.get("network")
            prefix = route.get("prefix_length")
            if network is None or prefix is None:
                continue
            present.add((str(network), int(prefix)))
        tables[rname] = present

    for expected in state.get("expected_routes", []):
        rname = expected.get("router")
        network = expected.get("network")
        prefix = expected.get("prefix_length")
        if not rname or network is None or prefix is None:
            continue
        present = tables.get(rname, set())
        if (str(network), int(prefix)) not in present:
            findings.append(
                Finding(
                    level="ERROR",
                    code="MISSING_ROUTE",
                    message="Missing route",
                    detail=(
                        f"{rname} has no route for {network}/{prefix}. "
                        f"{expected.get('reason', '')}"
                    ).strip(),
                )
            )
    return findings


def run_checks(state: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(check_duplicate_ips(state))
    findings.extend(check_subnet_masks(state))
    findings.extend(check_gateway_mismatch(state))
    findings.extend(check_interfaces_down(state))
    findings.extend(check_missing_vlans(state))
    findings.extend(check_missing_routes(state))
    findings.sort(key=lambda item: (-SEVERITY_ORDER.get(item.level, 0), item.code))
    return findings


def format_report(findings: list[Finding]) -> str:
    lines = [
        "NetSage Rule Checker",
        "--------------------",
        "",
    ]
    if not findings:
        lines.append("[INFO] No rule violations found in this snapshot.")
        return "\n".join(lines)

    for item in findings:
        lines.append(f"[{item.level}] {item.message}")
        if item.detail:
            lines.append(f"        {item.detail}")
    return "\n".join(lines)


def load_state(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run NetSage deterministic checks against a JSON snapshot."
    )
    parser.add_argument(
        "snapshot",
        nargs="?",
        default=None,
        help="Path to sample_network_state.json",
    )
    args = parser.parse_args()

    if args.snapshot:
        snapshot_path = Path(args.snapshot)
    else:
        snapshot_path = (
            Path(__file__).resolve().parent.parent / "data" / "sample_network_state.json"
        )

    state = load_state(snapshot_path)
    findings = run_checks(state)
    print(format_report(findings))
    errors = sum(1 for item in findings if item.level == "ERROR")
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
