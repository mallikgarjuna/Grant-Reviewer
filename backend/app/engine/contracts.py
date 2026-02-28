from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

EngineMode = Literal["DIAGNOSTIC", "STRICT"]
FindingKind = Literal["MISSING_CONTENT", "PRESENT_CONTENT"]
FindingSeverity = Literal["ERROR", "WARNING", "NOTE"]
AssessmentStatus = Literal["ASSESSED", "NOT_ASSESSABLE"]
ReviewRating = Literal["CRITICAL", "WARNING", "NOTE"]


@dataclass(frozen=True)
class ReviewRequestV1:
    request_id: str
    mode: EngineMode
    stage_ref: str
    call_config_digest: str
    call_config_snapshot: dict
    proposal_nodes: dict[str, str]


@dataclass(frozen=True)
class SubjectRef:
    node_logical_id: str


@dataclass(frozen=True)
class AnchorV1:
    anchor_type: str
    locator: str
    text_hash: str


@dataclass(frozen=True)
class ObservationV1:
    observation_id: str
    subject_ref: SubjectRef
    expectation_ref: str
    observation_kind: str
    anchor: AnchorV1
    details: dict[str, object]


@dataclass(frozen=True)
class DiagnosticFindingV1:
    finding_id: str
    primary_expectation_ref: str
    subject_ref: SubjectRef
    check_id: str
    finding_kind: FindingKind
    severity: FindingSeverity
    assessment_status: AssessmentStatus
    reason: str


@dataclass(frozen=True)
class ReviewCard:
    node_logical_id: str
    expectation_id: str
    rating: ReviewRating
    feedback: str


@dataclass(frozen=True)
class PipelineResult:
    findings: list[DiagnosticFindingV1]
    review_cards: list[ReviewCard]

    def to_dict(self) -> dict:
        return asdict(self)
