import csv
from pathlib import Path

from sqlalchemy.orm import Session

from models import Case, ResponsibleAIRecord

ROOT = Path(__file__).resolve().parent.parent

def find_cases_csv() -> Path:
    candidates = [
        ROOT / "data" / "cases.csv",
        ROOT / "data" / "dataset" / "cases (2).csv",
    ]
    for path in candidates:
        if path.exists():
            return path
    data_dir = ROOT / "data"
    if data_dir.exists():
        for csv_file in data_dir.glob("*.csv"):
            return csv_file
        dataset_dir = data_dir / "dataset"
        if dataset_dir.exists():
            for csv_file in dataset_dir.glob("*.csv"):
                return csv_file
    return ROOT / "data" / "cases.csv"


TEMPLATE_RECORDS = [
    {
        "case_id": "NS-VLAN-03",
        "initial_ai_diagnosis": "[TEMPLATE — replace after lab testing] Possible native VLAN mismatch on the trunk.",
        "human_correction": "[TEMPLATE] Allowed VLAN list on SW-A is missing VLAN 40.",
        "why_incorrect": "[TEMPLATE] The model focused on native VLAN because both sides showed native 1. The pasted trunk allowed list was the stronger clue.",
        "evidence_used": "[TEMPLATE] SW-A allowed 1,10,20 vs SW-B allowed 1,10,20,40. Replace with the actual show interfaces trunk paste.",
        "final_decision": "Edited",
        "final_approved_diagnosis": "[TEMPLATE] Add VLAN 40 to the SW-A trunk allowed list, then ping again.",
    },
    {
        "case_id": "NS-DHCP-03",
        "initial_ai_diagnosis": "[TEMPLATE — replace after lab testing] DHCP pool is empty or excluded.",
        "human_correction": "[TEMPLATE] VLAN 70 has no ip helper-address toward 10.1.1.5.",
        "why_incorrect": "[TEMPLATE] APIPA can come from several DHCP faults. The running-config showed the helper was missing, not a full pool.",
        "evidence_used": "[TEMPLATE] show running-config interface fa0/0.70 — Helper address is not set.",
        "final_decision": "Edited",
        "final_approved_diagnosis": "[TEMPLATE] Configure ip helper-address 10.1.1.5 on Fa0/0.70.",
    },
    {
        "case_id": "NS-ACL-01",
        "initial_ai_diagnosis": "[TEMPLATE — replace after lab testing] Server is down or HTTP service is stopped.",
        "human_correction": "[TEMPLATE] ACL WEB-IN line 10 denies TCP/80 to 192.168.200.10.",
        "why_incorrect": "[TEMPLATE] Ping success was treated as 'server is healthy' without reading the ACL. ICMP and HTTP are different.",
        "evidence_used": "[TEMPLATE] show access-lists WEB-IN and inbound application on Fa0/1.",
        "final_decision": "Edited",
        "final_approved_diagnosis": "[TEMPLATE] Replace the HTTP deny with a staff-only permit if the lab requires web access.",
    },
    {
        "case_id": "NS-NAT-02",
        "initial_ai_diagnosis": "[TEMPLATE — replace after lab testing] Access-list 1 does not match inside hosts.",
        "human_correction": "[TEMPLATE] ip nat inside and ip nat outside are on the wrong interfaces.",
        "why_incorrect": "[TEMPLATE] The ACL permit line was correct. Empty translation table came from reversed inside/outside.",
        "evidence_used": "[TEMPLATE] show running-config interface section plus show ip nat translations.",
        "final_decision": "Edited",
        "final_approved_diagnosis": "[TEMPLATE] Move ip nat inside to the LAN interface and ip nat outside to the WAN interface.",
    },
    {
        "case_id": "NS-WL-01",
        "initial_ai_diagnosis": "[TEMPLATE — replace after lab testing] Wrong WPA key on the client.",
        "human_correction": "[TEMPLATE] SSID CAMPUS-STAFF is mapped to VLAN 90 (guest).",
        "why_incorrect": "[TEMPLATE] Clients associated, so the key was not the issue. The IP they received was from the guest subnet.",
        "evidence_used": "[TEMPLATE] AP WLAN mapping and ipconfig showing 192.168.90.40.",
        "final_decision": "Edited",
        "final_approved_diagnosis": "[TEMPLATE] Map CAMPUS-STAFF to VLAN 20 and renew the wireless client address.",
    },
]


def load_cases(db: Session) -> int:
    if db.query(Case).count() > 0:
        return db.query(Case).count()

    csv_path = find_cases_csv()
    if not csv_path.exists():
        return 0

    with csv_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw_row in reader:
            row = {k.lower().strip(): v for k, v in raw_row.items() if k}
            case_id = row.get("case_id", "").strip()
            if not case_id:
                continue
            show_val = row.get("show_outputs") or row.get("show_output") or ""
            db.add(
                Case(
                    case_id=case_id,
                    issue_type=row.get("issue_type", "").strip(),
                    symptom=row.get("symptom", "").strip(),
                    topology_note=row.get("topology_note", "").strip(),
                    show_outputs=show_val.strip(),
                    expected_fault=row.get("expected_fault", "").strip(),
                    osi_layer=row.get("osi_layer", "").strip(),
                    concept=row.get("concept", "").strip(),
                    severity=row.get("severity", "").strip(),
                )
            )
    db.commit()
    return db.query(Case).count()


def load_responsible_ai_templates(db: Session) -> int:
    if db.query(ResponsibleAIRecord).count() > 0:
        return db.query(ResponsibleAIRecord).count()

    for item in TEMPLATE_RECORDS:
        db.add(ResponsibleAIRecord(is_template=1, **item))
    db.commit()
    return db.query(ResponsibleAIRecord).count()
