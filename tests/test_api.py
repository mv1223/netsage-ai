import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
os.environ["NETSAGE_DB"] = str(ROOT / "data" / "test_netsage.db")

sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "checker"))

from diagnosis import local_diagnose  # noqa: E402
from main import app  # noqa: E402
from schemas import DiagnosisResult  # noqa: E402


@pytest.fixture(scope="module")
def client():
    db_path = Path(os.environ["NETSAGE_DB"])
    if db_path.exists():
        try:
            db_path.unlink()
        except OSError:
            pass
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    if db_path.exists():
        try:
            db_path.unlink()
        except OSError:
            pass


def _get_first_case_id(client: TestClient) -> str:
    res = client.get("/api/cases")
    items = res.json().get("items", [])
    assert len(items) > 0, "No cases found in database"
    return items[0]["case_id"]


def _analyze(client: TestClient) -> int:
    cid = _get_first_case_id(client)
    res = client.post(
        "/api/analyze",
        json={
            "case_id": cid,
            "symptom": "Ping works but HTTP fails",
            "topology_note": "R17 Fa0/1 faces 192.168.200.10",
            "show_outputs": (
                "Extended IP access list WEB-IN\n"
                " 10 deny tcp any host 192.168.200.10 eq www\n"
                "Incoming access list is WEB-IN\n"
            ),
        },
    )
    assert res.status_code == 200, res.text
    return res.json()["id"]


def test_health(client: TestClient):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["ok"] is True


def test_case_search(client: TestClient):
    cid = _get_first_case_id(client)
    res = client.get("/api/cases", params={"q": cid})
    assert res.status_code == 200
    ids = [row["case_id"] for row in res.json()["items"]]
    assert cid in ids


def test_missing_case(client: TestClient):
    res = client.get("/api/cases/NO-SUCH")
    assert res.status_code == 404


def test_analyze_requires_symptom(client: TestClient):
    res = client.post(
        "/api/analyze",
        json={"symptom": "", "topology_note": "x", "show_outputs": "show ip route"},
    )
    assert res.status_code == 400


def test_analyze_requires_show_output(client: TestClient):
    res = client.post(
        "/api/analyze",
        json={"symptom": "PC cannot ping", "topology_note": "x", "show_outputs": ""},
    )
    assert res.status_code == 400


def test_ai_diagnosis_and_json_shape(client: TestClient):
    cid = _get_first_case_id(client)
    res = client.post(
        "/api/analyze",
        json={
            "case_id": cid,
            "symptom": "Ping works but HTTP fails",
            "topology_note": "R17 Fa0/1 faces 192.168.200.10",
            "show_outputs": (
                "Extended IP access list WEB-IN\n"
                " 10 deny tcp any host 192.168.200.10 eq www\n"
                "Incoming access list is WEB-IN\n"
            ),
        },
    )
    assert res.status_code == 200
    body = res.json()
    result = body["result"]
    DiagnosisResult.model_validate(result)
    assert body["review_status"] == "PENDING"
    assert result["human_review"]["status"] == "PENDING"
    assert 0 <= result["confidence"] <= 1


def test_json_validation_rejects_bad_confidence():
    with pytest.raises(Exception):
        DiagnosisResult.model_validate(
            {
                "root_cause": "x",
                "confidence": 1.4,
                "osi_layer": "Layer 3",
                "evidence": [],
                "next_command": [],
                "fix_steps": [],
                "verification": [],
                "human_review": {"status": "PENDING", "reason": ""},
            }
        )


def test_accepted_review(client: TestClient):
    diag_id = _analyze(client)
    res = client.post(
        "/api/reviews",
        json={
            "diagnosis_id": diag_id,
            "decision": "Accepted",
            "reviewer_comment": "Matches the ACL line.",
            "human_correction": "",
        },
    )
    assert res.status_code == 200
    assert res.json()["decision"] == "Accepted"


def test_edited_review_requires_correction(client: TestClient):
    diag_id = _analyze(client)
    res = client.post(
        "/api/reviews",
        json={
            "diagnosis_id": diag_id,
            "decision": "Edited",
            "reviewer_comment": "Need a better cause",
            "human_correction": "",
        },
    )
    assert res.status_code == 400


def test_edited_review_ok(client: TestClient):
    diag_id = _analyze(client)
    res = client.post(
        "/api/reviews",
        json={
            "diagnosis_id": diag_id,
            "decision": "Edited",
            "reviewer_comment": "ACL order is the real issue.",
            "human_correction": "Line 10 deny www is the fault.",
        },
    )
    assert res.status_code == 200


def test_rejected_review_requires_reason(client: TestClient):
    diag_id = _analyze(client)
    res = client.post(
        "/api/reviews",
        json={
            "diagnosis_id": diag_id,
            "decision": "Rejected",
            "reviewer_comment": "",
            "human_correction": "",
        },
    )
    assert res.status_code == 400


def test_rejected_review_ok(client: TestClient):
    diag_id = _analyze(client)
    res = client.post(
        "/api/reviews",
        json={
            "diagnosis_id": diag_id,
            "decision": "Rejected",
            "reviewer_comment": "This paste is from the wrong router.",
            "human_correction": "",
        },
    )
    assert res.status_code == 200


def test_dashboard_agreement_formula(client: TestClient):
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert data["total_cases"] == 30
    if data["reviewed"] == 0:
        assert data["agreement_label"] == "Awaiting real test data"
    else:
        expected = round((data["accepted"] / data["reviewed"]) * 100, 1)
        assert data["agreement_rate"] == expected


def test_local_diagnose_does_not_invent_empty_cli():
    result = local_diagnose("PC cannot ping", "two routers", "")
    assert result.confidence < 0.5
