"""Tests for the tool dispatcher in tools/__init__.py."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from recruit_crm_mcp.api_client import RecruitCRMError
from recruit_crm_mcp.tools import get_tools, handle_tool_call


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

async def test_get_tools_returns_79():
    assert len(get_tools()) == 79


async def test_tool_names_unique():
    names = [t.name for t in get_tools()]
    duplicates = [n for n in set(names) if names.count(n) > 1]
    assert not duplicates, f"Duplicate tool names: {duplicates}"


# ---------------------------------------------------------------------------
# Error serialisation
# ---------------------------------------------------------------------------

async def test_unknown_tool_returns_non_empty_error():
    """An unknown tool name must produce a TextContent with a non-empty error string."""
    mock_client = MagicMock()

    result = await handle_tool_call(mock_client, "nonexistent_tool_xyz", {})

    assert len(result) == 1
    assert result[0].type == "text"
    data = json.loads(result[0].text)
    assert isinstance(data.get("error"), str) and data["error"]


async def test_recruit_crm_error_message_and_status_serialized():
    mock_client = MagicMock()
    mock_client.list_candidates = AsyncMock(
        side_effect=RecruitCRMError("Resource not found", status_code=404)
    )

    result = await handle_tool_call(mock_client, "list_candidates", {})

    data = json.loads(result[0].text)
    assert data["error"] == "Resource not found"
    assert data["status_code"] == 404
    assert "details" not in data  # details omitted when empty


async def test_recruit_crm_error_details_serialized():
    mock_client = MagicMock()
    mock_client.list_candidates = AsyncMock(
        side_effect=RecruitCRMError(
            "Validation error", status_code=422, details={"field": "required"}
        )
    )

    result = await handle_tool_call(mock_client, "list_candidates", {})

    data = json.loads(result[0].text)
    assert data["status_code"] == 422
    assert data["details"] == {"field": "required"}


async def test_unexpected_exception_returns_error_content():
    """Non-RecruitCRMError exceptions must also produce a safe error TextContent."""
    mock_client = MagicMock()
    mock_client.list_candidates = AsyncMock(side_effect=RuntimeError("internal boom"))

    result = await handle_tool_call(mock_client, "list_candidates", {})

    data = json.loads(result[0].text)
    assert isinstance(data.get("error"), str)
    assert "internal boom" in data["error"]


# ---------------------------------------------------------------------------
# Argument forwarding
# ---------------------------------------------------------------------------

async def test_successful_call_returns_json_text_content():
    mock_client = MagicMock()
    mock_client.list_candidates = AsyncMock(return_value={"data": [], "total": 0})

    result = await handle_tool_call(mock_client, "list_candidates", {})

    assert len(result) == 1
    assert result[0].type == "text"
    data = json.loads(result[0].text)
    assert data == {"data": [], "total": 0}


async def test_required_argument_forwarded_to_client():
    """The candidate_slug argument must be forwarded positionally to get_candidate."""
    mock_client = MagicMock()
    mock_client.get_candidate = AsyncMock(return_value={"slug": "cand-123"})

    await handle_tool_call(mock_client, "get_candidate", {"candidate_slug": "cand-123"})

    mock_client.get_candidate.assert_called_once_with("cand-123")


async def test_optional_arguments_with_defaults_forwarded():
    """Omitting optional pagination args must forward the default values to the client."""
    mock_client = MagicMock()
    mock_client.list_candidates = AsyncMock(return_value={"data": []})

    await handle_tool_call(mock_client, "list_candidates", {})

    mock_client.list_candidates.assert_called_once_with(page=1, limit=25)
