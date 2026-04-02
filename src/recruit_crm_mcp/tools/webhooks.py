"""Webhook/Subscription tools for Recruit CRM MCP Server."""

from mcp.types import Tool

from ..api_client import RecruitCRMClient


def get_tools() -> list[Tool]:
    """Return webhook-related tools."""
    return [
        Tool(
            name="list_subscriptions",
            description="Get all webhook subscriptions configured for the account.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="create_subscription",
            description="Create a new webhook subscription to receive event notifications.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Webhook URL to receive events (required)"},
                    "events": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of events to subscribe to (e.g., candidate.added, job.updated)",
                    },
                },
                "required": ["url", "events"],
            },
        ),
        Tool(
            name="delete_subscription",
            description="Delete a webhook subscription.",
            inputSchema={
                "type": "object",
                "properties": {
                    "subscription_id": {"type": "string", "description": "ID of the subscription to delete"},
                },
                "required": ["subscription_id"],
            },
        ),
    ]


async def handle_tool(client: RecruitCRMClient, name: str, arguments: dict) -> dict:
    """Handle webhook tool calls."""
    if name == "list_subscriptions":
        return await client.list_subscriptions()
    elif name == "create_subscription":
        return await client.create_subscription(
            url=arguments["url"],
            events=arguments["events"],
        )
    elif name == "delete_subscription":
        return await client.delete_subscription(arguments["subscription_id"])

    return None
