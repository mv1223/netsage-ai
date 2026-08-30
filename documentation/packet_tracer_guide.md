# Packet Tracer workflow

NetSage AI never opens Packet Tracer by itself. You break a small lab, copy show output, paste it into the web app, review the suggestion, then type the approved change back in Packet Tracer.

## Included Packet Tracer (.pkt) Lab Files

The repository includes ready-to-use Cisco Packet Tracer lab files in the `Packet_Tracer/` directory:
- `NetSage_Master.pkt` — Master lab topology
- `Case_01_Wrong_Gateway.pkt` — Lab pre-configured with Wrong Gateway fault
- `Case_02_Wrong_IP.pkt` — Lab pre-configured with Wrong IP fault
- `Case_03_Wrong_Subnet.pkt` — Lab pre-configured with Wrong Subnet Mask fault
- `Case_04_Duplicate_IP.pkt` — Lab pre-configured with Duplicate IP fault

## Suggested lab shape

Keep topologies small: two switches, one or two routers, a few PCs, optional AP. That is enough for a 5–10 minute demo.

## How a case is reproduced

1. Build the working topology from the case topology note.
2. Confirm a ping or HTTP test that should succeed.
3. Introduce only the fault listed as expected_fault.
4. Copy the show commands named in the case.
5. Paste them on the Troubleshoot page.
6. Run Analyze, then complete human review.
7. Apply the accepted (or edited) fix in Packet Tracer.
8. Run the verification commands and keep the text for the report.

Use this placeholder in the report until you have a real capture:

```
[ADD ACTUAL PACKET TRACER OUTPUT HERE]
```

## Command list used in this project

| Goal | Command |
| Interface up/down and IPs | show ip interface brief |
| Switch port state | show interfaces status |
| Trunk allowed VLANs | show interfaces trunk |
| Access vs trunk | show interfaces &lt;interface&gt; switchport |
| VLAN database | show vlan brief |
| Routing table | show ip route |
| Routing protocol | show ip protocols |
| OSPF adjacency | show ip ospf neighbor |
| Filters | show access-lists |
| NAT table | show ip nat translations |
| NAT counters | show ip nat statistics |
| DHCP pool | show ip dhcp pool |
| DHCP leases | show ip dhcp binding |
| Full device config | show running-config |

## Case-by-case build notes

NET-001 — Default Gateway: PC1 configured with gateway 192.168.10.254 instead of R1 G0/0 (192.168.10.1).
NET-002 — Incorrect IP Address: PC1 assigned 192.168.20.10 on the 192.168.10.0/24 LAN.
NET-003 — Incorrect Subnet Mask: PC1 configured with subnet mask 255.255.255.255 instead of /24.
NET-004 — Duplicate IP Address: PC1 and PC2 both configured with 192.168.10.10.
NET-005 — Incorrect PC2 IP Address: PC2 assigned 192.168.20.11 on the client LAN.
NET-006 — Incorrect PC2 Gateway: PC2 set to gateway 192.168.20.1 (remote router IP).
NET-007 — Incorrect PC2 Subnet Mask: PC2 configured with 255.255.255.255 subnet mask.
NET-008 — Incorrect Server IP Address: Server assigned 192.168.10.100 on the 192.168.20.0/24 LAN.
NET-009 — Incorrect Server Gateway: Server set to gateway 192.168.10.1 (client-side gateway).
NET-010 — Incorrect Server Subnet Mask: Server configured with 255.255.255.255 subnet mask.
NET-011 — Unreachable PC1 Gateway: PC1 points to unused gateway address 192.168.10.254.
NET-012 — Unreachable PC2 Gateway: PC2 points to unused gateway address 192.168.10.254.
NET-013 — Unreachable Server Gateway: Server points to unused gateway address 192.168.20.254.
NET-014 — PC1 Incorrect Subnet Size: PC1 configured with /25 (255.255.255.128) instead of /24.
NET-015 — PC2 Incorrect Subnet Size: PC2 configured with /25 (255.255.255.128) instead of /24.
NET-016 — Server Incorrect Subnet Size: Server configured with /25 (255.255.255.128) instead of /24.
NET-017 — PC1 Wrong Network Address: PC1 assigned 192.168.20.10 instead of 192.168.10.x.
NET-018 — PC2 Wrong Network Address: PC2 assigned 192.168.20.11 instead of 192.168.10.x.
NET-019 — Server Wrong Network Address: Server assigned 192.168.10.100 instead of 192.168.20.x.
NET-020 — PC1 Gateway Typo: PC1 gateway set to 192.168.10.2 (typo).
NET-021 — PC2 Gateway Typo: PC2 gateway set to 192.168.10.2 (typo).
NET-022 — Server Gateway Typo: Server gateway set to 192.168.20.2 (typo).
NET-023 — PC1 Address Conflict with PC2: PC1 assigned PC2's address (192.168.10.11).
NET-024 — PC2 Address Conflict with PC1: PC2 assigned PC1's address (192.168.10.10).
NET-025 — PC1 /30 Subnet Error: PC1 given subnet mask 255.255.255.252 (/30).
NET-026 — PC2 /30 Subnet Error: PC2 given subnet mask 255.255.255.252 (/30).
NET-027 — Server /30 Subnet Error: Server given subnet mask 255.255.255.252 (/30).
NET-028 — PC1 Remote Gateway: PC1 gateway points to remote router G0/1 (192.168.20.1).
NET-029 — PC2 Remote Gateway: PC2 gateway points to remote router G0/1 (192.168.20.1).
NET-030 — Server Remote Gateway: Server gateway points to local router G0/0 (192.168.10.1).

## After the fix

Paste verification output into your report. Do not reuse the CSV teaching output as if it were your live capture.

```
[INSERT ACTUAL SHOW IP ROUTE OUTPUT]
[INSERT ACTUAL SCREENSHOT]
```
