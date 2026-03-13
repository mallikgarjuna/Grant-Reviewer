"""backend/app/services/structured_review_synthesis_service.py
Typed additive synthesis helper for structured-review cards.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from app.services.llm_client import LLMClientError, LLMClientProtocol

BOUNDARY_EXCERPT_CHARS = 280


@dataclass(frozen=True)
class StructuredReviewSynthesisRequest:
    """Single-card synthesis input constrained to approved same-card context."""

    expectation_id: str
    node_logical_id: str
    evaluation_criterion_name: str
    evaluation_element_logical_id: str
    evaluation_element_name: str
    deterministic_feedback: str
    submitted_excerpt: str
    subordinate_prompt_context: tuple[str, ...]
    node_title: str = ""


@dataclass(frozen=True)
class StructuredReviewSynthesisAcceptedResult:
    """Accepted additive synthesis companion for a deterministic review card."""

    expectation_id: str
    node_logical_id: str
    evaluation_element_logical_id: str
    synthesized_feedback: str
    evidence_quotes: tuple[str, ...]


@dataclass(frozen=True)
class StructuredReviewSynthesisRejectedResult:
    """Fail-closed synthesis rejection classification for one card."""

    expectation_id: str
    node_logical_id: str
    evaluation_element_logical_id: str
    rejection_code: str
    detail: str


StructuredReviewSynthesisResult = (
    StructuredReviewSynthesisAcceptedResult | StructuredReviewSynthesisRejectedResult
)


class StructuredReviewSynthesisService:
    """LLM-backed additive synthesis helper with strict card-anchored validation."""

    def __init__(self, llm_client: LLMClientProtocol) -> None:
        self._llm_client = llm_client

    def build_request(
        self,
        *,
        expectation_id: str,
        node_logical_id: str,
        node_title: str,
        evaluation_criterion_name: str,
        evaluation_element_logical_id: str,
        evaluation_element_name: str,
        deterministic_feedback: str,
        submitted_text: str,
        subordinate_prompt_context: tuple[str, ...],
    ) -> StructuredReviewSynthesisRequest:
        return StructuredReviewSynthesisRequest(
            expectation_id=expectation_id,
            node_logical_id=node_logical_id,
            node_title=node_title,
            evaluation_criterion_name=evaluation_criterion_name,
            evaluation_element_logical_id=evaluation_element_logical_id,
            evaluation_element_name=evaluation_element_name,
            deterministic_feedback=deterministic_feedback,
            submitted_excerpt=submitted_text.strip()[:BOUNDARY_EXCERPT_CHARS],
            subordinate_prompt_context=subordinate_prompt_context,
        )

    def attempt_card_synthesis(
        self,
        request: StructuredReviewSynthesisRequest,
    ) -> StructuredReviewSynthesisResult:
        try:
            raw_response = self._llm_client.generate(self._build_prompt(request))
        except TimeoutError as err:
            return StructuredReviewSynthesisRejectedResult(
                expectation_id=request.expectation_id,
                node_logical_id=request.node_logical_id,
                evaluation_element_logical_id=request.evaluation_element_logical_id,
                rejection_code="timeout",
                detail=str(err),
            )
        except LLMClientError as err:
            return StructuredReviewSynthesisRejectedResult(
                expectation_id=request.expectation_id,
                node_logical_id=request.node_logical_id,
                evaluation_element_logical_id=request.evaluation_element_logical_id,
                rejection_code="client_error",
                detail=str(err),
            )
        except Exception as err:
            return StructuredReviewSynthesisRejectedResult(
                expectation_id=request.expectation_id,
                node_logical_id=request.node_logical_id,
                evaluation_element_logical_id=request.evaluation_element_logical_id,
                rejection_code="unexpected_error",
                detail=str(err),
            )

        return self._parse_response(request, raw_response)

    def _build_prompt(self, request: StructuredReviewSynthesisRequest) -> str:
        prompt_lines = [
            "Produce additive, same-card-only synthesis as JSON.",
            "Do not use any context outside this card.",
            f"expectation_id: {request.expectation_id}",
            f"node_logical_id: {request.node_logical_id}",
            f"node_title: {request.node_title}",
            f"evaluation_criterion: {request.evaluation_criterion_name}",
            f"evaluation_element_logical_id: {request.evaluation_element_logical_id}",
            f"evaluation_element_name: {request.evaluation_element_name}",
            f"deterministic_feedback: {request.deterministic_feedback}",
            f"submitted_excerpt: {request.submitted_excerpt}",
        ]
        if request.subordinate_prompt_context:
            prompt_lines.append(
                "subordinate_prompt_context: "
                + " | ".join(request.subordinate_prompt_context)
            )
        prompt_lines.append(
            "Return JSON with expectation_id, node_logical_id, "
            "evaluation_element_logical_id, synthesized_feedback, evidence_quotes."
        )
        return "\n".join(prompt_lines)

    def _parse_response(
        self,
        request: StructuredReviewSynthesisRequest,
        raw_response: str,
    ) -> StructuredReviewSynthesisResult:
        try:
            payload = json.loads(raw_response)
        except json.JSONDecodeError as err:
            return self._reject(request, "malformed_output", str(err))

        if not isinstance(payload, dict):
            return self._reject(request, "malformed_output", "Expected JSON object.")

        expectation_id = payload.get("expectation_id")
        node_logical_id = payload.get("node_logical_id")
        element_logical_id = payload.get("evaluation_element_logical_id")
        synthesized_feedback = payload.get("synthesized_feedback")
        evidence_quotes = payload.get("evidence_quotes")

        if not isinstance(expectation_id, str) or not expectation_id.strip():
            return self._reject(request, "malformed_output", "Missing expectation_id.")
        if not isinstance(node_logical_id, str) or not node_logical_id.strip():
            return self._reject(request, "malformed_output", "Missing node_logical_id.")
        if not isinstance(element_logical_id, str) or not element_logical_id.strip():
            return self._reject(
                request,
                "malformed_output",
                "Missing evaluation_element_logical_id.",
            )
        if (
            not isinstance(synthesized_feedback, str)
            or not synthesized_feedback.strip()
        ):
            return self._reject(
                request,
                "malformed_output",
                "Missing synthesized_feedback.",
            )
        if not isinstance(evidence_quotes, list) or not evidence_quotes:
            return self._reject(
                request,
                "malformed_output",
                "Missing evidence_quotes.",
            )
        if not all(isinstance(item, str) and item.strip() for item in evidence_quotes):
            return self._reject(
                request,
                "malformed_output",
                "Evidence quotes must be non-empty strings.",
            )

        if element_logical_id != request.evaluation_element_logical_id:
            return self._reject(
                request,
                "wrong_element",
                "Returned evaluation element does not match the anchored card.",
            )
        if (
            expectation_id != request.expectation_id
            or node_logical_id != request.node_logical_id
        ):
            return self._reject(
                request,
                "ambiguous_or_mismatched_output",
                "Returned card identity does not match the anchored request.",
            )
        if any(quote not in request.submitted_excerpt for quote in evidence_quotes):
            return self._reject(
                request,
                "ungrounded_output",
                "Evidence quotes must come from the submitted excerpt.",
            )

        return StructuredReviewSynthesisAcceptedResult(
            expectation_id=request.expectation_id,
            node_logical_id=request.node_logical_id,
            evaluation_element_logical_id=request.evaluation_element_logical_id,
            synthesized_feedback=synthesized_feedback.strip(),
            evidence_quotes=tuple(item.strip() for item in evidence_quotes),
        )

    def _reject(
        self,
        request: StructuredReviewSynthesisRequest,
        rejection_code: str,
        detail: str,
    ) -> StructuredReviewSynthesisRejectedResult:
        return StructuredReviewSynthesisRejectedResult(
            expectation_id=request.expectation_id,
            node_logical_id=request.node_logical_id,
            evaluation_element_logical_id=request.evaluation_element_logical_id,
            rejection_code=rejection_code,
            detail=detail,
        )
