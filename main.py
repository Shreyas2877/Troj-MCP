#!/usr/bin/env python3
"""
Macro-Man MCP Server Entry Point

This is the main entry point for the Macro-Man MCP server.
Run this script to start the server.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from macro_man.core.server import run_server


def main() -> None:
    """Main entry point for the MCP server."""
    try:
        run_server()
    except KeyboardInterrupt:
        print("\nServer shutdown requested by user")
    except Exception as e:
        print(f"Server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
