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
        "case_id": "NET-001",
        "initial_ai_diagnosis": "[TEMPLATE — replace after lab testing] Incorrect default gateway configured on PC1.",
        "human_correction": "[TEMPLATE] PC1 gateway set to 192.168.10.254 instead of R1 G0/0 (192.168.10.1).",
        "why_incorrect": "[TEMPLATE] The model flagged remote router G0/1. The local interface ip brief gave the true gateway address.",
        "evidence_used": "[TEMPLATE] show ip interface brief on R1 vs ipconfig gateway on PC1.",
        "final_decision": "Edited",
        "final_approved_diagnosis": "[TEMPLATE] Change PC1 default gateway to 192.168.10.1.",
    },
    {
        "case_id": "NET-003",
        "initial_ai_diagnosis": "[TEMPLATE — replace after lab testing] Subnet mask mismatch on host.",
        "human_correction": "[TEMPLATE] Subnet mask 255.255.255.255 places gateway outside PC1 calculated subnet.",
        "why_incorrect": "[TEMPLATE] Initial check missed host mask /32 vs LAN /24.",
        "evidence_used": "[TEMPLATE] PC1 ipconfig subnet mask 255.255.255.255.",
        "final_decision": "Edited",
        "final_approved_diagnosis": "[TEMPLATE] Update PC1 subnet mask to 255.255.255.0.",
    },
    {
        "case_id": "NET-004",
        "initial_ai_diagnosis": "[TEMPLATE — replace after lab testing] Unreliable LAN communication.",
        "human_correction": "[TEMPLATE] Duplicate IP address conflict between PC1 and PC2 (192.168.10.10).",
        "why_incorrect": "[TEMPLATE] Focus was on switch port state instead of duplicate ARP table entries.",
        "evidence_used": "[TEMPLATE] PC1 and PC2 both show IP 192.168.10.10 and arp -a MAC flap.",
        "final_decision": "Edited",
        "final_approved_diagnosis": "[TEMPLATE] Assign PC2 a unique host address 192.168.10.11.",
    },
    {
        "case_id": "NET-011",
        "initial_ai_diagnosis": "[TEMPLATE — replace after lab testing] Unreachable gateway IP.",
        "human_correction": "[TEMPLATE] PC1 points to unused gateway 192.168.10.254.",
        "why_incorrect": "[TEMPLATE] Router interface was active, but PC1 pointed to unassigned IP.",
        "evidence_used": "[TEMPLATE] show ip interface brief on R1.",
        "final_decision": "Edited",
        "final_approved_diagnosis": "[TEMPLATE] Reconfigure PC1 gateway to 192.168.10.1.",
    },
    {
        "case_id": "NET-028",
        "initial_ai_diagnosis": "[TEMPLATE — replace after lab testing] Remote network reachability failure.",
        "human_correction": "[TEMPLATE] PC1 gateway set to R1 G0/1 remote address 192.168.20.1.",
        "why_incorrect": "[TEMPLATE] PC1 is on 192.168.10.0/24 LAN, so local gateway is G0/0.",
        "evidence_used": "[TEMPLATE] Topology note and show ip interface brief.",
        "final_decision": "Edited",
        "final_approved_diagnosis": "[TEMPLATE] Set PC1 gateway to local router interface 192.168.10.1.",
    },
]


def load_cases(db: Session) -> int:
    csv_path = find_cases_csv()
    if not csv_path.exists():
        return db.query(Case).count()

    csv_cases: dict[str, dict] = {}
    with csv_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw_row in reader:
            row = {k.lower().strip(): v for k, v in raw_row.items() if k}
            case_id = row.get("case_id", "").strip()
            if not case_id:
                continue
            show_val = row.get("show_outputs") or row.get("show_output") or ""
            title_val = row.get("title", "").strip()
            issue_type_val = row.get("issue_type", "").strip() or title_val or "General"
            csv_cases[case_id] = {
                "case_id": case_id,
                "issue_type": issue_type_val,
                "symptom": row.get("symptom", "").strip(),
                "topology_note": row.get("topology_note", "").strip(),
                "show_outputs": show_val.strip(),
                "expected_fault": row.get("expected_fault", "").strip(),
                "osi_layer": row.get("osi_layer", "").strip(),
                "concept": row.get("concept", "").strip(),
                "severity": row.get("severity", "").strip(),
            }

    if not csv_cases:
        return db.query(Case).count()

    existing = {c.case_id: c for c in db.query(Case).all()}
    
    # Upsert cases from CSV
    for cid, data in csv_cases.items():
        if cid in existing:
            obj = existing[cid]
            obj.issue_type = data["issue_type"]
            obj.symptom = data["symptom"]
            obj.topology_note = data["topology_note"]
            obj.show_outputs = data["show_outputs"]
            obj.expected_fault = data["expected_fault"]
            obj.osi_layer = data["osi_layer"]
            obj.concept = data["concept"]
            obj.severity = data["severity"]
        else:
            db.add(Case(**data))

    # Remove cases in DB that are no longer in CSV
    for cid, obj in existing.items():
        if cid not in csv_cases:
            db.delete(obj)

    db.commit()
    return db.query(Case).count()


def load_responsible_ai_templates(db: Session) -> int:
    if db.query(ResponsibleAIRecord).count() > 0:
        return db.query(ResponsibleAIRecord).count()

    for item in TEMPLATE_RECORDS:
        db.add(ResponsibleAIRecord(is_template=1, **item))
    db.commit()
    return db.query(ResponsibleAIRecord).count()
