# Recruit CRM MCP Server

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![MCP](https://img.shields.io/badge/MCP-1.0%2B-purple)

An MCP (Model Context Protocol) server that connects Claude Desktop with the Recruit CRM API — 79 tools covering candidates, jobs, companies, contacts, deals, notes, tasks, meetings, and more.

## Quick start

```bash
git clone https://github.com/cdas/recruit-crm-mcp.git
cd recruit-crm-mcp
docker build -t recruit-crm-mcp .
```

Add to your Claude Desktop config (`Settings → Developer → Edit Config`):

```json
{
  "mcpServers": {
    "recruit-crm": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "RECRUIT_CRM_API_TOKEN=your-token-here",
        "recruit-crm-mcp"
      ]
    }
  }
}
```

Restart Claude Desktop. See [SETUP.md](SETUP.md) for the full guide including how to get your API token and troubleshooting.

## Features

- **79 MCP Tools** covering the entire Recruit CRM API
- **Rate limiting** with automatic retry (60 requests/minute)
- **Full CRUD** for all entities
- **Pipeline management** for candidate-job assignments
- **Activity tracking** via notes, tasks, meetings, and call logs

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Recruit CRM Business Plan or higher (required for API access)

## Available Tools (79 total)

### Candidates (17 tools)
| Tool | Description |
|------|-------------|
| `list_candidates` | List all candidates with pagination |
| `search_candidates` | Search candidates by query |
| `get_candidate` | Get candidate details |
| `create_candidate` | Create new candidate |
| `update_candidate` | Update candidate info |
| `delete_candidate` | Delete candidate |
| `assign_candidate_to_job` | Add candidate to job pipeline |
| `unassign_candidate_from_job` | Remove from job pipeline |
| `update_hiring_stage` | Move candidate to different stage |
| `get_candidate_history` | Get hiring stage history |
| `get_candidate_jobs` | Get jobs candidate is assigned to |
| `get_job_candidates` | Get all candidates in a job pipeline |
| `pitch_candidate` | Pitch candidate to a contact |
| `get_candidate_pitches` | Get pitch history |
| `get_offlimit_candidates` | Get off-limit candidates |
| `get_candidate_questions` | Get screening Q&A |
| `update_candidate_visibility` | Control client visibility |

### Companies (6 tools)
`list_companies`, `get_company`, `create_company`, `update_company`, `delete_company`, `search_companies`

### Contacts (6 tools)
`list_contacts`, `get_contact`, `create_contact`, `update_contact`, `delete_contact`, `search_contacts`

### Jobs (8 tools)
`list_jobs`, `get_job`, `create_job`, `update_job`, `delete_job`, `search_jobs`, `get_job_associated_fields`, `update_job_associated_fields`

### Deals (6 tools)
`list_deals`, `get_deal`, `create_deal`, `update_deal`, `delete_deal`, `search_deals`

### Notes (6 tools)
`list_notes`, `get_note`, `create_note`, `update_note`, `delete_note`, `search_notes`

### Tasks (6 tools)
`list_tasks`, `get_task`, `create_task`, `update_task`, `delete_task`, `search_tasks`

### Meetings (5 tools)
`list_meetings`, `get_meeting`, `create_meeting`, `update_meeting`, `delete_meeting`

### Call Logs (4 tools)
`list_call_logs`, `get_call_log`, `create_call_log`, `update_call_log`

### Hotlists (8 tools)
`list_hotlists`, `get_hotlist`, `create_hotlist`, `update_hotlist`, `delete_hotlist`, `add_record_to_hotlist`, `remove_record_from_hotlist`, `search_hotlists`

### Metadata (4 tools)
`list_users`, `get_hiring_stages`, `get_job_hiring_stages`, `get_custom_fields`

### Webhooks (3 tools)
`list_subscriptions`, `create_subscription`, `delete_subscription`

## Rate limits

- 60 requests per minute per API token
- Automatic retry with exponential backoff on 429 responses

## Error handling

| Code | Meaning |
|------|---------|
| `401` | Invalid or expired API token |
| `404` | Resource not found |
| `422` | Validation error (details included) |
| `429` | Rate limit — auto-retried |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

See [SECURITY.md](SECURITY.md) for the security policy and how to report vulnerabilities.

## License

MIT
