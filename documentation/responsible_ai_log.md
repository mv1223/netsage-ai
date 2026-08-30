# Responsible AI log

Human review is part of the grade for this project. The helper is allowed to be wrong. The log is where we record that.

Template rows below are **not** results from a completed Packet Tracer session. Replace each block after you actually run the case.

Live Edited and Rejected reviews also appear in the web app table.

---

## Record 1 — Trunk / VLAN (TEMPLATE)

- Case ID: NS-VLAN-03
- Initial AI diagnosis: [TEMPLATE — replace after lab testing] Possible native VLAN mismatch on the trunk.
- Human correction: [TEMPLATE] Allowed VLAN list on SW-A is missing VLAN 40.
- Why AI was incorrect/incomplete: [TEMPLATE] Native VLAN 1 on both sides looked like a mismatch story. The allowed lists were the stronger evidence.
- Evidence used by human: [TEMPLATE] [ADD ACTUAL PACKET TRACER OUTPUT HERE]
- Final decision: Edited
- Final approved diagnosis: [TEMPLATE] Add VLAN 40 to the SW-A trunk allowed list.

---

## Record 2 — DHCP (TEMPLATE)

- Case ID: NS-DHCP-03
- Initial AI diagnosis: [TEMPLATE — replace after lab testing] DHCP pool is empty or excluded.
- Human correction: [TEMPLATE] Missing ip helper-address on Fa0/0.70.
- Why AI was incorrect/incomplete: [TEMPLATE] APIPA has several causes. The interface config showed the relay was absent.
- Evidence used by human: [TEMPLATE] [ADD ACTUAL PACKET TRACER OUTPUT HERE]
- Final decision: Edited
- Final approved diagnosis: [TEMPLATE] Configure helper 10.1.1.5 on the branch SVI.

---

## Record 3 — ACL (TEMPLATE)

- Case ID: NS-ACL-01
- Initial AI diagnosis: [TEMPLATE — replace after lab testing] HTTP service is down on the server.
- Human correction: [TEMPLATE] ACL WEB-IN denies TCP/80.
- Why AI was incorrect/incomplete: [TEMPLATE] Successful ping was read as “server is fine” without reading the ACL.
- Evidence used by human: [TEMPLATE] [ADD ACTUAL PACKET TRACER OUTPUT HERE]
- Final decision: Edited
- Final approved diagnosis: [TEMPLATE] Adjust line 10; do not remove the whole ACL.

---

## Record 4 — NAT (TEMPLATE)

- Case ID: NS-NAT-02
- Initial AI diagnosis: [TEMPLATE — replace after lab testing] ACL 1 does not match inside hosts.
- Human correction: [TEMPLATE] NAT inside/outside are on the wrong interfaces.
- Why AI was incorrect/incomplete: [TEMPLATE] The ACL permit was correct. The empty translation table came from reversed roles.
- Evidence used by human: [TEMPLATE] [ADD ACTUAL PACKET TRACER OUTPUT HERE]
- Final decision: Edited
- Final approved diagnosis: [TEMPLATE] LAN = ip nat inside, WAN = ip nat outside.

---

## Record 5 — Guest wireless isolation (TEMPLATE)

- Case ID: NS-WL-01 (related isolation: NS-ACL-03)
- Initial AI diagnosis: [TEMPLATE — replace after lab testing] Wrong WPA key.
- Human correction: [TEMPLATE] Staff SSID mapped to guest VLAN / DNS blocked in guest ACL as applicable.
- Why AI was incorrect/incomplete: [TEMPLATE] Clients associated, so the key was not the first problem. The IP or DNS path was.
- Evidence used by human: [TEMPLATE] [ADD ACTUAL PACKET TRACER OUTPUT HERE]
- Final decision: Edited
- Final approved diagnosis: [TEMPLATE] Fix SSID-to-VLAN mapping or permit DNS without dropping guest isolation.

---

## After real testing

[INSERT ACTUAL HUMAN REVIEW RESULT]

Keep the original helper JSON, the reviewer name, the timestamp from SQLite, and the verification CLI.
