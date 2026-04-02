"""Candidate tools for Recruit CRM MCP Server."""

from mcp.types import Tool

from ..api_client import RecruitCRMClient


def get_tools() -> list[Tool]:
    """Return candidate-related tools."""
    return [
        # Basic CRUD
        Tool(
            name="list_candidates",
            description="List all candidates with pagination. Returns candidate profiles including names, emails, skills, and other information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25, max: 100)", "default": 25},
                },
            },
        ),
        Tool(
            name="search_candidates",
            description="Search candidates by name, email, skills, or other criteria using a query string.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query string"},
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_candidate",
            description="Get detailed information about a specific candidate by their slug/ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "candidate_slug": {"type": "string", "description": "Unique slug/ID of the candidate"},
                },
                "required": ["candidate_slug"],
            },
        ),
        Tool(
            name="create_candidate",
            description="Create a new candidate profile. Required: first_name, last_name. Optional: email, phone, position, skills, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "first_name": {"type": "string", "description": "Candidate's first name (required)"},
                    "last_name": {"type": "string", "description": "Candidate's last name (required)"},
                    "email": {"type": "string", "description": "Email address"},
                    "contact_number": {"type": "string", "description": "Phone number"},
                    "position": {"type": "string", "description": "Current or desired position"},
                    "current_organization": {"type": "string", "description": "Current employer"},
                    "skill": {"type": "string", "description": "Comma-separated skills"},
                    "city": {"type": "string", "description": "City"},
                    "country": {"type": "string", "description": "Country"},
                    "linkedin": {"type": "string", "description": "LinkedIn profile URL"},
                    "work_ex_year": {"type": "integer", "description": "Years of experience"},
                },
                "required": ["first_name", "last_name"],
            },
        ),
        Tool(
            name="update_candidate",
            description="Update an existing candidate's information. Only provided fields will be updated.",
            inputSchema={
                "type": "object",
                "properties": {
                    "candidate_slug": {"type": "string", "description": "Unique slug/ID of the candidate to update (required)"},
                    "first_name": {"type": "string", "description": "First name"},
                    "last_name": {"type": "string", "description": "Last name"},
                    "email": {"type": "string", "description": "Email address"},
                    "contact_number": {"type": "string", "description": "Phone number"},
                    "position": {"type": "string", "description": "Current or desired position"},
                    "current_organization": {"type": "string", "description": "Current employer"},
                    "skill": {"type": "string", "description": "Comma-separated skills"},
                    "city": {"type": "string", "description": "City"},
                    "country": {"type": "string", "description": "Country"},
                },
                "required": ["candidate_slug"],
            },
        ),
        Tool(
            name="delete_candidate",
            description="Permanently delete a candidate. This action cannot be undone.",
            inputSchema={
                "type": "object",
                "properties": {
                    "candidate_slug": {"type": "string", "description": "Unique slug/ID of the candidate to delete"},
                },
                "required": ["candidate_slug"],
            },
        ),
        # Pipeline & Pitch
        Tool(
            name="assign_candidate_to_job",
            description="Assign a candidate to a job pipeline. This adds the candidate to the job's hiring workflow.",
            inputSchema={
                "type": "object",
                "properties": {
                    "candidate_slug": {"type": "string", "description": "Slug/ID of the candidate"},
                    "job_slug": {"type": "string", "description": "Slug/ID of the job"},
                    "hiring_stage_id": {"type": "integer", "description": "Initial hiring stage ID (default: 1)", "default": 1},
                },
                "required": ["candidate_slug", "job_slug"],
            },
        ),
        Tool(
            name="unassign_candidate_from_job",
            description="Remove a candidate from a job pipeline.",
            inputSchema={
                "type": "object",
                "properties": {
                    "candidate_slug": {"type": "string", "description": "Slug/ID of the candidate"},
                    "job_slug": {"type": "string", "description": "Slug/ID of the job"},
                },
                "required": ["candidate_slug", "job_slug"],
            },
        ),
        Tool(
            name="update_hiring_stage",
            description="Move a candidate to a different hiring stage within a job pipeline.",
            inputSchema={
                "type": "object",
                "properties": {
                    "candidate_slug": {"type": "string", "description": "Slug/ID of the candidate"},
                    "job_slug": {"type": "string", "description": "Slug/ID of the job"},
                    "hiring_stage_id": {"type": "integer", "description": "New hiring stage ID"},
                },
                "required": ["candidate_slug", "job_slug", "hiring_stage_id"],
            },
        ),
        Tool(
            name="get_candidate_history",
            description="Get the hiring stage history for a candidate, showing all stage transitions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "candidate_slug": {"type": "string", "description": "Slug/ID of the candidate"},
                },
                "required": ["candidate_slug"],
            },
        ),
        Tool(
            name="get_candidate_jobs",
            description="Get all jobs a candidate is currently assigned to.",
            inputSchema={
                "type": "object",
                "properties": {
                    "candidate_slug": {"type": "string", "description": "Slug/ID of the candidate"},
                },
                "required": ["candidate_slug"],
            },
        ),
        Tool(
            name="get_job_candidates",
            description="Get all candidates in a job's pipeline with their current hiring stages.",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_slug": {"type": "string", "description": "Slug/ID of the job"},
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
                "required": ["job_slug"],
            },
        ),
        Tool(
            name="pitch_candidate",
            description="Pitch/present a candidate to a client contact for a specific job opportunity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "candidate_slug": {"type": "string", "description": "Slug/ID of the candidate to pitch"},
                    "contact_slug": {"type": "string", "description": "Slug/ID of the client contact"},
                    "job_slug": {"type": "string", "description": "Slug/ID of the related job"},
                    "message": {"type": "string", "description": "Pitch message/notes", "default": ""},
                },
                "required": ["candidate_slug", "contact_slug", "job_slug"],
            },
        ),
        Tool(
            name="get_candidate_pitches",
            description="Get all contacts a candidate has been pitched to.",
            inputSchema={
                "type": "object",
                "properties": {
                    "candidate_slug": {"type": "string", "description": "Slug/ID of the candidate"},
                },
                "required": ["candidate_slug"],
            },
        ),
        Tool(
            name="get_offlimit_candidates",
            description="Get all candidates marked as off-limit (not to be contacted/placed).",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
            },
        ),
        Tool(
            name="get_candidate_questions",
            description="Get screening questions and answers for a candidate.",
            inputSchema={
                "type": "object",
                "properties": {
                    "candidate_slug": {"type": "string", "description": "Slug/ID of the candidate"},
                },
                "required": ["candidate_slug"],
            },
        ),
        Tool(
            name="update_candidate_visibility",
            description="Update whether a candidate is visible to the client for a specific job.",
            inputSchema={
                "type": "object",
                "properties": {
                    "candidate_slug": {"type": "string", "description": "Slug/ID of the candidate"},
                    "job_slug": {"type": "string", "description": "Slug/ID of the job"},
                    "visible": {"type": "boolean", "description": "Whether candidate should be visible"},
                },
                "required": ["candidate_slug", "job_slug", "visible"],
            },
        ),
    ]


