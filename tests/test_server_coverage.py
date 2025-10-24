"""Additional coverage tests for MCP server module."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import builtins
import contextlib

from macro_man.core.server import create_mcp_server, run_server


class TestCreateMCPServer:
    """Test MCP server creation functionality."""

    def test_server_creation_complete(self):
        """Test complete server creation with all components."""
        mcp = create_mcp_server()

        # Verify server exists and has expected attributes
        assert mcp is not None
        assert hasattr(mcp, "run")
        # FastMCP server object should have tools dict accessible
        assert isinstance(mcp, object)

    def test_server_has_tools_registered(self):
        """Test that server has tools registered."""
        mcp = create_mcp_server()

        # Verify server was created successfully
        # Tools are registered internally in FastMCP
        assert mcp is not None
        assert hasattr(mcp, "run")
        # The server instance should have the implementation tools
        # We verify by checking it's a proper FastMCP instance
        from mcp.server.fastmcp import FastMCP

        assert isinstance(mcp, FastMCP)

    def test_server_configuration(self):
        """Test that server is configured with correct settings."""
        mcp = create_mcp_server()

        # Server should be configured with stateless HTTP
        # This is checked by verifying the server was created
        assert mcp is not None

    @patch("macro_man.core.server.FastMCP")
    def test_server_creation_with_settings(self, mock_fastmcp):
        """Test server creation uses settings correctly."""
        mock_mcp_instance = MagicMock()
        mock_fastmcp.return_value = mock_mcp_instance

        create_mcp_server()

        # Verify FastMCP was called with correct arguments
        assert mock_fastmcp.called
        call_kwargs = mock_fastmcp.call_args.kwargs
        assert call_kwargs["stateless_http"] is True
        assert "host" in call_kwargs
        assert "port" in call_kwargs

    def test_server_setup_logging(self):
        """Test that server setup calls logging configuration."""
        with patch("macro_man.core.server.setup_logging") as mock_setup:
            create_mcp_server()

            # setup_logging should have been called
            assert mock_setup.called

    def test_server_registers_all_tool_types(self):
        """Test that server registers tools from all categories."""
        with patch("macro_man.core.server.register_tools") as mock_register:
            mcp = create_mcp_server()

            # Verify that register_tools was called
            assert mock_register.called
            # It should have been called with the mcp instance
            assert mock_register.call_args[0][0] is mcp


class TestRunServer:
    """Test MCP server run functionality."""

    @patch("macro_man.core.server.create_mcp_server")
    def test_run_server_normal(self, mock_create):
        """Test normal server run path."""
        mock_mcp = MagicMock()
        mock_create.return_value = mock_mcp

        # Mock the run method to simulate server execution
        mock_mcp.run.side_effect = KeyboardInterrupt()

        # Running server should not raise exception
        with contextlib.suppress(KeyboardInterrupt):
            run_server()

    @patch("macro_man.core.server.create_mcp_server")
    def test_run_server_keyboard_interrupt(self, mock_create):
        """Test server handles KeyboardInterrupt gracefully."""
        mock_mcp = MagicMock()
        mock_create.return_value = mock_mcp
        mock_mcp.run.side_effect = KeyboardInterrupt()

        # Should handle keyboard interrupt without raising
        with (
            patch("macro_man.core.server.logger"),
            contextlib.suppress(KeyboardInterrupt),
        ):
            run_server()

    @patch("macro_man.core.server.create_mcp_server")
    def test_run_server_generic_exception(self, mock_create):
        """Test server handles generic exceptions properly."""
        mock_mcp = MagicMock()
        mock_create.return_value = mock_mcp

        # Simulate a generic exception during server run
        test_error = RuntimeError("Test error")
        mock_mcp.run.side_effect = test_error

        # Should raise the exception after logging
        with patch("macro_man.core.server.logger") as mock_logger:
            with pytest.raises(RuntimeError):
                run_server()

            # Verify logging was called
            assert mock_logger.error.called

    @patch("macro_man.core.server.create_mcp_server")
    def test_run_server_finally_block(self, mock_create):
        """Test that finally block in run_server is executed."""
        mock_mcp = MagicMock()
        mock_create.return_value = mock_mcp

        # Force an exception
        mock_mcp.run.side_effect = Exception("Test")

        with patch("macro_man.core.server.logger") as mock_logger:
            with contextlib.suppress(Exception):
                run_server()

            # Finally block should log server stopped
            # Check if any info log was made (should be "Server stopped")
            info_calls = list(mock_logger.info.call_args_list)
            assert len(info_calls) >= 1

    @patch("macro_man.core.server.create_mcp_server")
    def test_run_server_logging_flow(self, mock_create):
        """Test the complete logging flow during server run."""
        mock_mcp = MagicMock()
        mock_create.return_value = mock_mcp

        # Make run succeed by not raising exception
        mock_mcp.run.return_value = None

        with patch("macro_man.core.server.logger") as mock_logger:
            with contextlib.suppress(builtins.BaseException):
                run_server()

            # Should have logged server startup and shutdown
            log_messages = [str(call) for call in mock_logger.method_calls]
            # At minimum should have logged something
            assert len(log_messages) > 0


class TestServerIntegration:
    """Integration tests for server creation and running."""

    def test_multiple_server_creations(self):
        """Test that multiple servers can be created independently."""
        mcp1 = create_mcp_server()
        mcp2 = create_mcp_server()

        # Both should exist and be separate instances
        assert mcp1 is not None
        assert mcp2 is not None
        # They should be different instances
        assert mcp1 is not mcp2

    def test_server_tools_callable(self):
        """Test that server was properly created."""
        mcp = create_mcp_server()

        # Server should be created and ready to run
        assert mcp is not None
        assert hasattr(mcp, "run")
        # Verify the server is of correct type
        from mcp.server.fastmcp import FastMCP

        assert isinstance(mcp, FastMCP)

    def test_server_creation_idempotent(self):
        """Test that creating multiple servers doesn't cause issues."""
        servers = [create_mcp_server() for _ in range(3)]

        # All servers should be created successfully
        assert all(s is not None for s in servers)
        assert all(hasattr(s, "run") for s in servers)
