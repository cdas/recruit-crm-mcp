# CLAUDE.md - Test

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Python MCP (Model Context Protocol) server** that exposes the Recruit CRM REST API as 79 Claude-accessible tools. It runs via stdio and connects to Claude Desktop, allowing conversational management of recruitment workflows.

## Development Commands

```bash
# Install dependencies
pip3 install .

# Run the server directly (for testing)
python3 -m recruit_crm_mcp

# Test with MCP Inspector (interactive UI)
npx @modelcontextprotocol/inspector python3 -m recruit_crm_mcp
```

**Environment:** Requires `RECRUIT_CRM_API_TOKEN` set via the `env` block in `claude_desktop_config.json`.

## Architecture

```
src/recruit_crm_mcp/
  server.py          → MCP stdio entry point; dispatches list_tools / call_tool
  tools/__init__.py  → Aggregates all tool definitions + routes tool calls to domain handlers
  tools/{domain}.py  → One file per domain (candidates, companies, jobs, contacts, deals,
                       activities, hotlists, metadata, webhooks)
  api_client.py      → Single RecruitCRMClient; all HTTP, rate limiting, retries
```

**Request flow:** Claude Desktop → `server.py` → `tools/__init__.py:handle_tool_call()` → `tools/{domain}.py:handle_tool()` → `api_client.py` → `https://api.recruitcrm.io/v1/`

## Key Patterns

**Adding a new tool:**
1. Add an MCP `Tool` object to `get_tools()` in the appropriate `tools/{domain}.py`
2. Add a matching branch in that module's `handle_tool()` function
3. Add the API method to `api_client.py:RecruitCRMClient`
4. The central dispatcher in `tools/__init__.py` picks it up automatically

**Tool module structure:** Every domain module exports two functions:
- `get_tools() → list[Tool]` — defines input JSON schema for Claude
- `handle_tool(client, name, args) → dict | None` — returns `None` if the tool name is not handled by this module; the dispatcher in `tools/__init__.py` iterates all modules and uses the first non-`None` result

**API client:** Uses `httpx` with async throughout. Token bucket rate limiter (60 req/min), exponential backoff retry (3 attempts), raises typed exceptions for 401/404/422/429.

**Search API inconsistency:** Candidate search uses `GET /candidates/search?q=`, while all other entities (companies, contacts, jobs, deals, hotlists) use `POST /{entity}/search` with a JSON body containing filter fields.

**Activities module** (`tools/activities.py`) consolidates four separate Recruit CRM API endpoints: notes (`/notes`), tasks (`/tasks`), meetings (`/meetings`), and call logs (`/calllogs`). These are distinct sub-resources despite being grouped in one module.

**Claude Desktop setup:** See `SETUP.md` for the Claude Desktop `mcpServers` config block.

## Domain Coverage

| Domain | Tools | Module |
|--------|-------|--------|
| Candidates | 17 | `tools/candidates.py` |
| Activities (notes, tasks, meetings, call logs) | 27 | `tools/activities.py` |
| Hotlists | 8 | `tools/hotlists.py` |
| Jobs | 8 | `tools/jobs.py` |
| Deals | 6 | `tools/deals.py` |
| Companies | 6 | `tools/companies.py` |
| Contacts | 6 | `tools/contacts.py` |
| Metadata (users, hiring stages, custom fields) | 4 | `tools/metadata.py` |
| Webhooks | 3 | `tools/webhooks.py` |
