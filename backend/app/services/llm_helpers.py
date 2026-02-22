"""Shared LLM helper functions for review services."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor

from pydantic import ValidationError

from app.schemas.llm_response import LLMReviewResponse
from app.services.llm_client import LLMClientProtocol


def generate_with_timeout(
    llm_client: LLMClientProtocol,
    prompt: str,
    timeout_seconds: float,
) -> str:
    """Run blocking LLM call with a timeout."""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(llm_client.generate, prompt)
        return future.result(timeout=timeout_seconds)


def parse_llm_response(raw_response: str) -> LLMReviewResponse:
    """Parse raw LLM JSON response into structured schema."""
    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM: {e}") from e

    try:
        return LLMReviewResponse.model_validate(data)
    except ValidationError as e:
        raise ValueError(f"LLM response schema validation failed: {e}") from e
