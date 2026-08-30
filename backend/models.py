from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Case(Base):
    __tablename__ = "cases"

    case_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    issue_type: Mapped[str] = mapped_column(String(32), index=True)
    symptom: Mapped[str] = mapped_column(Text)
    topology_note: Mapped[str] = mapped_column(Text)
    show_outputs: Mapped[str] = mapped_column(Text)
    expected_fault: Mapped[str] = mapped_column(Text)
    osi_layer: Mapped[str] = mapped_column(String(32), index=True)
    concept: Mapped[str] = mapped_column(String(128))
    severity: Mapped[str] = mapped_column(String(16), index=True)

    diagnoses: Mapped[list["Diagnosis"]] = relationship(back_populates="case")


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str | None] = mapped_column(String(32), ForeignKey("cases.case_id"), nullable=True)
    symptom: Mapped[str] = mapped_column(Text)
    topology_note: Mapped[str] = mapped_column(Text)
    show_outputs: Mapped[str] = mapped_column(Text)
    root_cause: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    osi_layer: Mapped[str] = mapped_column(String(32))
    evidence_json: Mapped[str] = mapped_column(Text)
    next_command_json: Mapped[str] = mapped_column(Text)
    fix_steps_json: Mapped[str] = mapped_column(Text)
    verification_json: Mapped[str] = mapped_column(Text)
    result_json: Mapped[str] = mapped_column(Text)
    engine: Mapped[str] = mapped_column(String(32), default="local")
    review_status: Mapped[str] = mapped_column(String(16), default="PENDING", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    case: Mapped[Case | None] = relationship(back_populates="diagnoses")
    review: Mapped["HumanReview | None"] = relationship(back_populates="diagnosis", uselist=False)


class HumanReview(Base):
    __tablename__ = "human_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    diagnosis_id: Mapped[int] = mapped_column(Integer, ForeignKey("diagnoses.id"))
    case_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    decision: Mapped[str] = mapped_column(String(16), index=True)
    ai_diagnosis: Mapped[str] = mapped_column(Text)
    ai_confidence: Mapped[float] = mapped_column(Float)
    human_correction: Mapped[str] = mapped_column(Text, default="")
    reviewer_comment: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    diagnosis: Mapped[Diagnosis] = relationship(back_populates="review")


class ResponsibleAIRecord(Base):
    __tablename__ = "responsible_ai_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(String(32))
    initial_ai_diagnosis: Mapped[str] = mapped_column(Text)
    human_correction: Mapped[str] = mapped_column(Text)
    why_incorrect: Mapped[str] = mapped_column(Text)
    evidence_used: Mapped[str] = mapped_column(Text)
    final_decision: Mapped[str] = mapped_column(String(32))
    final_approved_diagnosis: Mapped[str] = mapped_column(Text)
    is_template: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
