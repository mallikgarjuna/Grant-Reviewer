"""Pure compliance evaluation logic decoupled from API transport concerns."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.schemas.compliance import (
    ComplianceCheckRequest,
    ComplianceCheckResponse,
    ComplianceViolation,
)
from app.services.call_definition_service import HydratedNode

_REQUEST_NODE_ID = "__request__"


@dataclass(frozen=True)
class _ResolvedLimits:
    """Effective word limits for one node after domain resolution."""

    min_words: int | None
    max_words: int | None


def _count_words(text: str) -> int:
    """Count words using deterministic whitespace tokenization."""
    normalized = text.strip()
    if not normalized:
        return 0
    return len(normalized.split())


def _as_int(value: Any) -> int | None:
    """Return integer value when present and valid, else None."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _canonical_domain_from_limit_key(key: str) -> str | None:
    """Map keys like science_enw_max_words -> science_enw."""
    if not key.endswith("_max_words"):
        return None
    if key == "default_max_words":
        return None
    return key[: -len("_max_words")]


def _derive_domain_catalog(hydrated_nodes: list[HydratedNode]) -> set[str]:
    """Collect canonical domain ids referenced by node constraints."""
    domains: set[str] = set()
    for hydrated in hydrated_nodes:
        constraints = hydrated.config.get("content_constraints")
        if not isinstance(constraints, dict):
            continue
        by_domain = constraints.get("word_limit_by_domain")
        if not isinstance(by_domain, dict):
            continue
        for key in by_domain:
            if not isinstance(key, str):
                continue
            domain = _canonical_domain_from_limit_key(key)
            if domain:
                domains.add(domain)
    return domains


def _resolve_limits(
    *,
    content_constraints: dict[str, Any],
    domain: str | None,
) -> _ResolvedLimits:
    """Resolve effective min/max limits for one node."""
    total_limit = content_constraints.get("total_word_limit")
    min_words: int | None = None
    max_words: int | None = None
    if isinstance(total_limit, dict):
        min_words = _as_int(total_limit.get("min_words"))
        max_words = _as_int(total_limit.get("max_words"))

    by_domain = content_constraints.get("word_limit_by_domain")
    if isinstance(by_domain, dict):
        default_max = _as_int(by_domain.get("default_max_words"))
        if domain:
            explicit_domain_max = _as_int(by_domain.get(f"{domain}_max_words"))
            if explicit_domain_max is not None:
                max_words = explicit_domain_max
            elif default_max is not None:
                max_words = default_max
        elif default_max is not None:
            max_words = default_max

    return _ResolvedLimits(min_words=min_words, max_words=max_words)


def _error(
    *,
    node_logical_id: str,
    rule_id: str,
    actual: str,
    expected: str,
    message: str,
    is_blocking: bool = True,
) -> ComplianceViolation:
    """Factory for deterministic compliance error objects."""
    return ComplianceViolation(
        node_logical_id=node_logical_id,
        rule_id=rule_id,
        severity="ERROR",
        actual=actual,
        expected=expected,
        message=message,
        is_blocking=is_blocking,
    )


def evaluate_compliance(
    request: ComplianceCheckRequest,
    hydrated_nodes: list[HydratedNode],
) -> ComplianceCheckResponse:
    """Evaluate deterministic compliance for submitted draft nodes."""
    errors: list[ComplianceViolation] = []
    warnings: list[ComplianceViolation] = []

    normalized_domain = request.domain.strip().lower() if request.domain else None
    known_domains = _derive_domain_catalog(hydrated_nodes)
    if normalized_domain and known_domains and normalized_domain not in known_domains:
        errors.append(
            _error(
                node_logical_id=_REQUEST_NODE_ID,
                rule_id="domain_invalid",
                actual=normalized_domain,
                expected=f"one of: {', '.join(sorted(known_domains))}",
                message=(
                    f"Domain '{normalized_domain}' is not recognized for this call."
                ),
            )
        )

    text_by_node: dict[str, str] = {
        node.node_logical_id: node.text for node in request.draft_nodes
    }

    for hydrated in hydrated_nodes:
        logical_id = hydrated.node.logical_id
        if not logical_id:
            continue

        constraints_raw = hydrated.config.get("content_constraints")
        content_constraints = constraints_raw if isinstance(constraints_raw, dict) else {}
        limits = _resolve_limits(
            content_constraints=content_constraints,
            domain=normalized_domain,
        )

        submitted_text = text_by_node.get(logical_id)
        normalized_text = submitted_text.strip() if submitted_text is not None else ""
        word_count = _count_words(normalized_text)
        is_missing_text = submitted_text is None or not normalized_text
        is_mandatory = (limits.min_words or 0) > 0

        if is_mandatory and is_missing_text:
            errors.append(
                _error(
                    node_logical_id=logical_id,
                    rule_id="mandatory_presence",
                    actual="missing",
                    expected="present",
                    message="Mandatory section is missing text.",
                )
            )
            continue

        if is_missing_text:
            continue

        if limits.min_words is not None and word_count < limits.min_words:
            errors.append(
                _error(
                    node_logical_id=logical_id,
                    rule_id="word_limit_min",
                    actual=str(word_count),
                    expected=str(limits.min_words),
                    message=f"Minimum word limit is {limits.min_words}.",
                )
            )

        if limits.max_words is not None and word_count > limits.max_words:
            errors.append(
                _error(
                    node_logical_id=logical_id,
                    rule_id="word_limit_max",
                    actual=str(word_count),
                    expected=str(limits.max_words),
                    message=f"Maximum word limit is {limits.max_words}.",
                )
            )

    return ComplianceCheckResponse(
        is_compliant=not errors,
        errors=errors,
        warnings=warnings,
    )
