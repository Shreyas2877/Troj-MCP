"""Simple tests for basic MCP tools."""

import sys
from pathlib import Path
import pytest

# Add src to Python path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def test_add_numbers():
    """Test adding two numbers."""
    # Import the function directly from the module
    import macro_man.tools.basic as basic_module
    
    # Test the add_numbers function
    result = basic_module.add_numbers(5, 3)
    assert result == 8
    
    result = basic_module.add_numbers(-2, 7)
    assert result == 5
    
    result = basic_module.add_numbers(0, 0)
    assert result == 0


def test_multiply_numbers():
    """Test multiplying two numbers."""
    import macro_man.tools.basic as basic_module
    
    result = basic_module.multiply_numbers(4, 5)
    assert result == 20
    
    result = basic_module.multiply_numbers(-3, 2)
    assert result == -6
    
    result = basic_module.multiply_numbers(0, 100)
    assert result == 0


def test_greet_user():
    """Test greeting a user."""
    import macro_man.tools.basic as basic_module
    
    result = basic_module.greet_user("Alice")
    assert result == "Hello, Alice! Nice to meet you."
    
    result = basic_module.greet_user("  Bob  ")
    assert result == "Hello, Bob! Nice to meet you."


def test_greet_user_empty_name():
    """Test greeting with empty name raises validation error."""
    import macro_man.tools.basic as basic_module
    from macro_man.utils.exceptions import ValidationError
    
    with pytest.raises(ValidationError) as exc_info:
        basic_module.greet_user("")
    
    assert "Name cannot be empty" in str(exc_info.value)
    assert exc_info.value.field == "name"


def test_echo_message():
    """Test echoing a message."""
    import macro_man.tools.basic as basic_module
    
    result = basic_module.echo_message("Hello World")
    assert result == "Echo: Hello World"
    
    result = basic_module.echo_message("Test message")
    assert result == "Echo: Test message"


def test_echo_message_empty():
    """Test echoing empty message raises validation error."""
    import macro_man.tools.basic as basic_module
    from macro_man.utils.exceptions import ValidationError
    
    with pytest.raises(ValidationError) as exc_info:
        basic_module.echo_message("")
    
    assert "Message cannot be empty" in str(exc_info.value)
    assert exc_info.value.field == "message"


def test_get_system_info():
    """Test getting system information."""
    import macro_man.tools.basic as basic_module
    
    info = basic_module.get_system_info()
    
    assert isinstance(info, dict)
    assert "platform" in info
    assert "python_version" in info
    assert "architecture" in info
    assert "processor" in info
    assert "timestamp" in info
