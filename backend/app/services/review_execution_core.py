from __future__ import annotations

import logging
from concurrent.futures import TimeoutError
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from app.models.domain import NodeExpectation, ProposalNode
from app.schemas.llm_response import ExpectationFeedback
from app.services.llm_client import LLMClientError, LLMClientProtocol
from app.services.llm_helpers import generate_with_timeout, parse_llm_response
from app.services.prompt_builder import build_review_prompt
from app.services.reviewer_policy import ReviewerPolicyRule, find_policy_violations

logger = logging.getLogger(__name__)


class ExecutionFailureCategory(StrEnum):
    TIMEOUT = "timeout"
    LLM_FAILURE = "llm_failure"
    VALIDATION_FAILURE = "validation_failure"
    POLICY_BLOCKING = "policy_blocking"


@dataclass(frozen=True)
class ExecutionFailure:
    category: ExecutionFailureCategory
    message: str


@dataclass(frozen=True)
class NodeExecutionResult:
    prompt: str
    raw_response: str | None
    feedbacks: list[ExpectationFeedback]
    warning_violations: list[str]
    failure: ExecutionFailure | None = None


@dataclass(frozen=True)
class ExecutionTelemetryPayload:
    node_logical_id: str | None
    expectation_count: int
    failure_category: str | None = None


class ExecutionTelemetryHooks(Protocol):
    def on_execution_start(self, payload: ExecutionTelemetryPayload) -> None:
        ...

    def on_execution_complete(self, payload: ExecutionTelemetryPayload) -> None:
        ...

    def on_execution_failure(self, payload: ExecutionTelemetryPayload) -> None:
        ...


class NoOpExecutionTelemetryHooks:
    def on_execution_start(self, payload: ExecutionTelemetryPayload) -> None:
        del payload

    def on_execution_complete(self, payload: ExecutionTelemetryPayload) -> None:
        del payload

    def on_execution_failure(self, payload: ExecutionTelemetryPayload) -> None:
        del payload


class ReviewExecutionCore:
    """Shared execution seam for assessable expectation processing."""

    def __init__(
        self,
        *,
        llm_client: LLMClientProtocol,
        timeout_seconds: float,
        telemetry_hooks: ExecutionTelemetryHooks | None = None,
    ) -> None:
        self._llm_client = llm_client
        self._timeout_seconds = timeout_seconds
        self._telemetry_hooks = telemetry_hooks or NoOpExecutionTelemetryHooks()

    def execute_assessable_node(
        self,
        *,
        node: ProposalNode,
        snippet_text: str,
        expectations: list[NodeExpectation],
        reviewer_policy_rules: list[ReviewerPolicyRule],
        cross_node_context: dict[str, str] | None = None,
    ) -> NodeExecutionResult:
        base_payload = self._build_telemetry_payload(
            node_logical_id=node.logical_id,
            expectation_count=len(expectations),
        )
        self._emit_start(base_payload)

        prompt = build_review_prompt(
            node=node,
            snippet_text=snippet_text,
            expectations=expectations,
            reviewer_policy_rules=reviewer_policy_rules,
            cross_node_context=cross_node_context,
        )

        try:
            raw_response = generate_with_timeout(
                llm_client=self._llm_client,
                prompt=prompt,
                timeout_seconds=self._timeout_seconds,
            )
        except TimeoutError:
            return self._failure_result(
                payload=base_payload,
                prompt=prompt,
                raw_response=None,
                category=ExecutionFailureCategory.TIMEOUT,
                message=f"LLM call timed out after {self._timeout_seconds:.2f}s.",
            )
        except LLMClientError as err:
            return self._failure_result(
                payload=base_payload,
                prompt=prompt,
                raw_response=None,
                category=ExecutionFailureCategory.LLM_FAILURE,
                message=str(err),
            )

        try:
            parsed_response = parse_llm_response(raw_response)
            self._validate_feedbacks(
                feedbacks=parsed_response.feedbacks,
                expectations=expectations,
            )
            blocking_violations, warning_violations = find_policy_violations(
                feedback_texts=[feedback.feedback for feedback in parsed_response.feedbacks],
                policy_rules=reviewer_policy_rules,
            )
            if blocking_violations:
                return self._failure_result(
                    payload=base_payload,
                    prompt=prompt,
                    raw_response=raw_response,
                    category=ExecutionFailureCategory.POLICY_BLOCKING,
                    message="; ".join(blocking_violations),
                    warning_violations=warning_violations,
                )
            result = NodeExecutionResult(
                prompt=prompt,
                raw_response=raw_response,
                feedbacks=parsed_response.feedbacks,
                warning_violations=warning_violations,
            )
            self._emit_complete(base_payload)
            return result
        except ValueError as err:
            return self._failure_result(
                payload=base_payload,
                prompt=prompt,
                raw_response=raw_response,
                category=ExecutionFailureCategory.VALIDATION_FAILURE,
                message=str(err),
            )

    def _validate_feedbacks(
        self,
        *,
        feedbacks: list[ExpectationFeedback],
        expectations: list[NodeExpectation],
    ) -> None:
        expected_ids = {str(expectation.id) for expectation in expectations}
        received_ids = {feedback.node_expectation_id for feedback in feedbacks}

        if len(feedbacks) != len(expectations):
            raise ValueError(
                f"Cardinality mismatch: expected {len(expectations)} feedbacks, "
                f"got {len(feedbacks)}"
            )

        missing = expected_ids - received_ids
        if missing:
            raise ValueError(f"Missing feedback for expectations: {missing}")

        extra = received_ids - expected_ids
        if extra:
            raise ValueError(f"Unknown expectation IDs in response: {extra}")

    def _failure_result(
        self,
        *,
        payload: ExecutionTelemetryPayload,
        prompt: str,
        raw_response: str | None,
        category: ExecutionFailureCategory,
        message: str,
        warning_violations: list[str] | None = None,
    ) -> NodeExecutionResult:
        self._emit_failure(
            self._build_telemetry_payload(
                node_logical_id=payload.node_logical_id,
                expectation_count=payload.expectation_count,
                failure_category=category.value,
            )
        )
        return NodeExecutionResult(
            prompt=prompt,
            raw_response=raw_response,
            feedbacks=[],
            warning_violations=warning_violations or [],
            failure=ExecutionFailure(
                category=category,
                message=message,
            ),
        )

    def _build_telemetry_payload(
        self,
        *,
        node_logical_id: str | None,
        expectation_count: int,
        failure_category: str | None = None,
    ) -> ExecutionTelemetryPayload:
        return ExecutionTelemetryPayload(
            node_logical_id=node_logical_id,
            expectation_count=expectation_count,
            failure_category=failure_category,
        )

    def _emit_start(self, payload: ExecutionTelemetryPayload) -> None:
        try:
            self._telemetry_hooks.on_execution_start(payload)
        except Exception:
            logger.exception("execution telemetry start hook failed")

    def _emit_complete(self, payload: ExecutionTelemetryPayload) -> None:
        try:
            self._telemetry_hooks.on_execution_complete(payload)
        except Exception:
            logger.exception("execution telemetry complete hook failed")

    def _emit_failure(self, payload: ExecutionTelemetryPayload) -> None:
        try:
            self._telemetry_hooks.on_execution_failure(payload)
        except Exception:
            logger.exception("execution telemetry failure hook failed")
