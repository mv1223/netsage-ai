# Responsible AI log

Human review is part of the grade for this project. The helper is allowed to be wrong. The log is where we record that.

Template rows below are **not** results from a completed Packet Tracer session. Replace each block after you actually run the case.

Live Edited and Rejected reviews also appear in the web app table.

---

## Record 1 — Default Gateway (TEMPLATE)

- Case ID: NET-001
- Initial AI diagnosis: [TEMPLATE — replace after lab testing] Incorrect default gateway configured on PC1.
- Human correction: [TEMPLATE] PC1 gateway set to 192.168.10.254 instead of R1 G0/0 (192.168.10.1).
- Why AI was incorrect/incomplete: [TEMPLATE] Focus was on remote side router interface instead of local subnet IP.
- Evidence used by human: [TEMPLATE] [ADD ACTUAL PACKET TRACER OUTPUT HERE]
- Final decision: Edited
- Final approved diagnosis: [TEMPLATE] Change PC1 default gateway to 192.168.10.1.

---

## Record 2 — Subnet Mask / Subnetting (TEMPLATE)

- Case ID: NET-003
- Initial AI diagnosis: [TEMPLATE — replace after lab testing] Subnet mask mismatch on host.
- Human correction: [TEMPLATE] Subnet mask 255.255.255.255 places gateway outside PC1 calculated subnet.
- Why AI was incorrect/incomplete: [TEMPLATE] Missed host mask /32 vs LAN /24 interface.
- Evidence used by human: [TEMPLATE] [ADD ACTUAL PACKET TRACER OUTPUT HERE]
- Final decision: Edited
- Final approved diagnosis: [TEMPLATE] Update PC1 subnet mask to 255.255.255.0.

---

## Record 3 — Duplicate / IP Conflict (TEMPLATE)

- Case ID: NET-004
- Initial AI diagnosis: [TEMPLATE — replace after lab testing] Unreliable LAN communication.
- Human correction: [TEMPLATE] Duplicate IP address conflict between PC1 and PC2 (192.168.10.10).
- Why AI was incorrect/incomplete: [TEMPLATE] Focused on interface status rather than MAC address conflict.
- Evidence used by human: [TEMPLATE] [ADD ACTUAL PACKET TRACER OUTPUT HERE]
- Final decision: Edited
- Final approved diagnosis: [TEMPLATE] Change PC2 address to 192.168.10.11.

---

## Record 4 — Unreachable Gateway (TEMPLATE)

- Case ID: NET-011
- Initial AI diagnosis: [TEMPLATE — replace after lab testing] Unreachable gateway IP.
- Human correction: [TEMPLATE] PC1 points to unused gateway address 192.168.10.254.
- Why AI was incorrect/incomplete: [TEMPLATE] Router G0/0 was up but host pointed to wrong IP.
- Evidence used by human: [TEMPLATE] [ADD ACTUAL PACKET TRACER OUTPUT HERE]
- Final decision: Edited
- Final approved diagnosis: [TEMPLATE] Reconfigure PC1 gateway to 192.168.10.1.

---

## Record 5 — Network/Gateway Matching (TEMPLATE)

- Case ID: NET-028
- Initial AI diagnosis: [TEMPLATE — replace after lab testing] Remote network reachability failure.
- Human correction: [TEMPLATE] PC1 gateway set to R1 G0/1 remote address 192.168.20.1.
- Why AI was incorrect/incomplete: [TEMPLATE] PC1 is on 192.168.10.0/24 LAN, so local gateway is G0/0.
- Evidence used by human: [TEMPLATE] [ADD ACTUAL PACKET TRACER OUTPUT HERE]
- Final decision: Edited
- Final approved diagnosis: [TEMPLATE] Set PC1 gateway to local router interface 192.168.10.1.

---

## After real testing

[INSERT ACTUAL HUMAN REVIEW RESULT]

Keep the original helper JSON, the reviewer name, the timestamp from SQLite, and the verification CLI.
