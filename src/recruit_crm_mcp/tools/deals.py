"""Deal tools for Recruit CRM MCP Server."""

from mcp.types import Tool

from ..api_client import RecruitCRMClient


def get_tools() -> list[Tool]:
    """Return deal-related tools."""
    return [
        Tool(
            name="list_deals",
            description="List all deals with pagination. Deals track revenue and placement fees.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
            },
        ),
        Tool(
            name="get_deal",
            description="Get detailed information about a specific deal.",
            inputSchema={
                "type": "object",
                "properties": {
                    "deal_slug": {"type": "string", "description": "Unique slug/ID of the deal"},
                },
                "required": ["deal_slug"],
            },
        ),
        Tool(
            name="create_deal",
            description="Create a new deal record for tracking revenue.",
            inputSchema={
                "type": "object",
                "properties": {
                    "deal_name": {"type": "string", "description": "Deal name (required)"},
                    "company_slug": {"type": "string", "description": "Associated company"},
                    "contact_slug": {"type": "string", "description": "Associated contact"},
                    "deal_value": {"type": "number", "description": "Deal value/amount"},
                    "currency_id": {"type": "integer", "description": "Currency ID"},
                    "deal_stage": {"type": "string", "description": "Current deal stage"},
                    "candidate_slug": {"type": "string", "description": "Associated candidate"},
                    "job_slug": {"type": "string", "description": "Associated job"},
                },
                "required": ["deal_name"],
            },
        ),
        Tool(
            name="update_deal",
            description="Update an existing deal.",
            inputSchema={
                "type": "object",
                "properties": {
                    "deal_slug": {"type": "string", "description": "Slug/ID of the deal to update (required)"},
                    "deal_name": {"type": "string", "description": "Deal name"},
                    "deal_value": {"type": "number", "description": "Deal value/amount"},
                    "deal_stage": {"type": "string", "description": "Current deal stage"},
                },
                "required": ["deal_slug"],
            },
        ),
        Tool(
            name="delete_deal",
            description="Permanently delete a deal. This action cannot be undone.",
            inputSchema={
                "type": "object",
                "properties": {
                    "deal_slug": {"type": "string", "description": "Slug/ID of the deal to delete"},
                },
                "required": ["deal_slug"],
            },
        ),
        Tool(
            name="search_deals",
            description="Search deals with filters like name, stage, company.",
            inputSchema={
                "type": "object",
                "properties": {
                    "deal_name": {"type": "string", "description": "Deal name to search"},
                    "deal_stage": {"type": "string", "description": "Deal stage filter"},
                    "company_name": {"type": "string", "description": "Company name filter"},
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
            },
        ),
    ]


async def handle_tool(client: RecruitCRMClient, name: str, arguments: dict) -> dict:
    """Handle deal tool calls."""
    args = arguments.copy()

    if name == "list_deals":
        return await client.list_deals(
            page=args.get("page", 1),
            limit=args.get("limit", 25),
        )
    elif name == "get_deal":
        return await client.get_deal(args["deal_slug"])
    elif name == "create_deal":
        return await client.create_deal(args)
    elif name == "update_deal":
        slug = args.pop("deal_slug")
        return await client.update_deal(slug, args)
    elif name == "delete_deal":
        return await client.delete_deal(args["deal_slug"])
    elif name == "search_deals":
        page = args.pop("page", 1)
        limit = args.pop("limit", 25)
        return await client.search_deals(args, page=page, limit=limit)

    return None
