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

NS-VLAN-01 — Put PC1 and S1 in VLAN 20. Leave Fa0/1 in VLAN 1.

NS-VLAN-02 — `switchport access vlan 30` on Fa0/5-7 without `vlan 30`.

NS-VLAN-03 — Allow VLAN 40 on SW-B only. Omit 40 on SW-A.

NS-VLAN-04 — Leave the router-facing port in access mode.

NS-GW-01 — Static PC gateway 192.168.10.254 while R1 is .1.

NS-GW-02 — PC /24, router LAN /26.

NS-GW-03 — `shutdown` on the LAN gateway interface.

NS-GW-04 — Gateway IP from another worksheet subnet.

NS-DHCP-01 — DHCP pool without `default-router`.

NS-DHCP-02 — Pool `network` statement on the wrong prefix.

NS-DHCP-03 — DHCP server on HQ, no helper on the branch SVI.

NS-DHCP-04 — Exclude almost the entire /29.

NS-DNS-01 — DHCP `dns-server` pointing at an unused address.

NS-DNS-02 — Wrong A record for web.campus.lab.

NS-DNS-03 — Guest ACL deny to the DNS subnet.

NS-RT-01 — Static route only on one router of a two-router lab.

NS-RT-02 — Static next hop that is not on the serial /30.

NS-RT-03 — OSPF area 0 on one side, area 1 on the other.

NS-RT-04 — No `ip route 0.0.0.0 0.0.0.0`.

NS-RT-05 — Loopback up, missing from OSPF network list.

NS-ACL-01 — deny tcp eq www in front of permit ip any any.

NS-ACL-02 — Correct SSH ACL applied outbound.

NS-ACL-03 — Guest ACL deny UDP/53.

NS-ACL-04 — deny host before permit 443.

NS-NAT-01 — Inside hosts, no NAT statements.

NS-NAT-02 — inside/outside swapped.

NS-NAT-03 — Static PAT to the wrong inside host.

NS-WL-01 — Staff SSID mapped to guest VLAN.

NS-WL-02 — AP uplink access VLAN 1.

NS-WL-03 — AP switchport shut.

## After the fix

Paste verification output into your report. Do not reuse the CSV teaching output as if it were your live capture.

```
[INSERT ACTUAL SHOW IP ROUTE OUTPUT]
[INSERT ACTUAL SCREENSHOT]
```
