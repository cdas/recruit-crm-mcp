# Setup Guide

This guide connects the Recruit CRM MCP server to Claude Desktop using Docker. No Python installation required.

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

---

## Step 1 — Clone the repository

```bash
git clone https://github.com/cdas/recruit-crm-mcp.git
cd recruit-crm-mcp
```

---

## Step 2 — Build the Docker image

```bash
docker build -t recruit-crm-mcp .
```

This runs once. Rebuild only when you update to a newer version.

---

## Step 3 — Get your API token

Log into Recruit CRM → **Admin Settings** → **Account Management** → **API Token**

Copy the token — you'll paste it into the config in the next step.

> Requires Recruit CRM Business Plan or higher.

---

## Step 4 — Configure Claude Desktop

Open Claude Desktop → **Settings** → **Developer** → **Edit Config**.

Add the `recruit-crm` block inside `mcpServers`, replacing `your-token-here` with your actual token:

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

> **Windows path to config file:** `%APPDATA%\Claude\claude_desktop_config.json`
> **Mac path to config file:** `~/Library/Application Support/Claude/claude_desktop_config.json`

---

## Step 5 — Restart Claude Desktop

Fully quit Claude Desktop — don't just close the window.

- **Mac:** Right-click the Dock icon → **Quit**
- **Windows:** Right-click the tray icon → **Quit**

Then reopen it.

---

## Step 6 — Verify

In Claude Desktop, ask:

> "List all open jobs in Recruit CRM"

If everything is working, Claude will return your jobs. You should also see a hammer icon near the chat input indicating MCP tools are active.

---

## Updating to a newer version

```bash
git pull
docker build -t recruit-crm-mcp .
```

Restart Claude Desktop after rebuilding.

---

## Troubleshooting

**Hammer icon missing / Claude doesn't have the tools**
- Make sure Docker Desktop is running before opening Claude Desktop
- Verify the JSON in your config file is valid (no trailing commas, correct brackets)
- Fully quit and restart Claude Desktop — closing the window is not enough

**"Configuration error: API token is required"**
The token is missing or not being passed through. Double-check that `RECRUIT_CRM_API_TOKEN=your-token-here` in the `args` list contains your actual token, not the placeholder.

**"Configuration error: API token is invalid or expired"**
The token value is wrong. Re-copy it from Recruit CRM → Admin Settings → Account Management → API Token.

**`docker: command not found`**
Docker Desktop is not installed or not running. Install it from [docker.com](https://www.docker.com/products/docker-desktop/) and make sure it's started before opening Claude Desktop.

**`Cannot connect to the Docker daemon`**
Docker Desktop is installed but not running. Open Docker Desktop and wait for it to fully start, then restart Claude Desktop.

**Updating your API token**
Edit the `args` list in `claude_desktop_config.json`, replace the token value, save, and restart Claude Desktop.
