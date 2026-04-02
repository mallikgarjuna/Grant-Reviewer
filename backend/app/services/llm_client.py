"""
OpenAI LLM Client for Grant Reviewer.

Simple client that calls OpenAI API and returns raw text response.
For MVP: OpenAI only, Azure support deferred.
"""

import json
import logging
import os
import re
import time
from typing import ClassVar, Protocol

from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """Raised when LLM call fails."""

    pass


class LLMClientProtocol(Protocol):
    """Protocol for interchangeable LLM clients."""

    def generate(self, prompt: str) -> str:
        """Generate raw JSON response text for a prompt."""
        ...

    def get_model_name(self) -> str:
        """Return model identifier."""
        ...


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


class StubLLMClient:
    """Deterministic local client for non-network verification."""

    MODEL_NAME: ClassVar[str] = "stub-llm"
    EXPECTATION_ID_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"ID:\s*([0-9a-fA-F-]{36})"
    )
    SYNTHESIS_FIELD_PATTERNS: ClassVar[dict[str, re.Pattern[str]]] = {
        "expectation_id": re.compile(r"^expectation_id:\s*(.+)$", re.MULTILINE),
        "node_logical_id": re.compile(r"^node_logical_id:\s*(.+)$", re.MULTILINE),
        "element_logical_id": re.compile(
            r"^evaluation_element_logical_id:\s*(.+)$", re.MULTILINE
        ),
        "submitted_excerpt": re.compile(r"^submitted_excerpt:\s*(.+)$", re.MULTILINE),
    }

    def generate(self, prompt: str) -> str:
        """Return valid deterministic JSON without external API calls."""
        synthesis_payload = self._build_synthesis_payload(prompt)
        if synthesis_payload is not None:
            return json.dumps(synthesis_payload)

        expectation_ids = self.EXPECTATION_ID_PATTERN.findall(prompt)
        if not expectation_ids:
            raise LLMClientError("Stub mode could not detect expectation IDs in prompt")

        feedbacks = [
            {
                "node_expectation_id": expectation_id,
                "feedback": (
                    "Stub feedback: strengthen this section with concrete, "
                    "criterion-linked evidence."
                ),
            }
            for expectation_id in expectation_ids
        ]
        return json.dumps({"feedbacks": feedbacks})

    def get_model_name(self) -> str:
        """Return stub model name."""
        return self.MODEL_NAME

    @classmethod
    def _build_synthesis_payload(cls, prompt: str) -> dict[str, object] | None:
        expectation_id = cls._extract_synthesis_field(prompt, "expectation_id")
        node_logical_id = cls._extract_synthesis_field(prompt, "node_logical_id")
        element_logical_id = cls._extract_synthesis_field(prompt, "element_logical_id")
        submitted_excerpt = cls._extract_synthesis_field(prompt, "submitted_excerpt")
        if not all(
            [expectation_id, node_logical_id, element_logical_id, submitted_excerpt]
        ):
            return None

        evidence_quote = submitted_excerpt[:80].strip()
        if not evidence_quote:
            evidence_quote = submitted_excerpt.strip()

        return {
            "expectation_id": expectation_id,
            "node_logical_id": node_logical_id,
            "evaluation_element_logical_id": element_logical_id,
            "synthesized_feedback": (
                "Stub companion guidance: expand the cited evidence into a sharper, "
                "evaluation-criteria-grounded revision."
            ),
            "evidence_quotes": [evidence_quote],
        }

    @classmethod
    def _extract_synthesis_field(cls, prompt: str, field_name: str) -> str | None:
        match = cls.SYNTHESIS_FIELD_PATTERNS[field_name].search(prompt)
        if match is None:
            return None
        value = match.group(1).strip()
        return value or None


def build_llm_client() -> LLMClientProtocol:
    """Build LLM client from environment configuration."""
    llm_mode = os.getenv("LLM_MODE", "openai").strip().lower()
    if llm_mode == "stub":
        logger.info("Using StubLLMClient (LLM_MODE=stub)")
        return StubLLMClient()
    return OpenAIClient()
