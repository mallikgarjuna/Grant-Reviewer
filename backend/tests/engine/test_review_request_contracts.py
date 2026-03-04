from __future__ import annotations

import hashlib
import json
import operator
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from app.engine.contracts import ActivatedCallConfigSnapshotV1
from app.engine.pipeline_v1 import run_review_pipeline
from app.engine.review_request_validator import (
    ReviewRequestValidationError,
    canonicalize_for_digest,
    validate_review_request_payload,
)

# Module-level marker keeps all WF contract suites (including WF-0052) in CI gate scope.
pytestmark = [pytest.mark.no_db, pytest.mark.contract_gate]


def _build_snapshot() -> dict[str, object]:
    return {
        "schema_version": "v1",
        "expectations": [
            {
                "expectation_id": "exp-1",
                "node_logical_id": "research_idea",
                "check_id": "check.presence",
            }
        ],
    }


def _build_payload() -> dict[str, object]:
    snapshot = _build_snapshot()
    return {
        "request_id": "req-1",
        "mode": "DIAGNOSTIC",
        "stage_ref": "STEP_1",
        "call_config_snapshot": snapshot,
        "call_config_digest": _canonical_digest_for_snapshot(snapshot),
        "proposal_nodes": {"research_idea": "text"},
    }


def _assert_field_errors_are_sorted(errors: list[dict[str, str]]) -> None:
    assert errors == sorted(
        errors,
        key=operator.itemgetter("path", "kind", "message"),
    )


def _assert_malformed_request_with_field_error(
    err: ReviewRequestValidationError,
    *,
    path: str,
    kind: str,
    message: str,
) -> None:
    assert err.code == "MALFORMED_REVIEW_REQUEST"
    assert {
        "path": path,
        "kind": kind,
        "message": message,
    } in err.details["field_errors"]


def _find_field_error_by_path(
    errors: list[dict[str, str]],
    *,
    path: str,
) -> dict[str, str]:
    for entry in errors:
        if entry["path"] == path:
            return entry
    raise AssertionError(f"Expected field error for path {path!r}, got {errors!r}")


def _load_wf0049_compat_matrix() -> dict[str, dict[str, object]]:
    fixture = yaml.safe_load(
        Path("tests/fixtures/wf_0049_nested_schema_compat_matrix.yaml").read_text(
            encoding="utf-8"
        )
    )
    cases: list[dict[str, object]] = fixture["cases"]
    by_case = {str(case["class_id"]): case for case in cases}
    required = {
        "happy_valid_payload",
        "legacy_extra_nested_key",
        "nested_type_mismatch",
        "omitted_optional_default_equivalence",
    }
    missing = sorted(required - by_case.keys())
    assert not missing, f"Missing required compatibility classes: {missing}"
    return by_case


def _load_wf0052_compat_matrix() -> dict[str, dict[str, object]]:
    fixture = yaml.safe_load(
        Path("tests/fixtures/wf_0052_real_snapshot_compat_matrix.yaml").read_text(
            encoding="utf-8"
        )
    )
    cases: list[dict[str, object]] = fixture["cases"]
    by_case = {str(case["class_id"]): case for case in cases}
    required = {
        "happy_valid_payload_real_snapshot",
        "legacy_extra_nested_key_real_snapshot",
        "nested_type_mismatch_real_snapshot",
        "omitted_optional_default_equivalence_real_snapshot",
    }
    missing = sorted(required - by_case.keys())
    assert not missing, f"Missing required WF-0052 compatibility classes: {missing}"
    return by_case


def _load_source_call(path: str) -> dict[str, object]:
    raw = Path(path).read_text(encoding="utf-8")
    loaded = yaml.safe_load(raw)
    assert isinstance(loaded, dict)
    return loaded


def _source_call_element_ids(call_payload: dict[str, object]) -> set[str]:
    criteria = call_payload.get("evaluation_criteria", [])
    assert isinstance(criteria, list)
    element_ids: set[str] = set()
    for criterion in criteria:
        if not isinstance(criterion, dict):
            continue
        elements = criterion.get("evaluation_elements", [])
        if not isinstance(elements, list):
            continue
        for element in elements:
            if isinstance(element, dict) and isinstance(element.get("id"), str):
                element_ids.add(element["id"])
    return element_ids


