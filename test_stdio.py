#!/usr/bin/env python3
"""
Test script for stdio MCP server
"""

import subprocess
import json
import time

def test_stdio_mcp():
    """Test the stdio MCP server with proper initialization."""
    
    # Start the MCP server process
    process = subprocess.Popen(
        ["python", "main_stdio.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/Users/trojan/Documents/GitHub/macro-man"
    )
    
    try:
        # Step 1: Initialize
        print("1️⃣ Initializing MCP session...")
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            },
            "id": 1
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Initialize response: {json.dumps(response, indent=2)}")
        
        # Step 2: List tools
        print("\n2️⃣ Listing tools...")
        tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Tools list: {json.dumps(response, indent=2)}")
        
        # Step 3: Call a tool
        print("\n3️⃣ Calling add_numbers tool...")
        call_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "add_numbers",
                "arguments": {"a": 5, "b": 3}
            },
            "id": 3
        }
        
        process.stdin.write(json.dumps(call_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Tool call result: {json.dumps(response, indent=2)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up
        process.stdin.close()
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_stdio_mcp()
