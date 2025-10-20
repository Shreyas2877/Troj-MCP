# Macro-Man: Model Context Protocol (MCP) Server

A comprehensive Model Context Protocol (MCP) server implementation that provides a standardized interface for AI models to interact with various tools and services. This server enables seamless integration between AI applications and external systems through a well-defined protocol.

## What is Model Context Protocol (MCP)?

Model Context Protocol (MCP) is a standardized communication protocol that enables AI models to interact with external tools and services in a consistent, secure, and efficient manner. It provides:

- **Standardized Interface**: Common protocol for tool registration and execution
- **Type Safety**: Strong typing for tool parameters and responses
- **Error Handling**: Comprehensive error management and reporting
- **Security**: Built-in validation and sanitization
- **Extensibility**: Easy addition of new tools and services

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Server Architecture                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   HTTP Client   │    │  Claude Desktop │    │  Other MCP   │ │
│  │   (Web/API)     │    │   (stdio)       │    │  Clients     │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                       │                       │      │
│           │ HTTP/JSON-RPC         │ stdio/JSON-RPC        │      │
│           │                       │                       │      │
│           ▼                       ▼                       ▼      │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                MCP Server Core                              │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │   Router    │  │  Validator  │  │   Error Handler     │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│           │                       │                       │      │
│           ▼                       ▼                       ▼      │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Tool Registry                            │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │ Basic Tools │  │ File Ops    │  │   System Utils      │ │ │
│  │  │ Email Tools │  │ Custom Tools│  │   External APIs     │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│           │                       │                       │      │
│           ▼                       ▼                       ▼      │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                External Services                            │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │ Email API   │  │ File System │  │   System Commands   │ │ │
│  │  │ (localhost: │  │             │  │                     │ │ │
│  │  │   3000)     │  │             │  │                     │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Available Tools

### Basic Operations
- **`add_numbers(a, b)`** - Add two numbers
- **`multiply_numbers(a, b)`** - Multiply two numbers  
- **`greet_user(name)`** - Greet a user by name
- **`echo_message(message)`** - Echo back a message

### File Operations
- **`read_file(file_path)`** - Read text file contents
- **`write_file(file_path, content, overwrite)`** - Write content to file
- **`list_directory(directory_path, include_hidden)`** - List directory contents
- **`read_json_file(file_path)`** - Read and parse JSON file
- **`write_json_file(file_path, data, indent)`** - Write data as JSON

### System Utilities
- **`get_system_info()`** - Get basic system information
- **`get_system_stats()`** - Get comprehensive system statistics
- **`get_process_info(pid)`** - Get process information
- **`get_environment_variables(prefix)`** - Get environment variables
- **`get_python_info()`** - Get Python runtime information
- **`execute_command(command, timeout)`** - Execute system command safely

### Email Service Integration
- **`send_email(to, subject, body)`** - Send email via external service

## Tool Registration Framework

### How Tools Are Registered

Tools are registered through a modular system that allows for easy extension and maintenance:

```python
# Example: Registering a new tool
from macro_man.tools import register_tool

@register_tool
def my_custom_tool(param1: str, param2: int) -> dict:
    """
    Custom tool description.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2
        
    Returns:
        Dictionary with tool execution result
    """
    # Tool implementation
    return {"result": "success", "data": f"Processed {param1} with {param2}"}
```

### Tool Registration Process

1. **Tool Definition**: Define your tool function with proper type hints
2. **Documentation**: Add comprehensive docstring with parameter descriptions
3. **Registration**: Use the `@register_tool` decorator
4. **Validation**: Framework automatically validates parameters and types
5. **Integration**: Tool becomes available to all MCP clients

### Adding New Tools

To add a new tool to the server:

1. Create a new file in `src/macro_man/tools/`
2. Implement your tool function with proper typing
3. Add the tool to `src/macro_man/tools/__init__.py`
4. The tool will be automatically available to MCP clients

## Framework Architecture

### Core Components

#### 1. MCP Server Core
- **Router**: Handles incoming requests and routes to appropriate tools
- **Validator**: Validates tool parameters and request format
- **Error Handler**: Manages errors and provides consistent error responses

#### 2. Tool Registry
- **Tool Discovery**: Automatically discovers and registers available tools
- **Type Validation**: Ensures parameter types match tool definitions
- **Execution Engine**: Executes tools with proper error handling

#### 3. Transport Layer
- **HTTP Transport**: Web-based communication via JSON-RPC over HTTP
- **stdio Transport**: Process-based communication via stdin/stdout

### Configuration Management

The server uses environment variables for configuration:

```bash
# Core settings
SECRET_KEY=your-secret-key
LOG_LEVEL=INFO
DEBUG=false

# Email service integration
EMAIL_SERVICE_URL=http://localhost:3000

# Server settings
HTTP_HOST=0.0.0.0
HTTP_PORT=8000
```

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- (Optional) Virtual environment for isolation

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd macro-man
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env file with your settings
   ```

### Running the Server

#### Option 1: HTTP Transport (Web/API)

Start the server for web-based access:

```bash
python main.py
```

The server will start on `http://localhost:8000` by default.

**Test the HTTP server:**
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "add_numbers", "params": [5, 3], "id": 1}'
```

#### Option 2: stdio Transport (Claude Desktop)

Start the server for Claude Desktop integration:

```bash
python main_stdio.py
```

This starts the server in stdio mode, waiting for input via stdin.

**Claude Desktop Configuration:**
```json
{
  "mcpServers": {
    "macro-man": {
      "command": "python",
      "args": ["/path/to/main_stdio.py"]
    }
  }
}
```

### Transport Comparison

| Feature | HTTP Transport | stdio Transport |
|---------|----------------|-----------------|
| **Use Case** | Web APIs, external clients | Claude Desktop, process communication |
| **Communication** | HTTP/JSON-RPC | stdin/stdout/JSON-RPC |
| **Port** | 8000 (configurable) | None (process communication) |
| **Client** | Any HTTP client | Claude Desktop, other MCP clients |
| **Startup** | Manual (`python main.py`) | Automatic (managed by client) |
| **Lifecycle** | Manual management | Client-managed |

## Email Service Integration Example

### Overview

The server integrates with an external email service running on `localhost:3000`. This demonstrates how to integrate with external APIs and services.

### Email Service API

The email service expects the following format:

**Endpoint:** `POST http://localhost:3000/send-email`

**Request Body:**
```json
{
  "to": "recipient@example.com",
  "subject": "Email Subject",
  "body": "Email content"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email sent successfully",
  "messageId": "<message-id@example.com>"
}
```

### Integration Implementation

```python
# src/macro_man/tools/email.py
def send_email(to: str, subject: str, body: str) -> dict:
    """
    Send email via external email service.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        
    Returns:
        Dictionary with email sending result
    """
    # Get email service URL from configuration
    settings = get_settings()
    email_service_url = f"{settings.email_service_url}/send-email"
    
    # Prepare request payload
    payload = {"to": to, "subject": subject, "body": body}
    
    # Make HTTP request to email service
    response = httpx.post(
        email_service_url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30.0,
    )
    
    # Handle response and return result
    return response.json()
```

### Configuration

Set the email service URL in your `.env` file:

```bash
EMAIL_SERVICE_URL=http://localhost:3000
```

### Usage

Once configured, the email tool is available to all MCP clients:

```python
# Via HTTP client
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "send_email",
    "params": {
      "to": "user@example.com",
      "subject": "Test Email",
      "body": "This is a test email"
    },
    "id": 1
  }'
```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src/macro_man --cov-report=html

# Run specific test file
python -m pytest tests/test_email_tools.py -v
```

### Code Quality

```bash
# Linting
ruff check src/ tests/

# Formatting
ruff format src/ tests/

# Type checking
mypy src/ --ignore-missing-imports
```

### Adding New Tools

1. **Create tool file** in `src/macro_man/tools/`
2. **Implement tool function** with proper typing and documentation
3. **Add to tool registry** in `src/macro_man/tools/__init__.py`
4. **Write tests** in `tests/`
5. **Update documentation** as needed

## API Reference

### MCP Protocol

The server implements the Model Context Protocol specification:

- **Request Format**: JSON-RPC 2.0
- **Response Format**: JSON-RPC 2.0
- **Error Handling**: Standardized error codes and messages
- **Type Safety**: Strong typing for all parameters and responses

### Tool Execution

All tools follow a consistent pattern:

```python
def tool_name(param1: Type1, param2: Type2) -> dict:
    """
    Tool description.
    
    Args:
        param1: Parameter description
        param2: Parameter description
        
    Returns:
        Dictionary with execution result
        
    Raises:
        ValidationError: If parameters are invalid
        MacroManError: If tool execution fails
    """
    # Implementation
    return {"result": "success", "data": "..."}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions, issues, or contributions, please:

1. Check the existing issues
2. Create a new issue with detailed information
3. Provide reproduction steps for bugs
4. Include relevant logs and error messages

---

*Last Updated: December 2024*
*Version: 1.0.0*