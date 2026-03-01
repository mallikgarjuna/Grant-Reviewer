import pytest
from uuid import uuid4
from app.models.domain import NodeType, ProposalNode
from app.schemas.compliance import ComplianceCheckRequest, DraftNode
from app.services.call_definition_service import HydratedNode
from app.services.compliance_engine import evaluate_compliance

pytestmark = pytest.mark.no_db


def _hydrated_node(logical_id: str, config: dict) -> HydratedNode:
    """Build a hydrated node fixture with deterministic logical id."""
    return HydratedNode(
        node=ProposalNode(
            funding_call_id=uuid4(),
            logical_id=logical_id,
            node_type=NodeType.SECTION,
            title=logical_id,
            order_index=1,
        ),
        config=config,
    )


def _request(*draft_nodes: DraftNode, domain: str | None = None) -> ComplianceCheckRequest:
    """Build compliance request payload fixtures."""
    return ComplianceCheckRequest(
        call_id=uuid4(),
        domain=domain,
        draft_nodes=list(draft_nodes),
    )


def test_happy_path_returns_compliant() -> None:
    """All nodes satisfying limits should pass."""
    nodes = [
        _hydrated_node(
            "academic_profile",
            {
                "content_constraints": {
                    "total_word_limit": {"min_words": 2, "max_words": 5},
                }
            },
        )
    ]
    request = _request(
        DraftNode(node_logical_id="academic_profile", text="one two three")
    )

    response = evaluate_compliance(request, nodes)

    assert response.is_compliant is True
    assert response.errors == []
    assert response.warnings == []


def test_word_limit_exceeded_returns_non_blocking_warning() -> None:
    """Node above max limit should return word_limit_max warning."""
    nodes = [
        _hydrated_node(
            "research_idea",
            {
                "content_constraints": {
                    "total_word_limit": {"max_words": 3},
                }
            },
        )
    ]
    request = _request(
        DraftNode(node_logical_id="research_idea", text="one two three four")
    )

    response = evaluate_compliance(request, nodes)

    assert response.is_compliant is True
    assert len(response.errors) == 0
    assert len(response.warnings) == 1
    warning = response.warnings[0]
    assert warning.rule_id == "word_limit_max"
    assert warning.actual == "4"
    assert warning.expected == "3"
    assert warning.is_blocking is False


def test_word_limit_under_minimum_returns_non_blocking_warning() -> None:
    """Node below min limit should return word_limit_min warning."""
    nodes = [
        _hydrated_node(
            "academic_profile",
            {
                "content_constraints": {
                    "total_word_limit": {"min_words": 3, "max_words": 10},
                }
            },
        )
    ]
    request = _request(DraftNode(node_logical_id="academic_profile", text="one two"))

    response = evaluate_compliance(request, nodes)

    assert response.is_compliant is True
    assert len(response.errors) == 0
    assert len(response.warnings) == 1
    warning = response.warnings[0]
    assert warning.rule_id == "word_limit_min"
    assert warning.actual == "2"
    assert warning.expected == "3"
    assert warning.is_blocking is False


def test_domain_specific_override_applies_when_domain_provided() -> None:
    """Domain max override should take precedence over default and total limits."""
    nodes = [
        _hydrated_node(
            "research_idea",
            {
                "content_constraints": {
                    "total_word_limit": {"max_words": 50},
                    "word_limit_by_domain": {
                        "default_max_words": 4,
                        "science_enw_max_words": 6,
                    },
                }
            },
        )
    ]
    request = _request(
        DraftNode(node_logical_id="research_idea", text="one two three four five"),
        domain="science_enw",
    )

    response = evaluate_compliance(request, nodes)

    assert response.is_compliant is True
    assert response.errors == []


