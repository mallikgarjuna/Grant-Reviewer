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
