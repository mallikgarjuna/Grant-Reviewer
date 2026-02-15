"""
YAML Ingestion Schemas for Admin Call Definition.

Pydantic models for validating YAML call definition files.
These map 1:1 to the database models in models/domain.py.

WHY SEPARATE SCHEMAS (not reusing SQLModel from domain.py)?
-----------------------------------------------------------
1. **Different ID types**: YAML uses human-readable string IDs (e.g., "elem_novelty")
   that get mapped to UUIDs during ingestion. SQLModel expects actual UUIDs.

2. **No auto-generated fields**: YAML doesn't include `id`, `created_at`, `updated_at`,
   or foreign key UUIDs - these are database concerns, not user input.

3. **Nested structure**: YAML uses inline nesting (children inside parent), while
   SQLModel uses flat tables with foreign key references.

4. **Custom validators**: Pydantic allows `check_references` and `check_recursion`
   validators that wouldn't make sense on database models.

Key validation features:
- check_references: Ensures all evaluation_element_id references exist in the rubric
- check_recursion: Prevents cyclic relationships in proposal_nodes
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

# ============================================================================
# Enum Aliases (Match domain.py)
# ============================================================================
NodeType = Literal["SECTION", "SUBSECTION"]
ExpectationStrength = Literal["MANDATORY", "IMPORTANT", "OPTIONAL"]
EvaluationIntent = Literal["COMPLIANCE", "QUALITY", "RISK", "STRATEGIC_FIT"]


# ============================================================================
# Component Definitions (Bottom-up: leaf models first)
# ============================================================================
class FundingAgencyDefinition(BaseModel):
    """Funding agency metadata for YAML ingestion."""

    name: str = Field(description="Full legal name of the funding agency")
    short_name: str = Field(description="Commonly used acronym (business key)")
    description: str | None = Field(
        default=None, description="General mission statement"
    )


class FundingCallDefinition(BaseModel):
    """Funding call metadata for YAML ingestion."""

    name: str = Field(description="Common name of the grant call")
    code: str = Field(description="Official call identifier code (business key)")
    year: int = Field(description="The calendar year of the call")
    aim_objectives: str | None = Field(
        default=None, description="The intended impact and goals of the call"
    )
    scope: str | None = Field(
        default=None, description="The thematic areas or boundaries of the call"
    )
    general_guidelines: str | None = Field(
        default=None, description="General instructions for applicants"
    )


class EvaluationElementDefinition(BaseModel):
    """Atomic reviewable concern within a criterion."""

    id: str = Field(
        description="Logical ID for cross-referencing (e.g., 'elem_novelty')"
    )
    name: str = Field(description="Name of the specific reviewable concern")
    description: str | None = Field(
        default=None, description="What the element explicitly evaluates"
    )


class EvaluationCriterionDefinition(BaseModel):
    """Top-level assessment dimension with its child elements."""

    id: str = Field(
        description="Logical ID for cross-referencing (e.g., 'crit_excellence')"
    )
    name: str = Field(description="Name of the assessment dimension")
    description: str | None = Field(
        default=None, description="Brief explanation of the criterion"
    )
    evaluation_elements: list[EvaluationElementDefinition] = Field(
        default_factory=list,
        description="List of atomic reviewable elements under this criterion",
    )


class NodeExpectationDefinition(BaseModel):
    """Links a proposal node to a rubric element with strictness metadata."""

    evaluation_element_id: str = Field(
        description="Reference to EvaluationElementDefinition.id"
    )
    expectation_strength: ExpectationStrength = Field(
        description="Priority/Strictness: MANDATORY | IMPORTANT | OPTIONAL"
    )
    evaluation_intent: EvaluationIntent = Field(
        description="Reviewer check type: COMPLIANCE | QUALITY | RISK | STRATEGIC_FIT"
    )
    guidance_note: str | None = Field(
        default=None, description="Specific reviewer orientation"
    )


class ProposalNodeDefinition(BaseModel):
    """Structural section or subsection with optional nested children."""

    title: str = Field(description="Display title of the section")
    node_type: NodeType = Field(description="Type: SECTION or SUBSECTION")
    guidance_text: str | None = Field(
        default=None, description="Guidance provided to the applicant"
    )
    children: list[ProposalNodeDefinition] = Field(
        default_factory=list, description="Nested child nodes"
    )
    node_expectations: list[NodeExpectationDefinition] = Field(
        default_factory=list,
        description="Rubric expectations for this node",
    )


# ============================================================================
# Root Definition (Top-level Call Definition)
# ============================================================================
class CallDefinition(BaseModel):
    """
    Complete call definition for YAML ingestion.

    This is the root model that aggregates agency, call, rubric, and proposal structure.
    Validators ensure referential integrity and prevent recursive cycles.
    """

    funding_agency: FundingAgencyDefinition = Field(description="Agency metadata")
    funding_call: FundingCallDefinition = Field(description="Call metadata")
    evaluation_criteria: list[EvaluationCriterionDefinition] = Field(
        default_factory=list,
        description="Rubric: list of criteria with their elements",
    )
    proposal_nodes: list[ProposalNodeDefinition] = Field(
        default_factory=list,
        description="Proposal structure: hierarchical sections",
    )

    # ========================================================================
    # Validators
    # ========================================================================
    @model_validator(mode="after")
    def check_references(self) -> CallDefinition:
        """
        Validate that all evaluation_element_id references in node_expectations
        exist in the defined evaluation_criteria.

        Raises:
            ValueError: If an unknown element_id is referenced.
        """
        # Build set of all valid element IDs from the rubric
        valid_element_ids: set[str] = set()
        for criterion in self.evaluation_criteria:
            for element in criterion.evaluation_elements:
                valid_element_ids.add(element.id)

        # Collect all referenced element IDs from proposal nodes
        referenced_ids: set[str] = set()
        errors: list[str] = []

        def collect_references(
            nodes: list[ProposalNodeDefinition], path: str = ""
        ) -> None:
            for _i, node in enumerate(nodes):
                node_path = f"{path}/{node.title}" if path else node.title
                for exp in node.node_expectations:
                    referenced_ids.add(exp.evaluation_element_id)
                    if exp.evaluation_element_id not in valid_element_ids:
                        errors.append(
                            f"Node '{node_path}': Unknown evaluation_element_id "
                            f"'{exp.evaluation_element_id}'"
                        )
                # Recurse into children
                collect_references(node.children, node_path)

        collect_references(self.proposal_nodes)

        if errors:
            raise ValueError(
                "Reference validation failed:\n  - " + "\n  - ".join(errors)
            )

        # Optional: Warn about unused elements (not an error, just logged)
        unused = valid_element_ids - referenced_ids
        if unused:
            # Log warning but don't fail - elements might be used in future nodes
            import logging

            logging.getLogger(__name__).warning(
                f"Unused evaluation elements (defined but not referenced): {unused}"
            )

        return self

    @model_validator(mode="after")
    def check_recursion(self) -> CallDefinition:
        """
        Validate that proposal_nodes do not exceed maximum depth
        and do not contain title-based cycles.

        Raises:
            ValueError: If max depth exceeded or cycle detected.
        """
        MAX_DEPTH = 5
        errors: list[str] = []

        def check_depth(
            nodes: list[ProposalNodeDefinition],
            depth: int,
            ancestors: set[str],
            path: str = "",
        ) -> None:
            if depth > MAX_DEPTH:
                errors.append(f"Max depth ({MAX_DEPTH}) exceeded at path: {path}")
                return

            for node in nodes:
                node_path = f"{path}/{node.title}" if path else node.title

                # Cycle detection via title (simple heuristic)
                if node.title in ancestors:
                    errors.append(
                        f"Potential cycle detected: '{node.title}' appears in "
                        f"ancestor path at '{node_path}'"
                    )
                    continue

                # Continue recursion with updated ancestors
                new_ancestors = ancestors | {node.title}
                check_depth(node.children, depth + 1, new_ancestors, node_path)

        check_depth(self.proposal_nodes, depth=1, ancestors=set())

        if errors:
            raise ValueError(
                "Recursion validation failed:\n  - " + "\n  - ".join(errors)
            )

        return self
