import logging
import asyncio
import ha_mcp_bot.tools as tools
from mcp.server.fastmcp import FastMCP
from ha_mcp_bot.api import get_default_api

logger = logging.getLogger(__name__)

mcp = FastMCP("HomeAssistantBot")
tools.register_tools(mcp)


async def main():
    try:
        await mcp.run_async()
    finally:
        logger.info("Shutting down Home Assistant MCP Server...")
        api = get_default_api()
        await api.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass