#!/usr/bin/env python3
"""
Macro-Man MCP Server Entry Point for Claude Desktop (stdio transport)

This version uses stdio transport which is preferred by Claude Desktop.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from macro_man.core.server import create_mcp_server


def main() -> None:
    """Main entry point for the MCP server with stdio transport."""
    try:
        # Create MCP server
        mcp = create_mcp_server()
        
        # Run with stdio transport for Claude Desktop
        mcp.run(transport="stdio")
        
    except KeyboardInterrupt:
        print("Server shutdown requested by user", file=sys.stderr)
    except Exception as e:
        print(f"Server failed to start: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
