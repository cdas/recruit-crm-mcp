"""Hotlist tools for Recruit CRM MCP Server."""

from mcp.types import Tool

from ..api_client import RecruitCRMClient


def get_tools() -> list[Tool]:
    """Return hotlist-related tools."""
    return [
        Tool(
            name="list_hotlists",
            description="List all hotlists with pagination. Hotlists are curated collections of records.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
            },
        ),
        Tool(
            name="get_hotlist",
            description="Get a specific hotlist by slug, including its records.",
            inputSchema={
                "type": "object",
                "properties": {
                    "hotlist_slug": {"type": "string", "description": "Unique slug/ID of the hotlist"},
                },
                "required": ["hotlist_slug"],
            },
        ),
        Tool(
            name="create_hotlist",
            description="Create a new hotlist for organizing records.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Hotlist name (required)"},
                    "entity_type": {"type": "string", "description": "Type of records: candidate, contact, or company"},
                    "description": {"type": "string", "description": "Hotlist description"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="update_hotlist",
            description="Update an existing hotlist.",
            inputSchema={
                "type": "object",
                "properties": {
                    "hotlist_slug": {"type": "string", "description": "Slug/ID of the hotlist to update (required)"},
                    "name": {"type": "string", "description": "Hotlist name"},
                    "description": {"type": "string", "description": "Hotlist description"},
                },
                "required": ["hotlist_slug"],
            },
        ),
        Tool(
            name="delete_hotlist",
            description="Permanently delete a hotlist.",
            inputSchema={
                "type": "object",
                "properties": {
                    "hotlist_slug": {"type": "string", "description": "Slug/ID of the hotlist to delete"},
                },
                "required": ["hotlist_slug"],
            },
        ),
        Tool(
            name="add_record_to_hotlist",
            description="Add a record (candidate/contact/company) to a hotlist.",
            inputSchema={
                "type": "object",
                "properties": {
                    "hotlist_slug": {"type": "string", "description": "Slug/ID of the hotlist"},
                    "record_slug": {"type": "string", "description": "Slug/ID of the record to add"},
                },
                "required": ["hotlist_slug", "record_slug"],
            },
        ),
        Tool(
            name="remove_record_from_hotlist",
            description="Remove a record from a hotlist.",
            inputSchema={
                "type": "object",
                "properties": {
                    "hotlist_slug": {"type": "string", "description": "Slug/ID of the hotlist"},
                    "record_slug": {"type": "string", "description": "Slug/ID of the record to remove"},
                },
                "required": ["hotlist_slug", "record_slug"],
            },
        ),
        Tool(
            name="search_hotlists",
            description="Search hotlists with filters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Hotlist name to search"},
                    "entity_type": {"type": "string", "description": "Entity type filter"},
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
            },
        ),
    ]


async def handle_tool(client: RecruitCRMClient, name: str, arguments: dict) -> dict:
    """Handle hotlist tool calls."""
    args = arguments.copy()

    if name == "list_hotlists":
        return await client.list_hotlists(
            page=args.get("page", 1),
            limit=args.get("limit", 25),
        )
    elif name == "get_hotlist":
        return await client.get_hotlist(args["hotlist_slug"])
    elif name == "create_hotlist":
        return await client.create_hotlist(args)
    elif name == "update_hotlist":
        slug = args.pop("hotlist_slug")
        return await client.update_hotlist(slug, args)
    elif name == "delete_hotlist":
        return await client.delete_hotlist(args["hotlist_slug"])
    elif name == "add_record_to_hotlist":
        return await client.add_record_to_hotlist(
            hotlist_slug=args["hotlist_slug"],
            record_slug=args["record_slug"],
        )
    elif name == "remove_record_from_hotlist":
        return await client.remove_record_from_hotlist(
            hotlist_slug=args["hotlist_slug"],
            record_slug=args["record_slug"],
        )
    elif name == "search_hotlists":
        page = args.pop("page", 1)
        limit = args.pop("limit", 25)
        return await client.search_hotlists(args, page=page, limit=limit)

    return None
