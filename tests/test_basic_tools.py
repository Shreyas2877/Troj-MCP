"""Tests for basic MCP tools."""

import sys
from pathlib import Path

import pytest

# Add src to Python path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from macro_man.utils.exceptions import ValidationError


class TestBasicTools:
    """Test cases for basic MCP tools."""

    def test_add_numbers(self):
        """Test adding two numbers."""
        from macro_man.tools.basic import add_numbers

        result = add_numbers(5, 3)
        assert result == 8

        result = add_numbers(-2, 7)
        assert result == 5

        result = add_numbers(0, 0)
        assert result == 0

    def test_multiply_numbers(self):
        """Test multiplying two numbers."""
        from macro_man.tools.basic import multiply_numbers

        result = multiply_numbers(4, 5)
        assert result == 20

        result = multiply_numbers(-3, 2)
        assert result == -6

        result = multiply_numbers(0, 100)
        assert result == 0

    def test_greet_user(self):
        """Test greeting a user."""
        from macro_man.tools.basic import greet_user

        result = greet_user("Alice")
        assert result == "Hello, Alice! Nice to meet you."

        result = greet_user("  Bob  ")
        assert result == "Hello, Bob! Nice to meet you."

    def test_greet_user_empty_name(self):
        """Test greeting with empty name raises validation error."""
        from macro_man.tools.basic import greet_user

        with pytest.raises(ValidationError) as exc_info:
            greet_user("")

        assert "Name cannot be empty" in str(exc_info.value)
        assert exc_info.value.field == "name"

    def test_greet_user_whitespace_name(self):
        """Test greeting with whitespace-only name raises validation error."""
        from macro_man.tools.basic import greet_user

        with pytest.raises(ValidationError) as exc_info:
            greet_user("   ")

        assert "Name cannot be empty" in str(exc_info.value)

    def test_get_system_info(self):
        """Test getting system information."""
        from macro_man.tools.basic import get_system_info

        info = get_system_info()

        assert isinstance(info, dict)
        assert "platform" in info
        assert "python_version" in info
        assert "architecture" in info
        assert "processor" in info
        assert "timestamp" in info

    def test_echo_message(self):
        """Test echoing a message."""
        from macro_man.tools.basic import echo_message

        result = echo_message("Hello World")
        assert result == "Echo: Hello World"

        result = echo_message("Test message")
        assert result == "Echo: Test message"

    def test_echo_message_empty(self):
        """Test echoing empty message raises validation error."""
        from macro_man.tools.basic import echo_message

        with pytest.raises(ValidationError) as exc_info:
            echo_message("")

        assert "Message cannot be empty" in str(exc_info.value)
        assert exc_info.value.field == "message"
