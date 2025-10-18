# Macro-Man: Personal MCP Server & iOS App

A comprehensive project to build a personal Model Context Protocol (MCP) server deployed on AWS EC2 with a simple iOS frontend for seamless AI model interactions and service integrations.

## 🎯 Project Vision

Build a personal MCP server that acts as a universal interface between AI models and various services (existing or custom), with an intuitive iOS app for easy interaction. This setup will enable easy integration with any service while keeping all the complex MCP logic in the backend.

## 📋 Project Roadmap

### Phase 1: Foundation & Research ✅
- [x] Research MCP protocol specifications and capabilities
- [x] Analyze system architecture requirements
- [x] Identify technology stack for each component
- [x] Create comprehensive project roadmap

### Phase 2: Backend Infrastructure Setup ✅
- [x] **Project Structure & Development Setup**
  - [x] Create proper project directory structure with industry standards
  - [x] Set up requirements.txt with all dependencies
  - [x] Implement basic MCP server with core tools
  - [x] Add configuration management and environment variables
  - [x] Implement proper logging system with structured logging
  - [x] Add comprehensive error handling and custom exceptions
  - [x] Create Docker configuration for easy deployment
  - [x] Set up basic test structure with pytest

- [ ] **AWS EC2 Instance Setup**
  - [ ] Choose appropriate EC2 instance type (t3.medium/large recommended)
  - [ ] Configure security groups (ports 22, 80, 443, 8000)
  - [ ] Set up Ubuntu 20.04+ or Amazon Linux 2
  - [ ] Install Python 3.10+, pip, virtualenv
  - [ ] Configure SSL/TLS certificates (Let's Encrypt)

- [ ] **MCP Server Deployment**
  - [ ] Deploy MCP server to EC2
  - [ ] Implement authentication and authorization (JWT)
  - [ ] Set up process management (systemd/PM2)
  - [ ] Configure monitoring and alerting

### Phase 3: Core MCP Tools Implementation ✅
- [x] **Basic Tools**
  - [x] Mathematical operations (add, multiply)
  - [x] User interaction (greet, echo)
  - [x] System information (system info, Python info)
  - [x] File operations (read, write, list, JSON)
  - [x] System utilities (process info, system stats, environment variables)
  - [x] Command execution (safe command execution with validation)

- [ ] **Advanced Tools**
  - [ ] Database operations (CRUD)
  - [ ] API integrations (REST/GraphQL)
  - [ ] Custom service integrations
  - [ ] Data processing and transformation
  - [ ] Notification systems
  - [ ] Analytics and reporting

### Phase 4: iOS Application Development
- [ ] **Project Setup**
  - [ ] Create new iOS project in Xcode
  - [ ] Set up Swift networking layer
  - [ ] Implement MCP client protocol
  - [ ] Design intuitive UI/UX

- [ ] **Core Features**
  - [ ] User authentication
  - [ ] Tool discovery and execution
  - [ ] Real-time communication with MCP server
  - [ ] Response handling and display
  - [ ] Offline capabilities

### Phase 5: Integration & Testing
- [ ] **Service Integrations**
  - [ ] Connect to existing APIs
  - [ ] Implement custom service endpoints
  - [ ] Test data flow and error handling
  - [ ] Performance optimization

- [ ] **Testing & Quality Assurance**
  - [ ] Unit tests for MCP server
  - [ ] Integration tests for iOS app
  - [ ] End-to-end testing
  - [ ] Security testing and vulnerability assessment

### Phase 6: Deployment & Production
- [ ] **Production Deployment**
  - [ ] Deploy MCP server to EC2
  - [ ] Set up monitoring and alerting (CloudWatch)
  - [ ] Configure backup and disaster recovery
  - [ ] Implement CI/CD pipeline

- [ ] **iOS App Store Submission**
  - [ ] App Store review preparation
  - [ ] Privacy policy and terms of service
  - [ ] App Store metadata and screenshots
  - [ ] Beta testing with TestFlight

### Phase 7: Maintenance & Enhancement
- [ ] **Ongoing Maintenance**
  - [ ] Regular security updates
  - [ ] Performance monitoring
  - [ ] User feedback integration
  - [ ] Feature enhancements

## 🏗️ System Architecture

```
┌─────────────────┐    HTTPS/WSS    ┌──────────────────┐
│   iOS App       │◄──────────────►│   MCP Server     │
│   (Frontend)    │                 │   (EC2 Backend)  │
└─────────────────┘                 └──────────────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │   External       │
                                    │   Services       │
                                    │   (APIs, DBs,    │
                                    │    Custom)       │
                                    └──────────────────┘
```

## 🛠️ Technology Stack

### Backend (MCP Server)
- **Language**: Python 3.10+
- **Framework**: FastMCP (MCP Python package)
- **Deployment**: AWS EC2
- **Process Management**: systemd or PM2
- **Monitoring**: AWS CloudWatch
- **Security**: JWT, HTTPS, SSL/TLS

### Frontend (iOS App)
- **Language**: Swift
- **Framework**: SwiftUI or UIKit
- **Networking**: URLSession or Alamofire
- **Architecture**: MVVM or Clean Architecture
- **Testing**: XCTest

### Infrastructure
- **Cloud Provider**: AWS
- **Compute**: EC2 (t3.medium/large)
- **Storage**: EBS volumes
- **Networking**: VPC, Security Groups
- **SSL**: Let's Encrypt or AWS Certificate Manager

## 🚀 Getting Started

### Prerequisites
- Python 3.10+ installed
- Basic understanding of MCP protocol
- (Optional) AWS account with EC2 access for deployment
- (Optional) macOS with Xcode for iOS development

### Quick Start (Local Development)

1. **Clone and Setup**
   ```bash
   git clone <your-repo-url>
   cd macro-man
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

2. **Configure Environment**
   ```bash
   # Edit the .env file with your settings
   cp env.example .env
   # Edit .env file with your SECRET_KEY and other settings
   ```

3. **Run the MCP Server**
   ```bash
   source venv/bin/activate
   python main.py
   ```

4. **Test the Server**
   ```bash
   # Run tests
   python -m pytest tests/ -v
   
   # Test with curl (server should be running on localhost:8000)
   curl -X POST http://localhost:8000/mcp \
     -H "Content-Type: application/json" \
     -d '{"method": "add_numbers", "params": [5, 3], "id": 1}'
   ```

### Available MCP Tools

The server comes with these built-in tools:

**Basic Operations:**
- `add_numbers(a, b)` - Add two numbers
- `multiply_numbers(a, b)` - Multiply two numbers
- `greet_user(name)` - Greet a user by name
- `echo_message(message)` - Echo back a message

**File Operations:**
- `read_file(file_path)` - Read text file contents
- `write_file(file_path, content, overwrite)` - Write content to file
- `list_directory(directory_path, include_hidden)` - List directory contents
- `read_json_file(file_path)` - Read and parse JSON file
- `write_json_file(file_path, data, indent)` - Write data as JSON

**System Utilities:**
- `get_system_info()` - Get basic system information
- `get_system_stats()` - Get comprehensive system statistics
- `get_process_info(pid)` - Get process information
- `get_environment_variables(prefix)` - Get environment variables
- `get_python_info()` - Get Python runtime information
- `execute_command(command, timeout)` - Execute system command safely

## 📚 Key Resources

- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [MCP Python Package](https://pypi.org/project/mcp/)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [iOS Networking Guide](https://developer.apple.com/documentation/foundation/urlsession)

## 🔄 Progress Tracking

This README will be updated as we progress through each phase. Check the checkboxes above to track our advancement through the project roadmap.

---

*Last Updated: October 16, 2024*
*Current Phase: Phase 2 - Backend Infrastructure Setup (Project Structure Complete)*

## 🎉 Current Status

**✅ COMPLETED:**
- ✅ Complete project structure with industry standards
- ✅ MCP server implementation with 15+ built-in tools
- ✅ Configuration management with environment variables
- ✅ Structured logging with Rich console output
- ✅ Comprehensive error handling and custom exceptions
- ✅ Docker configuration for easy deployment
- ✅ Development environment setup script
- ✅ All dependencies installed and tested

**🚀 READY TO USE:**
Your MCP server is now fully functional and ready to run! You can start it with:
```bash
source venv/bin/activate
python main.py
```

**📋 NEXT STEPS:**
1. Deploy to AWS EC2 (Phase 2 - AWS Setup)
2. Build iOS app (Phase 4)
3. Add authentication (Phase 2 - Security)
4. Integrate with external services (Phase 3 - Advanced Tools)
