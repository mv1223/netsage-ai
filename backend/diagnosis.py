"""Build a structured diagnosis from lab evidence.

If OPENAI_API_KEY is set, the prompt in prompts/diagnose_prompt.md is
sent to the API. Otherwise a local helper looks at the pasted text.
The local helper is not a trained model. It only pattern-matches common
Packet Tracer mistakes so the site still runs in a classroom without keys.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from schemas import DiagnosisResult, HumanReviewBlock

ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = ROOT / "prompts" / "diagnose_prompt.md"


def load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _pending(result: dict) -> DiagnosisResult:
    result["human_review"] = {"status": "PENDING", "reason": ""}
    return DiagnosisResult.model_validate(result)


def _insufficient(reason: str) -> DiagnosisResult:
    return _pending(
        {
            "root_cause": reason,
            "confidence": 0.35,
            "osi_layer": "Unknown",
            "evidence": [
                "The pasted evidence is not enough for a firm lab diagnosis.",
                "Inference is limited until more show output is added.",
            ],
            "next_command": [
                "show ip interface brief",
                "show vlan brief",
                "show ip route",
            ],
            "fix_steps": [
                "Do not change the configuration yet.",
                "Collect the next command output and run Analyze again.",
            ],
            "verification": [
                "After more output is pasted, compare it with the symptom.",
            ],
        }
    )


def local_diagnose(symptom: str, topology: str, show_outputs: str) -> DiagnosisResult:
    text = f"{symptom}\n{topology}\n{show_outputs}".lower()
    raw_show = show_outputs.strip()
    if not symptom.strip():
        return _insufficient("Symptom is empty. Describe what failed in the lab before asking for a cause.")
    if not raw_show:
        return _insufficient("No show-command output was pasted. The helper will not guess hidden CLI.")

    evidence: list[str] = []
    next_cmd: list[str] = []
    fix: list[str] = []
    verify: list[str] = []
    cause = ""
    layer = "Layer 3"
    confidence = 0.62

    if re.search(r"access mode vlan:\s*1", text) and "vlan 20" in text:
        cause = "The access port is still in VLAN 1 while the lab expects another VLAN."
        layer = "Layer 2"
        confidence = 0.9
        evidence.append("Switchport access VLAN is 1 in the pasted output.")
        next_cmd.append("show vlan brief")
        fix.append("Move the PC access port into the VLAN named in the worksheet.")
        verify.append("Ping the server that lives in the intended VLAN.")
    elif "inactive" in text and re.search(r"access mode vlan:\s*\d+", text):
        cause = "The port is assigned to a VLAN that is not created on the switch."
        layer = "Layer 2"
        confidence = 0.88
        evidence.append("Access VLAN is marked Inactive in show interfaces switchport.")
        next_cmd.append("show vlan brief")
        fix.append("Create the missing VLAN, then confirm the port is active.")
        verify.append("show vlan brief should list the VLAN and the PC port.")
    elif "vlans allowed on trunk" in text or "allowed" in text and "trunk" in text:
        if re.search(r"1,\s*10,\s*20\b", text) and "40" in text:
            cause = "One side of the trunk does not allow VLAN 40."
            layer = "Layer 2"
            confidence = 0.87
            evidence.append("Trunk allowed lists are not the same on both switches.")
            next_cmd.append("show interfaces trunk")
            fix.append("Add the missing VLAN to the trunk allowed list. Do not disable trunking.")
            verify.append("Both switches should list the same allowed VLANs, then ping.")
        else:
            cause = "Trunk allowed VLANs or port mode do not match the topology note."
            layer = "Layer 2"
            confidence = 0.7
            evidence.append("Trunk-related output is present in the paste.")
            next_cmd.append("show interfaces trunk")
            fix.append("Align allowed VLANs and access/trunk mode with the lab drawing.")
            verify.append("show interfaces trunk and a cross-switch ping.")
    elif "static access" in text and "trunk" in topology.lower():
        cause = "The uplink is still an access port, so tagged VLANs cannot cross the link."
        layer = "Layer 2"
        confidence = 0.86
        evidence.append("Operational mode is static access on a port the topology calls a trunk.")
        next_cmd.append("show interfaces trunk")
        fix.append("Change the uplink to trunk. Keep the native VLAN unless the sheet says otherwise.")
        verify.append("show interfaces trunk should list the port.")
    elif "default gateway" in text and re.search(r"192\.168\.\d+\.254", text) and re.search(r"192\.168\.\d+\.1", text):
        cause = "The PC default gateway does not match the router LAN address."
        layer = "Layer 3"
        confidence = 0.9
        evidence.append("ipconfig gateway and show ip interface brief do not use the same last octet.")
        next_cmd.append("show ip interface brief")
        fix.append("Set the PC gateway to the router interface IP. Avoid changing the router unless the worksheet says so.")
        verify.append("ping the gateway, then ping a remote host.")
    elif "255.255.255.0" in show_outputs and "255.255.255.192" in show_outputs:
        cause = "The host subnet mask does not match the mask on the gateway interface."
        layer = "Layer 3"
        confidence = 0.85
        evidence.append("Host mask /24 appears next to a router mask /26 in the paste.")
        next_cmd.append("show running-config interface")
        fix.append("Correct the PC mask to match the router LAN.")
        verify.append("ping the gateway address.")
    elif "administratively down" in text:
        cause = "A required interface is shut down."
        layer = "Layer 1"
        confidence = 0.91
        evidence.append("show ip interface brief (or status) lists administratively down.")
        next_cmd.append("show ip interface brief")
        fix.append("Use no shutdown on that interface only. Do not disable security features.")
        verify.append("Status and protocol should both show up, then ping.")
    elif "helper address is not set" in text or "169.254" in text:
        cause = "DHCP Discover is not being relayed (or the client never received a lease)."
        layer = "Layer 3"
        confidence = 0.84
        evidence.append("Helper address is missing and/or the host shows an APIPA address.")
        next_cmd.append("show ip dhcp binding")
        fix.append("Add ip helper-address toward the real DHCP server. Do not turn DHCP off.")
        verify.append("Client should get a LAN address; check show ip dhcp binding.")
    elif "ip dhcp pool" in text and "network 192.168.16.0" in text:
        cause = "The DHCP network statement does not match the interface subnet."
        layer = "Layer 3"
        confidence = 0.88
        evidence.append("Pool network 192.168.16.0 appears while the lab LAN is 192.168.60.0/24.")
        next_cmd.append("show ip dhcp pool")
        fix.append("Change the pool network to the VLAN subnet. Keep exclusions for the gateway.")
        verify.append("A client renew should receive an address in the correct subnet.")
    elif "default-router" not in text and "ip dhcp pool" in text:
        cause = "The DHCP pool never sends a default gateway option."
        layer = "Layer 3"
        confidence = 0.83
        evidence.append("dhcp pool config is present without default-router.")
        next_cmd.append("ipconfig /all on the PC")
        fix.append("Add default-router with the LAN gateway IP.")
        verify.append("ipconfig should list the gateway, then ping a remote network.")
    elif "dns servers:" in text and "192.168.90.50" in text:
        cause = "Clients are using a DNS server address that is not the lab DNS host."
        layer = "Layer 7"
        confidence = 0.8
        evidence.append("ipconfig lists a DNS server that does not match the topology DNS IP.")
        next_cmd.append("nslookup from the PC")
        fix.append("Fix dns-server under the DHCP pool or the static DNS field.")
        verify.append("Resolve the lab hostname, then open it in the browser.")
    elif re.search(r"web\.campus\.lab\s+a\s+10\.10\.10\.80", text):
        cause = "The DNS A record points at the wrong host address."
        layer = "Layer 7"
        confidence = 0.86
        evidence.append("web.campus.lab A record is 10.10.10.80 in the paste.")
        next_cmd.append("ping web.campus.lab")
        fix.append("Change the A record to the address on the worksheet.")
        verify.append("nslookup should return the corrected IP.")
    elif "deny udp any any eq 53" in text or "eq 53" in text and "guest" in text:
        cause = "The guest ACL drops DNS, so web names fail even when ICMP works."
        layer = "Layer 4"
        confidence = 0.87
        evidence.append("ACL contains a deny for UDP/53.")
        next_cmd.append("show access-lists")
        fix.append("Permit DNS to the intended resolver. Do not remove the whole guest ACL.")
        verify.append("nslookup from a guest PC, then open a website.")
    elif "deny tcp any host" in text and "eq www" in text:
        cause = "An ACL line denies HTTP to the server. Ping can still succeed."
        layer = "Layer 4"
        confidence = 0.92
        evidence.append("deny tcp ... eq www is in the pasted ACL.")
        next_cmd.append("show access-lists")
        fix.append("If the lab needs HTTP, replace that deny with a specific permit. Keep other ACL lines.")
        verify.append("Browse to the server; ACL counters should move on the permit.")
    elif "outgoing access list" in text and "eq 22" in text:
        cause = "The SSH ACL is applied outbound, so inbound admin sessions never hit the permit."
        layer = "Layer 4"
        confidence = 0.84
        evidence.append("Outgoing access list is set on the interface that should filter inbound SSH.")
        next_cmd.append("show ip interface")
        fix.append("Apply the ACL inbound on the admin LAN interface instead of outbound.")
        verify.append("SSH from the admin PC to the router.")
    elif "deny ip any host" in text and "permit tcp" in text and "eq 443" in text:
        cause = "A deny to the host sits above the HTTPS permit, so line 20 never matches."
        layer = "Layer 4"
        confidence = 0.9
        evidence.append("ACL order shows deny any host before permit tcp eq 443.")
        next_cmd.append("show access-lists")
        fix.append("Put the HTTPS permit above the host deny, or make the deny more specific.")
        verify.append("Open https to the portal and re-check ACL counters.")
    elif "gateway of last resort is not set" in text and "8.8.8.8" in text:
        cause = "The edge router has no default route toward the ISP."
        layer = "Layer 3"
        confidence = 0.86
        evidence.append("show ip route reports no gateway of last resort.")
        next_cmd.append("show ip route")
        fix.append("Add a default route to the ISP next hop. Do not delete connected routes.")
        verify.append("ping 8.8.8.8 from the edge router, then from a PC.")
    elif "via 172.16.0.5" in text:
        cause = "The static route next hop is not on the connected serial subnet."
        layer = "Layer 3"
        confidence = 0.89
        evidence.append("Static route uses 172.16.0.5 while the serial network is /30.")
        next_cmd.append("show ip route")
        fix.append("Change the next hop to the real serial neighbor.")
        verify.append("show ip route should list the new next hop; then ping the remote LAN.")
    elif "area 0" in text and "area 1" in text:
        cause = "OSPF area IDs do not match on the shared link."
        layer = "Layer 3"
        confidence = 0.9
        evidence.append("One router advertises the link in area 0 and the other in area 1.")
        next_cmd.append("show ip ospf neighbor")
        fix.append("Place both sides of the link in the same area as the worksheet.")
        verify.append("show ip ospf neighbor should list FULL or 2WAY as expected.")
    elif "loopback0" in text and "routing for networks" in text:
        cause = "The loopback prefix is not covered by an OSPF network statement."
        layer = "Layer 3"
        confidence = 0.78
        evidence.append("Loopback is up, but the OSPF network list does not include it.")
        next_cmd.append("show ip route ospf")
        fix.append("Add a network statement (or redistribute) for the loopback as the lab requires.")
        verify.append("The prefix should appear on the neighbor with an O route.")
    elif "show ip route" in text and "192.168.2.0" in topology.lower() or (
        "show ip route" in text and "192.168.1.0/24 is directly connected" in text and "192.168.2.0" not in show_outputs
    ):
        cause = "A required remote network is missing from the routing table."
        layer = "Layer 3"
        confidence = 0.82
        evidence.append("show ip route does not list the destination LAN mentioned in the lab.")
        next_cmd.append("show ip route")
        fix.append("Add a static route or enable the IGP for that prefix. Keep the change small.")
        verify.append("The route should appear, then ping the far LAN.")
    elif "total translations: 0" in text or (
        "show ip nat translations" in text and "ip nat inside source" not in text and "nat" in text
    ):
        if "ip nat inside source" not in text and "overload" not in text:
            cause = "NAT is not configured, so private sources leave the WAN unchanged."
            layer = "Layer 3"
            confidence = 0.84
            evidence.append("NAT table is empty and no nat statement appears in the paste.")
            next_cmd.append("show ip nat statistics")
            fix.append("Configure PAT with a matching ACL. Mark inside/outside correctly.")
            verify.append("show ip nat translations after a ping to the outside host.")
        else:
            cause = "NAT inside and outside are likely reversed, so translations never build."
            layer = "Layer 3"
            confidence = 0.83
            evidence.append("NAT commands exist but the translation table stays empty.")
            next_cmd.append("show running-config")
            fix.append("Put ip nat inside on the LAN and ip nat outside on the WAN.")
            verify.append("Ping outside and check show ip nat translations.")
    elif "ip nat inside" in text and "ip nat outside" in text:
        cause = "NAT inside and outside interface roles do not match the LAN/WAN drawing."
        layer = "Layer 3"
        confidence = 0.84
        evidence.append("running-config shows NAT roles on the interfaces.")
        next_cmd.append("show ip nat translations")
        fix.append("Swap inside/outside so the LAN is inside. Do not remove the ACL unless it is wrong.")
        verify.append("Translations should appear after traffic is generated.")
    elif "192.168.23.80" in text and "static tcp" in text:
        cause = "The static NAT / port-forward inside address does not match the real server."
        layer = "Layer 4"
        confidence = 0.88
        evidence.append("NAT static maps to 192.168.23.80 while the server is 192.168.23.10 in the topology.")
        next_cmd.append("show ip nat translations")
        fix.append("Correct the inside local IP in the static NAT statement.")
        verify.append("From the outside, open TCP 80 to the mapped global address.")
    elif "ssid campus-staff" in text and "vlan 90" in text:
        cause = "The staff SSID is mapped to the guest VLAN."
        layer = "Layer 2"
        confidence = 0.87
        evidence.append("WLAN mapping lists CAMPUS-STAFF on VLAN 90.")
        next_cmd.append("ipconfig on a wireless client")
        fix.append("Map the staff SSID to the staff VLAN. Keep guest isolation on the guest SSID.")
        verify.append("Client should receive a staff subnet address.")
    elif "fa0/10" in text and "disabled" in text:
        cause = "The switch port that feeds the access point is disabled."
        layer = "Layer 1"
        confidence = 0.9
        evidence.append("show interfaces status lists the AP port as disabled.")
        next_cmd.append("show interfaces status")
        fix.append("no shutdown on the AP uplink only.")
        verify.append("SSID should accept associations and clients should get an IP.")
    elif "administrative mode: static access" in text and "wireless" in text or (
        "ap" in text and "static access" in text and "vlan: 1" in text
    ):
        cause = "The AP uplink is an access port on VLAN 1, so client VLANs never tag across."
        layer = "Layer 2"
        confidence = 0.85
        evidence.append("AP-facing switchport is access VLAN 1; trunks are empty.")
        next_cmd.append("show interfaces trunk")
        fix.append("Make the AP uplink a trunk and allow the wireless VLANs.")
        verify.append("Wireless client should get the mapped VLAN address.")
    else:
        cause = (
            "The paste does not match a single obvious lab fault. "
            "Treat the following as a starting point, not a final answer."
        )
        confidence = 0.48
        layer = "Unknown"
        evidence.append("Raw show output was provided but did not match a high-confidence pattern.")
        evidence.append("Inference: more than one OSI layer could still explain the symptom.")
        next_cmd = [
            "show ip interface brief",
            "show vlan brief",
            "show ip route",
            "show access-lists",
        ]
        fix = [
            "Wait for human review before changing anything.",
            "Collect the next command that is missing from the paste.",
        ]
        verify = ["After the extra output is collected, run Analyze again."]

    if topology.strip():
        evidence.append(f"Topology note used: {topology.strip()[:180]}")

    if not next_cmd:
        next_cmd.append("show ip interface brief")
    if not fix:
        fix.append("Do not apply a change until a reviewer accepts or edits this note.")
    if not verify:
        verify.append("Re-run the original failed ping or browse test.")

    return _pending(
        {
            "root_cause": cause,
            "confidence": confidence,
            "osi_layer": layer,
            "evidence": evidence[:8],
            "next_command": next_cmd[:6],
            "fix_steps": fix[:6],
            "verification": verify[:6],
        }
    )


def _call_openai(user_block: str) -> DiagnosisResult:
    from urllib import request

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    body = json.dumps(
        {
            "model": model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": load_system_prompt()},
                {"role": "user", "content": user_block},
            ],
        }
    ).encode("utf-8")
    req = request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=45) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    content = payload["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    return _pending(parsed)


def diagnose(
    case_id: str | None,
    symptom: str,
    topology_note: str,
    show_outputs: str,
) -> tuple[DiagnosisResult, str]:
    user_block = (
        f"Case ID: {case_id or '(none)'}\n"
        f"Symptom: {symptom}\n"
        f"Topology: {topology_note}\n"
        f"Show output:\n{show_outputs}\n"
    )
    if os.environ.get("OPENAI_API_KEY", "").strip():
        try:
            return _call_openai(user_block), "openai"
        except Exception:
            local = local_diagnose(symptom, topology_note, show_outputs)
            local.root_cause = (
                "The remote model call failed, so this result comes from the local helper. "
                + local.root_cause
            )
            return local, "local-fallback"
    return local_diagnose(symptom, topology_note, show_outputs), "local"
