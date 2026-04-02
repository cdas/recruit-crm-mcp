# Testing Guide

## Automated tests (pytest)

Install dev dependencies and run the full test suite:

```bash
pip install ".[dev]"
pytest -v
```

Run a specific file:

```bash
pytest tests/test_tool_schemas.py -v   # fastest: schema validation only
pytest tests/test_api_client.py -v     # HTTP error handling + retry logic
pytest tests/test_rate_limiter.py -v   # token bucket logic
pytest tests/test_dispatcher.py -v     # tool routing + error serialization
```

All tests run without a real API token or network access.

---

## Manual end-to-end testing (MCP Inspector)

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) provides an interactive UI to call tools against a running server.

### Prerequisites

- Node.js 18+ installed
- A valid `RECRUIT_CRM_API_TOKEN`

### Option A — against Docker image

Build the image first (see SETUP.md), then:

```bash
npx @modelcontextprotocol/inspector \
  docker run --rm -i -e RECRUIT_CRM_API_TOKEN=your-token-here recruit-crm-mcp
```

### Option B — against local Python install

```bash
pip install .
RECRUIT_CRM_API_TOKEN=your-token-here \
  npx @modelcontextprotocol/inspector python3 -m recruit_crm_mcp
```

Open http://localhost:5173 in your browser.

---

## Manual test checklist

Work through this list in the MCP Inspector after any significant change.

### Candidates
- [ ] `list_candidates` — returns paginated list
- [ ] `search_candidates` with a name query — returns matching results
- [ ] `create_candidate` — creates a test record
- [ ] `get_candidate` — fetches the record by slug
- [ ] `update_candidate` — modifies a field
- [ ] `delete_candidate` — removes the test record
- [ ] `assign_candidate_to_job` — assigns to an existing job
- [ ] `update_hiring_stage` — moves to a different stage

### Jobs
- [ ] `list_jobs` — returns job list
- [ ] `get_job` — fetches a single job by slug

### Companies
- [ ] `list_companies` — returns company list
- [ ] `search_companies` — returns filtered results

### Activities
- [ ] `create_note` — creates a note on a candidate
- [ ] `list_notes` — lists notes for a candidate
- [ ] `create_task` — creates a task

### Hotlists
- [ ] `list_hotlists` — returns hotlist overview
- [ ] `get_hotlist` — fetches a single hotlist

### Metadata
- [ ] `list_users` — returns CRM users
- [ ] `get_hiring_stages` — returns global hiring stages

### Webhooks
- [ ] `list_subscriptions` — returns current subscriptions

### Error handling
- [ ] Call any tool with a missing required argument — verify error message is clear
- [ ] Call `get_candidate` with an invalid slug — verify 404 is surfaced cleanly
