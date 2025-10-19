"""Tests for system utility tools."""

import os
import subprocess
import sys

# Add src to Python path
from pathlib import Path
from unittest.mock import patch

import pytest

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from macro_man.tools.system import (
    execute_command,
    get_environment_variables,
    get_process_info,
    get_python_info,
    get_system_stats,
)
from macro_man.utils.exceptions import MacroManError, ValidationError


class TestGetProcessInfo:
    """Test get_process_info function."""

    def test_get_current_process_info(self):
        """Test getting current process info."""
        result = get_process_info()

        assert isinstance(result, dict)
        assert "pid" in result
        assert "name" in result
        assert "status" in result
        assert "cpu_percent" in result
        assert "memory_info" in result
        assert "create_time" in result
        assert "num_threads" in result

        # Verify data types
        assert isinstance(result["pid"], int)
        assert isinstance(result["name"], str)
        assert isinstance(result["status"], str)
        assert isinstance(result["cpu_percent"], (int, float))
        assert isinstance(result["memory_info"], dict)
        assert "rss" in result["memory_info"]
        assert "vms" in result["memory_info"]
        assert isinstance(result["create_time"], str)
        assert isinstance(result["num_threads"], int)

    def test_get_specific_process_info(self):
        """Test getting info for a specific process."""
        # Get current process PID
        current_pid = os.getpid()
        result = get_process_info(current_pid)

        assert result["pid"] == current_pid
        assert isinstance(result["name"], str)
        assert isinstance(result["status"], str)

    def test_get_nonexistent_process_info(self):
        """Test getting info for non-existent process raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            get_process_info(999999)  # Very unlikely to exist

        assert "Process with PID 999999 not found" in str(exc_info.value)
        assert exc_info.value.field == "pid"


class TestGetSystemStats:
    """Test get_system_stats function."""

    def test_get_system_stats(self):
        """Test getting system statistics."""
        result = get_system_stats()

        assert isinstance(result, dict)
        assert "timestamp" in result
        assert "cpu" in result
        assert "memory" in result
        assert "swap" in result
        assert "disk" in result
        assert "network" in result

        # Verify CPU info
        cpu = result["cpu"]
        assert "percent" in cpu
        assert "count" in cpu
        assert "frequency" in cpu
        assert isinstance(cpu["percent"], (int, float))
        assert isinstance(cpu["count"], int)
        assert isinstance(cpu["frequency"], dict)

        # Verify memory info
        memory = result["memory"]
        assert "total" in memory
        assert "available" in memory
        assert "percent" in memory
        assert "used" in memory
        assert "free" in memory
        assert all(isinstance(v, (int, float)) for v in memory.values())

        # Verify swap info
        swap = result["swap"]
        assert "total" in swap
        assert "used" in swap
        assert "free" in swap
        assert "percent" in swap
        assert all(isinstance(v, (int, float)) for v in swap.values())

        # Verify disk info
        disk = result["disk"]
        assert "total" in disk
        assert "used" in disk
        assert "free" in disk
        assert "percent" in disk
        assert all(isinstance(v, (int, float)) for v in disk.values())

        # Verify network info
        network = result["network"]
        assert "bytes_sent" in network
        assert "bytes_recv" in network
        assert "packets_sent" in network
        assert "packets_recv" in network
        assert all(isinstance(v, (int, float)) for v in network.values())


class TestExecuteCommand:
    """Test execute_command function."""

    def test_execute_simple_command(self):
        """Test executing a simple command."""
        result = execute_command("echo 'Hello World'")

        assert isinstance(result, dict)
        assert result["command"] == "echo 'Hello World'"
        assert result["return_code"] == 0
        assert "Hello World" in result["stdout"]
        assert result["success"] is True
        assert result["stderr"] == ""

    def test_execute_command_with_error(self):
        """Test executing a command that fails."""
        result = execute_command("ls /nonexistent/directory")

        assert isinstance(result, dict)
        assert result["command"] == "ls /nonexistent/directory"
        assert result["return_code"] != 0
        assert result["success"] is False
        assert "stderr" in result

    def test_execute_empty_command(self):
        """Test executing empty command raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            execute_command("")

        assert "Command cannot be empty" in str(exc_info.value)
        assert exc_info.value.field == "command"

    def test_execute_whitespace_only_command(self):
        """Test executing whitespace-only command raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            execute_command("   ")

        assert "Command cannot be empty" in str(exc_info.value)
        assert exc_info.value.field == "command"

    def test_execute_dangerous_command(self):
        """Test executing dangerous command raises ValidationError."""
        dangerous_commands = [
            "rm -rf /",
            "sudo rm -rf /",
            "su root",
            "chmod 777 /",
            "dd if=/dev/zero of=/dev/sda",
            "mkfs.ext4 /dev/sda",
        ]

        for cmd in dangerous_commands:
            with pytest.raises(ValidationError) as exc_info:
                execute_command(cmd)

            assert "Command contains potentially dangerous operations" in str(
                exc_info.value
            )
            assert exc_info.value.field == "command"

    def test_execute_command_with_timeout(self):
        """Test executing command with custom timeout."""
        result = execute_command("echo 'test'", timeout=5)

        assert result["command"] == "echo 'test'"
        assert result["return_code"] == 0
        assert result["success"] is True

    @patch("subprocess.run")
    def test_execute_command_timeout_exception(self, mock_run):
        """Test command timeout raises MacroManError."""
        mock_run.side_effect = subprocess.TimeoutExpired("test", 30)

        with pytest.raises(MacroManError) as exc_info:
            execute_command("sleep 60")

        assert "Command timed out after 30 seconds" in str(exc_info.value)


class TestGetEnvironmentVariables:
    """Test get_environment_variables function."""

    def test_get_all_environment_variables(self):
        """Test getting all environment variables."""
        result = get_environment_variables()

        assert isinstance(result, dict)
        assert len(result) > 0

        # Should contain some common environment variables
        common_vars = ["PATH", "HOME", "USER", "SHELL"]
        for var in common_vars:
            if var in os.environ:
                assert var in result
                assert result[var] == os.environ[var]

    def test_get_environment_variables_with_prefix(self):
        """Test getting environment variables with prefix filter."""
        # Test with a common prefix
        result = get_environment_variables("PATH")

        assert isinstance(result, dict)
        # Should only contain variables starting with "PATH"
        for key in result:
            assert key.startswith("PATH")

    def test_get_environment_variables_with_nonexistent_prefix(self):
        """Test getting environment variables with non-existent prefix."""
        result = get_environment_variables("NONEXISTENT_PREFIX_12345")

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_get_environment_variables_with_empty_prefix(self):
        """Test getting environment variables with empty prefix."""
        result = get_environment_variables("")

        assert isinstance(result, dict)
        assert len(result) > 0


class TestGetPythonInfo:
    """Test get_python_info function."""

    def test_get_python_info(self):
        """Test getting Python runtime information."""
        result = get_python_info()

        assert isinstance(result, dict)
        assert "version" in result
        assert "version_info" in result
        assert "executable" in result
        assert "platform" in result
        assert "path" in result
        assert "modules_count" in result

        # Verify version info
        assert isinstance(result["version"], str)
        assert len(result["version"]) > 0  # Version string should not be empty

        # Verify version_info structure
        version_info = result["version_info"]
        assert "major" in version_info
        assert "minor" in version_info
        assert "micro" in version_info
        assert isinstance(version_info["major"], int)
        assert isinstance(version_info["minor"], int)
        assert isinstance(version_info["micro"], int)

        # Verify executable
        assert isinstance(result["executable"], str)
        assert "python" in result["executable"].lower()

        # Verify platform
        assert isinstance(result["platform"], str)
        assert len(result["platform"]) > 0

        # Verify path
        assert isinstance(result["path"], list)
        assert len(result["path"]) > 0

        # Verify modules count
        assert isinstance(result["modules_count"], int)
        assert result["modules_count"] > 0


class TestSystemToolsIntegration:
    """Integration tests for system tools."""

    def test_all_system_functions_return_dict(self):
        """Test that all system functions return dictionaries."""
        functions = [
            get_process_info,
            get_system_stats,
            get_environment_variables,
            get_python_info,
        ]

        for func in functions:
            result = func()
            assert isinstance(result, dict), f"{func.__name__} should return a dict"
            assert len(result) > 0, f"{func.__name__} should return non-empty dict"

    def test_command_execution_workflow(self):
        """Test a complete command execution workflow."""
        # Test multiple commands
        commands = [
            "echo 'test1'",
            "python -c 'print(\"test2\")'",
            "ls -la | head -1",  # This might fail on some systems, but should not crash
        ]

        for cmd in commands:
            try:
                result = execute_command(cmd)
                assert isinstance(result, dict)
                assert "command" in result
                assert "return_code" in result
                assert "stdout" in result
                assert "stderr" in result
                assert "success" in result
                assert result["command"] == cmd
            except ValidationError:
                # Some commands might be blocked by security checks
                pass

    def test_system_stats_consistency(self):
        """Test that system stats are consistent."""
        stats1 = get_system_stats()
        stats2 = get_system_stats()

        # Both should have the same structure
        assert set(stats1.keys()) == set(stats2.keys())

        # CPU count should be the same
        assert stats1["cpu"]["count"] == stats2["cpu"]["count"]

        # Memory total should be the same
        assert stats1["memory"]["total"] == stats2["memory"]["total"]

        # Disk total should be the same
        assert stats1["disk"]["total"] == stats2["disk"]["total"]
