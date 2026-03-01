from __future__ import annotations

from typing import Final

from app.engine.contracts import (
    DiagnosticFindingV1,
    FindingSeverity,
    ReviewCard,
    ReviewRating,
)

_SEVERITY_PRIORITY = {
    "ERROR": 3,
    "WARNING": 2,
    "NOTE": 1,
}

_SEVERITY_TO_RATING: Final[dict[FindingSeverity, ReviewRating]] = {
    "ERROR": "CRITICAL",
    "WARNING": "WARNING",
    "NOTE": "NOTE",
}


class ReviewCardMappingError(ValueError):
    def __init__(self, *, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


def _join_reasons_stably(reasons: list[str]) -> str:
    return " | ".join(sorted(set(reasons)))


def map_findings_to_review_cards(
    *,
    findings: list[DiagnosticFindingV1],
    resolvable_expectation_refs: set[str],
) -> list[ReviewCard]:
    grouped: dict[tuple[str, str], list[DiagnosticFindingV1]] = {}

    for finding in findings:
        expectation_ref = finding.primary_expectation_ref
        if expectation_ref not in resolvable_expectation_refs:
            raise ReviewCardMappingError(
                code="EXPECTATION_REF_UNRESOLVABLE",
                message=f"Unresolvable expectation ref: {expectation_ref}",
            )

        key = (finding.subject_ref.node_logical_id, expectation_ref)
        grouped.setdefault(key, []).append(finding)

    cards: list[ReviewCard] = []
    for (node_logical_id, expectation_ref), grouped_findings in sorted(grouped.items()):
        rolled_up = max(
            grouped_findings,
            key=lambda item: _SEVERITY_PRIORITY.get(item.severity, 0),
        )
        cards.append(
            ReviewCard(
                node_logical_id=node_logical_id,
                expectation_id=expectation_ref,
                rating=_SEVERITY_TO_RATING[rolled_up.severity],
                feedback=_join_reasons_stably([item.reason for item in grouped_findings]),
            )
        )

    return cards
