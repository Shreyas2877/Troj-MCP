"""System utility tools for the MCP server."""

import os
import psutil
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog

from ..utils.exceptions import ValidationError, MacroManError

logger = structlog.get_logger(__name__)


def register_system_tools(mcp_server) -> None:
    """Register system utility tools."""
    
    @mcp_server.tool()
    def get_process_info(pid: Optional[int] = None) -> Dict[str, Any]:
        """Get information about system processes.
        
        Args:
            pid: Process ID to get info for. If None, returns current process info.
            
        Returns:
            Dictionary containing process information
        """
        try:
            if pid is None:
                process = psutil.Process()
            else:
                process = psutil.Process(pid)
            
            info = {
                "pid": process.pid,
                "name": process.name(),
                "status": process.status(),
                "cpu_percent": process.cpu_percent(),
                "memory_info": {
                    "rss": process.memory_info().rss,
                    "vms": process.memory_info().vms,
                },
                "create_time": datetime.fromtimestamp(process.create_time()).isoformat(),
                "num_threads": process.num_threads(),
            }
            
            logger.info("Process info retrieved", pid=process.pid)
            return info
            
        except psutil.NoSuchProcess:
            raise ValidationError(f"Process with PID {pid} not found", field="pid")
        except Exception as e:
            logger.error("Error getting process info", pid=pid, error=str(e))
            raise MacroManError(f"Failed to get process info: {str(e)}")
    
    @mcp_server.tool()
    def get_system_stats() -> Dict[str, Any]:
        """Get comprehensive system statistics.
        
        Returns:
            Dictionary containing system statistics
        """
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk information
            disk = psutil.disk_usage('/')
            
            # Network information
            network = psutil.net_io_counters()
            
            stats = {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "frequency": {
                        "current": cpu_freq.current if cpu_freq else None,
                        "min": cpu_freq.min if cpu_freq else None,
                        "max": cpu_freq.max if cpu_freq else None,
                    }
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free,
                },
                "swap": {
                    "total": swap.total,
                    "used": swap.used,
                    "free": swap.free,
                    "percent": swap.percent,
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100,
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv,
                }
            }
            
            logger.info("System stats retrieved")
            return stats
            
        except Exception as e:
            logger.error("Error getting system stats", error=str(e))
            raise MacroManError(f"Failed to get system stats: {str(e)}")
    
    @mcp_server.tool()
    def execute_command(command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute a system command safely.
        
        Args:
            command: The command to execute
            timeout: Timeout in seconds for command execution
            
        Returns:
            Dictionary containing command execution results
        """
        try:
            if not command or not command.strip():
                raise ValidationError("Command cannot be empty", field="command")
            
            # Basic security check - prevent dangerous commands
            dangerous_commands = ['rm -rf', 'sudo', 'su', 'chmod 777', 'dd if=', 'mkfs']
            if any(dangerous in command.lower() for dangerous in dangerous_commands):
                raise ValidationError("Command contains potentially dangerous operations", field="command")
            
            logger.info("Executing command", command=command, timeout=timeout)
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()
            )
            
            response = {
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }
            
            logger.info("Command executed", **response)
            return response
            
        except subprocess.TimeoutExpired:
            logger.error("Command timeout", command=command, timeout=timeout)
            raise MacroManError(f"Command timed out after {timeout} seconds")
        except Exception as e:
            logger.error("Error executing command", command=command, error=str(e))
            raise MacroManError(f"Failed to execute command: {str(e)}")
    
    @mcp_server.tool()
    def get_environment_variables(prefix: Optional[str] = None) -> Dict[str, str]:
        """Get environment variables.
        
        Args:
            prefix: Optional prefix to filter environment variables
            
        Returns:
            Dictionary of environment variables
        """
        try:
            env_vars = dict(os.environ)
            
            if prefix:
                env_vars = {
                    key: value for key, value in env_vars.items()
                    if key.startswith(prefix)
                }
            
            logger.info("Environment variables retrieved", prefix=prefix, count=len(env_vars))
            return env_vars
            
        except Exception as e:
            logger.error("Error getting environment variables", error=str(e))
            raise MacroManError(f"Failed to get environment variables: {str(e)}")
    
    @mcp_server.tool()
    def get_python_info() -> Dict[str, Any]:
        """Get Python runtime information.
        
        Returns:
            Dictionary containing Python information
        """
        try:
            info = {
                "version": sys.version,
                "version_info": {
                    "major": sys.version_info.major,
                    "minor": sys.version_info.minor,
                    "micro": sys.version_info.micro,
                },
                "executable": sys.executable,
                "platform": sys.platform,
                "path": sys.path,
                "modules_count": len(sys.modules),
            }
            
            logger.info("Python info retrieved")
            return info
            
        except Exception as e:
            logger.error("Error getting Python info", error=str(e))
            raise MacroManError(f"Failed to get Python info: {str(e)}")
