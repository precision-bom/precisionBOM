"""Utilities for parsing potentially malformed JSON from LLM responses."""

import json
import logging
import re
from typing import TypeVar, Type

from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def fuzzy_parse_json(raw_text: str, model: Type[T]) -> T:
    """
    Attempt to parse JSON from LLM output with various cleanup strategies.

    Handles common LLM JSON issues:
    - Markdown code blocks (```json ... ```)
    - Trailing commas
    - Missing commas between array elements
    - Extra text before/after JSON
    - Truncated responses

    Args:
        raw_text: Raw text from LLM that should contain JSON
        model: Pydantic model to parse into

    Returns:
        Parsed Pydantic model instance

    Raises:
        ValueError: If JSON cannot be parsed after all attempts
    """
    if not raw_text:
        raise ValueError("Empty response from LLM")

    # Store original for error message
    original_text = raw_text

    # List of extraction/cleanup strategies to try
    strategies = [
        ("raw", lambda t: t),
        ("strip_markdown", strip_markdown_code_blocks),
        ("extract_json_object", extract_json_object),
        ("extract_json_array", extract_json_array),
        ("fix_trailing_commas", fix_trailing_commas),
        ("fix_missing_commas", fix_missing_commas),
        ("combined_fixes", lambda t: fix_missing_commas(fix_trailing_commas(strip_markdown_code_blocks(t)))),
    ]

    last_error = None
    for strategy_name, cleanup_fn in strategies:
        try:
            cleaned = cleanup_fn(raw_text)
            if not cleaned:
                continue

            # Try to parse as JSON first
            data = json.loads(cleaned)

            # Then validate with Pydantic
            result = model.model_validate(data)
            logger.debug(f"Successfully parsed JSON using strategy: {strategy_name}")
            return result

        except (json.JSONDecodeError, ValueError) as e:
            last_error = e
            logger.debug(f"Strategy '{strategy_name}' failed: {e}")
            continue

    # All strategies failed
    logger.error(f"Failed to parse JSON after all strategies. Raw text:\n{original_text[:1000]}")
    raise ValueError(f"Could not parse LLM response as JSON. Last error: {last_error}")


def strip_markdown_code_blocks(text: str) -> str:
    """Remove markdown code block markers."""
    # Remove ```json or ``` markers
    text = re.sub(r"```(?:json)?\s*\n?", "", text)
    return text.strip()


def extract_json_object(text: str) -> str:
    """Extract the first JSON object from text."""
    # Find first { and last }
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        return text

    return text[start:end + 1]


def extract_json_array(text: str) -> str:
    """Extract the first JSON array from text."""
    # Find first [ and last ]
    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1 or end <= start:
        return text

    return text[start:end + 1]


def fix_trailing_commas(text: str) -> str:
    """Remove trailing commas before } or ]."""
    # Remove trailing commas before closing brackets
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)
    return text


def fix_missing_commas(text: str) -> str:
    """Add missing commas between JSON elements."""
    # Add comma between "}" and "{" or "]" and "["
    text = re.sub(r'}\s*{', '},{', text)
    text = re.sub(r']\s*\[', '],[', text)

    # Add comma between closing quote and opening quote on next line
    # This handles: "value"\n"key" -> "value",\n"key"
    text = re.sub(r'"\s*\n\s*"', '",\n"', text)

    # Add comma between number and opening quote on next line
    text = re.sub(r'(\d)\s*\n\s*"', r'\1,\n"', text)

    # Add comma between closing bracket and opening quote
    text = re.sub(r'}\s*\n\s*"', '},\n"', text)
    text = re.sub(r']\s*\n\s*"', '],\n"', text)

    return text
