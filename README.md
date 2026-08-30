# NetSage AI

Lab helper for Cisco Packet Tracer troubleshooting. A student types a symptom and pastes show-command output. The app suggests a likely cause. A person must accept, edit, or reject that suggestion before anyone changes the lab.

This is a college project. It does not log into Packet Tracer and it does not push configuration.

## Problem statement

Junior engineers often collect the right CLI and still jump to the wrong layer. Ping works and HTTP fails, or a PC gets an address and still cannot leave the VLAN. Course worksheets list commands, but they do not sit next to a short, reviewable diagnosis.

## Objective

Build a local web tool that:

- stores 30 original practice cases
- reads pasted Packet Tracer evidence
- returns a structured diagnosis (cause, confidence, OSI layer, next command, fix, verification)
- runs a deterministic Python checker beside the helper
- forces human review on every diagnosis
- keeps a responsible-AI log, including five template rows to replace after real labs

## Features

- Dashboard with case counts, severity, and AI–human agreement
- Case list with search and filters
- Case detail with Analyze / Review / Reset
- Troubleshoot form and diagnosis panel
- Human review: Accepted, Edited, Rejected
- Rule checker (duplicate IP, mask, gateway, interface down, missing VLAN, missing route)
- Responsible AI table (templates clearly marked)
- SQLite storage for cases, diagnoses, and reviews

## Technology used

- React 18, TypeScript, Vite
- FastAPI, SQLAlchemy, SQLite
- Python 3 for the rule checker and tests (pytest)
- 
## System architecture

The browser talks to `/api` on the Vite dev server, which proxies to FastAPI on port 8000. FastAPI loads `data/cases.csv` into SQLite on first start. `/api/analyze` calls either OpenAI (if a key exists) or a local pattern helper. Both paths must return the same JSON shape and leave `human_review.status` as `PENDING`. `/api/rule-check` imports `checker/rule_checker.py` and never calls a model.

## Dataset description

`data/cases.csv` has 30 rows:

| Topic | Count |
| Default Gateway | 9 |
| Subnet Mask / Subnetting | 9 |
| IP Addressing | 6 |
| Duplicate / IP Conflict | 3 |
| Network/Gateway Matching | 3 |

Each row has case_id, issue_type, symptom, topology_note, show_outputs, expected_fault, osi_layer, concept, and severity. The show output is teaching text written for this project, not a dump from a production network.

## AI diagnosis workflow

1. Student pastes symptom, topology, and CLI.
2. Backend refuses empty symptom or empty show output.
3. Helper returns JSON (root cause, confidence 0–1, evidence, next commands, fix steps, verification).
4. Record is stored as PENDING.
5. UI labels it as a suggestion, not an approved fix.
6. Reviewer submits Accepted, Edited, or Rejected.

Prompt text lives in `prompts/diagnose_prompt.md`.

## Rule checker

`checker/rule_checker.py` reads a JSON snapshot. Sample input: `data/sample_network_state.json`. From the project root:

```
python checker/rule_checker.py data/sample_network_state.json
```

## Human review

Edited reviews need a corrected diagnosis and a comment. Rejected reviews need a reason. Accepted reviews store the original helper text plus a comment. Nothing in the UI is treated as approved until that submit step.

## Responsible AI

The Responsible AI page lists five TEMPLATE records (trunk/VLAN, DHCP, ACL, NAT, guest wireless). They are not lab results. After you actually test, replace those rows and keep real Edited/Rejected reviews from the app.

## Dashboard

The dashboard shows total cases, per-topic counts, Critical / High / Medium, and agreement:

agreement rate = (number of Accepted diagnoses / number of reviewed cases) × 100

If no reviews exist, the label is **Awaiting real test data**. Template responsible-AI rows are not counted as reviews.

## Packet Tracer workflow

Typical commands:

- show ip interface brief
- show interfaces status
- show interfaces trunk
- show interfaces &lt;interface&gt; switchport
- show vlan brief
- show ip route
- show ip protocols
- show ip ospf neighbor
- show access-lists
- show ip nat translations
- show ip nat statistics
- show ip dhcp pool
- show ip dhcp binding
- show running-config

Paste the text into Troubleshoot. Apply any accepted fix by hand in Packet Tracer.

## Team contribution

| Area | Owner |
| Dataset and Packet Tracer write-up | [ADD NAME] |
| FastAPI, SQLite, rule checker | [ADD NAME] |
| React pages and demo script | [ADD NAME] |
| Human review notes after lab testing | [ADD NAME] |
