"""Recruit CRM MCP Server."""

from __future__ import annotations

import asyncio
import logging

from dotenv import load_dotenv
load_dotenv()  # loads .env from cwd; no-ops if file absent

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import ListToolsResult

from .api_client import RecruitCRMClient, RecruitCRMError
from .tools import get_tools, handle_tool_call

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Create server instance
server = Server("recruit-crm")

# Global client instance
_client: RecruitCRMClient | None = None


def get_client() -> RecruitCRMClient:
    """Get or create the API client."""
    global _client
    if _client is None:
        _client = RecruitCRMClient()
    return _client


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List all available tools."""
    return ListToolsResult(tools=get_tools())


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list:
    """Handle tool calls."""
    try:
        client = get_client()
        return await handle_tool_call(client, name, arguments)
    except RecruitCRMError as e:
        logger.error(f"Recruit CRM API error: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Error handling tool call: {e}")
        raise


async def run_server():
    """Run the MCP server."""
    import sys
    try:
        get_client()
    except RecruitCRMError as e:
        print(f"Configuration error: {e.message}", file=sys.stderr)
        raise SystemExit(1)
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    finally:
        if _client is not None:
            await _client.close()


def main():
    """Main entry point."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
