"""backend/app/services/structured_reviewer_service.py
Structured review service for multi-node proposal assessments.
"""

from __future__ import annotations

import hashlib
import logging
import os
from datetime import datetime
from typing import Any
from uuid import UUID

from app.engine.contracts import PipelineResult
from app.engine.errors import EngineContractError, EngineErrorCode
from app.engine.pipeline_v1 import run_review_pipeline
from app.engine.review_request_validator import (
    ReviewRequestValidationError,
    canonicalize_for_digest,
    validate_review_request_payload,
)
from app.models.domain import (
    AssessmentStatus,
    NodeExpectation,
    Review,
    ReviewCard,
    ReviewDetailMode,
    ReviewFinding,
    ReviewRating,
    ReviewStatus,
)
from app.repositories.review_repository import ReviewRepository
from app.services.llm_client import LLMClientProtocol, OpenAIClient
from app.services.node_role_resolution import (
    resolve_supporting_node_logical_ids_for_primary_path,
)
from app.services.review_execution_core import ReviewExecutionCore
from app.services.reviewer_policy import (
    ReviewerPolicyRule,
    ReviewStage,
    compute_stage_scope_leaf_ids,
    find_policy_violations,
    get_applicable_reviewer_policy_rules,
)
from app.services.structured_review_synthesis_service import (
    StructuredReviewSynthesisAcceptedResult,
    StructuredReviewSynthesisRequest,
    StructuredReviewSynthesisResult,
    StructuredReviewSynthesisService,
)

logger = logging.getLogger(__name__)

ALIGNMENT_ELEMENT_IDS = {
    "elem_cv_idea_alignment",
    "elem_alignment_plan_credibility",
}
ALIGNMENT_REQUIRED_NODES = ("academic_profile", "key_outputs")
STRUCTURED_SUMMARY_COMPLETED_PREFIX = "Structured review completed with"
STRUCTURED_POLICY_BLOCKING_PREFIX = "POLICY_BLOCKING:"
STRUCTURED_POLICY_WARNING_PREFIX = "Reviewer-policy warnings:"
WF0060_ERC_CONTAINER_NODE_IDS = {"part_a", "budget", "part_b", "b1", "b2"}
WF0069_ACTIONABILITY_CALL_CODES = {
    "nwo_veni_2025_preproposal",
    "erc_stg_2026_full",
    "MSCA-PF-2025",
}
WF0076_SUBORDINATE_PROMPT_PRESENTATION_CALL_CODES = {"ERC-2026-PoC"}
WF0077_DETERMINISTIC_RESEARCHER_GUIDANCE_CALL_CODES = {"ERC-2026-PoC"}
WF0076_SUBORDINATE_PROMPT_REASON_PREFIX = "content_evaluated;subordinate_prompt_ids="
WF0081_FINDING_MAPPING_FAILURE_CODE = "WF0081_FINDING_MAPPING_FAILED"
WF0081_FINDING_SEVERITY_TO_RATING: dict[str, ReviewRating] = {
    "ERROR": ReviewRating.CRITICAL,
    "WARNING": ReviewRating.WARNING,
    "NOTE": ReviewRating.NOTE,
}


class ReviewFindingMappingError(ValueError):
    """Raised when a diagnostic finding cannot be persisted safely."""

    def __init__(self, *, message: str, finding_id: str) -> None:
        self.message = message
        self.finding_id = finding_id
        super().__init__(message)


