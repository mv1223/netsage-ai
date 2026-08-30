# Demo script (5–10 minutes)

Speak in a normal lab voice. Pause for Packet Tracer. Do not claim tests you did not run.

---

“This is NetSage AI. It is a small web app we built for Packet Tracer troubleshooting. You paste a symptom and show output. It suggests a cause. A person still has to accept, edit, or reject that suggestion. The helper is not allowed to apply config.”

[Open Packet Tracer]

“Here is a small topology: [describe your actual file]. We broke one thing on purpose. For this demo we are using case [ID]. The symptom is [read the symptom].”

[Show the failed ping or browser test]

“I am copying show output from the CLI. Common ones for us are show ip interface brief, show vlan brief, show ip route, and show access-lists.”

[Paste into Troubleshoot]

“What's wrong, topology note, network evidence. Analyze Problem.”

[Wait for the diagnosis panel]

“Likely cause, confidence, OSI layer. Why we think this is taken from the paste, not from a hidden capture. Next command is what I would run if I were still unsure. Suggested fix is still pending review.”

“Human review required. I am going to [Accept / Edit / Reject] because [one sentence]. Submit review.”

“Now I type only the approved change in Packet Tracer.”

[Apply fix]

“Verification: [command]. If this lab is not finished yet I will say so and show the placeholder in the report instead of inventing a success.”

[Open Dashboard]

“Thirty cases, split by VLAN, gateway, DHCP, DNS, routing, ACL, NAT, and wireless. Agreement rate uses Accepted divided by reviewed. If we have not reviewed live cases it still says Awaiting real test data.”

[Open Responsible AI]

“Five template rows for the write-up, marked TEMPLATE, plus any real Edited or Rejected rows from this demo.”

“That is the workflow: evidence in, suggestion out, human decision, manual fix, verify.”
