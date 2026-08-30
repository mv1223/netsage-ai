from typing import Any

from pydantic import BaseModel, Field, field_validator


class HumanReviewBlock(BaseModel):
    status: str = "PENDING"
    reason: str = ""


class DiagnosisResult(BaseModel):
    root_cause: str
    confidence: float
    osi_layer: str
    evidence: list[str] = Field(default_factory=list)
    next_command: list[str] = Field(default_factory=list)
    fix_steps: list[str] = Field(default_factory=list)
    verification: list[str] = Field(default_factory=list)
    human_review: HumanReviewBlock = Field(default_factory=HumanReviewBlock)

    @field_validator("confidence")
    @classmethod
    def confidence_range(cls, value: float) -> float:
        if value < 0 or value > 1:
            raise ValueError("confidence must be between 0 and 1")
        return value

    @field_validator("human_review")
    @classmethod
    def force_pending(cls, value: HumanReviewBlock) -> HumanReviewBlock:
        return HumanReviewBlock(status="PENDING", reason="")


class AnalyzeRequest(BaseModel):
    case_id: str | None = None
    symptom: str = ""
    topology_note: str = ""
    show_outputs: str = ""


class ReviewRequest(BaseModel):
    diagnosis_id: int
    decision: str
    reviewer_comment: str = ""
    human_correction: str = ""

    @field_validator("decision")
    @classmethod
    def allowed_decision(cls, value: str) -> str:
        allowed = {"Accepted", "Edited", "Rejected"}
        if value not in allowed:
            raise ValueError("decision must be Accepted, Edited, or Rejected")
        return value


class RuleCheckRequest(BaseModel):
    state: dict[str, Any] | None = None