class StructuredReviewerService:
    """Service for generating structured multi-node reviews."""

    def __init__(
        self,
        repository: ReviewRepository,
        llm_client: LLMClientProtocol | None = None,
        execution_core: ReviewExecutionCore | None = None,
        synthesis_service: StructuredReviewSynthesisService | None = None,
    ) -> None:
        self.repository = repository
        self._llm_client = llm_client
        self._timeout_seconds = float(os.getenv("REVIEW_TIMEOUT_SECONDS", "30"))
        self._execution_core = execution_core
        self._synthesis_service = synthesis_service
        self.last_synthesis_requests: tuple[StructuredReviewSynthesisRequest, ...] = ()
        self.last_synthesis_results: tuple[StructuredReviewSynthesisResult, ...] = ()

    @property
    def llm_client(self) -> LLMClientProtocol:
        """Lazy-load LLM client."""
        if self._llm_client is None:
            self._llm_client = OpenAIClient()
        return self._llm_client

    @property
    def execution_core(self) -> ReviewExecutionCore:
        if self._execution_core is None:
            self._execution_core = ReviewExecutionCore(
                llm_client=self.llm_client,
                timeout_seconds=self._timeout_seconds,
            )
        return self._execution_core

    @property
    def synthesis_service(self) -> StructuredReviewSynthesisService:
        if self._synthesis_service is None:
            self._synthesis_service = StructuredReviewSynthesisService(
                llm_client=self.llm_client
            )
        return self._synthesis_service

    def _partition_expectations(
        self,
        *,
        node_logical_id: str,
        expectations: list[NodeExpectation],
        submitted_text_by_node: dict[str, str],
    ) -> tuple[list[NodeExpectation], list[tuple[NodeExpectation, str]]]:
        assessable: list[NodeExpectation] = []
        not_assessable: list[tuple[NodeExpectation, str]] = []

        for expectation in expectations:
            if not self._needs_alignment_context(node_logical_id, expectation):
                assessable.append(expectation)
                continue

            missing_nodes = [
                upstream_node
                for upstream_node in ALIGNMENT_REQUIRED_NODES
                if not submitted_text_by_node.get(upstream_node, "").strip()
            ]
            if missing_nodes:
                not_assessable.append(
                    (
                        expectation,
                        "Missing required context from: " + ", ".join(missing_nodes),
                    )
                )
            else:
                assessable.append(expectation)

        return assessable, not_assessable

    def generate_structured_review_pipeline_v1(
        self,
        *,
        review_stage: ReviewStage,
        call_id: UUID,
        nodes: list[tuple[str, str]],
        external_user_id: str,
        idempotency_key: str | None = None,
        request_payload_sha256: str | None = None,
        idempotency_expires_at: datetime | None = None,
        call_config_digest_override: str | None = None,
        detail_mode: ReviewDetailMode = ReviewDetailMode.LEGACY_CARDS,
    ) -> tuple[Review, list[ReviewCard]]:
        if not nodes:
            raise ValueError("At least one node is required.")
        self.last_synthesis_requests = ()
        self.last_synthesis_results = ()

        template = self.repository.get_active_prompt_template()
        if template is None:
            raise ValueError("No active prompt template found.")

        call = self.repository.get_call_by_id(call_id)
        if call is None:
            raise ValueError("Funding call not found.")
        call_definition = self.repository.get_call_definition_by_call_id(call_id)
        supporting_node_ids = resolve_supporting_node_logical_ids_for_primary_path(
            call_definition
        )
        submitted_supporting_ids = sorted(
            {
                node_logical_id
                for node_logical_id, _ in nodes
                if node_logical_id in supporting_node_ids
            }
        )
        if submitted_supporting_ids:
            raise ValueError(
                "Supporting node_logical_id values are not allowed for primary review path: "
                + ", ".join(submitted_supporting_ids)
            )

        call_nodes = self.repository.get_nodes_for_call(call_id)
        node_by_logical_id = {
            node.logical_id: node
            for node, _ in call_nodes
            if isinstance(node.logical_id, str) and node.logical_id
        }
        submitted_text_by_node = {
            node_logical_id: text for node_logical_id, text in nodes
        }
        submitted_leaf_ids = [node_logical_id for node_logical_id, _ in nodes]
        # WF-0070 Task 6: Compute stage-eligible leaf IDs from the authoritative
        # contract snapshot at review-run time (not recomputed at read time).
        # Phase 3.3 PB-1: Only include nodes that have expectations (true leaves).
        nodes_with_expectations = {
            node.logical_id
            for node, has_expectations in call_nodes
            if has_expectations and isinstance(node.logical_id, str)
        }
        stage_scope_leaf_ids = compute_stage_scope_leaf_ids(
            call_definition=call_definition,
            review_stage=review_stage,
            nodes_with_expectations=nodes_with_expectations,
        )
        structured_payload = {
            "call_id": str(call_id),
            "call_name": call.name,
            "review_stage": review_stage,
            "nodes": submitted_text_by_node,
            "submitted_leaf_ids": submitted_leaf_ids,
            "stage_scope_leaf_ids": stage_scope_leaf_ids,
            "legacy_ambiguous_container_ids": [],
            "moved_legacy_node_references": [],
            "engine_path": "pipeline_v1",
        }

        review = self.repository.create_review(
            template_id=template.id,
            snippet_id=None,
            external_user_id=external_user_id,
            idempotency_key=idempotency_key,
            request_payload_sha256=request_payload_sha256,
            idempotency_expires_at=idempotency_expires_at,
            review_type="structured",
            detail_mode=detail_mode,
            structured_payload=structured_payload,
        )
        review.llm_model = "engine-pipeline-v1"
        self.repository.update_review(review)

        expectation_map: dict[str, NodeExpectation] = {}
        not_assessable_payloads: list[
            tuple[UUID, ReviewRating, str, AssessmentStatus, str | None, str | None]
        ] = []
        request_expectations: list[dict[str, object]] = []
        applicable_policy_by_node: dict[str, list[ReviewerPolicyRule]] = {}
        subordinate_prompts_by_element_id = (
            self._build_subordinate_prompts_by_element_id(call_definition)
        )
        for node_logical_id, _ in nodes:
            node = node_by_logical_id.get(node_logical_id)
            if node is None:
                return self._fail_contract_error(
                    review,
                    code=EngineErrorCode.MALFORMED_REVIEW_REQUEST.value,
                    message=f"Unknown node_logical_id: '{node_logical_id}'",
                )
            if (
                call.code == "erc_stg_2026_full"
                and node_logical_id in WF0060_ERC_CONTAINER_NODE_IDS
            ):
                return self._fail_contract_error(
                    review,
                    code=EngineErrorCode.MALFORMED_REVIEW_REQUEST.value,
                    message=f"ERC container node_logical_id is not submittable: '{node_logical_id}'",
                )
            applicable_rules = self._resolve_reviewer_policy_rules(
                call_definition=call_definition,
                node_logical_id=node_logical_id,
                review_stage=review_stage,
            )
            applicable_policy_by_node[node_logical_id] = applicable_rules

            expectations = self.repository.get_expectations_for_node(node.id)
            assessable, not_assessable = self._partition_expectations(
                node_logical_id=node_logical_id,
                expectations=expectations,
                submitted_text_by_node=submitted_text_by_node,
            )

            for expectation, reason in not_assessable:
                not_assessable_payloads.append(
                    (
                        expectation.id,
                        ReviewRating.NOTE,
                        "Not assessable due to missing cross-node context.",
                        AssessmentStatus.NOT_ASSESSABLE,
                        reason,
                        None,
                    )
                )

            for expectation in assessable:
                expectation_id = str(expectation.id)
                expectation_payload: dict[str, object] = {
                    "expectation_id": expectation_id,
                    "node_logical_id": node_logical_id,
                }
                if expectation.expectation_strength.value == "MANDATORY":
                    expectation_payload["required"] = True
                element_logical_id = (
                    expectation.element.logical_id if expectation.element else None
                )
                if isinstance(element_logical_id, str):
                    subordinate_prompts = subordinate_prompts_by_element_id.get(
                        element_logical_id
                    )
                    if subordinate_prompts:
                        expectation_payload["subordinate_prompts"] = [
                            dict(prompt) for prompt in subordinate_prompts
                        ]
                request_expectations.append(expectation_payload)
                expectation_map[expectation_id] = expectation

        call_config_snapshot = {
            "schema_version": "v1",
            "expectations": request_expectations,
        }
        canonical_snapshot = canonicalize_for_digest(call_config_snapshot)
        computed_digest = (
            "sha256:" + hashlib.sha256(canonical_snapshot.encode("utf-8")).hexdigest()
        )
        payload = {
            "request_id": str(review.id),
            "mode": "DIAGNOSTIC",
            "stage_ref": review_stage,
            "call_config_snapshot": call_config_snapshot,
            "call_config_digest": call_config_digest_override or computed_digest,
            "proposal_nodes": submitted_text_by_node,
        }

        try:
            review_request = validate_review_request_payload(payload)
            result = (
                run_review_pipeline(review_request)
                if request_expectations
                else PipelineResult(
                    request_id=str(review.id),
                    pipeline_status="SUCCESS",
                    failure_code=None,
                    diagnostics=[],
                    compatibility_output={},
                    findings=[],
                    review_cards=[],
                    telemetry={},
                )
            )
        except ReviewRequestValidationError as err:
            return self._fail_contract_error(review, code=err.code, message=err.message)
        except EngineContractError as err:
            return self._fail_contract_error(
                review,
                code=err.code.value,
                message=err.message,
            )
        except TimeoutError as err:
            return self._fail_execution_error(
                review,
                code=EngineErrorCode.TIMEOUT.value,
                message=str(err),
            )
        except Exception as err:
            return self._fail_execution_error(
                review,
                code=EngineErrorCode.ENGINE_EXECUTION_FAILED.value,
                message=str(err),
            )

        unresolved = [
            card.expectation_id
            for card in result.review_cards
            if card.expectation_id not in expectation_map
        ]
        if unresolved:
            return self._fail_contract_error(
                review,
                code=EngineErrorCode.EXPECTATION_REF_UNRESOLVABLE.value,
                message=f"Unresolvable expectation ref: {sorted(set(unresolved))[0]}",
            )

        feedback_texts_by_node: dict[str, list[str]] = {}
        for card in result.review_cards:
            feedback_texts_by_node.setdefault(card.node_logical_id, []).append(
                card.feedback
            )

        blocking_policy_violations: list[str] = []
        warning_policy_violations: list[str] = []
        for node_logical_id, node_feedbacks in feedback_texts_by_node.items():
            applicable_rules = applicable_policy_by_node.get(node_logical_id, [])
            blocking, warning = find_policy_violations(
                feedback_texts=node_feedbacks,
                policy_rules=applicable_rules,
            )
            blocking_policy_violations.extend(blocking)
            warning_policy_violations.extend(warning)
        if blocking_policy_violations:
            review.status = ReviewStatus.FAILED
            review.overall_summary = (
                f"{STRUCTURED_POLICY_BLOCKING_PREFIX} "
                + "; ".join(blocking_policy_violations)
            )
            self.repository.update_review(review)
            return review, []

        card_payloads: list[
            tuple[UUID, ReviewRating, str, AssessmentStatus, str | None, str | None]
        ] = list(not_assessable_payloads)
        synthesis_requests: list[StructuredReviewSynthesisRequest] = []
        synthesis_results: list[StructuredReviewSynthesisResult] = []
        for card in result.review_cards:
            expectation = expectation_map[card.expectation_id]
            feedback_text = self._resolve_feedback_text_for_card(
                call_code=call.code,
                node_logical_id=card.node_logical_id,
                expectation=expectation,
                feedback_text=card.feedback,
                subordinate_prompts_by_element_id=subordinate_prompts_by_element_id,
            )
            synthesized_companion_text: str | None = None
            synthesis_request = self._build_synthesis_request_for_card(
                call_code=call.code,
                node_logical_id=card.node_logical_id,
                node_title=(
                    node_by_logical_id[card.node_logical_id].title
                    if card.node_logical_id in node_by_logical_id
                    else None
                ),
                expectation=expectation,
                feedback_text=feedback_text,
                submitted_text_by_node=submitted_text_by_node,
                subordinate_prompts_by_element_id=subordinate_prompts_by_element_id,
            )
            if synthesis_request is not None:
                synthesis_requests.append(synthesis_request)
                synthesis_result = self.synthesis_service.attempt_card_synthesis(
                    synthesis_request
                )
                synthesis_results.append(synthesis_result)
                if isinstance(synthesis_result, StructuredReviewSynthesisAcceptedResult):
                    synthesized_companion_text = (
                        synthesis_result.synthesized_feedback
                    )

            card_payloads.append(
                (
                    expectation.id,
                    ReviewRating[card.rating],
                    feedback_text,
                    AssessmentStatus.ASSESSED,
                    None,
                    synthesized_companion_text,
                )
            )

        self.last_synthesis_requests = tuple(synthesis_requests)
        self.last_synthesis_results = tuple(synthesis_results)

        try:
            if detail_mode == ReviewDetailMode.REVIEWED_NODE_FINDINGS:
                findings = self._build_review_findings_from_pipeline_result(
                    review=review,
                    result=result,
                    expectation_map=expectation_map,
                    node_by_logical_id=node_by_logical_id,
                )
                self.repository.create_review_findings_batch(findings=findings)
                cards = []
                persisted_item_count = len(findings)
            else:
                cards = self.repository.create_review_cards_batch(
                    review_id=review.id,
                    cards=card_payloads,
                )
                persisted_item_count = len(cards)
        except ReviewFindingMappingError as err:
            self.repository.rollback()
            logger.error(
                "%s review_id=%s finding_id=%s message=%s",
                WF0081_FINDING_MAPPING_FAILURE_CODE,
                review.id,
                err.finding_id,
                err.message,
            )
            return self._fail_contract_error(
                review,
                code=WF0081_FINDING_MAPPING_FAILURE_CODE,
                message=err.message,
            )
        except Exception as err:
            self.repository.rollback()
            return self._fail_execution_error(
                review,
                code=EngineErrorCode.ENGINE_EXECUTION_FAILED.value,
                message=str(err),
            )

        review.status = ReviewStatus.COMPLETED
        review.overall_summary = (
            f"{STRUCTURED_SUMMARY_COMPLETED_PREFIX} "
            f"{persisted_item_count} findings via pipeline_v1."
        )
        if warning_policy_violations:
            review.overall_summary += (
                f" {STRUCTURED_POLICY_WARNING_PREFIX} "
                + "; ".join(warning_policy_violations)
            )
        review.overall_rating = ReviewRating.NOTE
        self.repository.update_review(review)
        return review, cards

    def _build_review_findings_from_pipeline_result(
        self,
        *,
        review: Review,
        result: PipelineResult,
        expectation_map: dict[str, NodeExpectation],
        node_by_logical_id: dict[str, Any],
    ) -> list[ReviewFinding]:
        findings: list[ReviewFinding] = []
        for finding in result.findings:
            expectation = expectation_map.get(finding.primary_expectation_ref)
            if expectation is None:
                raise ReviewFindingMappingError(
                    finding_id=finding.finding_id,
                    message=(
                        "Unresolvable expectation ref for persisted review finding: "
                        f"{finding.primary_expectation_ref}"
                    ),
                )

            proposal_node = node_by_logical_id.get(finding.subject_ref.node_logical_id)
            if proposal_node is None:
                raise ReviewFindingMappingError(
                    finding_id=finding.finding_id,
                    message=(
                        "Unresolvable proposal node snapshot for persisted review finding: "
                        f"{finding.subject_ref.node_logical_id}"
                    ),
                )

            evaluation_element = expectation.element
            evaluation_criterion = (
                evaluation_element.criterion if evaluation_element is not None else None
            )
            if evaluation_element is None or evaluation_criterion is None:
                raise ReviewFindingMappingError(
                    finding_id=finding.finding_id,
                    message=(
                        "Missing evaluation criteria/elements snapshot for persisted "
                        f"review finding: {finding.primary_expectation_ref}"
                    ),
                )

            assessment_status = AssessmentStatus(finding.assessment_status)
            severity = self._resolve_review_finding_severity(
                assessment_status=assessment_status,
                pipeline_severity=finding.severity,
            )
            findings.append(
                ReviewFinding(
                    review_id=review.id,
                    proposal_node_id=proposal_node.id,
                    proposal_node_logical_id_snapshot=proposal_node.logical_id
                    or proposal_node.title,
                    proposal_node_title_snapshot=proposal_node.title,
                    evaluation_criterion_logical_id_snapshot=(
                        evaluation_criterion.logical_id or evaluation_criterion.name
                    ),
                    evaluation_criterion_name_snapshot=evaluation_criterion.name,
                    evaluation_element_logical_id_snapshot=(
                        evaluation_element.logical_id or evaluation_element.name
                    ),
                    evaluation_element_name_snapshot=evaluation_element.name,
                    severity=severity,
                    assessment_status=assessment_status,
                    issue_summary_text=finding.reason.strip(),
                    evidence_basis_text=finding.reason.strip(),
                    actionable_feedback_text=finding.reason.strip(),
                )
            )

        return findings

    def _resolve_review_finding_severity(
        self,
        *,
        assessment_status: AssessmentStatus,
        pipeline_severity: str,
    ) -> ReviewRating:
        if assessment_status == AssessmentStatus.REQUIREMENTS_MET:
            return ReviewRating.SUCCESS
        severity = WF0081_FINDING_SEVERITY_TO_RATING.get(pipeline_severity)
        if severity is None:
            raise ReviewFindingMappingError(
                finding_id="unknown",
                message=f"Unsupported finding severity for persisted review finding: {pipeline_severity}",
            )
        return severity

    def _fail_contract_error(
        self,
        review: Review,
        *,
        code: str,
        message: str,
    ) -> tuple[Review, list[ReviewCard]]:
        review.status = ReviewStatus.FAILED
        review.overall_summary = f"{code}: {message}"
        self.repository.update_review(review)
        return review, []

    def _fail_execution_error(
        self,
        review: Review,
        *,
        code: str,
        message: str,
    ) -> tuple[Review, list[ReviewCard]]:
        normalized_message = message.strip()
        if code == EngineErrorCode.TIMEOUT.value and not normalized_message:
            normalized_message = f"Structured review execution timed out after {self._timeout_seconds:.2f}s."
        review.status = ReviewStatus.FAILED
        review.overall_summary = f"{code}: {normalized_message}"
        self.repository.update_review(review)
        return review, []

    def _needs_alignment_context(
        self,
        node_logical_id: str,
        expectation: NodeExpectation,
    ) -> bool:
        if node_logical_id != "research_idea":
            return False
        element_logical_id = (
            expectation.element.logical_id if expectation.element else None
        )
        return element_logical_id in ALIGNMENT_ELEMENT_IDS

    def _resolve_reviewer_policy_rules(
        self,
        *,
        call_definition,
        node_logical_id: str,
        review_stage: ReviewStage,
    ) -> list[ReviewerPolicyRule]:
        return get_applicable_reviewer_policy_rules(
            call_definition=call_definition,
            node_logical_id=node_logical_id,
            review_stage=review_stage,
        )

    def _resolve_feedback_text_for_card(
        self,
        *,
        call_code: str,
        node_logical_id: str,
        expectation: NodeExpectation,
        feedback_text: str,
        subordinate_prompts_by_element_id: dict[str, list[dict[str, str]]],
    ) -> str:
        subordinate_prompt_feedback = (
            self._resolve_subordinate_prompt_feedback_for_card(
                call_code=call_code,
                node_logical_id=node_logical_id,
                expectation=expectation,
                feedback_text=feedback_text,
                subordinate_prompts_by_element_id=subordinate_prompts_by_element_id,
            )
        )
        if subordinate_prompt_feedback is not None:
            return subordinate_prompt_feedback

        if (
            feedback_text != "content_evaluated"
            or call_code not in WF0069_ACTIONABILITY_CALL_CODES
        ):
            return feedback_text

        # Keep the remediation scoped to the locked call wedge at the service seam.
        # Evaluator/mapper are call-agnostic and would widen behavior across unrelated calls.
        element_label = self._normalize_expectation_element_label(expectation)
        return (
            f"Revise {node_logical_id} to explicitly strengthen {element_label} "
            "with concrete evidence and outcomes."
        )

    def _resolve_subordinate_prompt_feedback_for_card(
        self,
        *,
        call_code: str,
        node_logical_id: str,
        expectation: NodeExpectation,
        feedback_text: str,
        subordinate_prompts_by_element_id: dict[str, list[dict[str, str]]],
    ) -> str | None:
        if call_code not in WF0076_SUBORDINATE_PROMPT_PRESENTATION_CALL_CODES:
            return None
        if not feedback_text.startswith(WF0076_SUBORDINATE_PROMPT_REASON_PREFIX):
            return None

        ordered_prompt_ids = self._parse_subordinate_prompt_ids(feedback_text)
        if not ordered_prompt_ids:
            return None

        element_logical_id = (
            expectation.element.logical_id if expectation.element else None
        )
        prompt_text_by_id: dict[str, str] = {}
        if isinstance(element_logical_id, str):
            for prompt in subordinate_prompts_by_element_id.get(element_logical_id, []):
                prompt_id = prompt.get("id")
                prompt_text = prompt.get("prompt")
                if isinstance(prompt_id, str) and isinstance(prompt_text, str):
                    prompt_text_by_id[prompt_id] = prompt_text

        if call_code in WF0077_DETERMINISTIC_RESEARCHER_GUIDANCE_CALL_CODES:
            resolved_prompt_texts = [
                prompt_text_by_id[prompt_id]
                for prompt_id in ordered_prompt_ids
                if prompt_id in prompt_text_by_id
            ]
            if len(resolved_prompt_texts) == len(ordered_prompt_ids):
                return self._build_deterministic_guidance_from_prompts(
                    node_logical_id=node_logical_id,
                    element_label=self._normalize_expectation_element_label(
                        expectation
                    ),
                    prompt_texts=resolved_prompt_texts,
                )

        feedback_lines = ["Address the following evaluation element prompts:"]
        for prompt_id in ordered_prompt_ids:
            prompt_text = prompt_text_by_id.get(prompt_id)
            if prompt_text is None:
                feedback_lines.append(
                    f"- Unresolved subordinate prompt ID: {prompt_id}."
                )
                continue
            feedback_lines.append(f"- {prompt_text}")
        return "\n".join(feedback_lines)

    def _build_synthesis_request_for_card(
        self,
        *,
        call_code: str,
        node_logical_id: str,
        node_title: str | None,
        expectation: NodeExpectation,
        feedback_text: str,
        submitted_text_by_node: dict[str, str],
        subordinate_prompts_by_element_id: dict[str, list[dict[str, str]]],
    ) -> StructuredReviewSynthesisRequest | None:
        if call_code != "ERC-2026-PoC":
            return None

        element = expectation.element
        if element is None:
            return None

        element_logical_id = element.logical_id
        element_name = element.name
        criterion_name = (
            element.criterion.name
            if element.criterion is not None and isinstance(element.criterion.name, str)
            else ""
        )
        if not isinstance(element_logical_id, str) or not element_logical_id.strip():
            return None

        submitted_text = submitted_text_by_node.get(node_logical_id, "")
        subordinate_prompt_context = tuple(
            prompt_text
            for prompt in subordinate_prompts_by_element_id.get(element_logical_id, [])
            for prompt_text in [prompt.get("prompt")]
            if isinstance(prompt_text, str) and prompt_text.strip()
        )
        if (
            not isinstance(node_title, str)
            or not node_title.strip()
            or not isinstance(element_name, str)
            or not element_name.strip()
            or not submitted_text.strip()
            or not feedback_text.strip()
            or not subordinate_prompt_context
            or not self._is_wf0078_guidance_feedback(feedback_text)
        ):
            return None

        return self.synthesis_service.build_request(
            expectation_id=str(expectation.id),
            node_logical_id=node_logical_id,
            node_title=node_title.strip(),
            evaluation_criterion_name=criterion_name,
            evaluation_element_logical_id=element_logical_id,
            evaluation_element_name=element_name,
            deterministic_feedback=feedback_text,
            submitted_text=submitted_text,
            subordinate_prompt_context=subordinate_prompt_context,
        )

    @staticmethod
    def _is_wf0078_guidance_feedback(feedback_text: str) -> bool:
        return feedback_text.startswith("Revise ")

    @classmethod
    def _build_deterministic_guidance_from_prompts(
        cls,
        *,
        node_logical_id: str | None,
        element_label: str,
        prompt_texts: list[str],
    ) -> str:
        normalized_node_logical_id = (
            node_logical_id.strip()
            if isinstance(node_logical_id, str) and node_logical_id.strip()
            else "this section"
        )
        guidance_clauses = [
            cls._rewrite_prompt_as_guidance_clause(prompt_text)
            for prompt_text in prompt_texts
        ]
        return (
            f"Revise {normalized_node_logical_id} to strengthen {element_label} by "
            f"{cls._join_guidance_clauses(guidance_clauses)}."
        )

    @staticmethod
    def _rewrite_prompt_as_guidance_clause(prompt_text: str) -> str:
        normalized_prompt_text = prompt_text.strip().rstrip("?").strip()
        lowered_prompt_text = normalized_prompt_text.lower()
        prefix_to_verb = (
            ("is ", "show how "),
            ("are ", "show how "),
            ("does ", "explain how "),
            ("do ", "explain how "),
            ("if successful, will ", "explain how success will "),
            ("will ", "explain how "),
        )
        for prefix, verb in prefix_to_verb:
            if lowered_prompt_text.startswith(prefix):
                remainder = (
                    StructuredReviewerService._normalize_prompt_guidance_remainder(
                        normalized_prompt_text[len(prefix) :].strip()
                    )
                )
                return verb + StructuredReviewerService._lowercase_first_character(
                    remainder
                )
        return "address " + StructuredReviewerService._lowercase_first_character(
            normalized_prompt_text
        )

    @staticmethod
    def _join_guidance_clauses(guidance_clauses: list[str]) -> str:
        if not guidance_clauses:
            return "address the evaluation element expectations"
        if len(guidance_clauses) == 1:
            return guidance_clauses[0]
        if len(guidance_clauses) == 2:
            return f"{guidance_clauses[0]} and {guidance_clauses[1]}"
        return ", ".join(guidance_clauses[:-1]) + f", and {guidance_clauses[-1]}"

    @staticmethod
    def _lowercase_first_character(value: str) -> str:
        if not value:
            return value
        return value[:1].lower() + value[1:]

    @staticmethod
    def _normalize_prompt_guidance_remainder(value: str) -> str:
        normalized_value = value.strip()
        phrase_rewrites = {
            "the idea high risk and with a potential high gain": (
                "the idea is high risk and has potential high gain"
            ),
            "the expected outcomes innovative or distinctive compared to existing solutions": (
                "the expected outcomes are innovative or distinctive compared to existing solutions"
            ),
        }
        return phrase_rewrites.get(normalized_value.lower(), normalized_value)

    @staticmethod
    def _parse_subordinate_prompt_ids(feedback_text: str) -> list[str]:
        if not feedback_text.startswith(WF0076_SUBORDINATE_PROMPT_REASON_PREFIX):
            return []
        raw_prompt_ids = feedback_text.removeprefix(
            WF0076_SUBORDINATE_PROMPT_REASON_PREFIX
        )
        seen_prompt_ids: set[str] = set()
        ordered_prompt_ids: list[str] = []
        for raw_prompt_id in raw_prompt_ids.split(","):
            prompt_id = raw_prompt_id.strip()
            if not prompt_id or prompt_id in seen_prompt_ids:
                continue
            seen_prompt_ids.add(prompt_id)
            ordered_prompt_ids.append(prompt_id)
        return ordered_prompt_ids

    @staticmethod
    def _normalize_expectation_element_label(expectation: NodeExpectation) -> str:
        if expectation.element is None:
            return "this evaluation element"
        if expectation.element.name:
            return expectation.element.name.strip().lower()
        if expectation.element.logical_id:
            return expectation.element.logical_id.replace("_", " ").strip().lower()
        return "this evaluation element"

    @staticmethod
    def _build_subordinate_prompts_by_element_id(
        call_definition: Any,
    ) -> dict[str, list[dict[str, str]]]:
        if call_definition is None:
            return {}
        canonical_json = getattr(call_definition, "canonical_json", None)
        if not isinstance(canonical_json, dict):
            return {}

        criteria = canonical_json.get("evaluation_criteria")
        if not isinstance(criteria, list):
            return {}

        prompts_by_element_id: dict[str, list[dict[str, str]]] = {}
        for criterion in criteria:
            if not isinstance(criterion, dict):
                continue
            elements = criterion.get("evaluation_elements")
            if not isinstance(elements, list):
                continue
            for element in elements:
                if not isinstance(element, dict):
                    continue
                element_id = element.get("id")
                if not isinstance(element_id, str) or not element_id.strip():
                    continue
                raw_prompts = element.get("subordinate_prompts")
                if not isinstance(raw_prompts, list):
                    continue

                normalized_prompts: list[dict[str, str]] = []
                seen_prompt_ids: set[str] = set()
                has_duplicate_prompt_ids = False
                for prompt in raw_prompts:
                    if not isinstance(prompt, dict):
                        continue
                    prompt_id = prompt.get("id")
                    prompt_text = prompt.get("prompt")
                    if not isinstance(prompt_id, str) or not isinstance(
                        prompt_text, str
                    ):
                        continue
                    normalized_prompt_id = prompt_id.strip()
                    normalized_prompt_text = prompt_text.strip()
                    if not normalized_prompt_id or not normalized_prompt_text:
                        continue
                    if normalized_prompt_id in seen_prompt_ids:
                        has_duplicate_prompt_ids = True
                        continue
                    seen_prompt_ids.add(normalized_prompt_id)
                    normalized_prompt = {
                        "id": normalized_prompt_id,
                        "prompt": normalized_prompt_text,
                    }
                    source_locator = prompt.get("source_locator")
                    if isinstance(source_locator, str) and source_locator.strip():
                        normalized_prompt["source_locator"] = source_locator.strip()
                    normalized_prompts.append(normalized_prompt)

                if normalized_prompts and not has_duplicate_prompt_ids:
                    prompts_by_element_id[element_id] = normalized_prompts
        return prompts_by_element_id
