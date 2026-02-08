"""
OpenAI LLM Client for Grant Reviewer.

Simple client that calls OpenAI API and returns raw text response.
For MVP: OpenAI only, Azure support deferred.
"""

import os
from typing import ClassVar

from openai import OpenAI, OpenAIError


class LLMClientError(Exception):
    """Raised when LLM call fails."""

    pass


class OpenAIClient:
    """OpenAI API client returning raw text responses."""

    DEFAULT_MODEL: ClassVar[str] = "gpt-4o-mini"
    TIMEOUT_SECONDS: ClassVar[int] = 30

    def __init__(self) -> None:
        """Initialize client with API key from environment."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMClientError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=api_key, timeout=self.TIMEOUT_SECONDS)
        self.model = os.getenv("LLM_MODEL", self.DEFAULT_MODEL)

    def generate(self, prompt: str) -> str:
        """
        Send prompt to OpenAI and return raw text response.

        Args:
            prompt: The complete prompt to send

        Returns:
            Raw text content from the LLM response

        Raises:
            LLMClientError: If API call fails or times out
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if content is None:
                raise LLMClientError("LLM returned empty response")

            return content

        except OpenAIError as e:
            raise LLMClientError(f"OpenAI API error: {e}") from e

    def get_model_name(self) -> str:
        """Return the model identifier being used."""
        return self.model
