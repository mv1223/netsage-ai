"""NetSage AI HTTP API."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session
from sqlalchemy import func

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "checker"))

from rule_checker import format_report, load_state, run_checks  # noqa: E402

from csv_loader import load_cases, load_responsible_ai_templates
from database import Base, SessionLocal, engine, get_db
from diagnosis import diagnose
from models import Case, Diagnosis, HumanReview, ResponsibleAIRecord
from schemas import AnalyzeRequest, ReviewRequest, RuleCheckRequest


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        load_cases(db)
        load_responsible_ai_templates(db)
    finally:
        db.close()
    yield


app = FastAPI(title="NetSage AI", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def invalid_body(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": "One of the fields is missing or invalid. Check Case ID, review choice, and comments."},
    )


@app.exception_handler(Exception)
async def hidden_server_error(_: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on the server. Try again. Details are not shown here."},
    )

ISSUE_TYPES = [
    "IP Addressing",
    "Default Gateway",
    "Subnet Mask / Subnetting",
    "Duplicate / IP Conflict",
    "Network/Gateway Matching",
]


def _diagnosis_payload(row: Diagnosis) -> dict:
    return {
        "id": row.id,
        "case_id": row.case_id,
        "symptom": row.symptom,
        "topology_note": row.topology_note,
        "show_outputs": row.show_outputs,
        "engine": row.engine,
        "review_status": row.review_status,
        "created_at": row.created_at.isoformat() + "Z",
        "result": json.loads(row.result_json),
    }


@app.get("/")
def root():
    index_file = ROOT / "frontend" / "dist" / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "name": "NetSage AI",
        "message": "This is the API. Open the website at http://127.0.0.1:5173",
    }


@app.get("/api/health")
def health():
    return {"ok": True, "name": "NetSage AI"}


@app.get("/api/cases")
def list_cases(
    q: str | None = None,
    issue_type: str | None = None,
    severity: str | None = None,
    osi_layer: str | None = None,
    review_status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Case)
    if issue_type:
        query = query.filter(Case.issue_type == issue_type)
    if severity:
        query = query.filter(Case.severity == severity)
    if osi_layer:
        query = query.filter(Case.osi_layer == osi_layer)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter((Case.case_id.ilike(like)) | (Case.symptom.ilike(like)))

    rows = query.order_by(Case.case_id).all()
    items = []
    for case in rows:
        latest = (
            db.query(Diagnosis)
            .filter(Diagnosis.case_id == case.case_id)
            .order_by(Diagnosis.created_at.desc())
            .first()
        )
        status = latest.review_status if latest else "NONE"
        if review_status and status != review_status:
            continue
        items.append(
            {
                "case_id": case.case_id,
                "issue_type": case.issue_type,
                "symptom": case.symptom,
                "severity": case.severity,
                "osi_layer": case.osi_layer,
                "concept": case.concept,
                "review_status": status,
            }
        )
    return {"items": items, "count": len(items)}


@app.get("/api/cases/{case_id}")
def get_case(case_id: str, db: Session = Depends(get_db)):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="That case ID is not in the dataset.")
    latest = (
        db.query(Diagnosis)
        .filter(Diagnosis.case_id == case_id)
        .order_by(Diagnosis.created_at.desc())
        .first()
    )
    return {
        "case_id": case.case_id,
        "issue_type": case.issue_type,
        "symptom": case.symptom,
        "topology_note": case.topology_note,
        "show_outputs": case.show_outputs,
        "expected_fault": case.expected_fault,
        "osi_layer": case.osi_layer,
        "concept": case.concept,
        "severity": case.severity,
        "latest_diagnosis": _diagnosis_payload(latest) if latest else None,
    }


@app.post("/api/analyze")
def analyze(body: AnalyzeRequest, db: Session = Depends(get_db)):
    symptom = (body.symptom or "").strip()
    show_outputs = (body.show_outputs or "").strip()
    if not symptom:
        raise HTTPException(status_code=400, detail="Please describe what is wrong (the symptom).")
    if not show_outputs:
        raise HTTPException(
            status_code=400,
            detail="Paste at least one show-command output. The helper will not invent CLI.",
        )

    case_id = (body.case_id or "").strip() or None
    if case_id and not db.get(Case, case_id):
        raise HTTPException(status_code=404, detail="That case ID is not in the dataset.")

    try:
        result, engine_name = diagnose(
            case_id,
            symptom,
            body.topology_note or "",
            show_outputs,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"The diagnosis JSON was invalid: {exc}") from exc

    row = Diagnosis(
        case_id=case_id,
        symptom=symptom,
        topology_note=body.topology_note or "",
        show_outputs=show_outputs,
        root_cause=result.root_cause,
        confidence=result.confidence,
        osi_layer=result.osi_layer,
        evidence_json=json.dumps(result.evidence),
        next_command_json=json.dumps(result.next_command),
        fix_steps_json=json.dumps(result.fix_steps),
        verification_json=json.dumps(result.verification),
        result_json=result.model_dump_json(),
        engine=engine_name,
        review_status="PENDING",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _diagnosis_payload(row)


@app.post("/api/reviews")
def submit_review(body: ReviewRequest, db: Session = Depends(get_db)):
    row = db.get(Diagnosis, body.diagnosis_id)
    if not row:
        raise HTTPException(status_code=404, detail="No diagnosis exists with that id.")
    if row.review_status != "PENDING":
        raise HTTPException(status_code=400, detail="This diagnosis already has a review.")

    comment = (body.reviewer_comment or "").strip()
    correction = (body.human_correction or "").strip()

    if body.decision == "Rejected" and not comment:
        raise HTTPException(status_code=400, detail="A rejection needs a reason.")
    if body.decision == "Edited":
        if not correction:
            raise HTTPException(status_code=400, detail="Edited reviews need a corrected diagnosis.")
        if not comment:
            raise HTTPException(status_code=400, detail="Edited reviews need a short explanation.")
    if body.decision == "Accepted" and not comment:
        comment = "Accepted as written."

    review = HumanReview(
        diagnosis_id=row.id,
        case_id=row.case_id,
        decision=body.decision,
        ai_diagnosis=row.root_cause,
        ai_confidence=row.confidence,
        human_correction=correction,
        reviewer_comment=comment,
    )
    row.review_status = body.decision.upper()
    db.add(review)

    if body.decision in {"Edited", "Rejected"} and row.case_id:
        approved = correction if body.decision == "Edited" else "Not approved — see reviewer comment."
        db.add(
            ResponsibleAIRecord(
                case_id=row.case_id,
                initial_ai_diagnosis=row.root_cause,
                human_correction=correction or comment,
                why_incorrect=comment,
                evidence_used=row.show_outputs[:1000],
                final_decision=body.decision,
                final_approved_diagnosis=approved,
                is_template=0,
            )
        )

    db.commit()
    db.refresh(review)
    return {
        "id": review.id,
        "diagnosis_id": review.diagnosis_id,
        "case_id": review.case_id,
        "decision": review.decision,
        "ai_diagnosis": review.ai_diagnosis,
        "ai_confidence": review.ai_confidence,
        "human_correction": review.human_correction,
        "reviewer_comment": review.reviewer_comment,
        "created_at": review.created_at.isoformat() + "Z",
    }


@app.post("/api/cases/{case_id}/reset")
def reset_case(case_id: str, db: Session = Depends(get_db)):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="That case ID is not in the dataset.")
    diags = db.query(Diagnosis).filter(Diagnosis.case_id == case_id).all()
    ids = [d.id for d in diags]
    if ids:
        db.query(HumanReview).filter(HumanReview.diagnosis_id.in_(ids)).delete(synchronize_session=False)
        db.query(Diagnosis).filter(Diagnosis.case_id == case_id).delete(synchronize_session=False)
    db.commit()
    return {"ok": True, "case_id": case_id}


@app.get("/api/reviews")
def list_reviews(db: Session = Depends(get_db)):
    rows = db.query(HumanReview).order_by(HumanReview.created_at.desc()).all()
    return {
        "items": [
            {
                "id": r.id,
                "diagnosis_id": r.diagnosis_id,
                "case_id": r.case_id,
                "decision": r.decision,
                "ai_diagnosis": r.ai_diagnosis,
                "ai_confidence": r.ai_confidence,
                "human_correction": r.human_correction,
                "reviewer_comment": r.reviewer_comment,
                "created_at": r.created_at.isoformat() + "Z",
            }
            for r in rows
        ]
    }


@app.get("/api/responsible-ai")
def responsible_ai(db: Session = Depends(get_db)):
    rows = (
        db.query(ResponsibleAIRecord)
        .order_by(ResponsibleAIRecord.is_template.desc(), ResponsibleAIRecord.id)
        .all()
    )
    return {
        "items": [
            {
                "id": r.id,
                "case_id": r.case_id,
                "initial_ai_diagnosis": r.initial_ai_diagnosis,
                "human_correction": r.human_correction,
                "why_incorrect": r.why_incorrect,
                "evidence_used": r.evidence_used,
                "final_decision": r.final_decision,
                "final_approved_diagnosis": r.final_approved_diagnosis,
                "is_template": bool(r.is_template),
                "created_at": r.created_at.isoformat() + "Z",
            }
            for r in rows
        ]
    }


@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db)):
    total = db.query(Case).count()
    by_type = {
        row[0]: row[1]
        for row in db.query(Case.issue_type, func.count(Case.case_id)).group_by(Case.issue_type)
    }
    by_sev = {
        row[0]: row[1]
        for row in db.query(Case.severity, func.count(Case.case_id)).group_by(Case.severity)
    }
    reviews = db.query(HumanReview).all()
    accepted = sum(1 for r in reviews if r.decision == "Accepted")
    edited = sum(1 for r in reviews if r.decision == "Edited")
    rejected = sum(1 for r in reviews if r.decision == "Rejected")
    reviewed = len(reviews)
    if reviewed == 0:
        agreement = None
        agreement_label = "Awaiting real test data"
    else:
        agreement = round((accepted / reviewed) * 100, 1)
        agreement_label = f"{agreement}%"

    db_types = [t[0] for t in db.query(Case.issue_type).distinct().all() if t[0]]
    all_types = list(dict.fromkeys(ISSUE_TYPES + db_types))
    return {
        "total_cases": total,
        "by_issue_type": {name: by_type.get(name, 0) for name in all_types},
        "critical": by_sev.get("Critical", 0),
        "high": by_sev.get("High", 0),
        "medium": by_sev.get("Medium", 0),
        "low": by_sev.get("Low", 0),
        "accepted": accepted,
        "edited": edited,
        "rejected": rejected,
        "reviewed": reviewed,
        "agreement_rate": agreement,
        "agreement_label": agreement_label,
    }


@app.post("/api/rule-check")
def rule_check(body: RuleCheckRequest):
    try:
        if body.state is None:
            snapshot = ROOT / "data" / "sample_network_state.json"
            state = load_state(snapshot)
        else:
            state = body.state
        findings = run_checks(state)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read the network snapshot: {exc}") from exc
    return {
        "report": format_report(findings),
        "findings": [item.as_dict() for item in findings],
        "error_count": sum(1 for item in findings if item.level == "ERROR"),
        "warning_count": sum(1 for item in findings if item.level == "WARNING"),
    }


frontend_dist = ROOT / "frontend" / "dist"
if frontend_dist.exists():
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")


