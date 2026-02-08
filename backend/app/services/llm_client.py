"""
OpenAI LLM Client for Grant Reviewer.

Simple client that calls OpenAI API and returns raw text response.
For MVP: OpenAI only, Azure support deferred.
"""

import logging
import os
import time
from typing import ClassVar

from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)


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
        logger.info(f"OpenAI client initialized with model: {self.model}")

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
        prompt_preview = prompt[:100] + "..." if len(prompt) > 100 else prompt
        logger.info(f"[LLM] Calling OpenAI ({self.model})...")
        logger.debug(f"[LLM] Prompt preview: {prompt_preview}")

        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )

            elapsed = time.time() - start_time
            content = response.choices[0].message.content

            if content is None:
                logger.error("[LLM] Received empty response from OpenAI")
                raise LLMClientError("LLM returned empty response")

            # Log token usage if available
            usage = response.usage
            if usage:
                logger.info(
                    f"[LLM] Response received in {elapsed:.2f}s "
                    f"(prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens}, "
                    f"total: {usage.total_tokens} tokens)"
                )
            else:
                logger.info(f"[LLM] Response received in {elapsed:.2f}s")

            return content

        except OpenAIError as e:
            elapsed = time.time() - start_time
            logger.error(f"[LLM] OpenAI API error after {elapsed:.2f}s: {e}")
            raise LLMClientError(f"OpenAI API error: {e}") from e

    def get_model_name(self) -> str:
        """Return the model identifier being used."""
        return self.model
