"""Job tools for Recruit CRM MCP Server."""

from mcp.types import Tool

from ..api_client import RecruitCRMClient


def get_tools() -> list[Tool]:
    """Return job-related tools."""
    return [
        Tool(
            name="list_jobs",
            description="List all jobs with pagination.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
            },
        ),
        Tool(
            name="get_job",
            description="Get detailed information about a specific job.",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_slug": {"type": "string", "description": "Unique slug/ID of the job"},
                },
                "required": ["job_slug"],
            },
        ),
        Tool(
            name="create_job",
            description="Create a new job posting. Required: name (job title).",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Job title (required)"},
                    "company_slug": {"type": "string", "description": "Slug/ID of the hiring company"},
                    "contact_slug": {"type": "string", "description": "Slug/ID of the hiring contact"},
                    "job_description_text": {"type": "string", "description": "Job description"},
                    "city": {"type": "string", "description": "Job location city"},
                    "country": {"type": "string", "description": "Job location country"},
                    "number_of_openings": {"type": "integer", "description": "Number of positions"},
                    "min_annual_salary": {"type": "number", "description": "Minimum salary"},
                    "max_annual_salary": {"type": "number", "description": "Maximum salary"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="update_job",
            description="Update an existing job posting.",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_slug": {"type": "string", "description": "Slug/ID of the job to update (required)"},
                    "name": {"type": "string", "description": "Job title"},
                    "company_slug": {"type": "string", "description": "Slug/ID of the hiring company"},
                    "contact_slug": {"type": "string", "description": "Slug/ID of the hiring contact"},
                    "job_description_text": {"type": "string", "description": "Job description"},
                    "city": {"type": "string", "description": "Job location city"},
                    "country": {"type": "string", "description": "Job location country"},
                },
                "required": ["job_slug"],
            },
        ),
        Tool(
            name="delete_job",
            description="Permanently delete a job. This action cannot be undone.",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_slug": {"type": "string", "description": "Slug/ID of the job to delete"},
                },
                "required": ["job_slug"],
            },
        ),
        Tool(
            name="search_jobs",
            description="Search jobs with filters like title, company, status, location.",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_title": {"type": "string", "description": "Job title to search"},
                    "company_name": {"type": "string", "description": "Company name filter"},
                    "job_status": {"type": "string", "description": "Job status filter (Open, Closed, etc.)"},
                    "city": {"type": "string", "description": "City filter"},
                    "country": {"type": "string", "description": "Country filter"},
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
            },
        ),
        Tool(
            name="get_job_associated_fields",
            description="Get associated/custom fields for a specific job.",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_slug": {"type": "string", "description": "Slug/ID of the job"},
                },
                "required": ["job_slug"],
            },
        ),
        Tool(
            name="update_job_associated_fields",
            description="Update associated/custom fields for a job.",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_slug": {"type": "string", "description": "Slug/ID of the job (required)"},
                    "fields": {"type": "object", "description": "Object with field_id: value pairs"},
                },
                "required": ["job_slug", "fields"],
            },
        ),
    ]


async def handle_tool(client: RecruitCRMClient, name: str, arguments: dict) -> dict:
    """Handle job tool calls."""
    args = arguments.copy()

    if name == "list_jobs":
        return await client.list_jobs(
            page=args.get("page", 1),
            limit=args.get("limit", 25),
        )
    elif name == "get_job":
        return await client.get_job(args["job_slug"])
    elif name == "create_job":
        return await client.create_job(args)
    elif name == "update_job":
        slug = args.pop("job_slug")
        return await client.update_job(slug, args)
    elif name == "delete_job":
        return await client.delete_job(args["job_slug"])
    elif name == "search_jobs":
        page = args.pop("page", 1)
        limit = args.pop("limit", 25)
        return await client.search_jobs(args, page=page, limit=limit)
    elif name == "get_job_associated_fields":
        return await client.get_job_associated_fields(args["job_slug"])
    elif name == "update_job_associated_fields":
        return await client.update_job_associated_fields(
            job_slug=args["job_slug"],
            data=args["fields"],
        )

    return None
