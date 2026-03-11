"""backend/tests/test_call_definitions_v2_schema.py
Schema-level tests for CallDefinitionV2 WF-0032 fields and validators.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from app.schemas.call_definitions_v2 import CallDefinitionV2

pytestmark = pytest.mark.no_db


def _load_nwo_v2_yaml() -> dict[str, object]:
    raw = Path("data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml").read_text(
        encoding="utf-8"
    )
    loaded = yaml.safe_load(raw)
    assert isinstance(loaded, dict)
    return loaded


def test_v2_schema_accepts_wf0032_optional_fields() -> None:
    payload = _load_nwo_v2_yaml()
    proposal_nodes = payload["proposal_nodes"]
    assert isinstance(proposal_nodes, list)
    first_node = proposal_nodes[0]
    assert isinstance(first_node, dict)
    first_node["parent_logical_id"] = None

    constraints = first_node.get("content_constraints")
    assert isinstance(constraints, dict)
    constraints["max_pages"] = 3

    criteria = payload["evaluation_criteria"]
    assert isinstance(criteria, list)
    first_criterion = criteria[0]
    assert isinstance(first_criterion, dict)
    elements = first_criterion["evaluation_elements"]
    assert isinstance(elements, list)
    first_element = elements[0]
    assert isinstance(first_element, dict)
    first_element["stage"] = "STEP_1"

    model = CallDefinitionV2.model_validate(payload)
    assert model.proposal_nodes[0].parent_logical_id is None
    assert model.proposal_nodes[0].content_constraints is not None
    assert model.proposal_nodes[0].content_constraints.max_pages == 3
    assert model.evaluation_criteria[0].evaluation_elements[0].stage == "STEP_1"


def test_v2_schema_rejects_duplicate_node_ids() -> None:
    payload = _load_nwo_v2_yaml()
    proposal_nodes = payload["proposal_nodes"]
    assert isinstance(proposal_nodes, list)
    first_node = proposal_nodes[0]
    assert isinstance(first_node, dict)

    duplicate_node = dict(first_node)
    proposal_nodes.append(duplicate_node)

    with pytest.raises(ValueError, match="Duplicate proposal node id"):
        CallDefinitionV2.model_validate(payload)


def test_v2_schema_rejects_policy_with_unknown_node_scope() -> None:
    payload = _load_nwo_v2_yaml()
    payload["reviewer_policy"] = [
        {
            "id": "pol_bad_scope",
            "applies_to_stage": "STEP_1",
            "applies_to_node_ids": ["unknown_node"],
            "rule_type": "stage_scope",
            "instruction": "Invalid node scope",
            "severity": "WARNING",
            "enforcement_mode": "PROMPT_ONLY",
            "forbidden_terms": [],
        }
    ]

    with pytest.raises(ValueError, match="Unknown applies_to_node_ids"):
        CallDefinitionV2.model_validate(payload)


def test_v2_schema_requires_forbidden_terms_for_blocking_policy() -> None:
    payload = _load_nwo_v2_yaml()
    payload["reviewer_policy"] = [
        {
            "id": "pol_missing_terms",
            "applies_to_stage": "BOTH",
            "applies_to_node_ids": [],
            "rule_type": "criterion_scope",
            "instruction": "Blocking rule without terms",
            "severity": "WARNING",
            "enforcement_mode": "BLOCKING",
            "forbidden_terms": [],
        }
    ]

    with pytest.raises(ValueError, match="forbidden_terms required"):
        CallDefinitionV2.model_validate(payload)


def test_wf0063_node_role_defaults_primary_and_supporting_requires_empty_expectations() -> None:
    payload = _load_nwo_v2_yaml()
    proposal_nodes = payload["proposal_nodes"]
    assert isinstance(proposal_nodes, list)

    primary_node = proposal_nodes[0]
    assert isinstance(primary_node, dict)
    primary_node.pop("node_role", None)

    supporting_node = proposal_nodes[1]
    assert isinstance(supporting_node, dict)
    supporting_node["node_role"] = "SUPPORTING"

    expectations = supporting_node.get("node_expectations")
    if not isinstance(expectations, list):
        expectations = []
        supporting_node["node_expectations"] = expectations
    expectations.append(
        {
            "evaluation_element_id": "elem_nonexistent",
            "expectation_strength": "MANDATORY",
            "evaluation_intent": "QUALITY",
        }
    )

    with pytest.raises(
        ValueError,
        match="SUPPORTING nodes cannot define node_expectations",
    ):
        CallDefinitionV2.model_validate(payload)

    expectations.clear()
    model = CallDefinitionV2.model_validate(payload)
    assert model.proposal_nodes[0].node_role == "PRIMARY"
    assert model.proposal_nodes[1].node_role == "SUPPORTING"


def test_wf0063_runtime_opt_in_flag_defaults_disabled() -> None:
    payload = _load_nwo_v2_yaml()
    payload.pop("runtime_config", None)

    model = CallDefinitionV2.model_validate(payload)
    assert model.runtime_config.split_visibility_reviewability_enabled is False


def test_wf0063_split_opt_in_calls_are_explicitly_allowlisted() -> None:
    allowed_call_codes = {"MSCA-PF-2025"}
    canonical_dir = Path("data/calls/canonical")
    yaml_paths = sorted(canonical_dir.rglob("*.yaml"))
    assert yaml_paths

    split_enabled_call_codes: set[str] = set()
    for yaml_path in yaml_paths:
        loaded = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            continue
        model = CallDefinitionV2.model_validate(loaded)
        if model.runtime_config.split_visibility_reviewability_enabled:
            split_enabled_call_codes.add(model.funding_call.code)
            for node in model.proposal_nodes:
                if node.node_role == "SUPPORTING":
                    assert len(node.node_expectations) == 0

    assert split_enabled_call_codes == allowed_call_codes


def test_wf0074_schema_accepts_typed_subordinate_prompts_and_legacy_flat_yaml() -> None:
    payload = _load_nwo_v2_yaml()
    typed_payload = deepcopy(payload)

    criteria = typed_payload["evaluation_criteria"]
    assert isinstance(criteria, list)
    first_criterion = criteria[0]
    assert isinstance(first_criterion, dict)
    elements = first_criterion["evaluation_elements"]
    assert isinstance(elements, list)
    first_element = elements[0]
    assert isinstance(first_element, dict)
    first_element["subordinate_prompts"] = [
        {
            "id": "prompt_research_question_fit",
            "prompt": "To what extent does the proposed research address the research question from the call effectively?",
            "source_locator": "Guide for applicants section 4.2",
            "source_hint": "Official evaluation form",
        },
        {
            "id": "prompt_feasibility",
            "prompt": "To what extent is the proposed approach feasible within the proposed period and resources?",
            "source_locator": "Guide for applicants section 4.2",
            "source_hint": "Official evaluation form",
        },
    ]

    typed_model = CallDefinitionV2.model_validate(typed_payload)
    subordinate_prompts = (
        typed_model.evaluation_criteria[0].evaluation_elements[0].subordinate_prompts
    )
    assert subordinate_prompts is not None
    assert [item.id for item in subordinate_prompts] == [
        "prompt_research_question_fit",
        "prompt_feasibility",
    ]

    legacy_model = CallDefinitionV2.model_validate(payload)
    assert (
        legacy_model.evaluation_criteria[0].evaluation_elements[0].subordinate_prompts
        is None
    )


def test_wf0074_schema_rejects_malformed_subordinate_prompt_items() -> None:
    payload = _load_nwo_v2_yaml()

    criteria = payload["evaluation_criteria"]
    assert isinstance(criteria, list)
    first_criterion = criteria[0]
    assert isinstance(first_criterion, dict)
    elements = first_criterion["evaluation_elements"]
    assert isinstance(elements, list)
    first_element = elements[0]
    assert isinstance(first_element, dict)

    first_element["subordinate_prompts"] = ["anonymous prompt"]
    with pytest.raises(ValueError, match="subordinate_prompts.0"):
        CallDefinitionV2.model_validate(payload)

    first_element["subordinate_prompts"] = [
        {
            "id": "duplicate_prompt",
            "prompt": "Question one",
            "source_locator": "Section 4.2",
            "source_hint": "Official evaluation form",
        },
        {
            "id": "duplicate_prompt",
            "prompt": "Question two",
            "source_locator": "Section 4.2",
            "source_hint": "Official evaluation form",
        },
    ]
    with pytest.raises(ValueError, match="Duplicate subordinate prompt id"):
        CallDefinitionV2.model_validate(payload)

    first_element["subordinate_prompts"] = [
        {
            "id": "empty_prompt",
            "prompt": "",
            "source_locator": "Section 4.2",
            "source_hint": "Official evaluation form",
        }
    ]
    with pytest.raises(ValueError, match="prompt"):
        CallDefinitionV2.model_validate(payload)

    first_element["subordinate_prompts"] = [
        {
            "id": "missing_traceability",
            "prompt": "Question without traceability",
            "source_hint": "Official evaluation form",
        }
    ]
    with pytest.raises(ValueError, match="source_locator"):
        CallDefinitionV2.model_validate(payload)
