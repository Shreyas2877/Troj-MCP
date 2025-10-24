# 🚀 Troj-MCP

A comprehensive Model Context Protocol (MCP) server that provides powerful tools for system integration, file operations, calendar management, email handling, and more.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/tests-passing-green.svg)](https://github.com/Shreyas2877/Troj-MCP/actions)

## 🎯 What is Troj-MCP?

Troj-MCP is a versatile MCP server that provides a comprehensive suite of tools for:

- **System Operations** - Monitor system performance, processes, and environment
- **File Management** - Read, write, and manage files and directories
- **Calendar Integration** - Schedule meetings and manage events
- **Email Operations** - Send and receive emails with advanced filtering
- **Command Execution** - Safely execute system commands with validation
- **Data Processing** - Handle JSON files and structured data

## ✨ Features

### 🛠️ **Comprehensive Tool Suite**

#### **Basic Operations**
- `add_numbers` - Mathematical addition with validation
- `multiply_numbers` - Mathematical multiplication with error handling
- `greet_user` - Personalized user greetings
- `echo_message` - Message echoing and validation

#### **System Monitoring**
- `get_system_info` - Complete system information retrieval
- `get_system_stats` - Real-time system performance metrics
- `get_process_info` - Process monitoring and analysis
- `get_environment_variables` - Environment variable inspection
- `get_python_info` - Python runtime information

#### **File Operations**
- `read_file` - Safe file reading with validation
- `write_file` - Secure file writing with overwrite protection
- `list_directory` - Directory listing with filtering options
- `read_json_file` - JSON file parsing and validation
- `write_json_file` - Structured JSON file creation

#### **Calendar Integration**
- `schedule_meet` - Meeting scheduling with timezone support
- `list_events` - Calendar event retrieval and filtering
- Full Google Calendar API integration
- Timezone-aware scheduling

#### **Email Management**
- `send_email` - Email sending with external service integration
- `read_email` - Email retrieval with advanced filtering
- Support for multiple email providers
- Thread-based email organization

#### **Command Execution**
- `execute_command` - Secure command execution with timeout protection
- Input validation and sanitization
- Dangerous command detection and prevention

### 🔒 **Security & Reliability**
- **Input Validation** - Comprehensive input sanitization and validation
- **Command Security** - Dangerous command detection and prevention
- **Error Handling** - Graceful error handling with detailed logging
- **Type Safety** - Runtime type checking and validation
- **Logging** - Comprehensive structured logging with correlation IDs

### 🧪 **Quality Assurance**
- **95%+ Test Coverage** - Comprehensive test suite
- **Linting** - Code quality enforcement with Ruff
- **Type Checking** - Static type analysis with MyPy
- **Security Scanning** - Automated security checks with Bandit and Safety

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Shreyas2877/Troj-MCP.git
   cd Troj-MCP
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**
   ```bash
   python main.py
   ```

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t trojan2877/troj-mcp:latest .
   ```

2. **Run the container**
   ```bash
   docker run -d --name troj-mcp -p 8000:8000 trojan2877/troj-mcp:latest
   ```

3. **Or use Docker Hub**
   ```bash
   docker run -d --name troj-mcp -p 8000:8000 trojan2877/troj-mcp:latest
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Server Configuration
SERVER_HOST=localhost
SERVER_PORT=8000
DEBUG=false

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/troj-mcp.log

# Email Configuration (Optional)
EMAIL_SERVICE_URL=your_email_service_url
EMAIL_API_KEY=your_email_api_key

# Calendar Configuration (Optional)
CALENDAR_SERVICE_URL=your_calendar_service_url
CALENDAR_API_KEY=your_calendar_api_key
```

### Configuration File

The server uses Pydantic Settings for configuration management. You can customize settings in `src/macro_man/config/settings.py`.

## 🛠️ Development

### Setup Development Environment

1. **Clone and setup**
   ```bash
   git clone https://github.com/Shreyas2877/Troj-MCP.git
   cd Troj-MCP
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run tests**
   ```bash
   python -m pytest tests/
   ```

3. **Run linting**
   ```bash
   ruff check .
   ruff format .
   ```

4. **Run type checking**
   ```bash
   mypy src/
   ```

### Project Structure

```
Troj-MCP/
├── src/
│   └── macro_man/
│       ├── config/          # Configuration management
│       ├── core/            # Core server implementation
│       ├── tools/           # MCP tool implementations
│       │   ├── basic.py     # Basic utility tools
│       │   ├── calendar.py  # Calendar integration
│       │   ├── email.py     # Email management
│       │   ├── file_ops.py  # File operations
│       │   └── system.py   # System monitoring
│       └── utils/           # Utility functions
├── tests/                   # Test suite
├── scripts/                 # Development scripts
├── examples/                # Usage examples
├── docs/                    # Documentation
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project configuration
├── Dockerfile              # Docker configuration
└── README.md               # This file
```

## 📚 Usage Examples

### Basic Operations

```python
# Add numbers
result = add_numbers(5, 3)  # Returns 8

# Multiply numbers
result = multiply_numbers(4, 7)  # Returns 28

# Greet user
greeting = greet_user("Alice")  # Returns "Hello, Alice!"
```

### File Operations

```python
# Read a file
content = read_file("path/to/file.txt")

# Write to a file
write_file("output.txt", "Hello, World!")

# List directory contents
files = list_directory("/path/to/directory")

# Read JSON file
data = read_json_file("config.json")
```

### System Monitoring

```python
# Get system information
info = get_system_info()

# Get system statistics
stats = get_system_stats()

# Get process information
process = get_process_info(pid=1234)
```

### Calendar Operations

```python
# Schedule a meeting
meeting = schedule_meet(
    title="Team Meeting",
    start="2024-01-15T10:00:00",
    end="2024-01-15T11:00:00",
    attendees=["alice@example.com", "bob@example.com"]
)

# List events
events = list_events(
    timeMin="2024-01-01T00:00:00Z",
    timeMax="2024-01-31T23:59:59Z"
)
```

### Email Operations

```python
# Send an email
send_email(
    to="recipient@example.com",
    subject="Test Email",
    body="This is a test email from Troj-MCP"
)

# Read emails
emails = read_email(
    maxResults=10,
    includeBody=True
)
```

## 🧪 Testing

### Run All Tests
```bash
python -m pytest tests/
```

### Run with Coverage
```bash
python -m pytest tests/ --cov=src/macro_man --cov-report=html
```

### Run Specific Test Categories
```bash
# Unit tests
python -m pytest tests/test_basic_tools.py

# Integration tests
python -m pytest tests/test_mcp_integration.py

# Coverage tests
python -m pytest tests/test_server_coverage.py
```

## 📊 Logging

Troj-MCP includes comprehensive logging capabilities:

- **Structured Logging** - JSON-formatted logs for machine processing
- **Correlation IDs** - Track requests across the entire system
- **Log Levels** - DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Rotation** - Automatic file rotation with retention policies
- **Performance Monitoring** - Execution time tracking

### Log Analysis

Use the included log analyzer to analyze your logs:

```bash
python scripts/log_analyzer.py --log-dir logs --hours 24
```

## 🔧 API Reference

### Tool Categories

#### **Basic Tools**
- `add_numbers(a: float, b: float) -> float`
- `multiply_numbers(a: float, b: float) -> float`
- `greet_user(name: str) -> str`
- `echo_message(message: str) -> str`

#### **System Tools**
- `get_system_info() -> dict`
- `get_system_stats() -> dict`
- `get_process_info(pid: int) -> dict`
- `get_environment_variables(prefix: str) -> dict`
- `get_python_info() -> dict`

#### **File Operations**
- `read_file(file_path: str) -> str`
- `write_file(file_path: str, content: str, overwrite: bool) -> bool`
- `list_directory(directory_path: str, include_hidden: bool) -> list`
- `read_json_file(file_path: str) -> dict`
- `write_json_file(file_path: str, data: dict, indent: int) -> bool`

#### **Calendar Tools**
- `schedule_meet(title: str, start: str, end: str, attendees: list) -> dict`
- `list_events(timeMin: str, timeMax: str, maxResults: int) -> list`

#### **Email Tools**
- `send_email(to: str, subject: str, body: str) -> dict`
- `read_email(maxResults: int, includeBody: bool) -> list`

#### **Command Execution**
- `execute_command(command: str, timeout: int) -> dict`

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   export SERVER_HOST=0.0.0.0
   export SERVER_PORT=8000
   export LOG_LEVEL=INFO
   ```

2. **Run with Gunicorn**
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
   ```

3. **Docker Production**
   ```bash
   docker run -d \
     --name troj-mcp \
     -p 8000:8000 \
     -e LOG_LEVEL=INFO \
     trojan2877/troj-mcp:latest
   ```

### Docker Compose

```yaml
version: '3.8'
services:
  troj-mcp:
    image: trojan2877/troj-mcp:latest
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `python -m pytest tests/`
5. Run linting: `ruff check .`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive tests
- Update documentation as needed
- Ensure all tests pass

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [GitHub Wiki](https://github.com/Shreyas2877/Troj-MCP/wiki)
- **Issues**: [GitHub Issues](https://github.com/Shreyas2877/Troj-MCP/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Shreyas2877/Troj-MCP/discussions)

## 🙏 Acknowledgments

- **MCP Protocol** - For the excellent Model Context Protocol specification
- **FastAPI** - For the amazing async web framework
- **Python Community** - For the rich ecosystem of libraries
- **Contributors** - For their valuable feedback and contributions

---

**Made with ❤️ by the Troj-MCP team**

*For more information, visit our [GitHub repository](https://github.com/Shreyas2877/Troj-MCP) or check out the [documentation](https://github.com/Shreyas2877/Troj-MCP/wiki).*