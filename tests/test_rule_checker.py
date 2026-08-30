from rule_checker import (
    check_duplicate_ips,
    check_gateway_mismatch,
    check_interfaces_down,
    check_missing_routes,
    check_missing_vlans,
    check_subnet_masks,
    format_report,
    run_checks,
)


def test_all_required_checks_fire(sample_state):
    findings = run_checks(sample_state)
    codes = {item.code for item in findings}
    assert "DUPLICATE_IP" in codes
    assert "MASK_MISMATCH" in codes
    assert "GATEWAY_MISMATCH" in codes
    assert "INTERFACE_DOWN" in codes
    assert "MISSING_VLAN" in codes
    assert "MISSING_ROUTE" in codes


def test_duplicate_ip_message(sample_state):
    items = check_duplicate_ips(sample_state)
    assert any("192.168.20.21" in item.detail for item in items)


def test_report_header(sample_state):
    text = format_report(run_checks(sample_state))
    assert text.startswith("NetSage Rule Checker")
    assert "[ERROR] Duplicate IP detected" in text
    assert "[ERROR] Gateway mismatch" in text
    assert "[WARNING] Interface is down" in text
    assert "[ERROR] Missing VLAN" in text
    assert "[ERROR] Missing route" in text


def test_individual_helpers_exist(sample_state):
    assert check_subnet_masks(sample_state)
    assert check_gateway_mismatch(sample_state)
    assert check_interfaces_down(sample_state)
    assert check_missing_vlans(sample_state)
    assert check_missing_routes(sample_state)
