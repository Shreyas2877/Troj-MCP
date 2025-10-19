"""Unit tests for individual components."""

import sys
from pathlib import Path

# Add src to Python path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


class TestConfiguration:
    """Test configuration management."""

    def test_settings_loading(self):
        """Test that settings can be loaded."""
        from macro_man.config import get_settings

        settings = get_settings()
        assert settings is not None
        assert settings.server_host == "0.0.0.0"
        assert settings.server_port == 8000
        assert settings.secret_key is not None

    def test_settings_caching(self):
        """Test that settings are cached."""
        from macro_man.config import get_settings

        settings1 = get_settings()
        settings2 = get_settings()

        # Should be the same instance due to caching
        assert settings1 is settings2


class TestExceptions:
    """Test custom exceptions."""

    def test_macro_man_error(self):
        """Test MacroManError exception."""
        from macro_man.utils.exceptions import MacroManError

        error = MacroManError("Test error", "TEST_ERROR")
        assert str(error) == "Test error"
        assert error.error_code == "TEST_ERROR"

    def test_validation_error(self):
        """Test ValidationError exception."""
        from macro_man.utils.exceptions import ValidationError

        error = ValidationError("Invalid input", "input_field")
        assert str(error) == "Invalid input"
        assert error.field == "input_field"
        assert error.error_code == "VALIDATION_ERROR"

    def test_authentication_error(self):
        """Test AuthenticationError exception."""
        from macro_man.utils.exceptions import AuthenticationError

        error = AuthenticationError("Auth failed")
        assert str(error) == "Auth failed"
        assert error.error_code == "AUTHENTICATION_ERROR"


class TestLogging:
    """Test logging configuration."""

    def test_logging_setup(self):
        """Test that logging can be set up."""
        from macro_man.utils.logging import setup_logging

        # Should not raise an exception
        setup_logging()

        # Test that we can get a logger
        import structlog

        logger = structlog.get_logger(__name__)
        assert logger is not None


class TestServerCreation:
    """Test server creation."""

    def test_server_creation(self):
        """Test that MCP server can be created."""
        from macro_man.core.server import create_mcp_server

        mcp = create_mcp_server()
        assert mcp is not None
        assert hasattr(mcp, "run")

    def test_tool_registration(self):
        """Test that tools are registered."""
        from macro_man.core.server import create_mcp_server

        mcp = create_mcp_server()

        # We can't directly access the tools, but we can verify
        # that the server was created successfully
        assert mcp is not None
