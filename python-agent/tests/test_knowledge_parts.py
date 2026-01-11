"""Tests for knowledge base parts API.

Test Cases:
- KP1: List all parts
- KP2: List parts with limit
- KP3: Get part by MPN
- KP4: Get unknown part returns 404
- KP5: Ban a part
- KP6: Verify part is banned
- KP7: Unban a part
- KP8: Add alternate to part
- KP9: Get alternates for part
"""

import pytest


@pytest.mark.asyncio
async def test_kp1_list_all_parts(client):
    """KP1: List all parts returns list (may be empty initially)."""
    response = await client.get("/knowledge/parts")

    assert response.status_code == 200
    parts = response.json()

    assert isinstance(parts, list)


@pytest.mark.asyncio
async def test_kp2_list_parts_with_limit(client):
    """KP2: List parts with limit returns at most N parts."""
    response = await client.get("/knowledge/parts", params={"limit": 10})

    assert response.status_code == 200
    parts = response.json()

    assert isinstance(parts, list)
    assert len(parts) <= 10


@pytest.mark.asyncio
async def test_kp3_get_part_by_mpn(client, test_state):
    """KP3: Get part by MPN returns part knowledge after banning creates it."""
    mpn = "TEST-PART-KP3"

    # First ban the part to create it in the knowledge base
    ban_response = await client.post(
        f"/knowledge/parts/{mpn}/ban",
        json={"reason": "Created for KP3 test", "user": "test"},
    )
    assert ban_response.status_code == 200
    test_state.banned_parts.append(mpn)

    # Now get the part
    response = await client.get(f"/knowledge/parts/{mpn}")

    assert response.status_code == 200
    part = response.json()

    assert part["mpn"] == mpn
    assert "notes" in part
    assert "approved_alternates" in part
    assert "banned" in part
    assert "ban_reason" in part
    assert "preferred" in part
    assert "times_used" in part
    assert "failure_count" in part


@pytest.mark.asyncio
async def test_kp4_get_unknown_part_returns_404(client):
    """KP4: Get unknown part returns 404 Not Found."""
    response = await client.get("/knowledge/parts/UNKNOWN-NONEXISTENT-PART-123")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_kp5_ban_a_part(client, test_state):
    """KP5: Ban a part marks it as banned."""
    mpn = "TEST-PART-KP5-BAN"

    response = await client.post(
        f"/knowledge/parts/{mpn}/ban",
        json={"reason": "Obsolete part", "user": "test_user"},
    )

    assert response.status_code == 200
    result = response.json()

    assert result["status"] == "banned"
    assert result["mpn"] == mpn
    assert result["reason"] == "Obsolete part"

    test_state.banned_parts.append(mpn)


@pytest.mark.asyncio
async def test_kp6_verify_part_is_banned(client, test_state):
    """KP6: After banning, get part shows banned: true."""
    mpn = "TEST-PART-KP6-VERIFY"

    # Ban the part
    await client.post(
        f"/knowledge/parts/{mpn}/ban",
        json={"reason": "Test ban", "user": "test"},
    )
    test_state.banned_parts.append(mpn)

    # Verify it's banned
    response = await client.get(f"/knowledge/parts/{mpn}")

    assert response.status_code == 200
    part = response.json()

    assert part["banned"] is True
    assert part["ban_reason"] == "Test ban"


@pytest.mark.asyncio
async def test_kp7_unban_a_part(client, test_state):
    """KP7: Unban a part removes the ban."""
    mpn = "TEST-PART-KP7-UNBAN"

    # First ban the part
    await client.post(
        f"/knowledge/parts/{mpn}/ban",
        json={"reason": "Temporary ban", "user": "test"},
    )

    # Unban the part
    response = await client.post(f"/knowledge/parts/{mpn}/unban")

    assert response.status_code == 200
    result = response.json()

    assert result["status"] == "unbanned"
    assert result["mpn"] == mpn

    # Verify it's unbanned
    get_response = await client.get(f"/knowledge/parts/{mpn}")
    part = get_response.json()
    assert part["banned"] is False


@pytest.mark.asyncio
async def test_kp8_add_alternate_to_part(client, test_state):
    """KP8: Add an approved alternate for a part."""
    mpn = "TEST-PART-KP8-PRIMARY"
    alternate_mpn = "TEST-PART-KP8-ALT"

    # First create the part by banning and unbanning
    await client.post(
        f"/knowledge/parts/{mpn}/ban",
        json={"reason": "temp", "user": "test"},
    )
    await client.post(f"/knowledge/parts/{mpn}/unban")

    # Add alternate
    response = await client.post(
        f"/knowledge/parts/{mpn}/alternates",
        json={"alternate_mpn": alternate_mpn, "reason": "Form fit function", "user": "test"},
    )

    assert response.status_code == 200
    result = response.json()

    assert result["status"] == "added"
    assert result["mpn"] == mpn
    assert result["alternate_mpn"] == alternate_mpn


@pytest.mark.asyncio
async def test_kp9_get_alternates_for_part(client):
    """KP9: Get approved alternates for a part returns alternate list."""
    mpn = "TEST-PART-KP9-PRIMARY"
    alternate1 = "TEST-PART-KP9-ALT1"
    alternate2 = "TEST-PART-KP9-ALT2"

    # Create the part
    await client.post(
        f"/knowledge/parts/{mpn}/ban",
        json={"reason": "temp", "user": "test"},
    )
    await client.post(f"/knowledge/parts/{mpn}/unban")

    # Add alternates
    await client.post(
        f"/knowledge/parts/{mpn}/alternates",
        json={"alternate_mpn": alternate1, "user": "test"},
    )
    await client.post(
        f"/knowledge/parts/{mpn}/alternates",
        json={"alternate_mpn": alternate2, "user": "test"},
    )

    # Get alternates
    response = await client.get(f"/knowledge/parts/{mpn}/alternates")

    assert response.status_code == 200
    alternates = response.json()

    assert isinstance(alternates, list)
    assert alternate1 in alternates
    assert alternate2 in alternates