async def handle_tool(client: RecruitCRMClient, name: str, arguments: dict) -> dict:
    """Handle candidate tool calls."""
    args = arguments.copy()

    if name == "list_candidates":
        return await client.list_candidates(
            page=args.get("page", 1),
            limit=args.get("limit", 25),
        )
    elif name == "search_candidates":
        return await client.search_candidates(
            query=args["query"],
            page=args.get("page", 1),
            limit=args.get("limit", 25),
        )
    elif name == "get_candidate":
        return await client.get_candidate(args["candidate_slug"])
    elif name == "create_candidate":
        return await client.create_candidate(args)
    elif name == "update_candidate":
        slug = args.pop("candidate_slug")
        return await client.update_candidate(slug, args)
    elif name == "delete_candidate":
        return await client.delete_candidate(args["candidate_slug"])
    elif name == "assign_candidate_to_job":
        return await client.assign_candidate_to_job(
            candidate_slug=args["candidate_slug"],
            job_slug=args["job_slug"],
            hiring_stage_id=args.get("hiring_stage_id", 1),
        )
    elif name == "unassign_candidate_from_job":
        return await client.unassign_candidate_from_job(
            candidate_slug=args["candidate_slug"],
            job_slug=args["job_slug"],
        )
    elif name == "update_hiring_stage":
        return await client.update_hiring_stage(
            candidate_slug=args["candidate_slug"],
            job_slug=args["job_slug"],
            hiring_stage_id=args["hiring_stage_id"],
        )
    elif name == "get_candidate_history":
        return await client.get_candidate_history(args["candidate_slug"])
    elif name == "get_candidate_jobs":
        return await client.get_candidate_jobs(args["candidate_slug"])
    elif name == "get_job_candidates":
        return await client.get_job_candidates(
            job_slug=args["job_slug"],
            page=args.get("page", 1),
            limit=args.get("limit", 25),
        )
    elif name == "pitch_candidate":
        return await client.pitch_candidate(
            candidate_slug=args["candidate_slug"],
            contact_slug=args["contact_slug"],
            job_slug=args["job_slug"],
            message=args.get("message", ""),
        )
    elif name == "get_candidate_pitches":
        return await client.get_candidate_pitches(args["candidate_slug"])
    elif name == "get_offlimit_candidates":
        return await client.get_offlimit_candidates(
            page=args.get("page", 1),
            limit=args.get("limit", 25),
        )
    elif name == "get_candidate_questions":
        return await client.get_candidate_questions(args["candidate_slug"])
    elif name == "update_candidate_visibility":
        return await client.update_candidate_visibility(
            candidate_slug=args["candidate_slug"],
            job_slug=args["job_slug"],
            visible=args["visible"],
        )

    return None
