"""MCP tools for Macro-Man server."""

from .basic import register_basic_tools
from .calendar import register_calendar_tools
from .email import register_email_tools
from .file_ops import register_file_tools
from .system import register_system_tools

__all__ = ["register_tools"]


def register_tools(mcp_server) -> None:
    """Register all available tools with the MCP server."""
    register_basic_tools(mcp_server)
    register_file_tools(mcp_server)
    register_system_tools(mcp_server)
    register_email_tools(mcp_server)
    register_calendar_tools(mcp_server)
