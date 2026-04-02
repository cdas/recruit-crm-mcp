"""MCP Tool definitions for Recruit CRM - Modular organization."""

from __future__ import annotations

import json
from typing import Any

from mcp.types import Tool, TextContent

from ..api_client import RecruitCRMClient, RecruitCRMError
from . import (
    activities,
    candidates,
    companies,
    contacts,
    deals,
    hotlists,
    jobs,
    metadata,
    webhooks,
)

# All tool modules
_MODULES = [
    candidates,
    companies,
    contacts,
    jobs,
    deals,
    activities,
    hotlists,
    metadata,
    webhooks,
]


def get_tools() -> list[Tool]:
    """Return all available MCP tools from all modules."""
    all_tools = []
    for module in _MODULES:
        all_tools.extend(module.get_tools())
    return all_tools


async def handle_tool_call(
    client: RecruitCRMClient, name: str, arguments: dict[str, Any]
) -> list[TextContent]:
    """Handle a tool call and return the result."""
    try:
        result = await _execute_tool(client, name, arguments)
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    except RecruitCRMError as e:
        error_response = {"error": e.message, "status_code": e.status_code}
        if e.details:
            error_response["details"] = e.details
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2))]


async def _execute_tool(
    client: RecruitCRMClient, name: str, arguments: dict[str, Any]
) -> dict[str, Any]:
    """Execute the appropriate tool by delegating to the correct module."""
    for module in _MODULES:
        result = await module.handle_tool(client, name, arguments)
        if result is not None:
            return result

    raise ValueError(f"Unknown tool: {name}")
