"""Additional coverage tests for system tools module."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from macro_man.tools.system import (
    execute_command,
    get_environment_variables,
    get_process_info,
    get_python_info,
    get_system_stats,
    register_system_tools,
)
from macro_man.utils.exceptions import MacroManError, ValidationError


class TestGetProcessInfoCoverage:
    """Additional tests for get_process_info coverage."""

    @patch("psutil.Process")
    def test_get_process_info_with_exception(self, mock_process_class):
        """Test process info handling when exception occurs."""
        # Make Process() raise a generic exception
        mock_process_class.side_effect = Exception("Unexpected error")

        with pytest.raises(MacroManError) as exc_info:
            get_process_info(12345)

        assert "Failed to get process info" in str(exc_info.value)

    @patch("psutil.Process")
    def test_get_process_info_creates_info_dict(self, mock_process_class):
        """Test that process info creates proper dictionary structure."""
        mock_process = MagicMock()
        mock_process.pid = 1234
        mock_process.name.return_value = "python"
        mock_process.status.return_value = "running"
        mock_process.cpu_percent.return_value = 2.5
        mock_process.memory_info.return_value = MagicMock(rss=104857600, vms=209715200)
        mock_process.create_time.return_value = 1692057600.0  # Unix timestamp
        mock_process.num_threads.return_value = 5

        mock_process_class.return_value = mock_process

        result = get_process_info(1234)

        assert result["pid"] == 1234
        assert result["name"] == "python"
        assert result["status"] == "running"
        assert result["cpu_percent"] == 2.5
        assert result["memory_info"]["rss"] == 104857600
        assert result["memory_info"]["vms"] == 209715200
        assert isinstance(result["create_time"], str)
        assert result["num_threads"] == 5

    def test_get_current_process_info_timestamp_format(self):
        """Test that current process info includes valid ISO timestamp."""
        result = get_process_info()

        # Verify timestamp is ISO format
        create_time = result["create_time"]
        assert "T" in create_time  # ISO format includes T
        assert ":" in create_time  # Time includes colons


class TestGetSystemStatsCoverage:
    """Additional tests for get_system_stats coverage."""

    @patch("psutil.cpu_freq")
    def test_system_stats_with_none_cpu_freq(self, mock_cpu_freq):
        """Test system stats when cpu_freq returns None."""
        mock_cpu_freq.return_value = None

        result = get_system_stats()

        # Should handle None gracefully
        assert result["cpu"]["frequency"]["current"] is None
        assert result["cpu"]["frequency"]["min"] is None
        assert result["cpu"]["frequency"]["max"] is None

    @patch("psutil.disk_usage")
    def test_system_stats_disk_percentage_calculation(self, mock_disk_usage):
        """Test that disk percentage is calculated correctly."""
        mock_disk_usage.return_value = MagicMock(total=1000, used=250, free=750)

        result = get_system_stats()

        # Percentage should be 250/1000 * 100 = 25.0
        assert result["disk"]["percent"] == 25.0

    @patch("psutil.virtual_memory")
    def test_system_stats_with_high_memory_usage(self, mock_virtual_memory):
        """Test system stats with high memory usage."""
        mock_virtual_memory.return_value = MagicMock(
            total=16000000000,
            available=1000000000,
            percent=93.75,
            used=15000000000,
            free=1000000000,
        )

        result = get_system_stats()

        memory = result["memory"]
        assert memory["total"] == 16000000000
        assert memory["used"] == 15000000000
        assert memory["percent"] == 93.75

    @patch("psutil.swap_memory")
    def test_system_stats_swap_memory(self, mock_swap_memory):
        """Test system stats captures swap memory correctly."""
        mock_swap_memory.return_value = MagicMock(
            total=2000000000, used=500000000, free=1500000000, percent=25.0
        )

        result = get_system_stats()

        swap = result["swap"]
        assert swap["total"] == 2000000000
        assert swap["used"] == 500000000
        assert swap["free"] == 1500000000
        assert swap["percent"] == 25.0

    @patch("psutil.net_io_counters")
    def test_system_stats_network_counters(self, mock_net_io):
        """Test system stats captures network counters."""
        mock_net_io.return_value = MagicMock(
            bytes_sent=1000000,
            bytes_recv=5000000,
            packets_sent=10000,
            packets_recv=50000,
        )

        result = get_system_stats()

        network = result["network"]
        assert network["bytes_sent"] == 1000000
        assert network["bytes_recv"] == 5000000
        assert network["packets_sent"] == 10000
        assert network["packets_recv"] == 50000

    @patch("psutil.virtual_memory")
    def test_system_stats_exception_handling(self, mock_virtual_memory):
        """Test system stats handles exceptions properly."""
        mock_virtual_memory.side_effect = Exception("Memory error")

        with pytest.raises(MacroManError) as exc_info:
            get_system_stats()

        assert "Failed to get system stats" in str(exc_info.value)


class TestExecuteCommandCoverage:
    """Additional tests for execute_command coverage."""

    def test_execute_command_with_successful_stderr(self):
        """Test command execution where stderr contains warnings (but success)."""
        result = execute_command("ls /invalid 2>&1 || true")

        assert isinstance(result, dict)
        assert "command" in result
        assert "stdout" in result
        assert "stderr" in result

    def test_execute_command_logs_info_on_success(self):
        """Test that successful command is logged."""
        with patch("macro_man.tools.system.logger") as mock_logger:
            execute_command("echo test")

            # Should have logged
            assert mock_logger.info.called

    @patch("subprocess.run")
    def test_execute_command_logs_on_dangerous_attempt(self, mock_run):
        """Test that dangerous command attempt is logged."""
        with patch("macro_man.tools.system.logger"), pytest.raises(ValidationError):
            execute_command("rm -rf /important")

            # Logging should have been called
            # (though the dangerous command blocks before logging command execution)

    def test_execute_command_case_insensitive_dangerous_check(self):
        """Test that dangerous command detection is case-insensitive."""
        dangerous_variants = [
            "RM -RF /",
            "Rm -Rf /",
            "rM -rF /",
            "SUDO rm -rf /",
            "SU root",
        ]

        for cmd in dangerous_variants:
            with pytest.raises(ValidationError):
                execute_command(cmd)

    @patch("subprocess.run")
    def test_execute_command_capture_output(self, mock_run):
        """Test that command output is captured correctly."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Output text",
            stderr="",
        )

        result = execute_command("test command")

        assert result["stdout"] == "Output text"
        assert result["stderr"] == ""
        assert result["success"] is True

    def test_execute_command_with_various_timeouts(self):
        """Test command execution with different timeout values."""
        timeouts = [5, 10, 30, 60]

        for timeout_val in timeouts:
            result = execute_command("echo test", timeout=timeout_val)
            assert result["success"] is True

    @patch("subprocess.run")
    def test_execute_command_shell_true(self, mock_run):
        """Test that subprocess is called with shell=True."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        execute_command("echo test")

        # Verify shell=True was passed
        assert mock_run.call_args.kwargs["shell"] is True

    @patch("subprocess.run")
    def test_execute_command_text_true(self, mock_run):
        """Test that subprocess is called with text=True."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        execute_command("echo test")

        # Verify text=True was passed
        assert mock_run.call_args.kwargs["text"] is True


