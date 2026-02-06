import logging
import sys
from contextlib import asynccontextmanager
from mcp.server.fastmcp import FastMCP
from ha_mcp_bot.api import get_default_api
from ha_mcp_bot.config import config
import ha_mcp_bot.tools as tools


logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

config.validate()

@asynccontextmanager
async def app_lifespan(server: FastMCP):
    """
    Everything before 'yield' happens on startup.
    Everything after 'yield' happens on shutdown.
    """
    try:
        yield 
    finally:
        logger.info("Shutting down Home Assistant MCP Server...")
        api = get_default_api()
        await api.close()

app = FastMCP(
    name="HomeAssistantBot",
    host=config.HOST,
    port=config.PORT,
    debug=config.DEBUG,
    streamable_http_path="/",
    lifespan=app_lifespan
)

tools.register_tools(app)


def main() -> int:
    try:
        logger.info("Starting %s on %s:%s", app.name, config.HOST, config.PORT)
        app.run(transport=config.TRANSPORT)
        return 0
    except Exception:
        logger.exception("Server error")
        return 1

if __name__ == "__main__":
    sys.exit(main())