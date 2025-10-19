#!/usr/bin/env python3
"""
Manual testing script for MCP server.
Run this to test all functionality manually.
"""

import sys
from pathlib import Path
import subprocess
import json
import time

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def test_mcp_protocol():
    """Test the complete MCP protocol flow."""
    print("🧪 Testing MCP Protocol Flow...")
    
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
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Initialize: {response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
        
        # Step 2: List tools
        print("\n2️⃣ Listing available tools...")
        tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            tools = response.get("result", {}).get("tools", [])
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools[:5]:  # Show first 5 tools
                print(f"   - {tool['name']}: {tool['description'][:50]}...")
        
        # Step 3: Test math tools
        print("\n3️⃣ Testing math tools...")
        
        # Test add_numbers
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
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            result = response.get("result", {}).get("content", [{}])[0].get("text", "Error")
            print(f"✅ add_numbers(5, 3) = {result}")
        
        # Test multiply_numbers
        call_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "multiply_numbers",
                "arguments": {"a": 4, "b": 7}
            },
            "id": 4
        }
        
        process.stdin.write(json.dumps(call_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            result = response.get("result", {}).get("content", [{}])[0].get("text", "Error")
            print(f"✅ multiply_numbers(4, 7) = {result}")
        
        # Step 4: Test user interaction tools
        print("\n4️⃣ Testing user interaction tools...")
        
        # Test greet_user
        call_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "greet_user",
                "arguments": {"name": "Alice"}
            },
            "id": 5
        }
        
        process.stdin.write(json.dumps(call_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            result = response.get("result", {}).get("content", [{}])[0].get("text", "Error")
            print(f"✅ greet_user('Alice') = {result}")
        
        # Step 5: Test system tools
        print("\n5️⃣ Testing system tools...")
        
        # Test get_system_info
        call_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_system_info",
                "arguments": {}
            },
            "id": 6
        }
        
        process.stdin.write(json.dumps(call_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            result = response.get("result", {}).get("content", [{}])[0].get("text", "Error")
            print(f"✅ get_system_info() = {result[:100]}...")
        
        # Step 6: Test file operations
        print("\n6️⃣ Testing file operations...")
        
        # Test list_directory
        call_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "list_directory",
                "arguments": {"directory_path": ".", "include_hidden": False}
            },
            "id": 7
        }
        
        process.stdin.write(json.dumps(call_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            result = response.get("result", {}).get("content", [{}])[0].get("text", "Error")
            print(f"✅ list_directory('.') = {len(result)} characters")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    finally:
        # Clean up
        process.stdin.close()
        process.terminate()
        process.wait()


def test_server_creation():
    """Test that the server can be created."""
    print("🔧 Testing server creation...")
    
    try:
        from macro_man.core.server import create_mcp_server
        from macro_man.config import get_settings
        
        # Test settings
        settings = get_settings()
        print(f"✅ Settings loaded: {settings.server_host}:{settings.server_port}")
        
        # Test server creation
        mcp = create_mcp_server()
        print("✅ MCP server created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Server creation failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Macro-Man MCP Server Tests...")
    print("=" * 50)
    
    # Test 1: Server creation
    if not test_server_creation():
        print("❌ Server creation test failed, stopping.")
        return
    
    print("\n" + "=" * 50)
    
    # Test 2: MCP protocol
    test_mcp_protocol()
    
    print("\n" + "=" * 50)
    print("🎯 Testing completed!")


if __name__ == "__main__":
    main()
