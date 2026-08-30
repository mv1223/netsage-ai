# Project summary — NetSage AI

## Introduction

NetSage AI is a local web application used next to Cisco Packet Tracer. A student pastes a symptom and show-command output. The application returns a structured note: likely cause, confidence, OSI layer, evidence, a next command, a suggested fix, and verification. Every note stays pending until a person accepts, edits, or rejects it.

## Problem

Lab faults are often mixed. A VLAN mistake looks like a gateway mistake until someone reads `show vlan brief`. Language models can invent CLI that was never captured. Course work needs a tool that stays inside the pasted evidence and leaves the last decision with a human.

## Proposed solution

Two paths sit behind one JSON contract. If an API key is present, `prompts/diagnose_prompt.md` is sent to a chat model. If not, a local helper in `backend/diagnosis.py` matches common lab patterns. Beside that, `checker/rule_checker.py` runs six deterministic checks on a JSON snapshot. The React UI is a lab notebook: dashboard, cases, troubleshoot, checker, responsible AI.

## Objectives

- Store 30 original cases across eight topic areas
- Return diagnosis JSON with mandatory pending review
- Record Accepted / Edited / Rejected with comments
- Show agreement only from real reviews
- Document Packet Tracer steps without claiming live captures we did not take

## System design

Vite (port 5173) proxies `/api` to FastAPI (port 8000). SQLAlchemy stores cases, diagnoses, human reviews, and responsible-AI rows in SQLite (`data/netsage.db`). CORS is limited to the local dev origin.

## Dataset

`data/cases.csv` holds the thirty cases. Distribution: VLAN 4, Gateway 4, DHCP 4, DNS 3, Routing 5, ACL 4, NAT 3, Wireless 3. Show output in the CSV is teaching text written for this repository.

## AI prompt design

The prompt file states the role, input block, JSON schema, evidence rules, confidence bands, human-review rule, and security notes (do not disable ACLs just to restore pings). Three worked examples cover trunk/VLAN, DHCP relay, and ACL.

## Rule checker

Checks: duplicate IPv4 addresses, host mask vs gateway mask, gateway not on the host subnet, interface down, VLAN missing on the switch, expected route missing. Sample snapshot: `data/sample_network_state.json`.

## Human review

The Troubleshoot page cannot mark a suggestion as approved by drawing alone. Submit review writes SQLite. Edited needs a correction plus explanation. Rejected needs a reason.

## Dashboard

Cards for total cases and severity. Bar list for the eight topics. Agreement label uses Accepted ÷ reviewed × 100, or “Awaiting real test data”.

## Responsible AI

Five template correction records (VLAN trunk, DHCP, ACL, NAT, wireless/guest) are loaded with `is_template=1`. They must be replaced after lab work. Real Edited/Rejected reviews append extra rows.

## Packet Tracer workflow

Build, break, capture, paste, review, fix by hand, verify. Details in `documentation/packet_tracer_guide.md`.

## Testing methodology

`pytest` covers dataset size and topic counts, case search, diagnosis JSON, confidence validation, rule-checker codes, review paths, dashboard math, and empty-input errors. UI checks are manual in the browser.

## Results

Automated tests: [INSERT ACTUAL PYTEST OUTPUT]

Packet Tracer demos: [ADD ACTUAL PACKET TRACER OUTPUT HERE]

During testing, the team observed that __________.

Do not fill the blanks with invented percentages.

## Limitations

No direct Packet Tracer control. Local helper coverage is limited to patterns in the code. Optional API calls need a key and a network path. Teaching CLI in the CSV is not a substitute for the student’s own captures.

## Future scope

Bulk import of CLI files, before/after diff of show output, faculty review login.

## Conclusion

The project is a working lab notebook: evidence in, structured suggestion out, human decision stored, checker independent of the model. Experimental accuracy is left blank until the team finishes Packet Tracer runs.
