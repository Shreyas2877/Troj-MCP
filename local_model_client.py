#!/usr/bin/env python3
"""
Local Model Client for MCP Server

This client connects a local LLM (Ollama, LM Studio, etc.) to your MCP server,
allowing the model to use all available MCP tools.

Usage:
    python local_model_client.py --model ollama:llama3
    python local_model_client.py --model lmstudio:local
    python local_model_client.py --model openai:gpt-3.5-turbo --api-base http://localhost:1234/v1
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()


class LocalModelClient:
    """Client that connects a local model to an MCP server."""

    def __init__(
        self,
        model_provider: str = "ollama",
        model_name: str = "llama3",
        api_base: str | None = None,
        mcp_server_path: str | None = None,
    ):
        """
        Initialize the local model client.

        Args:
            model_provider: Provider type (ollama, lmstudio, openai)
            model_name: Name of the model to use
            api_base: Custom API base URL (for OpenAI-compatible APIs)
            mcp_server_path: Path to main_stdio.py (defaults to current directory)
        """
        self.model_provider = model_provider.lower()
        self.model_name = model_name
        self.mcp_tools: list[dict[str, Any]] = []
        self.http_client = httpx.AsyncClient(timeout=60.0)
        self.mcp_session: ClientSession | None = None

        # Set API base based on provider
        if api_base:
            self.api_base = api_base
        elif self.model_provider == "ollama":
            self.api_base = "http://localhost:11434"
        elif self.model_provider == "lmstudio":
            self.api_base = "http://localhost:1234/v1"
        else:
            self.api_base = api_base or "http://localhost:1234/v1"

        # Set MCP server path
        if mcp_server_path:
            self.mcp_server_path = Path(mcp_server_path)
        else:
            self.mcp_server_path = Path(__file__).parent / "main_stdio.py"

    async def setup_mcp_connection(self):
        """Set up MCP server connection context managers."""
        python_exe = sys.executable
        server_params = StdioServerParameters(
            command=python_exe,
            args=[str(self.mcp_server_path)],
            env=None,
        )
        self._stdio_ctx = stdio_client(server_params)
        return self._stdio_ctx

    async def get_mcp_tools(self, session: ClientSession) -> list[dict[str, Any]]:
        """Get available tools from MCP server session."""
        # List tools
        tools_response = await session.list_tools()
        tools = tools_response.tools

        # Convert MCP tools to format needed for model
        formatted_tools = []
        for tool in tools:
            formatted_tools.append(
                {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": (
                        json.loads(tool.inputSchema)
                        if isinstance(tool.inputSchema, str)
                        else tool.inputSchema
                    )
                    if tool.inputSchema
                    else {},
                }
            )
        return formatted_tools

    async def call_mcp_tool(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Call a tool on the MCP server."""
        if not self.mcp_session:
            return {"success": False, "error": "Not connected to MCP server"}

        try:
            result = await self.mcp_session.call_tool(tool_name, arguments)
            # Extract text content from result
            if result.content:
                content_text = ""
                for item in result.content:
                    if hasattr(item, "text"):
                        content_text += item.text
                    elif isinstance(item, dict) and "text" in item:
                        content_text += item["text"]

                return {"success": True, "result": content_text}
            else:
                return {"success": True, "result": "Tool executed successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def chat_with_model(
        self, messages: list[dict[str, str]], tools: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """Send a chat request to the local model."""
        # Handle Ollama's different API format
        if self.model_provider == "ollama":
            url = f"{self.api_base}/api/chat"
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
            }
            # Ollama doesn't support tools in the same way, so we'll handle it differently
        else:
            url = f"{self.api_base}/chat/completions"
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.7,
                "stream": False,
            }
            if tools:
                payload["tools"] = tools
                payload["tool_choice"] = "auto"

        try:
            response = await self.http_client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            console.print(f"[red]Error calling model API: {e}[/red]")
            console.print(
                f"[yellow]Make sure your local model is running at {self.api_base}[/yellow]"
            )
            raise

    def format_tools_for_model(
        self, tools: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Format MCP tools for OpenAI-compatible API."""
        formatted = []
        for tool in tools:
            formatted.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.get("name", ""),
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {}),
                    },
                }
            )
        return formatted

    async def run_interactive(self):
        """Run an interactive chat session with tool calling."""
        console.print(
            Panel.fit(
                "[bold green]Local Model MCP Client[/bold green]\n\n"
                f"Model: {self.model_provider}:{self.model_name}\n"
                f"API Base: {self.api_base}\n"
                f"MCP Server: {self.mcp_server_path}",
                title="Configuration",
            )
        )

        # Connect to MCP server and get available tools
        console.print("[cyan]Connecting to MCP server...[/cyan]")
        mcp_connected = False
        stdio_ctx = None

        try:
            stdio_ctx = await self.setup_mcp_connection()
            async with (
                stdio_ctx as (read, write),
                ClientSession(read, write) as session,
            ):
                self.mcp_session = session

                # Initialize
                await session.initialize()

                # Get tools
                self.mcp_tools = await self.get_mcp_tools(session)
                formatted_tools = self.format_tools_for_model(self.mcp_tools)
                console.print(
                    f"[green]✓ Connected! Found {len(self.mcp_tools)} tools[/green]\n"
                )
                mcp_connected = True

                # Run interactive session within MCP connection
                messages = []
                await self._run_chat_loop(messages, formatted_tools, mcp_connected)

        except Exception as e:
            console.print(f"[red]Failed to connect to MCP server: {e}[/red]")
            console.print("[yellow]Continuing without MCP tools...[/yellow]")
            formatted_tools = []
            self.mcp_tools = []
            # Run without MCP
            messages = []
            await self._run_chat_loop(messages, formatted_tools, False)

    async def _run_chat_loop(
        self,
        messages: list[dict[str, str]],
        formatted_tools: list[dict[str, Any]],
        mcp_connected: bool,
    ):
        """Run the interactive chat loop."""
        # System message with tool descriptions
        if self.mcp_tools:
            tool_descriptions = "\n".join(
                [
                    f"- {tool['name']}: {tool.get('description', 'No description')}"
                    for tool in self.mcp_tools
                ]
            )
            system_message = f"""You are a helpful AI assistant with access to the following tools:

{tool_descriptions}

When the user asks you to do something that requires a tool, you should call the appropriate tool.
Always explain what you're doing before calling tools."""
        else:
            system_message = "You are a helpful AI assistant."

        if not messages:
            messages = [{"role": "system", "content": system_message}]

        console.print(
            "[bold]Starting interactive session. Type 'exit' or 'quit' to end.[/bold]\n"
        )

        while True:
            try:
                user_input = console.input("[bold cyan]You: [/bold cyan]")
                if user_input.lower() in ["exit", "quit", "q"]:
                    console.print("[yellow]Goodbye![/yellow]")
                    break

                messages.append({"role": "user", "content": user_input})

                # Get response from model
                console.print("[dim]Thinking...[/dim]")
                response = await self.chat_with_model(messages, formatted_tools)

                # Handle different response formats
                if self.model_provider == "ollama":
                    assistant_message = {
                        "role": "assistant",
                        "content": response.get("message", {}).get("content", ""),
                    }
                else:
                    assistant_message = response["choices"][0]["message"]
                messages.append(assistant_message)

                # Check if model wants to call a tool
                if assistant_message.get("tool_calls"):
                    for tool_call in assistant_message["tool_calls"]:
                        tool_name = tool_call["function"]["name"]
                        try:
                            arguments = json.loads(tool_call["function"]["arguments"])
                        except json.JSONDecodeError:
                            arguments = {}

                        console.print(
                            f"[yellow]🔧 Calling tool: {tool_name} with {arguments}[/yellow]"
                        )

                        # Call the MCP tool (only if connected)
                        if mcp_connected and self.mcp_session:
                            tool_result = await self.call_mcp_tool(tool_name, arguments)
                        else:
                            tool_result = {
                                "success": False,
                                "error": "MCP server not connected",
                            }

                        # Add tool result to messages
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "name": tool_name,
                                "content": json.dumps(tool_result),
                            }
                        )

                        if tool_result.get("success"):
                            console.print(
                                f"[green]✓ Tool result: {json.dumps(tool_result.get('result', {}), indent=2)}[/green]"
                            )
                        else:
                            console.print(
                                f"[red]✗ Tool error: {tool_result.get('error', 'Unknown error')}[/red]"
                            )

                    # Get final response after tool calls
                    response = await self.chat_with_model(messages, formatted_tools)
                    if self.model_provider == "ollama":
                        assistant_message = {
                            "role": "assistant",
                            "content": response.get("message", {}).get("content", ""),
                        }
                    else:
                        assistant_message = response["choices"][0]["message"]
                    messages.append(assistant_message)

                # Display response
                content = assistant_message.get("content", "")
                if content:
                    console.print(
                        Panel(
                            Markdown(content),
                            title="[bold green]Assistant[/bold green]",
                        )
                    )

            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

        await self.http_client.aclose()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Connect a local LLM to your MCP server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use Ollama with llama3
  python local_model_client.py --model ollama:llama3

  # Use LM Studio
  python local_model_client.py --model lmstudio:local

  # Use custom OpenAI-compatible API
  python local_model_client.py --model openai:custom --api-base http://localhost:1234/v1

  # Specify MCP server path
  python local_model_client.py --model ollama:llama3 --mcp-server /path/to/main_stdio.py
        """,
    )

    parser.add_argument(
        "--model",
        type=str,
        default="ollama:llama3",
        help="Model in format 'provider:model_name' (default: ollama:llama3)",
    )
    parser.add_argument(
        "--api-base",
        type=str,
        default=None,
        help="Custom API base URL (overrides provider defaults)",
    )
    parser.add_argument(
        "--mcp-server",
        type=str,
        default=None,
        help="Path to main_stdio.py (default: ./main_stdio.py)",
    )

    args = parser.parse_args()

    # Parse model string
    if ":" in args.model:
        provider, model_name = args.model.split(":", 1)
    else:
        provider = "ollama"
        model_name = args.model

    # Check if MCP server file exists
    mcp_server_path = args.mcp_server or (Path(__file__).parent / "main_stdio.py")
    if not mcp_server_path.exists():
        console.print(f"[red]Error: MCP server file not found: {mcp_server_path}[/red]")
        console.print(
            "[yellow]Make sure main_stdio.py exists in the project directory.[/yellow]"
        )
        sys.exit(1)

    # Create and run client
    client = LocalModelClient(
        model_provider=provider,
        model_name=model_name,
        api_base=args.api_base,
        mcp_server_path=str(mcp_server_path),
    )

    await client.run_interactive()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
        sys.exit(0)
