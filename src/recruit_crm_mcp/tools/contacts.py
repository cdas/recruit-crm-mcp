"""Contact tools for Recruit CRM MCP Server."""

from mcp.types import Tool

from ..api_client import RecruitCRMClient


def get_tools() -> list[Tool]:
    """Return contact-related tools."""
    return [
        Tool(
            name="list_contacts",
            description="List all contacts with pagination.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
            },
        ),
        Tool(
            name="get_contact",
            description="Get detailed information about a specific contact.",
            inputSchema={
                "type": "object",
                "properties": {
                    "contact_slug": {"type": "string", "description": "Unique slug/ID of the contact"},
                },
                "required": ["contact_slug"],
            },
        ),
        Tool(
            name="create_contact",
            description="Create a new contact. Required: first_name, last_name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "first_name": {"type": "string", "description": "Contact's first name (required)"},
                    "last_name": {"type": "string", "description": "Contact's last name (required)"},
                    "email": {"type": "string", "description": "Email address"},
                    "contact_number": {"type": "string", "description": "Phone number"},
                    "company_slug": {"type": "string", "description": "Slug/ID of associated company"},
                    "position": {"type": "string", "description": "Job title/position"},
                },
                "required": ["first_name", "last_name"],
            },
        ),
        Tool(
            name="update_contact",
            description="Update an existing contact's information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "contact_slug": {"type": "string", "description": "Slug/ID of the contact to update (required)"},
                    "first_name": {"type": "string", "description": "First name"},
                    "last_name": {"type": "string", "description": "Last name"},
                    "email": {"type": "string", "description": "Email address"},
                    "contact_number": {"type": "string", "description": "Phone number"},
                    "company_slug": {"type": "string", "description": "Slug/ID of associated company"},
                    "position": {"type": "string", "description": "Job title/position"},
                },
                "required": ["contact_slug"],
            },
        ),
        Tool(
            name="delete_contact",
            description="Permanently delete a contact. This action cannot be undone.",
            inputSchema={
                "type": "object",
                "properties": {
                    "contact_slug": {"type": "string", "description": "Slug/ID of the contact to delete"},
                },
                "required": ["contact_slug"],
            },
        ),
        Tool(
            name="search_contacts",
            description="Search contacts with filters like name, email, company.",
            inputSchema={
                "type": "object",
                "properties": {
                    "first_name": {"type": "string", "description": "First name to search"},
                    "last_name": {"type": "string", "description": "Last name to search"},
                    "email": {"type": "string", "description": "Email to search"},
                    "company_slug": {"type": "string", "description": "Filter by company"},
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
            },
        ),
    ]


async def handle_tool(client: RecruitCRMClient, name: str, arguments: dict) -> dict:
    """Handle contact tool calls."""
    args = arguments.copy()

    if name == "list_contacts":
        return await client.list_contacts(
            page=args.get("page", 1),
            limit=args.get("limit", 25),
        )
    elif name == "get_contact":
        return await client.get_contact(args["contact_slug"])
    elif name == "create_contact":
        return await client.create_contact(args)
    elif name == "update_contact":
        slug = args.pop("contact_slug")
        return await client.update_contact(slug, args)
    elif name == "delete_contact":
        return await client.delete_contact(args["contact_slug"])
    elif name == "search_contacts":
        page = args.pop("page", 1)
        limit = args.pop("limit", 25)
        return await client.search_contacts(args, page=page, limit=limit)

    return None
