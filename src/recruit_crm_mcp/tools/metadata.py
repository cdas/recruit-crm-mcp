"""Metadata tools (Users, Hiring Stages, Custom Fields) for Recruit CRM MCP Server."""

from mcp.types import Tool

from ..api_client import RecruitCRMClient


def get_tools() -> list[Tool]:
    """Return metadata-related tools."""
    return [
        Tool(
            name="list_users",
            description="Get all team members/users in the Recruit CRM account.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_hiring_stages",
            description="Get all global hiring stages configured in the system.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_job_hiring_stages",
            description="Get hiring stages configured for a specific job.",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_slug": {"type": "string", "description": "Slug/ID of the job"},
                },
                "required": ["job_slug"],
            },
        ),
        Tool(
            name="get_custom_fields",
            description="Get all custom fields configured in the system with their types.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


async def handle_tool(client: RecruitCRMClient, name: str, arguments: dict) -> dict:
    """Handle metadata tool calls."""
    if name == "list_users":
        return await client.list_users()
    elif name == "get_hiring_stages":
        return await client.get_hiring_stages()
    elif name == "get_job_hiring_stages":
        return await client.get_job_hiring_stages(arguments["job_slug"])
    elif name == "get_custom_fields":
        return await client.get_custom_fields()

    return None
