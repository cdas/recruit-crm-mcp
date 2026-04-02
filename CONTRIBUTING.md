# Contributing

## Development setup

```bash
git clone https://github.com/cdas/recruit-crm-mcp
cd recruit-crm-mcp
pip install -e .
```

Test interactively with the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python3 -m recruit_crm_mcp
```

You'll need a `RECRUIT_CRM_API_TOKEN` environment variable set (copy `.env.example` to `.env` and fill it in).

## Adding a new tool

1. Add an MCP `Tool` object to `get_tools()` in the appropriate `src/recruit_crm_mcp/tools/{domain}.py`
2. Add a matching branch in that module's `handle_tool()` function
3. Add the API method to `src/recruit_crm_mcp/api_client.py`
4. The central dispatcher in `src/recruit_crm_mcp/tools/__init__.py` picks it up automatically — no changes needed there

Every domain module exports exactly two functions:
- `get_tools() → list[Tool]`
- `handle_tool(client, name, args) → dict | None` — returns `None` if the tool name is not owned by this module

## Pull requests

- Keep PRs focused on a single change
- Match the code style of the surrounding file (snake_case, typed variables)
- No automated test suite — verify manually with the MCP Inspector before submitting
