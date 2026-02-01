import logging
import asyncio
import sys
import ha_mcp_bot.tools as tools
from mcp.server.fastmcp import FastMCP
from ha_mcp_bot.api import get_default_api

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

mcp = FastMCP("HomeAssistantBot")
tools.register_tools(mcp)


async def _run_server_logic():
    try:
        await mcp.run_async() 
    finally:
        logger.info("Shutting down Home Assistant MCP Server...")
        api = get_default_api()
        await api.close()

def main():
    """The LLM entry point."""
    mcp.run()

def dev_run():
    """DEV entry point."""
    try:
        asyncio.run(_run_server_logic())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    dev_run()