def _assert_case_grounded_to_source_call(case: dict[str, object]) -> None:
    source_call_path = case["source_call_path"]
    assert isinstance(source_call_path, str)
    source_call = _load_source_call(source_call_path)
    source_element_ids = _source_call_element_ids(source_call)
    grounding_element_ids = case["grounding_element_ids"]
    assert isinstance(grounding_element_ids, list)
    for element_id in grounding_element_ids:
        assert isinstance(element_id, str)
        assert element_id in source_element_ids, (
            f"Element {element_id!r} not found in source call {source_call_path}"
        )


def _build_payload_for_snapshot(snapshot: dict[str, object], *, digest: str) -> dict[str, object]:
    payload = _build_payload()
    payload["call_config_snapshot"] = snapshot
    payload["call_config_digest"] = digest
    return payload


def _canonical_digest_for_snapshot(snapshot: dict[str, object]) -> str:
    validated_snapshot = ActivatedCallConfigSnapshotV1.model_validate(snapshot)
    canonical = canonicalize_for_digest(validated_snapshot.to_canonical_payload())
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def test_wf0048_contract_tracer_valid_snapshot_digest_ok() -> None:
    payload = _build_payload()

    validated = validate_review_request_payload(payload)

    assert isinstance(validated.call_config_snapshot, ActivatedCallConfigSnapshotV1)
    assert validated.call_config_snapshot.schema_version == "v1"


def test_wf0048_contract_unknown_field_stable_pointer() -> None:
    payload = _build_payload()
    payload["unknown_top_level"] = "bad"
    payload["call_config_snapshot"]["expectations"][0]["unknown_nested"] = True

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    assert err_info.value.code == "MALFORMED_REVIEW_REQUEST"
    assert err_info.value.details["field_errors"] == [
        {
            "path": "/call_config_snapshot/expectations/0/unknown_nested",
            "kind": "unknown_field",
            "message": "Unknown field is not allowed.",
        },
        {
            "path": "/unknown_top_level",
            "kind": "unknown_field",
            "message": "Unknown field is not allowed.",
        },
    ]


def test_wf0048_contract_field_error_sort_order() -> None:
    payload = _build_payload()
    payload["unknown_top_level"] = "bad"
    del payload["request_id"]
    payload["call_config_snapshot"]["schema_version"] = "v2"
    payload["proposal_nodes"] = {"research_idea": 123}

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    errors = err_info.value.details["field_errors"]
    _assert_field_errors_are_sorted(errors)


def test_wf0048_contract_kind_message_templates() -> None:
    payload = _build_payload()
    del payload["request_id"]
    payload["unknown_top_level"] = "bad"
    payload["proposal_nodes"] = {"research_idea": 123}
    payload["call_config_snapshot"]["schema_version"] = "v2"

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    field_errors = err_info.value.details["field_errors"]
    actual_kind_to_message = {error["kind"]: error["message"] for error in field_errors}

    assert actual_kind_to_message["unknown_field"] == "Unknown field is not allowed."
    assert actual_kind_to_message["missing_field"] == "Field is required."
    assert actual_kind_to_message["type_error"] == "Invalid field type."
    assert actual_kind_to_message["value_error"] == "Invalid field value."


def test_wf0048_contract_schema_precedes_digest() -> None:
    payload = _build_payload()
    payload["call_config_digest"] = "sha256:deadbeef"
    del payload["request_id"]

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    assert err_info.value.code == "MALFORMED_REVIEW_REQUEST"
    assert "field_errors" in err_info.value.details


def test_wf0048_contract_digest_mismatch_post_schema() -> None:
    payload = _build_payload()
    payload["call_config_digest"] = "sha256:deadbeef"

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    assert err_info.value.code == "CALL_CONFIG_DIGEST_MISMATCH"


