"""Company tools for Recruit CRM MCP Server."""

from mcp.types import Tool

from ..api_client import RecruitCRMClient


def get_tools() -> list[Tool]:
    """Return company-related tools."""
    return [
        Tool(
            name="list_companies",
            description="List all companies with pagination.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
            },
        ),
        Tool(
            name="get_company",
            description="Get detailed information about a specific company.",
            inputSchema={
                "type": "object",
                "properties": {
                    "company_slug": {"type": "string", "description": "Unique slug/ID of the company"},
                },
                "required": ["company_slug"],
            },
        ),
        Tool(
            name="create_company",
            description="Create a new company record. Required: company_name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "Company name (required)"},
                    "website": {"type": "string", "description": "Company website URL"},
                    "industry": {"type": "string", "description": "Industry sector"},
                    "city": {"type": "string", "description": "City"},
                    "country": {"type": "string", "description": "Country"},
                    "description": {"type": "string", "description": "Company description"},
                },
                "required": ["company_name"],
            },
        ),
        Tool(
            name="update_company",
            description="Update an existing company's information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "company_slug": {"type": "string", "description": "Slug/ID of the company to update (required)"},
                    "company_name": {"type": "string", "description": "Company name"},
                    "website": {"type": "string", "description": "Company website URL"},
                    "industry": {"type": "string", "description": "Industry sector"},
                    "city": {"type": "string", "description": "City"},
                    "country": {"type": "string", "description": "Country"},
                },
                "required": ["company_slug"],
            },
        ),
        Tool(
            name="delete_company",
            description="Permanently delete a company. This action cannot be undone.",
            inputSchema={
                "type": "object",
                "properties": {
                    "company_slug": {"type": "string", "description": "Slug/ID of the company to delete"},
                },
                "required": ["company_slug"],
            },
        ),
        Tool(
            name="search_companies",
            description="Search companies with filters like name, city, country, industry.",
            inputSchema={
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "Company name to search"},
                    "city": {"type": "string", "description": "City filter"},
                    "country": {"type": "string", "description": "Country filter"},
                    "industry": {"type": "string", "description": "Industry filter"},
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
            },
        ),
    ]


async def handle_tool(client: RecruitCRMClient, name: str, arguments: dict) -> dict:
    """Handle company tool calls."""
    args = arguments.copy()

    if name == "list_companies":
        return await client.list_companies(
            page=args.get("page", 1),
            limit=args.get("limit", 25),
        )
    elif name == "get_company":
        return await client.get_company(args["company_slug"])
    elif name == "create_company":
        return await client.create_company(args)
    elif name == "update_company":
        slug = args.pop("company_slug")
        return await client.update_company(slug, args)
    elif name == "delete_company":
        return await client.delete_company(args["company_slug"])
    elif name == "search_companies":
        page = args.pop("page", 1)
        limit = args.pop("limit", 25)
        return await client.search_companies(args, page=page, limit=limit)

    return None