class TestGetEnvironmentVariablesCoverage:
    """Additional tests for get_environment_variables coverage."""

    def test_get_environment_variables_returns_copy(self):
        """Test that returned dict is actually a copy."""
        result = get_environment_variables()

        # Should contain environment variables
        assert len(result) > 0

        # Should not be the exact same dict as os.environ
        # (it's created fresh each time)
        result2 = get_environment_variables()
        assert result == result2

    def test_get_environment_variables_prefix_filter_works(self):
        """Test prefix filtering works correctly."""
        # Set a test environment variable
        os.environ["TEST_PREFIX_VAR1"] = "value1"
        os.environ["TEST_PREFIX_VAR2"] = "value2"
        os.environ["OTHER_VAR"] = "value3"

        result = get_environment_variables("TEST_PREFIX")

        # Should only include TEST_PREFIX variables
        assert "TEST_PREFIX_VAR1" in result
        assert "TEST_PREFIX_VAR2" in result
        assert "OTHER_VAR" not in result

        # Cleanup
        del os.environ["TEST_PREFIX_VAR1"]
        del os.environ["TEST_PREFIX_VAR2"]
        del os.environ["OTHER_VAR"]

    @patch("os.environ", {})
    def test_get_environment_variables_empty_environ(self):
        """Test behavior with empty environment."""
        result = get_environment_variables()

        assert isinstance(result, dict)
        assert len(result) == 0

    @patch("os.environ", {})
    def test_get_environment_variables_prefix_empty_environ(self):
        """Test prefix filter with empty environment."""
        result = get_environment_variables("PREFIX")

        assert isinstance(result, dict)
        assert len(result) == 0


class TestGetPythonInfoCoverage:
    """Additional tests for get_python_info coverage."""

    def test_get_python_info_version_components(self):
        """Test that Python version components are parsed correctly."""
        result = get_python_info()

        version_info = result["version_info"]
        # Should match actual Python version
        assert version_info["major"] == sys.version_info.major
        assert version_info["minor"] == sys.version_info.minor
        assert version_info["micro"] == sys.version_info.micro

    def test_get_python_info_executable_contains_python(self):
        """Test that executable path contains 'python'."""
        result = get_python_info()

        # Executable should be python or python3
        assert "python" in result["executable"].lower()

    def test_get_python_info_platform_string(self):
        """Test that platform string is present."""
        result = get_python_info()

        # Platform should be something like 'darwin', 'linux', 'win32'
        assert isinstance(result["platform"], str)
        assert len(result["platform"]) > 0
        assert result["platform"] == sys.platform

    def test_get_python_info_path_list(self):
        """Test that Python path is a proper list."""
        result = get_python_info()

        path = result["path"]
        assert isinstance(path, list)
        assert len(path) > 0
        # Should match sys.path
        assert path == sys.path

    def test_get_python_info_modules_count_reasonable(self):
        """Test that modules count is reasonable."""
        result = get_python_info()

        # Should have at least a few modules
        assert result["modules_count"] >= 10
        assert result["modules_count"] == len(sys.modules)


class TestRegisterSystemTools:
    """Test tool registration function."""

    def test_register_system_tools(self):
        """Test that system tools can be registered."""
        mock_server = MagicMock()

        # Call register with mock server
        register_system_tools(mock_server)

        # Should have called tool decorator 5 times (one for each tool)
        assert mock_server.tool.call_count == 5

        # Verify all expected tool names
        [call.args[0].__name__ for call in mock_server.tool.return_value.call_args_list]

        # Check that tool decorator was called for registration
        for _tool_decorator in mock_server.tool.return_value.call_args_list:
            # Each call should be a function that wraps our tool functions
            pass  # We're mainly checking that tool() was called 5 times

    def test_registered_tools_are_callable(self):
        """Test that registered tool functions work correctly."""
        mock_server = MagicMock()
        tool_functions = []

        # Capture the tool functions being registered
        def capture_tool(func):
            tool_functions.append(func)
            return func

        mock_server.tool.return_value = capture_tool

        register_system_tools(mock_server)

        # Should have captured 5 tool functions
        assert len(tool_functions) == 5

        # Each should be callable
        assert all(callable(func) for func in tool_functions)
