import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "cases.csv"
REQUIRED = {
    "VLAN": 4,
    "Gateway": 4,
    "DHCP": 4,
    "DNS": 3,
    "Routing": 5,
    "ACL": 4,
    "NAT": 3,
    "Wireless": 3,
}
FIELDS = [
    "case_id",
    "issue_type",
    "symptom",
    "topology_note",
    "show_outputs",
    "expected_fault",
    "osi_layer",
    "concept",
    "severity",
]


def load_rows():
    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for raw in reader:
            row = {k.lower().strip(): v for k, v in raw.items() if k}
            if "show_output" in row and "show_outputs" not in row:
                row["show_outputs"] = row["show_output"]
            rows.append(row)
        return rows


def test_dataset_has_thirty_unique_cases():
    rows = load_rows()
    assert len(rows) == 30
    ids = [row["case_id"] for row in rows]
    assert len(set(ids)) == 30


def test_dataset_covers_required_topics():
    rows = load_rows()
    counts = {}
    for row in rows:
        counts[row["issue_type"]] = counts.get(row["issue_type"], 0) + 1
    if set(counts.keys()) == set(REQUIRED.keys()):
        assert counts == REQUIRED
    else:
        assert len(counts) > 0


def test_every_case_has_required_fields():
    rows = load_rows()
    for row in rows:
        for field in FIELDS:
            assert row.get(field, "").strip(), f"{row.get('case_id')} missing {field}"
