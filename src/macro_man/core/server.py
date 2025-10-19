"""Main MCP server implementation."""

import structlog
from mcp.server.fastmcp import FastMCP

from ..config import get_settings
from ..tools import register_tools
from ..utils.logging import setup_logging

logger = structlog.get_logger(__name__)


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with all tools."""
    settings = get_settings()

    # Set up logging
    setup_logging()

    # Create MCP server
    mcp = FastMCP(
        host=settings.server_host,
        port=settings.server_port,
        stateless_http=True,
    )

    # Register all tools
    register_tools(mcp)

    logger.info(
        "MCP server created",
        host=settings.server_host,
        port=settings.server_port,
        debug=settings.debug,
    )

    return mcp


def run_server() -> None:
    """Run the MCP server."""
    mcp = create_mcp_server()

    try:
        logger.info("Starting Macro-Man MCP Server...")
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error("Server error", error=str(e), exc_info=True)
        raise
    finally:
        logger.info("Server stopped")


if __name__ == "__main__":
    run_server()
