# Architecture

## Philosophy

gob transforms your computer into a Linux development environment through Docker containers.

## Core Principles

### 1. Computer as Linux Environment
- All tools execute within Docker containers
- Full Linux command-line interface available
- Isolated execution preventing system conflicts
- Consistent behavior across Windows, macOS, Linux

### 2. Docker-First Architecture
- Every tool runs in its own Docker container space
- Sandboxed operations protect host system
- Network isolation for web operations
- File system isolation with controlled access

### 3. User-Friendly Tools
- Emoji-based error indicators (🐛, ⏰, 💥, 📁, 🔍)
- Detailed error messages with troubleshooting
- Timeout protection for operations
- Clear success/failure indicators

### 4. Modular, Extensible Design
- Plugin system for custom functionality
- Tool loader pattern for easy extension
- Configuration-driven behavior
- Core components remain lightweight

## System Overview

```
User Interface (TUI Chat, Discord Bot)
    ↓
Agent Orchestrator (Tool Router, Memory Manager, LLM Client)
    ↓
Core Components (Config Manager, Tool Loader, Logger)
    ↓
Tools Layer (Code Execution, Text Editor, Search Engine, Response Tool, Document Query)
    ↓
Docker Infrastructure (Container Isolation, Security, Consistency)
```

## Components

### Agent Orchestrator
Central coordination hub for all agent operations:
- Tool routing and execution
- Memory management and retrieval
- LLM client coordination
- Error handling and recovery

### Core Components
Essential services that power the agent system:
- **Config Manager**: Loads and validates configuration
- **Tool Loader**: Dynamically loads and registers tools
- **Logger**: Centralized logging with chat visibility
- **Memory Manager**: Semantic memory with FAISS embeddings
- **LLM Client**: Multi-model support with Ollama Cloud API

### Tools Layer
Execute specific functions within Docker containers:
1. **Code Execution**: Python and Linux command execution
2. **Text Editor**: File operations and text processing
3. **Search Engine**: Web search functionality
4. **Response Tool**: AI response generation and routing
5. **Document Query**: Document processing and analysis

### Interfaces
User interaction points for the agent system:
- **TUI Chat**: Terminal-based chat interface
- **Discord Bot**: Discord integration for multi-user collaboration

## Design Patterns

### Command Pattern (Tools)
Each tool implements a command interface with:
- `execute()` method for tool functionality
- `validate()` method for input validation
- Error handling with user-friendly messages

### Router Pattern (Orchestrator)
Agent orchestrator routes requests to appropriate tools:
- Tool selection based on request type
- Parameter passing and validation
- Result aggregation and formatting

### Service Locator (Core Components)
Core services are located and injected:
- Configuration service for settings
- Memory service for data persistence
- Logging service for user visibility

### Adapter Pattern (Interfaces)
Different interfaces adapt to the same core functionality:
- TUI interface for terminal users
- Discord interface for community collaboration

## Security

### Container Isolation
- Tools run in isolated Docker containers
- No direct access to host system
- Network isolation for web operations

### Sandboxed Execution
- Code execution within controlled environments
- Timeout protection for long operations
- Resource limits on containers

### Configuration Security
- API keys stored in environment variables
- Configuration validation and sanitization
- No hardcoded credentials

## Performance

### Asynchronous Operations
- Non-blocking tool execution
- Concurrent processing where possible
- Timeout protection for hung operations

### Resource Management
- Docker container lifecycle management
- Memory usage monitoring
- Cleanup of temporary resources

### Caching Strategy
- Semantic memory for repeated queries
- Configuration caching for performance
- Result caching for expensive operations

## Current Version

**Version**: 0.2.4
**Last Updated**: 2026-03-31
