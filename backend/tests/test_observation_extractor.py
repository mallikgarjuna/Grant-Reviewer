from __future__ import annotations

import pytest

from app.engine.observations.extractor import extract_observations

pytestmark = pytest.mark.no_db



def _snapshot_with_dependency() -> dict:
    return {
        "proposal_nodes": [
            {
                "id": "research_idea",
                "node_expectations": [
                    {
                        "evaluation_element_id": "elem_cv_idea_alignment",
                        "dependencies": ["academic_profile"],
                    }
                ],
            }
        ]
    }



def test_anchor_locator_is_deterministic_for_identical_input() -> None:
    snapshot = _snapshot_with_dependency()
    proposal_nodes = {
        "research_idea": "My research idea text",
        "academic_profile": "Academic profile text",
    }

    first = extract_observations(snapshot, proposal_nodes)
    second = extract_observations(snapshot, proposal_nodes)

    assert [item.anchor.locator for item in first] == [item.anchor.locator for item in second]



def test_missing_dependency_context_emits_observation() -> None:
    snapshot = _snapshot_with_dependency()
    proposal_nodes = {"research_idea": "My research idea text"}

    observations = extract_observations(snapshot, proposal_nodes)

    assert any(item.observation_kind == "DEPENDENCY_CONTEXT_MISSING" for item in observations)


def test_wf0045_contract_alignment_with_context() -> None:
    snapshot = _snapshot_with_dependency()
    proposal_nodes = {
        "research_idea": "My research idea text",
        "academic_profile": "Academic profile text",
    }

    observations = extract_observations(snapshot, proposal_nodes)

    assert len(observations) == 1
    assert observations[0].observation_kind == "TEXT_PRESENT"


def test_wf0045_contract_alignment_not_assessable() -> None:
    snapshot = _snapshot_with_dependency()
    proposal_nodes = {"research_idea": "My research idea text"}

    observations = extract_observations(snapshot, proposal_nodes)

    assert len(observations) == 1
    assert observations[0].observation_kind == "DEPENDENCY_CONTEXT_MISSING"
    assert observations[0].details["missing_dependencies"] == ["academic_profile"]
