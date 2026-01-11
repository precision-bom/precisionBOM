"""Tests for OpenAI-compatible chat completions API.

Test Cases:
- C1: Basic chat completion
- C2: Response has required fields
- C3: Chat with BOM question
- C4: Chat with temperature parameter

Note: These tests require OPENAI_API_KEY and make actual LLM calls.
"""

import pytest


@pytest.mark.asyncio
async def test_c1_basic_chat_completion(client):
    """C1: Basic chat completion returns OpenAI-format response."""
    response = await client.post(
        "/v1/chat/completions",
        json={
            "model": "bom-agent",
            "messages": [
                {"role": "user", "content": "Hello, what can you help me with?"}
            ],
        },
    )

    assert response.status_code == 200
    result = response.json()

    assert "id" in result
    assert result["object"] == "chat.completion"
    assert "created" in result
    assert "model" in result
    assert "choices" in result
    assert "usage" in result


@pytest.mark.asyncio
async def test_c2_response_has_required_fields(client):
    """C2: Chat completion response has all required OpenAI-format fields."""
    response = await client.post(
        "/v1/chat/completions",
        json={
            "model": "bom-agent",
            "messages": [
                {"role": "user", "content": "What is a BOM?"}
            ],
        },
    )

    assert response.status_code == 200
    result = response.json()

    # Check top-level fields
    assert result["id"].startswith("chatcmpl-")
    assert result["object"] == "chat.completion"
    assert isinstance(result["created"], int)
    assert result["model"] == "bom-agent"

    # Check choices
    assert len(result["choices"]) >= 1
    choice = result["choices"][0]
    assert "index" in choice
    assert "message" in choice
    assert "finish_reason" in choice
    assert choice["message"]["role"] == "assistant"
    assert len(choice["message"]["content"]) > 0

    # Check usage
    usage = result["usage"]
    assert "prompt_tokens" in usage
    assert "completion_tokens" in usage
    assert "total_tokens" in usage


@pytest.mark.asyncio
async def test_c3_chat_with_bom_question(client):
    """C3: Chat with BOM-related question returns relevant response."""
    response = await client.post(
        "/v1/chat/completions",
        json={
            "model": "bom-agent",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a BOM analysis assistant."
                },
                {
                    "role": "user",
                    "content": "What factors should I consider when sourcing electronic components?"
                }
            ],
        },
    )

    assert response.status_code == 200
    result = response.json()

    # Response should contain relevant content
    content = result["choices"][0]["message"]["content"]
    assert len(content) > 0


@pytest.mark.asyncio
async def test_c4_chat_with_temperature_parameter(client):
    """C4: Chat with temperature parameter generates response."""
    response = await client.post(
        "/v1/chat/completions",
        json={
            "model": "bom-agent",
            "messages": [
                {"role": "user", "content": "Give me a brief tip about component sourcing."}
            ],
            "temperature": 0.5,
        },
    )

    assert response.status_code == 200
    result = response.json()

    assert "choices" in result
    assert len(result["choices"]) >= 1
    assert len(result["choices"][0]["message"]["content"]) > 0
