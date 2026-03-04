"""Focused tests for shared review execution core."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import TypedDict
from uuid import uuid4

import pytest
import yaml

import app.engine.pipeline_v1 as pipeline_v1
from app.engine.contracts import ReviewRequestV1
from app.engine.pipeline_v1 import run_review_pipeline
from app.models.domain import (
    EvaluationIntent,
    ExpectationStrength,
    NodeExpectation,
    NodeType,
    ProposalNode,
)
from app.services.review_execution_core import (
    ExecutionFailureCategory,
    ExecutionTelemetryPayload,
    ReviewExecutionCore,
)
from app.services.reviewer_policy import ReviewerPolicyRule

pytestmark = pytest.mark.no_db


class Wf0043PolicyCase(TypedDict):
    case_id: str
    surface: str
    expected_http_status: int
    expected_error_code: str | None
    expect_review_persisted: bool
    expected_review_status: str
    expected_summary_convention: str
    enforcement_mode: str
    forbidden_term: str
    feedback_text: str


class Wf0044PolicyCase(TypedDict):
    case_id: str
    surface: str
    selector: str
    enforcement_mode: str
    forbidden_term: str
    feedback_text: str
    expected_review_status: str
    expected_summary_convention: str
    expected_cards_count: int


class Wf0045ContractCase(TypedDict):
    case_id: str
    surface: str
    selector: str
    expected_pipeline_status: str
    expected_failure_class: str | None


def _load_wf0043_policy_cases() -> list[Wf0043PolicyCase]:
    fixture = yaml.safe_load(
        Path("tests/fixtures/wf_0043_contract_matrix.yaml").read_text(encoding="utf-8")
    )
    raw_cases = fixture.get("cases", [])
    if not isinstance(raw_cases, list):
        return []
    return [
        case
        for case in raw_cases
        if isinstance(case, dict) and case.get("surface") == "single_snippet_policy"
    ]


def _wf0043_policy_case_id(value: str) -> str:
    return f"wf0043_contract_single_snippet_policy_{value}"


def _load_wf0044_policy_cases() -> list[Wf0044PolicyCase]:
    fixture = yaml.safe_load(
        Path("tests/fixtures/wf_0044_policy_matrix.yaml").read_text(encoding="utf-8")
    )
    raw_cases = fixture.get("cases", [])
    if not isinstance(raw_cases, list):
        return []
    return [
        case
        for case in raw_cases
        if isinstance(case, dict) and case.get("surface") == "review_execution_core"
    ]


def _wf0044_policy_case_id(value: str, *, surface: str) -> str:
    return f"wf0044_policy_{surface}_{value}"


def _load_wf0045_contract_cases() -> list[Wf0045ContractCase]:
    fixture = yaml.safe_load(
        Path("tests/fixtures/wf_0045_contract_matrix.yaml").read_text(encoding="utf-8")
    )
    raw_cases = fixture.get("cases", [])
    if not isinstance(raw_cases, list):
        return []
    return [case for case in raw_cases if isinstance(case, dict)]


def _wf0045_contract_case_id(case: Wf0045ContractCase) -> str:
    return case["selector"]


class EchoExpectationLLMClient:
    """Returns one feedback per expectation ID found in prompt."""

    def generate(self, prompt: str) -> str:
        expectation_ids = re.findall(r"ID:\s*([0-9a-fA-F-]{36})", prompt)
        payload = {
            "feedbacks": [
                {
                    "node_expectation_id": expectation_id,
                    "feedback": f"Feedback for {expectation_id}",
                }
                for expectation_id in expectation_ids
            ]
        }
        return json.dumps(payload)

    def get_model_name(self) -> str:
        return "echo-test-model"


class TimeoutLLMClient(EchoExpectationLLMClient):
    def generate(self, prompt: str) -> str:
        time.sleep(0.1)
        return super().generate(prompt)


class PolicyTermLLMClient:
    def __init__(self, feedback: str) -> None:
        self._feedback = feedback

    def generate(self, prompt: str) -> str:
        expectation_ids = re.findall(r"ID:\s*([0-9a-fA-F-]{36})", prompt)
        return json.dumps(
            {
                "feedbacks": [
                    {
                        "node_expectation_id": expectation_ids[0],
                        "feedback": self._feedback,
                    }
                ]
            }
        )

    def get_model_name(self) -> str:
        return "policy-term-model"


class SequencePolicyLLMClient:
    def __init__(self, feedbacks: list[str]) -> None:
        self._feedbacks = feedbacks
        self.calls = 0

    def generate(self, prompt: str) -> str:
        self.calls += 1
        expectation_ids = re.findall(r"ID:\s*([0-9a-fA-F-]{36})", prompt)
        feedback = self._feedbacks[min(self.calls - 1, len(self._feedbacks) - 1)]
        return json.dumps(
            {
                "feedbacks": [
                    {
                        "node_expectation_id": expectation_ids[0],
                        "feedback": feedback,
                    }
                ]
            }
        )

    def get_model_name(self) -> str:
        return "sequence-policy-model"


class RecordingTelemetryHooks:
    def __init__(self) -> None:
        self.starts: list[ExecutionTelemetryPayload] = []
        self.completes: list[ExecutionTelemetryPayload] = []
        self.failures: list[ExecutionTelemetryPayload] = []

    def on_execution_start(self, payload: ExecutionTelemetryPayload) -> None:
        self.starts.append(payload)

    def on_execution_complete(self, payload: ExecutionTelemetryPayload) -> None:
        self.completes.append(payload)

    def on_execution_failure(self, payload: ExecutionTelemetryPayload) -> None:
        self.failures.append(payload)


def _build_node() -> ProposalNode:
    return ProposalNode(
        id=uuid4(),
        funding_call_id=uuid4(),
        logical_id="research_idea",
        node_type=NodeType.SECTION,
        title="Research idea",
        order_index=1,
    )


def _build_expectations(count: int = 1) -> list[NodeExpectation]:
    expectations: list[NodeExpectation] = []
    for order in range(1, count + 1):
        expectations.append(
            NodeExpectation(
                id=uuid4(),
                proposal_node_id=uuid4(),
                evaluation_element_id=uuid4(),
                expectation_strength=ExpectationStrength.MANDATORY,
                evaluation_intent=EvaluationIntent.QUALITY,
                guidance_note="guidance",
                order_index=order,
            )
        )
    return expectations


def test_core_success_result() -> None:
    core = ReviewExecutionCore(llm_client=EchoExpectationLLMClient(), timeout_seconds=0.5)
    node = _build_node()
    expectations = _build_expectations(count=2)

    result = core.execute_assessable_node(
        node=node,
        snippet_text="Some snippet text",
        expectations=expectations,
        reviewer_policy_rules=[],
    )

    assert result.failure is None
    assert len(result.feedbacks) == 2
    assert result.raw_response is not None
    assert result.prompt
    assert result.warning_violations == []


def test_core_timeout_classification() -> None:
    core = ReviewExecutionCore(llm_client=TimeoutLLMClient(), timeout_seconds=0.01)
    node = _build_node()
    expectations = _build_expectations(count=1)

    result = core.execute_assessable_node(
        node=node,
        snippet_text="Some snippet text",
        expectations=expectations,
        reviewer_policy_rules=[],
    )

    assert result.failure is not None
    assert result.failure.category == ExecutionFailureCategory.TIMEOUT
    assert result.feedbacks == []
    assert result.raw_response is None


def test_core_policy_postcheck_classification() -> None:
    rule_post_check = ReviewerPolicyRule(
        id="pol_warn",
        applies_to_stage="STEP_1",
        applies_to_node_ids=(),
        rule_type="stage_scope",
        instruction="Warn on maybe wording",
        severity="WARNING",
        enforcement_mode="POST_CHECK",
        forbidden_terms=("maybe",),
    )
    rule_blocking = ReviewerPolicyRule(
        id="pol_block",
        applies_to_stage="STEP_1",
        applies_to_node_ids=(),
        rule_type="criterion_scope",
        instruction="Block budget assessment",
        severity="WARNING",
        enforcement_mode="BLOCKING",
        forbidden_terms=("insufficient budget",),
    )

    node = _build_node()
    expectations = _build_expectations(count=1)

    warning_core = ReviewExecutionCore(
        llm_client=PolicyTermLLMClient("This is maybe acceptable."),
        timeout_seconds=0.5,
    )
    warning_result = warning_core.execute_assessable_node(
        node=node,
        snippet_text="Some snippet text",
        expectations=expectations,
        reviewer_policy_rules=[rule_post_check],
    )
    assert warning_result.failure is None
    assert len(warning_result.warning_violations) == 1
    assert "pol_warn" in warning_result.warning_violations[0]

    blocking_core = ReviewExecutionCore(
        llm_client=PolicyTermLLMClient("The proposal has insufficient budget."),
        timeout_seconds=0.5,
    )
    blocking_result = blocking_core.execute_assessable_node(
        node=node,
        snippet_text="Some snippet text",
        expectations=expectations,
        reviewer_policy_rules=[rule_blocking],
    )
    assert blocking_result.failure is not None
    assert blocking_result.failure.category == ExecutionFailureCategory.POLICY_BLOCKING
    assert "pol_block" in blocking_result.failure.message


def test_core_policy_blocking_retries_once_then_succeeds() -> None:
    rule_blocking = ReviewerPolicyRule(
        id="pol_block",
        applies_to_stage="STEP_1",
        applies_to_node_ids=(),
        rule_type="criterion_scope",
        instruction="Block budget assessment",
        severity="WARNING",
        enforcement_mode="BLOCKING",
        forbidden_terms=("insufficient budget",),
    )
    llm_client = SequencePolicyLLMClient(
        [
            "The proposal has insufficient budget.",
            "The proposal scope is well supported.",
        ]
    )
    core = ReviewExecutionCore(llm_client=llm_client, timeout_seconds=0.5)
    node = _build_node()
    expectations = _build_expectations(count=1)

    result = core.execute_assessable_node(
        node=node,
        snippet_text="Some snippet text",
        expectations=expectations,
        reviewer_policy_rules=[rule_blocking],
    )

    assert result.failure is None
    assert llm_client.calls == 2
    assert len(result.feedbacks) == 1


def test_core_policy_blocking_fails_after_single_retry() -> None:
    rule_blocking = ReviewerPolicyRule(
        id="pol_block",
        applies_to_stage="STEP_1",
        applies_to_node_ids=(),
        rule_type="criterion_scope",
        instruction="Block budget assessment",
        severity="WARNING",
        enforcement_mode="BLOCKING",
        forbidden_terms=("insufficient budget",),
    )
    llm_client = SequencePolicyLLMClient(
        [
            "The proposal has insufficient budget.",
            "The proposal has insufficient budget.",
            "The proposal has insufficient budget.",
        ]
    )
    core = ReviewExecutionCore(llm_client=llm_client, timeout_seconds=0.5)
    node = _build_node()
    expectations = _build_expectations(count=1)

    result = core.execute_assessable_node(
        node=node,
        snippet_text="Some snippet text",
        expectations=expectations,
        reviewer_policy_rules=[rule_blocking],
    )

    assert result.failure is not None
    assert result.failure.category == ExecutionFailureCategory.POLICY_BLOCKING
    assert llm_client.calls == 2


@pytest.mark.parametrize(
    "case",
    _load_wf0043_policy_cases(),
    ids=lambda case: _wf0043_policy_case_id(case["case_id"]),
)
def test_wf0043_contract_single_snippet_policy_modes(case: Wf0043PolicyCase) -> None:
    rule = ReviewerPolicyRule(
        id=f"wf0043_{case['case_id']}",
        applies_to_stage="STEP_1",
        applies_to_node_ids=(),
        rule_type="criterion_scope",
        instruction="WF-0043 deterministic policy test rule",
        severity="WARNING",
        enforcement_mode=case["enforcement_mode"],
        forbidden_terms=(case["forbidden_term"],),
    )
    core = ReviewExecutionCore(
        llm_client=PolicyTermLLMClient(case["feedback_text"]),
        timeout_seconds=0.5,
    )

    result = core.execute_assessable_node(
        node=_build_node(),
        snippet_text="Some snippet text",
        expectations=_build_expectations(count=1),
        reviewer_policy_rules=[rule],
    )

    assert case["expected_http_status"] == 200
    assert case["expected_error_code"] is None
    assert case["expect_review_persisted"] is True

    if case["enforcement_mode"] == "BLOCKING":
        assert result.failure is not None
        assert result.failure.category == ExecutionFailureCategory.POLICY_BLOCKING
        assert case["expected_review_status"] == "FAILED"
        assert case["expected_summary_convention"] == "POLICY_BLOCKING"
        return

    assert result.failure is None
    assert case["expected_review_status"] == "COMPLETED"
    if case["enforcement_mode"] == "POST_CHECK":
        assert len(result.warning_violations) == 1
        assert case["expected_summary_convention"] == "POST_CHECK_WARNING"
    else:
        assert result.warning_violations == []
        assert case["expected_summary_convention"] == "PROMPT_ONLY_NON_BLOCKING"
        assert "WF-0043 deterministic policy test rule" in result.prompt


def test_wf0043_contract_single_snippet_policy_matrix_coverage() -> None:
    cases = _load_wf0043_policy_cases()
    case_ids = {case["case_id"] for case in cases}
    assert case_ids == {"policy_blocking", "policy_post_check", "policy_prompt_only"}
    for case in cases:
        assert case["surface"] == "single_snippet_policy"
        assert isinstance(case["feedback_text"], str) and bool(case["feedback_text"].strip())


@pytest.mark.parametrize(
    "case",
    _load_wf0044_policy_cases(),
    ids=lambda case: _wf0044_policy_case_id(
        case["case_id"], surface="review_execution_core"
    ),
)
def test_wf0044_policy_review_execution_core_modes(case: Wf0044PolicyCase) -> None:
    rule = ReviewerPolicyRule(
        id=f"wf0044_{case['case_id']}",
        applies_to_stage="STEP_1",
        applies_to_node_ids=(),
        rule_type="criterion_scope",
        instruction="WF-0044 deterministic policy test rule",
        severity="WARNING",
        enforcement_mode=case["enforcement_mode"],
        forbidden_terms=(case["forbidden_term"],),
    )
    core = ReviewExecutionCore(
        llm_client=PolicyTermLLMClient(case["feedback_text"]),
        timeout_seconds=0.5,
    )

    result = core.execute_assessable_node(
        node=_build_node(),
        snippet_text="Some snippet text",
        expectations=_build_expectations(count=1),
        reviewer_policy_rules=[rule],
    )

    if case["enforcement_mode"] == "BLOCKING":
        assert result.failure is not None
        assert result.failure.category == ExecutionFailureCategory.POLICY_BLOCKING
        assert result.feedbacks == []
        assert case["expected_review_status"] == "FAILED"
        assert case["expected_summary_convention"] == "POLICY_BLOCKING"
        return

    assert result.failure is None
    assert len(result.feedbacks) == case["expected_cards_count"]
    assert case["expected_review_status"] == "COMPLETED"
    if case["enforcement_mode"] == "POST_CHECK":
        assert len(result.warning_violations) == 1
        assert case["expected_summary_convention"] == "POST_CHECK_WARNING"
        return

    assert result.warning_violations == []
    assert case["expected_summary_convention"] == "PROMPT_ONLY_NON_BLOCKING"


def test_wf0044_policy_review_execution_core_matrix_coverage() -> None:
    cases = _load_wf0044_policy_cases()
    case_ids = {case["case_id"] for case in cases}
    assert case_ids == {"prompt_only", "post_check", "blocking"}
    for case in cases:
        assert case["surface"] == "review_execution_core"
        assert case["selector"].startswith("wf0044_policy_review_execution_core_")


def test_wf0045_contract_matrix_coverage() -> None:
    cases = _load_wf0045_contract_cases()
    case_ids = {case["case_id"] for case in cases}
    assert case_ids == {
        "happy_path",
        "contract_failure",
        "execution_failure",
        "ordering_parity",
        "call_agnostic_guardrails",
    }
    selectors = {case["selector"] for case in cases}
    assert len(selectors) == len(cases)
    assert all(selector.startswith("wf0045_contract_") for selector in selectors)


@pytest.mark.parametrize(
    "case",
    _load_wf0045_contract_cases(),
    ids=_wf0045_contract_case_id,
)
def test_wf0045_contract_matrix_execution(
    case: Wf0045ContractCase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if case["case_id"] == "call_agnostic_guardrails":
        core = ReviewExecutionCore(llm_client=EchoExpectationLLMClient(), timeout_seconds=0.5)
        node = _build_node()
        expectations = _build_expectations(count=1)
        first = core.execute_assessable_node(
            node=node,
            snippet_text="Some snippet text",
            expectations=expectations,
            reviewer_policy_rules=[],
            call_identity="matrix-call-a",
            optional_extensions={"program_specific_policy": True},
        )
        second = core.execute_assessable_node(
            node=node,
            snippet_text="Some snippet text",
            expectations=expectations,
            reviewer_policy_rules=[],
            call_identity="matrix-call-b",
            optional_extensions={"program_specific_policy": False},
        )
        assert case["expected_pipeline_status"] == "SUCCESS"
        assert first.failure is None
        assert second.failure is None
        return

    if case["case_id"] == "execution_failure":
        def _raise_execution_failure(*args, **kwargs):  # type: ignore[no-untyped-def]
            del args, kwargs
            raise RuntimeError("forced execution failure")

        monkeypatch.setattr(
            pipeline_v1,
            "evaluate_expectations",
            _raise_execution_failure,
        )
        request = ReviewRequestV1(
            request_id="wf0045-matrix-execution-failure",
            mode="DIAGNOSTIC",
            stage_ref="STEP_1",
            call_config_digest="sha256:demo",
            call_config_snapshot={
                "expectations": [
                    {
                        "expectation_id": "exp-exec",
                        "node_logical_id": "research_idea",
                        "check_id": "check.presence",
                        "required": True,
                    }
                ]
            },
            proposal_nodes={"research_idea": "text"},
        )
        result = run_review_pipeline(request)
    elif case["case_id"] == "contract_failure":
        request = ReviewRequestV1(
            request_id="wf0045-matrix-contract-failure",
            mode="DIAGNOSTIC",
            stage_ref="BAD_STAGE",
            call_config_digest="sha256:demo",
            call_config_snapshot={"expectations": []},
            proposal_nodes={},
        )
        result = run_review_pipeline(request)
    else:
        request = ReviewRequestV1(
            request_id=f"wf0045-matrix-{case['case_id']}",
            mode="DIAGNOSTIC",
            stage_ref="STEP_1",
            call_config_digest="sha256:demo",
            call_config_snapshot={
                "expectations": [
                    {
                        "expectation_id": "exp-1",
                        "node_logical_id": "research_idea",
                        "check_id": "check.presence",
                        "required": True,
                    }
                ]
            },
            proposal_nodes={"research_idea": "clear text"},
        )
        first = run_review_pipeline(request)
        second = run_review_pipeline(request)
        if case["case_id"] == "ordering_parity":
            assert [item.finding_id for item in first.findings] == [
                item.finding_id for item in second.findings
            ]
        result = first

    assert result.pipeline_status == case["expected_pipeline_status"]
    if case["expected_failure_class"] is None:
        assert result.compatibility_output.get("failure_class") is None
    else:
        assert result.compatibility_output["failure_class"] == case["expected_failure_class"]


def test_core_emits_telemetry_start_complete() -> None:
    hooks = RecordingTelemetryHooks()
    core = ReviewExecutionCore(
        llm_client=EchoExpectationLLMClient(),
        timeout_seconds=0.5,
        telemetry_hooks=hooks,
    )
    node = _build_node()
    expectations = _build_expectations(count=1)

    result = core.execute_assessable_node(
        node=node,
        snippet_text="Some snippet text",
        expectations=expectations,
        reviewer_policy_rules=[],
    )

    assert result.failure is None
    assert len(hooks.starts) == 1
    assert len(hooks.completes) == 1
    assert hooks.failures == []
    assert hooks.starts[0].node_logical_id == "research_idea"
    assert hooks.starts[0].expectation_count == 1


def test_core_emits_telemetry_failure_category() -> None:
    hooks = RecordingTelemetryHooks()
    core = ReviewExecutionCore(
        llm_client=TimeoutLLMClient(),
        timeout_seconds=0.01,
        telemetry_hooks=hooks,
    )
    node = _build_node()
    expectations = _build_expectations(count=1)

    result = core.execute_assessable_node(
        node=node,
        snippet_text="Some snippet text",
        expectations=expectations,
        reviewer_policy_rules=[],
    )

    assert result.failure is not None
    assert len(hooks.starts) == 1
    assert hooks.completes == []
    assert len(hooks.failures) == 1
    assert hooks.failures[0].failure_category == ExecutionFailureCategory.TIMEOUT.value


def test_wf0045_contract_call_agnostic_core() -> None:
    core = ReviewExecutionCore(llm_client=EchoExpectationLLMClient(), timeout_seconds=0.5)
    node = _build_node()
    expectations = _build_expectations(count=1)

    result_a = core.execute_assessable_node(
        node=node,
        snippet_text="Some snippet text",
        expectations=expectations,
        reviewer_policy_rules=[],
        call_identity="call-A",
    )
    result_b = core.execute_assessable_node(
        node=node,
        snippet_text="Some snippet text",
        expectations=expectations,
        reviewer_policy_rules=[],
        call_identity="call-B",
    )

    assert result_a.failure is None
    assert result_b.failure is None
    assert [feedback.feedback for feedback in result_a.feedbacks] == [
        feedback.feedback for feedback in result_b.feedbacks
    ]
