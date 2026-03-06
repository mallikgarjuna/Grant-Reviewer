"""backend/app/services/reviewer_policy.py
Reviewer-policy extraction and deterministic post-check enforcement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, cast

from app.models.domain import CallDefinition

ReviewStage = Literal["STEP_1", "STEP_2"]
EnforcementMode = Literal["PROMPT_ONLY", "POST_CHECK", "BLOCKING"]

_STEP_2_NODE_IDS = {"b2_part2_scientific_proposal", "resources_time_commitment"}


@dataclass(frozen=True)
class ReviewerPolicyRule:
    """Normalized runtime reviewer-policy rule."""

    id: str
    applies_to_stage: Literal["STEP_1", "STEP_2", "BOTH"]
    applies_to_node_ids: tuple[str, ...]
    rule_type: str
    instruction: str
    severity: Literal["ERROR", "WARNING"]
    enforcement_mode: EnforcementMode
    forbidden_terms: tuple[str, ...]
    source_hint: str | None = None


def infer_review_stage(
    node_logical_id: str | None,
    *,
    call_definition: CallDefinition | None = None,
) -> Literal["STEP_1", "STEP_2", "BOTH"]:
    """Infer review stage from canonical call-definition metadata when available."""
    if call_definition is not None:
        stage_map = _build_node_stage_map(call_definition)
        inferred = stage_map.get(node_logical_id)
        if inferred in {"STEP_1", "STEP_2", "BOTH"}:
            return inferred

    if node_logical_id in _STEP_2_NODE_IDS:
        return "STEP_2"
    return "STEP_1"


def matches_review_stage(
    *,
    node_logical_id: str | None,
    review_stage: ReviewStage,
    call_definition: CallDefinition | None = None,
) -> bool:
    """Return True when a node belongs to the requested review stage."""
    inferred = infer_review_stage(
        node_logical_id,
        call_definition=call_definition,
    )
    return inferred in {"BOTH", review_stage}


def _build_node_stage_map(
    call_definition: CallDefinition,
) -> dict[str, Literal["STEP_1", "STEP_2", "BOTH"]]:
    """Resolve per-node stage from canonical evaluation-element mappings."""
    canonical_json = call_definition.canonical_json
    if not isinstance(canonical_json, dict):
        return {}

    element_stage_by_id = _build_element_stage_map(canonical_json)
    proposal_nodes = canonical_json.get("proposal_nodes")
    if not isinstance(proposal_nodes, list):
        return {}

    node_stage_by_id: dict[str, Literal["STEP_1", "STEP_2", "BOTH"]] = {}
    for node in proposal_nodes:
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id.strip():
            continue
        expectations = node.get("node_expectations")
        if not isinstance(expectations, list) or len(expectations) == 0:
            continue

        stages: set[Literal["STEP_1", "STEP_2", "BOTH"]] = set()
        for expectation in expectations:
            if not isinstance(expectation, dict):
                continue
            element_id = expectation.get("evaluation_element_id")
            if not isinstance(element_id, str) or not element_id.strip():
                continue
            stages.add(element_stage_by_id.get(element_id, "BOTH"))

        if stages == {"STEP_1"}:
            node_stage_by_id[node_id] = "STEP_1"
        elif stages == {"STEP_2"}:
            node_stage_by_id[node_id] = "STEP_2"
        elif stages:
            node_stage_by_id[node_id] = "BOTH"
    return node_stage_by_id


def _build_element_stage_map(
    canonical_json: dict[str, Any],
) -> dict[str, Literal["STEP_1", "STEP_2", "BOTH"]]:
    """Index evaluation-element stage by logical id from canonical_json."""
    criteria = canonical_json.get("evaluation_criteria")
    if not isinstance(criteria, list):
        return {}

    element_stage_by_id: dict[str, Literal["STEP_1", "STEP_2", "BOTH"]] = {}
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
            stage = element.get("stage")
            if stage in {"STEP_1", "STEP_2", "BOTH"}:
                element_stage_by_id[element_id] = stage
            else:
                element_stage_by_id[element_id] = "BOTH"
    return element_stage_by_id


def get_applicable_reviewer_policy_rules(
    *,
    call_definition: CallDefinition | None,
    node_logical_id: str | None,
    review_stage: ReviewStage,
) -> list[ReviewerPolicyRule]:
    """Read and filter reviewer-policy rules from canonical_json."""
    if call_definition is None:
        return []

    canonical_json = call_definition.canonical_json
    if not isinstance(canonical_json, dict):
        return []

    raw_policy = canonical_json.get("reviewer_policy", [])
    if not isinstance(raw_policy, list):
        return []

    rules: list[ReviewerPolicyRule] = []
    for raw_rule in raw_policy:
        if not isinstance(raw_rule, dict):
            continue
        try:
            rule = _parse_rule(raw_rule)
        except ValueError:
            continue
        if not _rule_applies_to_stage(rule, review_stage):
            continue
        if not _rule_applies_to_node(rule, node_logical_id):
            continue
        rules.append(rule)
    return rules


def find_policy_violations(
    *,
    feedback_texts: list[str],
    policy_rules: list[ReviewerPolicyRule],
) -> tuple[list[str], list[str]]:
    """Find policy violations via deterministic forbidden-term checks."""
    checks = [
        rule
        for rule in policy_rules
        if rule.enforcement_mode in {"POST_CHECK", "BLOCKING"} and rule.forbidden_terms
    ]
    if not checks:
        return [], []

    blocking_violations: list[str] = []
    warning_violations: list[str] = []
    for rule in checks:
        lowered_terms = [term.casefold() for term in rule.forbidden_terms]
        for idx, feedback in enumerate(feedback_texts, start=1):
            lowered_feedback = feedback.casefold()
            hit = next((term for term in lowered_terms if term in lowered_feedback), None)
            if hit is None:
                continue
            violation = (
                f"{rule.id}: forbidden term '{hit}' detected in feedback #{idx}"
            )
            if rule.enforcement_mode == "BLOCKING":
                blocking_violations.append(violation)
            else:
                warning_violations.append(violation)
    return blocking_violations, warning_violations


def _parse_rule(raw_rule: dict[str, Any]) -> ReviewerPolicyRule:
    """Parse a raw canonical-json policy rule into a normalized dataclass."""
    rule_id = _require_str(raw_rule.get("id"), "id")
    stage_value = _require_str(raw_rule.get("applies_to_stage"), "applies_to_stage")
    stage = _parse_stage(stage_value)

    rule_type = _require_str(raw_rule.get("rule_type"), "rule_type")
    instruction = _require_str(raw_rule.get("instruction"), "instruction")
    severity = _parse_severity(raw_rule.get("severity"))
    enforcement_mode = _parse_enforcement_mode(raw_rule.get("enforcement_mode"))

    applies_to_node_ids = _parse_string_list(raw_rule.get("applies_to_node_ids"))
    forbidden_terms = _parse_string_list(raw_rule.get("forbidden_terms"))
    source_hint = _parse_optional_str(raw_rule.get("source_hint"))

    return ReviewerPolicyRule(
        id=rule_id,
        applies_to_stage=stage,
        applies_to_node_ids=tuple(applies_to_node_ids),
        rule_type=rule_type,
        instruction=instruction,
        severity=severity,
        enforcement_mode=enforcement_mode,
        forbidden_terms=tuple(forbidden_terms),
        source_hint=source_hint,
    )


def _rule_applies_to_stage(rule: ReviewerPolicyRule, review_stage: ReviewStage) -> bool:
    return rule.applies_to_stage in {"BOTH", review_stage}


def _rule_applies_to_node(rule: ReviewerPolicyRule, node_logical_id: str | None) -> bool:
    if not rule.applies_to_node_ids:
        return True
    if not node_logical_id:
        return False
    return node_logical_id in rule.applies_to_node_ids


def _require_str(value: Any, field_name: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise ValueError(f"Invalid policy field '{field_name}'")


def _parse_stage(value: str) -> Literal["STEP_1", "STEP_2", "BOTH"]:
    if value in {"STEP_1", "STEP_2", "BOTH"}:
        return cast(Literal["STEP_1", "STEP_2", "BOTH"], value)
    raise ValueError("Invalid applies_to_stage")


def _parse_severity(value: Any) -> Literal["ERROR", "WARNING"]:
    if value in {"ERROR", "WARNING"}:
        return value
    return "WARNING"


def _parse_enforcement_mode(value: Any) -> EnforcementMode:
    if value in {"PROMPT_ONLY", "POST_CHECK", "BLOCKING"}:
        return value
    return "PROMPT_ONLY"


def _parse_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    parsed: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            parsed.append(item.strip())
    return parsed


def _parse_optional_str(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None
