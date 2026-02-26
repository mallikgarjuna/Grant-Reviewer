"""
V2 YAML ingestion schemas for call definitions.

These models validate the richer NWO-style call definition payload used for
offline dry-run validation in WF-0020.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ExpectationStrength = Literal["MANDATORY", "IMPORTANT", "OPTIONAL"]
EvaluationIntent = Literal["COMPLIANCE", "QUALITY", "RISK", "STRATEGIC_FIT"]
RuleSeverity = Literal["ERROR", "WARNING"]


class StrictBaseModel(BaseModel):
    """Base model that rejects unknown fields."""

    model_config = ConfigDict(extra="forbid")


class FundingAgencyDefinitionV2(StrictBaseModel):
    """Funding agency metadata for V2 call definitions."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    country: str = Field(min_length=1)


class DeadlineDefinitionV2(StrictBaseModel):
    """Single deadline entry with timezone-aware local datetime."""

    datetime_local: str = Field(min_length=1)
    timezone: str = Field(min_length=1)


class DomainNoteDefinitionV2(StrictBaseModel):
    """Domain-specific note for the funding call."""

    domain_id: str = Field(min_length=1)
    note: str = Field(min_length=1)


class FundingCallDefinitionV2(StrictBaseModel):
    """Funding call metadata for V2 call definitions."""

    id: str = Field(min_length=1)
    code: str = Field(min_length=1)
    title: str = Field(min_length=1)
    year: int
    stage: str = Field(min_length=1)
    language: str = Field(min_length=1)
    deadlines: dict[str, DeadlineDefinitionV2] = Field(default_factory=dict)
    domain_notes: list[DomainNoteDefinitionV2] = Field(default_factory=list)


class EvaluationElementDefinitionV2(StrictBaseModel):
    """Atomic reviewable concern for an evaluation criterion."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    source_hint: str | None = None
    stage: Literal["STEP_1", "STEP_2", "BOTH"] | None = "BOTH"


class EvaluationCriterionDefinitionV2(StrictBaseModel):
    """Top-level evaluation criterion with child evaluation elements."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    stage: str = Field(min_length=1)
    weight_percent: int
    evaluation_elements: list[EvaluationElementDefinitionV2] = Field(
        default_factory=list
    )


class TotalWordLimitDefinitionV2(StrictBaseModel):
    """Shared total-word-limit shape used by multiple nodes."""

    min_words: int | None = None
    max_words: int | None = None
    includes: list[str] = Field(default_factory=list)
    excludes: list[str] = Field(default_factory=list)


class WordLimitByDomainDefinitionV2(StrictBaseModel):
    """Domain-specific word-limit configuration."""

    default_max_words: int
    science_enw_max_words: int | None = None


class ContentConstraintsDefinitionV2(StrictBaseModel):
    """Node-level authoring constraints."""

    total_word_limit: TotalWordLimitDefinitionV2 | None = None
    max_items: int | None = None
    max_pages: int | None = None
    word_limit_by_domain: WordLimitByDomainDefinitionV2 | None = None
    note: str | None = None


class ComplianceRuleDefinitionV2(StrictBaseModel):
    """Deterministic compliance rule metadata."""

    id: str = Field(min_length=1)
    severity: RuleSeverity
    rule_type: str = Field(min_length=1)
    description: str = Field(min_length=1)


class NodeExpectationDefinitionV2(StrictBaseModel):
    """Link from proposal node to evaluation element."""

    evaluation_element_id: str = Field(min_length=1)
    expectation_strength: ExpectationStrength
    evaluation_intent: EvaluationIntent
    guidance_note: str | None = None


class ProposalNodeDefinitionV2(StrictBaseModel):
    """Narrative node in the proposal structure."""

    id: str = Field(min_length=1)
    parent_logical_id: str | None = None
    label: str = Field(min_length=1)
    node_type: str = Field(min_length=1)
    source_section: str | None = None
    content_constraints: ContentConstraintsDefinitionV2 | None = None
    guidance_text: str | None = None
    compliance_rules: list[ComplianceRuleDefinitionV2] = Field(default_factory=list)
    node_expectations: list[NodeExpectationDefinitionV2] = Field(default_factory=list)


class RuntimeNoteDefinitionV2(StrictBaseModel):
    """Runtime behavior note stored alongside the call definition."""

    id: str = Field(min_length=1)
    description: str = Field(min_length=1)


class CallDefinitionV2(StrictBaseModel):
    """Root model for V2 call definition YAML."""

    funding_agency: FundingAgencyDefinitionV2
    funding_call: FundingCallDefinitionV2
    evaluation_criteria: list[EvaluationCriterionDefinitionV2] = Field(
        default_factory=list
    )
    proposal_nodes: list[ProposalNodeDefinitionV2] = Field(default_factory=list)
    runtime_notes: list[RuntimeNoteDefinitionV2] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_references(self) -> CallDefinitionV2:
        """Ensure every node expectation points to a defined evaluation element."""
        seen_node_ids: set[str] = set()
        duplicate_node_ids: list[str] = []
        for node in self.proposal_nodes:
            if node.id in seen_node_ids:
                duplicate_node_ids.append(node.id)
                continue
            seen_node_ids.add(node.id)

        if duplicate_node_ids:
            duplicate_label = ", ".join(sorted(set(duplicate_node_ids)))
            raise ValueError(f"Duplicate proposal node id: {duplicate_label}")

        valid_element_ids = {
            element.id
            for criterion in self.evaluation_criteria
            for element in criterion.evaluation_elements
        }
        errors: list[str] = []

        for node in self.proposal_nodes:
            for expectation in node.node_expectations:
                if expectation.evaluation_element_id not in valid_element_ids:
                    errors.append(
                        f"Node '{node.id}': Unknown evaluation_element_id "
                        f"'{expectation.evaluation_element_id}'"
                    )

        if errors:
            raise ValueError(
                "Reference validation failed:\n  - " + "\n  - ".join(errors)
            )

        return self
