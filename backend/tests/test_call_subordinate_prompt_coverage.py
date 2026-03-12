"""backend/tests/test_call_subordinate_prompt_coverage.py
Fail-closed coverage proof for ERC PoC page-43 subordinate prompts.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pytest
import yaml

pytestmark = pytest.mark.no_db

_ERC_POC_YAML_PATH = Path("data/calls/canonical/erc/erc_poc_2026_full.yaml")


CoverageState = Literal["absent_by_source", "fully_encoded", "partially_encoded"]


@dataclass(frozen=True)
class SourcePromptExpectation:
    source_label: str
    prompt_text: str


@dataclass(frozen=True)
class ElementCoverageExpectation:
    element_id: str
    source_locator: str
    source_prompts: tuple[SourcePromptExpectation, ...]


@dataclass(frozen=True)
class ElementCoverageResult:
    state: CoverageState
    matched_prompt_ids: dict[str, str]
    matched_prompt_paths: dict[str, str]
    missing_source_labels: tuple[str, ...]


def _load_erc_poc_payload() -> dict[str, object]:
    loaded = yaml.safe_load(_ERC_POC_YAML_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _page_43_expectations() -> tuple[ElementCoverageExpectation, ...]:
    locator_1a = "wp_horizon-erc-2026_en.pdf page 43 / 1.a"
    locator_1b = "wp_horizon-erc-2026_en.pdf page 43 / 1.b"
    locator_1c = "wp_horizon-erc-2026_en.pdf page 43 / 1.c"
    return (
        ElementCoverageExpectation(
            element_id="elem_breakthrough_innovation_potential",
            source_locator=locator_1a,
            source_prompts=(
                SourcePromptExpectation(
                    source_label="1.a.1",
                    prompt_text="Does the idea have the potential to drive innovation and business inventiveness or tackle societal challenges?",
                ),
                SourcePromptExpectation(
                    source_label="1.a.2",
                    prompt_text="Are the expected outcomes innovative or distinctive compared to existing solutions?",
                ),
                SourcePromptExpectation(
                    source_label="1.a.3",
                    prompt_text="Is the idea high risk and with a potential high gain?",
                ),
                SourcePromptExpectation(
                    source_label="1.a.4",
                    prompt_text="If successful, will the outcome result in a breakthrough innovation?",
                ),
                SourcePromptExpectation(
                    source_label="1.a.5",
                    prompt_text="Is there a risk that some aspects are difficult to overcome?",
                ),
            ),
        ),
        ElementCoverageExpectation(
            element_id="elem_approach_methodology",
            source_locator=locator_1b,
            source_prompts=(
                SourcePromptExpectation(
                    source_label="1.b.1",
                    prompt_text="Are the activities and planning appropriate and effective to explore the path from ground-breaking research towards innovation?",
                ),
                SourcePromptExpectation(
                    source_label="1.b.2",
                    prompt_text="Are the timescales and resources properly justified and adequate for the implementation and feasibility of the project, and properly justified? Will the activities be conducted by persons qualified for the purpose?",
                ),
            ),
        ),
        ElementCoverageExpectation(
            element_id="elem_pi_strategic_leadership",
            source_locator=locator_1c,
            source_prompts=(
                SourcePromptExpectation(
                    source_label="1.c.1",
                    prompt_text="Does the PI demonstrate a clear vision on how to manage the project, the consolidation of information and data needed to take strategic decisions and implement the proposed plan, including risk and contingency measures?",
                ),
            ),
        ),
    )


def _classify_element_coverage(
    payload: dict[str, object],
    expectation: ElementCoverageExpectation,
) -> ElementCoverageResult:
    criteria = payload.get("evaluation_criteria")
    assert isinstance(criteria, list)

    matched_prompt_ids: dict[str, str] = {}
    matched_prompt_paths: dict[str, str] = {}
    source_labels_by_prompt = {
        item.prompt_text: item.source_label for item in expectation.source_prompts
    }
    missing_source_labels = [item.source_label for item in expectation.source_prompts]

    for criterion_index, criterion in enumerate(criteria):
        assert isinstance(criterion, dict)
        elements = criterion.get("evaluation_elements")
        assert isinstance(elements, list)

        for element_index, element in enumerate(elements):
            assert isinstance(element, dict)
            if element.get("id") != expectation.element_id:
                continue

            subordinate_prompts = element.get("subordinate_prompts")
            if not expectation.source_prompts:
                return ElementCoverageResult(
                    state="absent_by_source",
                    matched_prompt_ids={},
                    matched_prompt_paths={},
                    missing_source_labels=(),
                )

            if not isinstance(subordinate_prompts, list):
                return ElementCoverageResult(
                    state="partially_encoded",
                    matched_prompt_ids={},
                    matched_prompt_paths={},
                    missing_source_labels=tuple(missing_source_labels),
                )

            for prompt_index, prompt in enumerate(subordinate_prompts):
                assert isinstance(prompt, dict)
                prompt_text = prompt.get("prompt")
                prompt_id = prompt.get("id")
                if not isinstance(prompt_text, str) or not isinstance(prompt_id, str):
                    continue
                source_label = source_labels_by_prompt.get(prompt_text)
                if source_label is None:
                    continue
                matched_prompt_ids[source_label] = prompt_id
                matched_prompt_paths[source_label] = (
                    f"evaluation_criteria[{criterion_index}]."
                    f"evaluation_elements[{element_index}]."
                    f"subordinate_prompts[{prompt_index}]"
                )

            unmatched = [
                item.source_label
                for item in expectation.source_prompts
                if item.source_label not in matched_prompt_ids
            ]
            state: CoverageState = (
                "fully_encoded" if not unmatched else "partially_encoded"
            )
            return ElementCoverageResult(
                state=state,
                matched_prompt_ids=matched_prompt_ids,
                matched_prompt_paths=matched_prompt_paths,
                missing_source_labels=tuple(unmatched),
            )

    if not expectation.source_prompts:
        return ElementCoverageResult(
            state="absent_by_source",
            matched_prompt_ids={},
            matched_prompt_paths={},
            missing_source_labels=(),
        )

    return ElementCoverageResult(
        state="partially_encoded",
        matched_prompt_ids={},
        matched_prompt_paths={},
        missing_source_labels=tuple(missing_source_labels),
    )


def test_wf0075_real_erc_poc_page_43_proof_call_is_partially_encoded() -> None:
    payload = _load_erc_poc_payload()

    results = {
        expectation.element_id: _classify_element_coverage(payload, expectation)
        for expectation in _page_43_expectations()
    }

    assert results["elem_breakthrough_innovation_potential"].state == "fully_encoded"
    assert results["elem_approach_methodology"].state == "partially_encoded"
    assert results["elem_pi_strategic_leadership"].state == "partially_encoded"
    assert (
        results["elem_approach_methodology"].missing_source_labels
        == ("1.b.1", "1.b.2")
    )
    assert results["elem_pi_strategic_leadership"].missing_source_labels == ("1.c.1",)
    assert (
        results["elem_breakthrough_innovation_potential"].matched_prompt_ids["1.a.1"]
        == "prompt_innovation_business_or_societal_impact"
    )
    assert (
        results["elem_breakthrough_innovation_potential"].matched_prompt_paths["1.a.5"]
        == "evaluation_criteria[0].evaluation_elements[0].subordinate_prompts[4]"
    )


def test_wf0075_absent_by_source_remains_distinct_from_partial_encoding() -> None:
    expectation = ElementCoverageExpectation(
        element_id="elem_outside_page_43_scope",
        source_locator="outside page 43",
        source_prompts=(),
    )
    payload = {
        "evaluation_criteria": [
            {
                "evaluation_elements": [
                    {
                        "id": "elem_outside_page_43_scope",
                        "name": "outside scope",
                    }
                ]
            }
        ]
    }

    result = _classify_element_coverage(payload, expectation)

    assert result.state == "absent_by_source"
    assert result.matched_prompt_ids == {}
    assert result.missing_source_labels == ()


def test_wf0075_omitting_an_official_page_43_prompt_fails_closed() -> None:
    payload = _load_erc_poc_payload()
    criteria = payload["evaluation_criteria"]
    assert isinstance(criteria, list)
    first_criterion = criteria[0]
    assert isinstance(first_criterion, dict)
    elements = first_criterion["evaluation_elements"]
    assert isinstance(elements, list)

    for element in elements:
        assert isinstance(element, dict)
        if element["id"] == "elem_approach_methodology":
            element["subordinate_prompts"] = [
                {
                    "id": "prompt_activities_and_planning",
                    "prompt": "Are the activities and planning appropriate and effective to explore the path from ground-breaking research towards innovation?",
                    "source_locator": "Work Programme 2026 section 2.1.6.1, element 1.b",
                    "source_hint": "wp_horizon-erc-2026_en.pdf page 43",
                }
            ]
        if element["id"] == "elem_pi_strategic_leadership":
            element["subordinate_prompts"] = [
                {
                    "id": "prompt_pi_clear_vision_risk_and_contingency",
                    "prompt": "Does the PI demonstrate a clear vision on how to manage the project, the consolidation of information and data needed to take strategic decisions and implement the proposed plan, including risk and contingency measures?",
                    "source_locator": "Work Programme 2026 section 2.1.6.1, element 1.c",
                    "source_hint": "wp_horizon-erc-2026_en.pdf page 43",
                }
            ]

    expectation = next(
        item
        for item in _page_43_expectations()
        if item.element_id == "elem_approach_methodology"
    )

    result = _classify_element_coverage(payload, expectation)

    assert result.state == "partially_encoded"
    assert result.missing_source_labels == ("1.b.2",)
