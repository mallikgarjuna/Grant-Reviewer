from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NonEmptyTrimmedStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

EngineMode = Literal["DIAGNOSTIC", "STRICT"]
FindingKind = Literal["MISSING_CONTENT", "PRESENT_CONTENT"]
FindingSeverity = Literal["ERROR", "WARNING", "NOTE"]
AssessmentStatus = Literal["ASSESSED", "NOT_ASSESSABLE"]
ReviewRating = Literal["CRITICAL", "WARNING", "NOTE"]
FailureCode = Literal["CONTRACT_FAILURE", "EXECUTION_FAILURE"]
EvaluationStage = Literal["STEP_1", "STEP_2", "BOTH"]
RuleSeverity = Literal["ERROR", "WARNING"]
ReviewerPolicyEnforcementMode = Literal["PROMPT_ONLY", "POST_CHECK", "BLOCKING"]


class _StrictContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ActivatedSubordinatePromptV1(_StrictContractModel):
    id: NonEmptyTrimmedStr
    prompt: NonEmptyTrimmedStr
    source_locator: str | None = None


class ActivatedExpectationV1(_StrictContractModel):
    expectation_id: str = Field(min_length=1)
    node_logical_id: str = Field(min_length=1)
    check_id: str = Field(default="check.presence", min_length=1)
    required: bool = False
    subordinate_prompts: list[ActivatedSubordinatePromptV1] | None = None


class ActivatedEvaluationCriterionV1(_StrictContractModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    stage: str = Field(min_length=1)
    weight_percent: int
    evaluation_elements: list[ActivatedEvaluationElementV1] = Field(default_factory=list)


class ActivatedEvaluationElementV1(_StrictContractModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    source_hint: str | None = None
    stage: str | None = "BOTH"


class ActivatedReviewerPolicyRuleV1(_StrictContractModel):
    id: str = Field(min_length=1)
    applies_to_stage: EvaluationStage = "BOTH"
    applies_to_node_ids: list[str] = Field(default_factory=list)
    rule_type: str = Field(min_length=1)
    instruction: str = Field(min_length=1)
    severity: RuleSeverity = "WARNING"
    enforcement_mode: ReviewerPolicyEnforcementMode = "PROMPT_ONLY"
    forbidden_terms: list[str] = Field(default_factory=list)
    source_hint: str | None = None


class ActivatedComplianceRuleV1(_StrictContractModel):
    id: str = Field(min_length=1)
    severity: RuleSeverity
    rule_type: str = Field(min_length=1)
    description: str = Field(min_length=1)


class ActivatedStageGatingV1(_StrictContractModel):
    active_stage: str | None = None
    allowed_stages: list[str] = Field(default_factory=list)
    stage_map: dict[str, list[str]] = Field(default_factory=dict)


class ActivatedHierarchyNodeV1(_StrictContractModel):
    id: str = Field(min_length=1)
    parent_id: str | None = None


class ActivatedHierarchyV1(_StrictContractModel):
    nodes: list[ActivatedHierarchyNodeV1] = Field(default_factory=list)
    root_ids: list[str] = Field(default_factory=list)


class ActivatedNestingV1(_StrictContractModel):
    mode: str | None = None
    max_depth: int | None = None
    allow_cross_refs: bool | None = None


class ActivatedPromptKnobsV1(_StrictContractModel):
    temperature: float | None = None
    top_p: float | None = None
    max_tokens: int | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None


class ActivatedCallConfigSnapshotV1(_StrictContractModel):
    schema_version: Literal["v1"]
    expectations: list[ActivatedExpectationV1]
    stage_gating: ActivatedStageGatingV1 | None = None
    hierarchy: ActivatedHierarchyV1 | None = None
    nesting: ActivatedNestingV1 | None = None
    evaluation_criteria: list[ActivatedEvaluationCriterionV1] | None = None
    evaluation_elements: list[ActivatedEvaluationElementV1] | None = None
    compliance_rules: list[ActivatedComplianceRuleV1] | None = None
    reviewer_policy: list[ActivatedReviewerPolicyRuleV1] | None = None
    prompt_knobs: ActivatedPromptKnobsV1 | None = None

    def to_canonical_payload(self) -> dict[str, object]:
        return self.model_dump(mode="json", exclude_none=True, exclude_defaults=True)

    def get(self, key: str, default: object | None = None) -> object:
        return self.to_canonical_payload().get(key, default)


@dataclass(frozen=True)
class ReviewRequestV1:
    request_id: str
    mode: EngineMode
    stage_ref: str
    call_config_digest: str
    call_config_snapshot: ActivatedCallConfigSnapshotV1
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
    risk_taxonomy: str | None = None


@dataclass(frozen=True)
class ReviewCard:
    node_logical_id: str
    expectation_id: str
    rating: ReviewRating
    feedback: str


@dataclass(frozen=True)
class PipelineResult:
    request_id: str
    pipeline_status: Literal["SUCCESS", "FAILURE"]
    failure_code: FailureCode | None
    diagnostics: list[str]
    compatibility_output: dict[str, object]
    findings: list[DiagnosticFindingV1]
    review_cards: list[ReviewCard]
    telemetry: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)
