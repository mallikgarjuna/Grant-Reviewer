"""
Pydantic schemas for LLM response validation.

These schemas validate the structured JSON output from the LLM.
Used by ReviewerService to parse and validate feedback before persisting.
"""

from pydantic import BaseModel, field_validator


class ExpectationFeedback(BaseModel):
    """Single feedback item for one NodeExpectation."""

    node_expectation_id: str  # UUID as string
    feedback: str  # Non-empty feedback text

    @field_validator("feedback")
    @classmethod
    def feedback_not_empty(cls, v: str) -> str:
        """Ensure feedback is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("Feedback must not be empty")
        return v.strip()


class LLMReviewResponse(BaseModel):
    """Complete LLM response containing feedback for all expectations."""

    feedbacks: list[ExpectationFeedback]

    @field_validator("feedbacks")
    @classmethod
    def feedbacks_not_empty(
        cls, v: list[ExpectationFeedback]
    ) -> list[ExpectationFeedback]:
        """Ensure at least one feedback item is present."""
        if not v:
            raise ValueError("Feedbacks list must not be empty")
        return v
