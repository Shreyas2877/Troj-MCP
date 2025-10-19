"""Integration tests for MCP server functionality."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# Add src to Python path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


class TestMCPIntegration:
    """Integration tests for MCP server."""

    def test_mcp_server_initialization(self):
        """Test that MCP server can be created and initialized."""
        from macro_man.core.server import create_mcp_server

        # Create server
        mcp = create_mcp_server()
        assert mcp is not None

        # Test that tools are registered
        # (We can't directly access tools, but we can verify server creation)
        assert hasattr(mcp, "run")

    def test_mcp_protocol_flow(self):
        """Test complete MCP protocol flow with stdio transport."""
        # Skip in CI environments where stdio transport may not work properly
        if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
            pytest.skip("Skipping stdio integration test in CI environment")

        # Get the project root directory (parent of tests directory)
        project_root = Path(__file__).parent.parent
        main_stdio_path = project_root / "main_stdio.py"

        # Check if main_stdio.py exists
        if not main_stdio_path.exists():
            pytest.skip("main_stdio.py not found - skipping stdio integration test")

        # Start the MCP server process
        process = subprocess.Popen(
            ["python", str(main_stdio_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(project_root),
        )

        try:
            # Step 1: Initialize
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"},
                },
                "id": 1,
            }

            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()

            # Read response
            response_line = process.stdout.readline()
            assert response_line
            response = json.loads(response_line.strip())
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "result" in response

            # Step 2: List tools
            tools_request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 2,
            }

            process.stdin.write(json.dumps(tools_request) + "\n")
            process.stdin.flush()

            # Read response
            response_line = process.stdout.readline()
            assert response_line
            response = json.loads(response_line.strip())
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 2
            assert "result" in response
            assert "tools" in response["result"]

            # Verify we have expected tools
            tools = response["result"]["tools"]
            tool_names = [tool["name"] for tool in tools]
            assert "_add_numbers" in tool_names
            assert "_multiply_numbers" in tool_names
            assert "_greet_user" in tool_names

            # Step 3: Call a tool
            call_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "_add_numbers", "arguments": {"a": 5, "b": 3}},
                "id": 3,
            }

            process.stdin.write(json.dumps(call_request) + "\n")
            process.stdin.flush()

            # Read response
            response_line = process.stdout.readline()
            assert response_line
            response = json.loads(response_line.strip())
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 3
            assert "result" in response
            assert "content" in response["result"]

            # Verify the result
            content = response["result"]["content"]
            assert len(content) > 0
            assert content[0]["type"] == "text"
            assert content[0]["text"] == "8.0"

        finally:
            # Clean up
            process.stdin.close()
            process.terminate()
            process.wait()

    def test_tool_error_handling(self):
        """Test that tools handle errors properly."""
        # Skip in CI environments where stdio transport may not work properly
        if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
            pytest.skip("Skipping stdio integration test in CI environment")

        # Get the project root directory (parent of tests directory)
        project_root = Path(__file__).parent.parent
        main_stdio_path = project_root / "main_stdio.py"

        # Check if main_stdio.py exists
        if not main_stdio_path.exists():
            pytest.skip("main_stdio.py not found - skipping stdio integration test")

        # Start the MCP server process
        process = subprocess.Popen(
            ["python", str(main_stdio_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(project_root),
        )

        try:
            # Initialize
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"},
                },
                "id": 1,
            }

            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            process.stdout.readline()  # Consume init response

            # Test error case - call greet_user with empty name
            call_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "greet_user", "arguments": {"name": ""}},
                "id": 2,
            }

            process.stdin.write(json.dumps(call_request) + "\n")
            process.stdin.flush()

            # Read response
            response_line = process.stdout.readline()
            assert response_line
            response = json.loads(response_line.strip())

            # Should be an error response
            assert "error" in response or response["result"]["isError"] is True

        finally:
            # Clean up
            process.stdin.close()
            process.terminate()
            process.wait()
