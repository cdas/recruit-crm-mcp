"""Activity tools (Notes, Tasks, Meetings, Call Logs) for Recruit CRM MCP Server."""

from mcp.types import Tool

from ..api_client import RecruitCRMClient


def get_tools() -> list[Tool]:
    """Return activity-related tools (notes, tasks, meetings, call logs)."""
    return [
        # Notes
        Tool(
            name="list_notes",
            description="List all notes with pagination. Notes document activities and interactions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
            },
        ),
        Tool(
            name="get_note",
            description="Get a specific note by slug.",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_slug": {"type": "string", "description": "Unique slug/ID of the note"},
                },
                "required": ["note_slug"],
            },
        ),
        Tool(
            name="create_note",
            description="Create a new note. Can be linked to multiple entities (candidate, contact, company, job, deal).",
            inputSchema={
                "type": "object",
                "properties": {
                    "note": {"type": "string", "description": "Note content (required)"},
                    "candidate_slug": {"type": "string", "description": "Link to candidate"},
                    "contact_slug": {"type": "string", "description": "Link to contact"},
                    "company_slug": {"type": "string", "description": "Link to company"},
                    "job_slug": {"type": "string", "description": "Link to job"},
                    "deal_slug": {"type": "string", "description": "Link to deal"},
                },
                "required": ["note"],
            },
        ),
        Tool(
            name="update_note",
            description="Update an existing note.",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_slug": {"type": "string", "description": "Slug/ID of the note to update (required)"},
                    "note": {"type": "string", "description": "Updated note content"},
                },
                "required": ["note_slug"],
            },
        ),
        Tool(
            name="delete_note",
            description="Permanently delete a note.",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_slug": {"type": "string", "description": "Slug/ID of the note to delete"},
                },
                "required": ["note_slug"],
            },
        ),
        Tool(
            name="search_notes",
            description="Search notes with filters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "candidate_slug": {"type": "string", "description": "Filter by candidate"},
                    "contact_slug": {"type": "string", "description": "Filter by contact"},
                    "company_slug": {"type": "string", "description": "Filter by company"},
                    "job_slug": {"type": "string", "description": "Filter by job"},
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
            },
        ),
        # Tasks
        Tool(
            name="list_tasks",
            description="List all tasks with pagination. Tasks are follow-up reminders and to-dos.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
            },
        ),
        Tool(
            name="get_task",
            description="Get a specific task by slug.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_slug": {"type": "string", "description": "Unique slug/ID of the task"},
                },
                "required": ["task_slug"],
            },
        ),
        Tool(
            name="create_task",
            description="Create a new task/follow-up. Can be linked to entities.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title (required)"},
                    "due_date": {"type": "string", "description": "Due date (ISO 8601 format)"},
                    "description": {"type": "string", "description": "Task description"},
                    "candidate_slug": {"type": "string", "description": "Link to candidate"},
                    "contact_slug": {"type": "string", "description": "Link to contact"},
                    "company_slug": {"type": "string", "description": "Link to company"},
                    "job_slug": {"type": "string", "description": "Link to job"},
                    "deal_slug": {"type": "string", "description": "Link to deal"},
                },
                "required": ["title"],
            },
        ),
        Tool(
            name="update_task",
            description="Update an existing task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_slug": {"type": "string", "description": "Slug/ID of the task to update (required)"},
                    "title": {"type": "string", "description": "Task title"},
                    "due_date": {"type": "string", "description": "Due date"},
                    "description": {"type": "string", "description": "Task description"},
                    "status": {"type": "string", "description": "Task status (e.g., completed)"},
                },
                "required": ["task_slug"],
            },
        ),
        Tool(
            name="delete_task",
            description="Permanently delete a task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_slug": {"type": "string", "description": "Slug/ID of the task to delete"},
                },
                "required": ["task_slug"],
            },
        ),
        Tool(
            name="search_tasks",
            description="Search tasks with filters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title to search"},
                    "status": {"type": "string", "description": "Task status filter"},
                    "due_date_from": {"type": "string", "description": "Due date from (ISO 8601)"},
                    "due_date_to": {"type": "string", "description": "Due date to (ISO 8601)"},
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
            },
        ),
        # Meetings
        Tool(
            name="list_meetings",
            description="List all meetings with pagination.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
            },
        ),
        Tool(
            name="get_meeting",
            description="Get a specific meeting by slug.",
            inputSchema={
                "type": "object",
                "properties": {
                    "meeting_slug": {"type": "string", "description": "Unique slug/ID of the meeting"},
                },
                "required": ["meeting_slug"],
            },
        ),
        Tool(
            name="create_meeting",
            description="Create a new meeting record.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Meeting title (required)"},
                    "meeting_date": {"type": "string", "description": "Meeting date/time (ISO 8601)"},
                    "description": {"type": "string", "description": "Meeting notes/agenda"},
                    "candidate_slug": {"type": "string", "description": "Associated candidate"},
                    "contact_slug": {"type": "string", "description": "Associated contact"},
                    "company_slug": {"type": "string", "description": "Associated company"},
                    "job_slug": {"type": "string", "description": "Associated job"},
                },
                "required": ["title"],
            },
        ),
        Tool(
            name="update_meeting",
            description="Update an existing meeting.",
            inputSchema={
                "type": "object",
                "properties": {
                    "meeting_slug": {"type": "string", "description": "Slug/ID of the meeting to update (required)"},
                    "title": {"type": "string", "description": "Meeting title"},
                    "meeting_date": {"type": "string", "description": "Meeting date/time"},
                    "description": {"type": "string", "description": "Meeting notes/agenda"},
                },
                "required": ["meeting_slug"],
            },
        ),
        Tool(
            name="delete_meeting",
            description="Permanently delete a meeting.",
            inputSchema={
                "type": "object",
                "properties": {
                    "meeting_slug": {"type": "string", "description": "Slug/ID of the meeting to delete"},
                },
                "required": ["meeting_slug"],
            },
        ),
        # Call Logs
        Tool(
            name="list_call_logs",
            description="List all call logs with pagination.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                    "limit": {"type": "integer", "description": "Results per page (default: 25)", "default": 25},
                },
            },
        ),
        Tool(
            name="get_call_log",
            description="Get a specific call log by slug.",
            inputSchema={
                "type": "object",
                "properties": {
                    "call_log_slug": {"type": "string", "description": "Unique slug/ID of the call log"},
                },
                "required": ["call_log_slug"],
            },
        ),
        Tool(
            name="create_call_log",
            description="Create a new call log record.",
            inputSchema={
                "type": "object",
                "properties": {
                    "note": {"type": "string", "description": "Call notes (required)"},
                    "duration": {"type": "integer", "description": "Call duration in seconds"},
                    "candidate_slug": {"type": "string", "description": "Associated candidate"},
                    "contact_slug": {"type": "string", "description": "Associated contact"},
                    "company_slug": {"type": "string", "description": "Associated company"},
                    "job_slug": {"type": "string", "description": "Associated job"},
                },
                "required": ["note"],
            },
        ),
        Tool(
            name="update_call_log",
            description="Update an existing call log.",
            inputSchema={
                "type": "object",
                "properties": {
                    "call_log_slug": {"type": "string", "description": "Slug/ID of the call log to update (required)"},
                    "note": {"type": "string", "description": "Call notes"},
                    "duration": {"type": "integer", "description": "Call duration in seconds"},
                },
                "required": ["call_log_slug"],
            },
        ),
    ]


