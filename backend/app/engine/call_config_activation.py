from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActivationResult:
    expectation_order_by_subject: dict[str, list[str]]


class CallConfigActivationError(ValueError):
    def __init__(self, *, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


def _stage_is_active(stage_value: str | None, stage_ref: str) -> bool:
    normalized = (stage_value or "BOTH").upper()
    if normalized in {"BOTH", "STEP1_STEP2", "STEP_1_STEP_2"}:
        return True
    if normalized in {"STEP1", "STEP_1", "PREPROPOSAL", "PRE_PROPOSAL"}:
        return stage_ref == "STEP_1"
    if normalized in {"STEP2", "STEP_2", "FULL", "FULL_PROPOSAL"}:
        return stage_ref == "STEP_2"
    return True


def activate_expectations_for_stage(
    call_config_snapshot: dict,
    *,
    stage_ref: str,
) -> ActivationResult:
    stage_ref_normalized = stage_ref.upper()

    active_element_ids: set[str] = set()
    for criterion in call_config_snapshot.get("evaluation_criteria", []):
        for element in criterion.get("evaluation_elements", []):
            element_id = str(element["id"])
            if _stage_is_active(element.get("stage"), stage_ref_normalized):
                active_element_ids.add(element_id)

    expectation_order_by_subject: dict[str, list[str]] = {}
    seen_expectation_refs: set[str] = set()

    for node in call_config_snapshot.get("proposal_nodes", []):
        node_id = str(node["id"])
        ordered_expectations: list[str] = []
        for node_expectation in node.get("node_expectations", []):
            element_id = str(node_expectation["evaluation_element_id"])
            if element_id not in active_element_ids:
                if any(
                    element_id == str(element.get("id"))
                    for criterion in call_config_snapshot.get("evaluation_criteria", [])
                    for element in criterion.get("evaluation_elements", [])
                ):
                    continue
                raise CallConfigActivationError(
                    code="UNKNOWN_EXPECTATION_ID",
                    message=f"Unknown expectation id in active scope: {element_id}",
                )

            expectation_ref = f"{node_id}:{element_id}"
            if expectation_ref in seen_expectation_refs:
                raise CallConfigActivationError(
                    code="DUPLICATE_EXPECTATION_ID",
                    message=f"Duplicate expectation id in active scope: {expectation_ref}",
                )
            seen_expectation_refs.add(expectation_ref)
            ordered_expectations.append(expectation_ref)

        if ordered_expectations:
            expectation_order_by_subject[node_id] = ordered_expectations

    return ActivationResult(expectation_order_by_subject=expectation_order_by_subject)