def test_wf0048_contract_replay_byte_stable_success() -> None:
    validated = validate_review_request_payload(_build_payload())

    first = run_review_pipeline(validated)
    second = run_review_pipeline(validated)

    first_canonical = json.dumps(
        first.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    second_canonical = json.dumps(
        second.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    assert first_canonical == second_canonical


def test_wf0048_contract_snapshot_driven_not_identity_driven() -> None:
    payload = _build_payload()
    payload["call_config_snapshot"]["call_code"] = "nwo_veni_2025_preproposal"

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    assert err_info.value.code == "MALFORMED_REVIEW_REQUEST"
    assert err_info.value.details["field_errors"][0] == {
        "path": "/call_config_snapshot/call_code",
        "kind": "unknown_field",
        "message": "Unknown field is not allowed.",
    }


def test_wf0048_contract_expectations_required_field_error() -> None:
    payload = _build_payload()
    del payload["call_config_snapshot"]["expectations"]
    payload["call_config_digest"] = "sha256:deadbeef"

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    assert err_info.value.code == "MALFORMED_REVIEW_REQUEST"
    assert {
        "path": "/call_config_snapshot/expectations",
        "kind": "missing_field",
        "message": "Field is required.",
    } in err_info.value.details["field_errors"]


def test_wf0048_contract_required_true_drives_error_severity() -> None:
    payload = _build_payload()
    payload["call_config_snapshot"]["expectations"][0]["required"] = True
    payload["proposal_nodes"]["research_idea"] = ""
    payload["call_config_digest"] = _canonical_digest_for_snapshot(
        payload["call_config_snapshot"]
    )

    result = run_review_pipeline(validate_review_request_payload(payload))

    assert [finding.severity for finding in result.findings] == ["ERROR"]


def test_wf0049_contract_tracer_criteria_nested_unknown_rejected() -> None:
    payload = _build_payload()
    payload["call_config_snapshot"]["evaluation_criteria"] = [
        {
            "id": "crit-1",
            "name": "Criterion 1",
            "stage": "STEP_1",
            "weight_percent": 50,
            "evaluation_elements": [],
            "unexpected_field": "bad",
        }
    ]
    digest = hashlib.sha256(
        canonicalize_for_digest(payload["call_config_snapshot"]).encode("utf-8")
    ).hexdigest()
    payload["call_config_digest"] = f"sha256:{digest}"

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    _assert_malformed_request_with_field_error(
        err_info.value,
        path="/call_config_snapshot/evaluation_criteria/0/unexpected_field",
        kind="unknown_field",
        message="Unknown field is not allowed.",
    )


def test_wf0049_contract_tracer_schema_precedes_digest() -> None:
    payload = _build_payload()
    payload["call_config_snapshot"]["evaluation_criteria"] = [
        {
            "id": "crit-1",
            "name": "Criterion 1",
            "stage": "STEP_1",
            "weight_percent": 50,
            "evaluation_elements": [],
            "unexpected_field": "bad",
        }
    ]
    payload["call_config_digest"] = "sha256:deadbeef"

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    _assert_malformed_request_with_field_error(
        err_info.value,
        path="/call_config_snapshot/evaluation_criteria/0/unexpected_field",
        kind="unknown_field",
        message="Unknown field is not allowed.",
    )
    assert "field_errors" in err_info.value.details
    assert not {"expected", "received"}.intersection(err_info.value.details)


def test_wf0049_contract_elements_surface_strict() -> None:
    valid_payload = _build_payload()
    valid_payload["call_config_snapshot"]["evaluation_criteria"] = [
        {
            "id": "crit-1",
            "name": "Criterion 1",
            "stage": "STEP_1",
            "weight_percent": 50,
            "evaluation_elements": [
                {
                    "id": "elem-1",
                    "name": "Element 1",
                    "description": "Element description",
                    "source_hint": "proposal",
                    "stage": "STEP_1",
                }
            ],
        }
    ]
    valid_payload["call_config_digest"] = _canonical_digest_for_snapshot(
        valid_payload["call_config_snapshot"]
    )

    validated = validate_review_request_payload(valid_payload)
    assert validated.call_config_snapshot.evaluation_criteria is not None
    assert validated.call_config_snapshot.evaluation_criteria[0].evaluation_elements[0].id == "elem-1"

    invalid_payload = _build_payload()
    invalid_payload["call_config_snapshot"]["evaluation_criteria"] = [
        {
            "id": "crit-1",
            "name": "Criterion 1",
            "stage": "STEP_1",
            "weight_percent": 50,
            "evaluation_elements": [
                {
                    "id": "elem-1",
                    "name": "Element 1",
                    "description": "Element description",
                    "stage": "STEP_1",
                    "unknown_nested": "bad",
                }
            ],
        }
    ]
    invalid_digest = hashlib.sha256(
        canonicalize_for_digest(invalid_payload["call_config_snapshot"]).encode("utf-8")
    ).hexdigest()
    invalid_payload["call_config_digest"] = f"sha256:{invalid_digest}"

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(invalid_payload)

    _assert_malformed_request_with_field_error(
        err_info.value,
        path="/call_config_snapshot/evaluation_criteria/0/evaluation_elements/0/unknown_nested",
        kind="unknown_field",
        message="Unknown field is not allowed.",
    )


def test_wf0049_contract_elements_root_surface_strict() -> None:
    valid_payload = _build_payload()
    valid_payload["call_config_snapshot"]["evaluation_elements"] = [
        {
            "id": "elem-1",
            "name": "Element 1",
            "description": "Element description",
            "stage": "STEP_1",
        }
    ]
    valid_payload["call_config_digest"] = _canonical_digest_for_snapshot(
        valid_payload["call_config_snapshot"]
    )

    validated = validate_review_request_payload(valid_payload)
    assert validated.call_config_snapshot.evaluation_elements is not None
    assert validated.call_config_snapshot.evaluation_elements[0].id == "elem-1"

    invalid_payload = _build_payload()
    invalid_payload["call_config_snapshot"]["evaluation_elements"] = [
        {
            "id": "elem-1",
            "name": "Element 1",
            "description": "Element description",
            "stage": "STEP_1",
            "unexpected_field": "bad",
        }
    ]
    invalid_payload["call_config_digest"] = _canonical_digest_for_snapshot(
        _build_snapshot()
    )

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(invalid_payload)

    _assert_malformed_request_with_field_error(
        err_info.value,
        path="/call_config_snapshot/evaluation_elements/0/unexpected_field",
        kind="unknown_field",
        message="Unknown field is not allowed.",
    )


def test_wf0049_contract_reviewer_policy_surface_strict() -> None:
    valid_payload = _build_payload()
    valid_payload["call_config_snapshot"]["reviewer_policy"] = [
        {
            "id": "policy-1",
            "applies_to_stage": "STEP_1",
            "applies_to_node_ids": ["research_idea"],
            "rule_type": "tone",
            "instruction": "Keep language specific.",
            "severity": "WARNING",
            "enforcement_mode": "PROMPT_ONLY",
            "forbidden_terms": ["always"],
            "source_hint": "call-doc",
        }
    ]
    valid_payload["call_config_digest"] = _canonical_digest_for_snapshot(
        valid_payload["call_config_snapshot"]
    )
    validated = validate_review_request_payload(valid_payload)
    assert validated.call_config_snapshot.reviewer_policy is not None
    assert validated.call_config_snapshot.reviewer_policy[0].id == "policy-1"

    invalid_payload = _build_payload()
    invalid_payload["call_config_snapshot"]["reviewer_policy"] = [
        {
            "id": "policy-1",
            "applies_to_stage": "STEP_1",
            "applies_to_node_ids": ["research_idea"],
            "rule_type": "tone",
            "instruction": "Keep language specific.",
            "severity": "WARNING",
            "enforcement_mode": "PROMPT_ONLY",
            "forbidden_terms": ["always"],
            "unknown_nested": "bad",
        }
    ]
    invalid_digest = hashlib.sha256(
        canonicalize_for_digest(invalid_payload["call_config_snapshot"]).encode("utf-8")
    ).hexdigest()
    invalid_payload["call_config_digest"] = f"sha256:{invalid_digest}"

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(invalid_payload)

    _assert_malformed_request_with_field_error(
        err_info.value,
        path="/call_config_snapshot/reviewer_policy/0/unknown_nested",
        kind="unknown_field",
        message="Unknown field is not allowed.",
    )


def test_wf0049_contract_prompt_knobs_surface_strict() -> None:
    valid_payload = _build_payload()
    valid_payload["call_config_snapshot"]["prompt_knobs"] = {
        "temperature": 0.2,
        "max_tokens": 600,
        "top_p": 0.9,
    }
    valid_payload["call_config_digest"] = _canonical_digest_for_snapshot(
        valid_payload["call_config_snapshot"]
    )
    validated = validate_review_request_payload(valid_payload)
    assert validated.call_config_snapshot.prompt_knobs is not None
    assert validated.call_config_snapshot.prompt_knobs.temperature == 0.2

    invalid_payload = _build_payload()
    invalid_payload["call_config_snapshot"]["prompt_knobs"] = {
        "temperature": 0.2,
        "unknown_knob": 1,
    }
    invalid_digest = hashlib.sha256(
        canonicalize_for_digest(invalid_payload["call_config_snapshot"]).encode("utf-8")
    ).hexdigest()
    invalid_payload["call_config_digest"] = f"sha256:{invalid_digest}"

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(invalid_payload)

    _assert_malformed_request_with_field_error(
        err_info.value,
        path="/call_config_snapshot/prompt_knobs/unknown_knob",
        kind="unknown_field",
        message="Unknown field is not allowed.",
    )


def test_wf0050_contract_compliance_rules_surface_strict() -> None:
    valid_payload = _build_payload()
    valid_payload["call_config_snapshot"]["compliance_rules"] = [
        {
            "id": "rule-1",
            "severity": "WARNING",
            "rule_type": "word_limit",
            "description": "Respect section word limit.",
        }
    ]
    valid_payload["call_config_digest"] = _canonical_digest_for_snapshot(
        valid_payload["call_config_snapshot"]
    )

    validated = validate_review_request_payload(valid_payload)
    assert validated.call_config_snapshot.compliance_rules is not None
    assert validated.call_config_snapshot.compliance_rules[0].id == "rule-1"

    invalid_payload = _build_payload()
    invalid_payload["call_config_snapshot"]["compliance_rules"] = [
        {
            "id": "rule-1",
            "severity": "WARNING",
            "rule_type": "word_limit",
            "description": "Respect section word limit.",
            "unexpected_field": "bad",
        }
    ]
    invalid_payload["call_config_digest"] = _canonical_digest_for_snapshot(
        _build_snapshot()
    )

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(invalid_payload)

    _assert_malformed_request_with_field_error(
        err_info.value,
        path="/call_config_snapshot/compliance_rules/0/unexpected_field",
        kind="unknown_field",
        message="Unknown field is not allowed.",
    )


def test_wf0050_contract_producer_stress_fixture_requests_validate() -> None:
    fixture = yaml.safe_load(
        Path("tests/fixtures/review_engine_stress_matrix.yaml").read_text(encoding="utf-8")
    )
    scenarios: list[dict[str, object]] = fixture["scenarios"]
    assert scenarios

    for scenario in scenarios:
        request_payload = dict(scenario["request"])
        snapshot = request_payload["call_config_snapshot"]
        assert isinstance(snapshot, dict)
        request_payload["call_config_digest"] = _canonical_digest_for_snapshot(snapshot)

        validated = validate_review_request_payload(request_payload)
        assert validated.call_config_snapshot.schema_version == "v1"


def test_wf0050_contract_stage_gating_surface_strict() -> None:
    valid_payload = _build_payload()
    valid_payload["call_config_snapshot"]["stage_gating"] = {
        "active_stage": "STEP_1",
        "allowed_stages": ["STEP_1", "STEP_2"],
        "stage_map": {"STEP_1": ["research_idea"]},
    }
    valid_payload["call_config_digest"] = _canonical_digest_for_snapshot(
        valid_payload["call_config_snapshot"]
    )

    validated = validate_review_request_payload(valid_payload)
    assert validated.call_config_snapshot.stage_gating is not None
    assert validated.call_config_snapshot.stage_gating.active_stage == "STEP_1"

    invalid_payload = _build_payload()
    invalid_payload["call_config_snapshot"]["stage_gating"] = {
        "active_stage": "STEP_1",
        "allowed_stages": ["STEP_1"],
        "unexpected_field": "bad",
    }
    invalid_payload["call_config_digest"] = _canonical_digest_for_snapshot(_build_snapshot())

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(invalid_payload)

    _assert_malformed_request_with_field_error(
        err_info.value,
        path="/call_config_snapshot/stage_gating/unexpected_field",
        kind="unknown_field",
        message="Unknown field is not allowed.",
    )


def test_wf0050_contract_hierarchy_surface_strict() -> None:
    valid_payload = _build_payload()
    valid_payload["call_config_snapshot"]["hierarchy"] = {
        "nodes": [{"id": "research_idea", "parent_id": None}],
        "root_ids": ["research_idea"],
    }
    valid_payload["call_config_digest"] = _canonical_digest_for_snapshot(
        valid_payload["call_config_snapshot"]
    )

    validated = validate_review_request_payload(valid_payload)
    assert validated.call_config_snapshot.hierarchy is not None
    assert validated.call_config_snapshot.hierarchy.root_ids == ["research_idea"]

    invalid_payload = _build_payload()
    invalid_payload["call_config_snapshot"]["hierarchy"] = {
        "nodes": [{"id": "research_idea", "parent_id": None, "unexpected_nested": "bad"}],
        "root_ids": ["research_idea"],
    }
    invalid_payload["call_config_digest"] = _canonical_digest_for_snapshot(_build_snapshot())

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(invalid_payload)

    _assert_malformed_request_with_field_error(
        err_info.value,
        path="/call_config_snapshot/hierarchy/nodes/0/unexpected_nested",
        kind="unknown_field",
        message="Unknown field is not allowed.",
    )


def test_wf0050_contract_nesting_surface_strict() -> None:
    valid_payload = _build_payload()
    valid_payload["call_config_snapshot"]["nesting"] = {
        "mode": "tree",
        "max_depth": 3,
        "allow_cross_refs": False,
    }
    valid_payload["call_config_digest"] = _canonical_digest_for_snapshot(
        valid_payload["call_config_snapshot"]
    )

    validated = validate_review_request_payload(valid_payload)
    assert validated.call_config_snapshot.nesting is not None
    assert validated.call_config_snapshot.nesting.max_depth == 3

    invalid_payload = _build_payload()
    invalid_payload["call_config_snapshot"]["nesting"] = {
        "mode": "tree",
        "max_depth": 3,
        "allow_cross_refs": False,
        "unexpected_field": "bad",
    }
    invalid_payload["call_config_digest"] = _canonical_digest_for_snapshot(_build_snapshot())

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(invalid_payload)

    _assert_malformed_request_with_field_error(
        err_info.value,
        path="/call_config_snapshot/nesting/unexpected_field",
        kind="unknown_field",
        message="Unknown field is not allowed.",
    )


def test_wf0049_contract_nested_field_error_sort() -> None:
    payload = _build_payload()
    del payload["request_id"]
    payload["unknown_top_level"] = "bad"
    payload["proposal_nodes"] = {"research_idea": 123}
    payload["call_config_snapshot"]["evaluation_criteria"] = [
        {
            "name": "Criterion 1",
            "stage": "STEP_1",
            "weight_percent": "heavy",
            "evaluation_elements": [
                {
                    "id": "elem-1",
                    "name": "Element 1",
                    "description": "desc",
                    "unknown_nested": "bad",
                }
            ],
            "unexpected_field": "bad",
        }
    ]

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    errors = err_info.value.details["field_errors"]
    _assert_field_errors_are_sorted(errors)


def test_wf0049_contract_kind_enum_frozen() -> None:
    payload = _build_payload()
    payload["call_config_snapshot"]["evaluation_criteria"] = [
        {
            "name": "Criterion 1",
            "stage": "STEP_1",
            "weight_percent": "heavy",
            "evaluation_elements": [],
            "unexpected_field": "bad",
        }
    ]
    digest = hashlib.sha256(
        canonicalize_for_digest(payload["call_config_snapshot"]).encode("utf-8")
    ).hexdigest()
    payload["call_config_digest"] = f"sha256:{digest}"

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    errors = err_info.value.details["field_errors"]
    kinds = {entry["kind"] for entry in errors}
    assert kinds <= {"unknown_field", "missing_field", "type_error", "value_error"}
    assert _find_field_error_by_path(
        errors,
        path="/call_config_snapshot/evaluation_criteria/0/weight_percent",
    )["kind"] == "type_error"


def test_wf0049_contract_message_template_stable() -> None:
    payload = _build_payload()
    del payload["request_id"]
    payload["call_config_snapshot"]["schema_version"] = "v2"
    payload["call_config_snapshot"]["evaluation_criteria"] = [
        {
            "name": "Criterion 1",
            "stage": "STEP_1",
            "weight_percent": "heavy",
            "evaluation_elements": [],
            "unexpected_field": "bad",
        }
    ]

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    errors = err_info.value.details["field_errors"]
    assert _find_field_error_by_path(errors, path="/request_id")["message"] == "Field is required."
    assert (
        _find_field_error_by_path(errors, path="/call_config_snapshot/schema_version")["message"]
        == "Invalid field value."
    )
    assert (
        _find_field_error_by_path(
            errors,
            path="/call_config_snapshot/evaluation_criteria/0/weight_percent",
        )["message"]
        == "Invalid field type."
    )
    assert (
        _find_field_error_by_path(
            errors,
            path="/call_config_snapshot/evaluation_criteria/0/unexpected_field",
        )["message"]
        == "Unknown field is not allowed."
    )


def test_wf0049_contract_digest_omitted_default_equivalence() -> None:
    payload = _build_payload()
    payload["call_config_snapshot"]["evaluation_criteria"] = [
        {
            "id": "crit-1",
            "name": "Criterion 1",
            "stage": "STEP_1",
            "weight_percent": 50,
            "evaluation_elements": [
                {
                    "id": "elem-1",
                    "name": "Element 1",
                    "description": "desc",
                }
            ],
        }
    ]
    canonical_projection = ActivatedCallConfigSnapshotV1.model_validate(
        payload["call_config_snapshot"]
    ).to_canonical_payload()
    digest = hashlib.sha256(
        canonicalize_for_digest(canonical_projection).encode("utf-8")
    ).hexdigest()
    payload["call_config_digest"] = f"sha256:{digest}"

    explicit_default_payload = deepcopy(payload)
    explicit_default_payload["call_config_snapshot"]["evaluation_criteria"][0]["evaluation_elements"][0][
        "stage"
    ] = "BOTH"

    validated = validate_review_request_payload(explicit_default_payload)
    assert validated.call_config_snapshot.evaluation_criteria is not None
    assert validated.call_config_snapshot.evaluation_criteria[0].evaluation_elements[0].stage == "BOTH"


def test_wf0049_contract_digest_projection_from_validated_schema() -> None:
    payload = _build_payload()
    payload["call_config_snapshot"]["evaluation_criteria"] = [
        {
            "id": "crit-1",
            "name": "Criterion 1",
            "stage": "STEP_1",
            "weight_percent": "50",
            "evaluation_elements": [],
        }
    ]

    validated_snapshot = ActivatedCallConfigSnapshotV1.model_validate(payload["call_config_snapshot"])
    digest = hashlib.sha256(
        canonicalize_for_digest(validated_snapshot.to_canonical_payload()).encode("utf-8")
    ).hexdigest()
    payload["call_config_digest"] = f"sha256:{digest}"

    validated = validate_review_request_payload(payload)
    assert validated.call_config_snapshot.evaluation_criteria is not None
    assert validated.call_config_snapshot.evaluation_criteria[0].weight_percent == 50


def test_wf0049_contract_compat_happy_valid_payload() -> None:
    case = _load_wf0049_compat_matrix()["happy_valid_payload"]
    snapshot = case["snapshot"]
    assert isinstance(snapshot, dict)
    payload = _build_payload_for_snapshot(
        snapshot,
        digest=_canonical_digest_for_snapshot(snapshot),
    )

    validated = validate_review_request_payload(payload)
    assert validated.call_config_snapshot.schema_version == "v1"


def test_wf0049_contract_compat_legacy_extra_nested_key() -> None:
    case = _load_wf0049_compat_matrix()["legacy_extra_nested_key"]
    snapshot = case["snapshot"]
    assert isinstance(snapshot, dict)
    payload = _build_payload_for_snapshot(
        snapshot,
        digest=_canonical_digest_for_snapshot(_build_snapshot()),
    )

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    _assert_malformed_request_with_field_error(
        err_info.value,
        path="/call_config_snapshot/evaluation_criteria/0/unexpected_field",
        kind="unknown_field",
        message="Unknown field is not allowed.",
    )


def test_wf0049_contract_compat_nested_type_mismatch() -> None:
    case = _load_wf0049_compat_matrix()["nested_type_mismatch"]
    snapshot = case["snapshot"]
    assert isinstance(snapshot, dict)
    payload = _build_payload_for_snapshot(
        snapshot,
        digest=_canonical_digest_for_snapshot(_build_snapshot()),
    )

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    _assert_malformed_request_with_field_error(
        err_info.value,
        path="/call_config_snapshot/prompt_knobs/max_tokens",
        kind="type_error",
        message="Invalid field type.",
    )


def test_wf0049_contract_compat_omitted_optional_default_equivalence() -> None:
    case = _load_wf0049_compat_matrix()["omitted_optional_default_equivalence"]
    baseline_snapshot = case["baseline_snapshot"]
    explicit_default_snapshot = case["explicit_default_snapshot"]
    assert isinstance(baseline_snapshot, dict)
    assert isinstance(explicit_default_snapshot, dict)

    payload = _build_payload_for_snapshot(
        explicit_default_snapshot,
        digest=_canonical_digest_for_snapshot(baseline_snapshot),
    )

    validated = validate_review_request_payload(payload)
    assert validated.call_config_snapshot.evaluation_criteria is not None


def test_wf0049_contract_scope_request_boundary_only() -> None:
    payload = _build_payload()
    payload["call_config_snapshot"]["funding_agency_id"] = "agency-123"
    payload["call_config_digest"] = "sha256:deadbeef"

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    _assert_malformed_request_with_field_error(
        err_info.value,
        path="/call_config_snapshot/funding_agency_id",
        kind="unknown_field",
        message="Unknown field is not allowed.",
    )
    assert err_info.value.code == "MALFORMED_REVIEW_REQUEST"


def test_wf0052_contract_compat_happy_valid_payload_real_snapshot() -> None:
    case = _load_wf0052_compat_matrix()["happy_valid_payload_real_snapshot"]
    _assert_case_grounded_to_source_call(case)
    snapshot = case["snapshot"]
    assert isinstance(snapshot, dict)
    payload = _build_payload_for_snapshot(
        snapshot,
        digest=_canonical_digest_for_snapshot(snapshot),
    )

    validated = validate_review_request_payload(payload)
    assert validated.call_config_snapshot.schema_version == "v1"
    assert validated.call_config_snapshot.evaluation_criteria is not None


def test_wf0052_contract_compat_legacy_extra_nested_key_real_snapshot() -> None:
    case = _load_wf0052_compat_matrix()["legacy_extra_nested_key_real_snapshot"]
    _assert_case_grounded_to_source_call(case)
    snapshot = case["snapshot"]
    expected_error = case["expected_error"]
    assert isinstance(snapshot, dict)
    assert isinstance(expected_error, dict)
    payload = _build_payload_for_snapshot(
        snapshot,
        digest=_canonical_digest_for_snapshot(_build_snapshot()),
    )

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    _assert_malformed_request_with_field_error(
        err_info.value,
        path=str(expected_error["path"]),
        kind=str(expected_error["kind"]),
        message=str(expected_error["message"]),
    )


def test_wf0052_contract_compat_nested_type_mismatch_real_snapshot() -> None:
    case = _load_wf0052_compat_matrix()["nested_type_mismatch_real_snapshot"]
    _assert_case_grounded_to_source_call(case)
    snapshot = case["snapshot"]
    expected_error = case["expected_error"]
    assert isinstance(snapshot, dict)
    assert isinstance(expected_error, dict)
    payload = _build_payload_for_snapshot(
        snapshot,
        digest=_canonical_digest_for_snapshot(_build_snapshot()),
    )

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    _assert_malformed_request_with_field_error(
        err_info.value,
        path=str(expected_error["path"]),
        kind=str(expected_error["kind"]),
        message=str(expected_error["message"]),
    )


def test_wf0052_contract_compat_omitted_optional_default_equivalence_real_snapshot() -> None:
    case = _load_wf0052_compat_matrix()["omitted_optional_default_equivalence_real_snapshot"]
    _assert_case_grounded_to_source_call(case)
    baseline_snapshot = case["baseline_snapshot"]
    explicit_default_snapshot = case["explicit_default_snapshot"]
    assert isinstance(baseline_snapshot, dict)
    assert isinstance(explicit_default_snapshot, dict)
    payload = _build_payload_for_snapshot(
        explicit_default_snapshot,
        digest=_canonical_digest_for_snapshot(baseline_snapshot),
    )

    validated = validate_review_request_payload(payload)
    assert validated.call_config_snapshot.evaluation_criteria is not None


def test_wf0052_contract_digest_validated_projection_equivalence_real_snapshot() -> None:
    case = _load_wf0052_compat_matrix()["omitted_optional_default_equivalence_real_snapshot"]
    _assert_case_grounded_to_source_call(case)
    baseline_snapshot = case["baseline_snapshot"]
    explicit_default_snapshot = case["explicit_default_snapshot"]
    assert isinstance(baseline_snapshot, dict)
    assert isinstance(explicit_default_snapshot, dict)

    baseline_digest = _canonical_digest_for_snapshot(baseline_snapshot)
    explicit_digest = _canonical_digest_for_snapshot(explicit_default_snapshot)

    assert baseline_digest == explicit_digest


def test_wf0052_contract_digest_raw_snapshot_mismatch_real_snapshot() -> None:
    case = _load_wf0052_compat_matrix()["omitted_optional_default_equivalence_real_snapshot"]
    _assert_case_grounded_to_source_call(case)
    explicit_default_snapshot = case["explicit_default_snapshot"]
    assert isinstance(explicit_default_snapshot, dict)

    raw_digest = "sha256:" + hashlib.sha256(
        canonicalize_for_digest(explicit_default_snapshot).encode("utf-8")
    ).hexdigest()
    payload = _build_payload_for_snapshot(
        explicit_default_snapshot,
        digest=raw_digest,
    )

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    assert err_info.value.code == "CALL_CONFIG_DIGEST_MISMATCH"