async def handle_tool(client: RecruitCRMClient, name: str, arguments: dict) -> dict:
    """Handle activity tool calls (notes, tasks, meetings, call logs)."""
    args = arguments.copy()

    # Notes
    if name == "list_notes":
        return await client.list_notes(
            page=args.get("page", 1),
            limit=args.get("limit", 25),
        )
    elif name == "get_note":
        return await client.get_note(args["note_slug"])
    elif name == "create_note":
        return await client.create_note(args)
    elif name == "update_note":
        slug = args.pop("note_slug")
        return await client.update_note(slug, args)
    elif name == "delete_note":
        return await client.delete_note(args["note_slug"])
    elif name == "search_notes":
        page = args.pop("page", 1)
        limit = args.pop("limit", 25)
        return await client.search_notes(args, page=page, limit=limit)

    # Tasks
    elif name == "list_tasks":
        return await client.list_tasks(
            page=args.get("page", 1),
            limit=args.get("limit", 25),
        )
    elif name == "get_task":
        return await client.get_task(args["task_slug"])
    elif name == "create_task":
        return await client.create_task(args)
    elif name == "update_task":
        slug = args.pop("task_slug")
        return await client.update_task(slug, args)
    elif name == "delete_task":
        return await client.delete_task(args["task_slug"])
    elif name == "search_tasks":
        page = args.pop("page", 1)
        limit = args.pop("limit", 25)
        return await client.search_tasks(args, page=page, limit=limit)

    # Meetings
    elif name == "list_meetings":
        return await client.list_meetings(
            page=args.get("page", 1),
            limit=args.get("limit", 25),
        )
    elif name == "get_meeting":
        return await client.get_meeting(args["meeting_slug"])
    elif name == "create_meeting":
        return await client.create_meeting(args)
    elif name == "update_meeting":
        slug = args.pop("meeting_slug")
        return await client.update_meeting(slug, args)
    elif name == "delete_meeting":
        return await client.delete_meeting(args["meeting_slug"])

    # Call Logs
    elif name == "list_call_logs":
        return await client.list_call_logs(
            page=args.get("page", 1),
            limit=args.get("limit", 25),
        )
    elif name == "get_call_log":
        return await client.get_call_log(args["call_log_slug"])
    elif name == "create_call_log":
        return await client.create_call_log(args)
    elif name == "update_call_log":
        slug = args.pop("call_log_slug")
        return await client.update_call_log(slug, args)

    return None