def test_word_limit_by_domain_uses_default_when_domain_missing() -> None:
    """Default max words should be used if no domain is supplied (warning if exceeded)."""
    nodes = [
        _hydrated_node(
            "research_idea",
            {
                "content_constraints": {
                    "word_limit_by_domain": {"default_max_words": 3},
                }
            },
        )
    ]
    request = _request(
        DraftNode(node_logical_id="research_idea", text="one two three four")
    )

    response = evaluate_compliance(request, nodes)

    assert response.is_compliant is True
    assert len(response.errors) == 0
    assert len(response.warnings) == 1
    assert response.warnings[0].rule_id == "word_limit_max"
    assert response.warnings[0].expected == "3"


def test_falls_back_to_total_word_limit_when_no_domain_limits_exist() -> None:
    """Total limit should apply if domain-specific config is absent."""
    nodes = [
        _hydrated_node(
            "research_idea",
            {
                "content_constraints": {
                    "total_word_limit": {"max_words": 2},
                }
            },
        )
    ]
    request = _request(
        DraftNode(node_logical_id="research_idea", text="one two three"),
        domain="science_enw",
    )

    response = evaluate_compliance(request, nodes)

    assert response.is_compliant is True
    assert response.warnings[0].rule_id == "word_limit_max"
    assert response.warnings[0].expected == "2"


def test_missing_mandatory_node_returns_blocking_error() -> None:
    """Mandatory nodes omitted from payload should fail."""
    nodes = [
        _hydrated_node(
            "academic_profile",
            {
                "content_constraints": {
                    "total_word_limit": {"min_words": 1, "max_words": 100},
                }
            },
        )
    ]
    request = _request()

    response = evaluate_compliance(request, nodes)

    assert response.is_compliant is False
    assert len(response.errors) == 1
    assert response.errors[0].rule_id == "mandatory_presence"
    assert response.errors[0].node_logical_id == "academic_profile"


def test_whitespace_text_on_mandatory_node_returns_blocking_error() -> None:
    """Whitespace text should be treated as missing."""
    nodes = [
        _hydrated_node(
            "academic_profile",
            {
                "content_constraints": {
                    "total_word_limit": {"min_words": 1},
                }
            },
        )
    ]
    request = _request(DraftNode(node_logical_id="academic_profile", text="   \n"))

    response = evaluate_compliance(request, nodes)

    assert response.is_compliant is False
    assert len(response.errors) == 1
    assert response.errors[0].rule_id == "mandatory_presence"


def test_node_with_no_constraints_passes_silently() -> None:
    """Nodes lacking constraints should not produce errors."""
    nodes = [_hydrated_node("optional_section", {"content_constraints": {}})]
    request = _request(DraftNode(node_logical_id="optional_section", text="hello world"))

    response = evaluate_compliance(request, nodes)

    assert response.is_compliant is True
    assert response.errors == []


def test_non_enforceable_constraints_are_informational_only() -> None:
    """Non-enforceable max_items constraints should surface as warnings only."""
    nodes = [
        _hydrated_node(
            "key_outputs",
            {
                "content_constraints": {
                    "max_items": 10,
                },
                "compliance_rules": [
                    {
                        "id": "comp_key_outputs_max_items",
                        "severity": "WARNING",
                        "rule_type": "hard_limit",
                        "description": "List no more than 10 key output items.",
                    }
                ],
            },
        )
    ]
    request = _request(DraftNode(node_logical_id="key_outputs", text="one two"))

    response = evaluate_compliance(request, nodes)

    assert response.is_compliant is True
    assert response.errors == []
    assert len(response.warnings) == 1
    warning = response.warnings[0]
    assert warning.rule_id == "comp_key_outputs_max_items"
    assert warning.is_blocking is False


def test_unrecognized_domain_alias_uses_default_fallback() -> None:
    """Engine should not validate domain aliases; route layer owns that validation."""
    nodes = [
        _hydrated_node(
            "research_idea",
            {
                "content_constraints": {
                    "word_limit_by_domain": {
                        "default_max_words": 100,
                        "science_enw_max_words": 500,
                    }
                }
            },
        )
    ]
    request = _request(
        DraftNode(node_logical_id="research_idea", text="short text"),
        domain="ENW",
    )

    response = evaluate_compliance(request, nodes)

    assert response.is_compliant is True
    assert response.errors == []
