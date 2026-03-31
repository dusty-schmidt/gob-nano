# GOB Tools Documentation

GOB provides 5 core tools that turn your computer into a powerful Linux development environment through Docker containers.

## Computer as a Tool: Linux Environment in Docker

GOB treats your computer as a complete Linux development environment. Each tool executes within a Docker container, providing:

- **Isolated execution environment**
- **Linux command-line interface**
- **Secure sandboxed operations**
- **Consistent cross-platform behavior**

## 5 Core Tools Overview

### 1. Code Execution Tool
**Purpose**: Execute Python code and Linux commands in Docker containers

**Features**:
- Python code execution with error handling
- Linux command execution with timeout protection
- Docker container isolation
- User-friendly error messages with emojis

**Usage**:
```python
from gob.tools.code_execution import execute

# Execute Python code
result = execute('print("Hello from Docker!")')
# Returns: "Hello from Docker!"

# Execute Linux command
result = execute('ls -la', timeout=30)
```

**Error Handling**:
- 🐛 **Python errors**: Detailed traceback with troubleshooting tips
- ⏰ **Command timeouts**: Suggests increasing timeout limits
- 💥 **Bash errors**: Provides command-fixing guidance

### 2. Text Editor Tool
**Purpose**: File operations within the Docker Linux environment

**Features**:
- Read/write files in Docker container
- Text manipulation and processing
- File system operations
- Error handling with emojis

**Usage**:
```python
from gob.tools.text_editor import read, write

# Read file content
content = read('/tmp/data.txt')

# Write content to file
write('/tmp/output.txt', 'Docker container data')
```

**Error Handling**:
- 📁 **File not found**: Clear error messages
- 🔒 **Permission errors**: Suggests permission fixes

### 3. Search Engine Tool
**Purpose**: Web search functionality from Docker environment

**Features**:
- Web search with multiple engines
- Docker container network access
- Result processing and formatting
- Error handling with emojis

**Usage**:
```python
from gob.tools.search_engine import search

# Search the web
results = search('Python Docker containers')
# Returns: Search results with URLs and descriptions
```

**Error Handling**:
- 🔍 **Search failures**: Suggests alternative queries
- 🌐 **Network errors**: Provides connectivity guidance

### 4. Response Tool
**Purpose**: AI response generation and tool routing

**Features**:
- Response generation and routing
- Tool selection and execution
- Error handling and recovery
- Docker container integration

**Usage**:
```python
from gob.tools.response import response

# Generate response using available tools
result = response('Search for Python tutorials')
# Automatically selects and executes appropriate tools
```

**Error Handling**:
- 🤖 **AI errors**: Provides fallback options
- 🔧 **Tool errors**: Suggests alternative approaches

### 5. Document Query Tool
**Purpose**: Document processing and analysis within Docker

**Features**:
- Document reading and processing
- Text extraction and analysis
- Docker container file access
- Error handling with emojis

**Usage**:
```python
from gob.tools.document_query import document_query

# Process document
text = document_query('/tmp/document.pdf')
# Returns: Extracted text content
```

**Error Handling**:
- 📄 **Document errors**: Suggests supported formats
- 🔍 **Extraction errors**: Provides alternative methods

## Docker Container Integration

### Container Environment
All tools execute within Docker containers, providing:

- **Linux environment**: Full Linux command-line interface
- **Isolated execution**: Each tool runs in its own container space
- **Security**: Sandboxed operations prevent system damage
- **Consistency**: Same behavior across Windows, macOS, Linux

### Container File System
Tools can access:
- `/tmp/` - Temporary files within container
- `/workspace/` - Persistent workspace directory
- Project files mounted from host system

### Error Handling Philosophy

All tools implement **user-friendly error messages** with emojis:

- **🐛 Python errors**: Detailed traceback with troubleshooting
- **⏰ Timeouts**: Clear timeout messages with suggestions
- **💥 Bash errors**: Command-fixing guidance
- **📁 File errors**: File operation guidance
- **🔍 Search errors**: Alternative query suggestions

## Development Guidelines

### Adding New Tools

1. Create tool file in `src/gob/tools/`
2. Implement required functions with proper error handling
3. Register in `src/gob/core/tool_loader.py`
4. Add emoji-based error messages
5. Replace print statements with `log_to_chat()` function

### Error Message Standards

All tools must implement user-friendly error messages:
```python
# ❌ Bad: Basic error
print("Error occurred")

# ✅ Good: User-friendly error with emoji
log_to_chat("ERROR", "🐛 **Python Error**\n" + traceback + "\n\nTry: Check your syntax and variable names")
```

### Docker Integration

Tools should be designed for Docker container execution:
```python
def execute(code, timeout=30):
    """Execute code in Docker container with timeout protection"""
    try:
        # Execute in container
        result = run_in_container(code, timeout)
        return result
    except TimeoutError:
        log_to_chat("ERROR", "⏰ **Command Timeout**\nYour command took too long. Try: Increase timeout or simplify command")
    except Exception as e:
        log_to_chat("ERROR", f"🐛 **Execution Error**\n{str(e)}\n\nTry: Check your code syntax")
```

## Common Use Cases

### Python Development
```bash
# Execute Python code
python -m gob.main --tui
# Then: /execute print("Hello from Docker!")
```

### File Operations
```bash
# Read/write files in Docker
/execute with open('/tmp/data.txt', 'w') as f: f.write('Docker data')
```

### System Commands
```bash
# Run Linux commands
/execute ls -la /tmp/
```

### Web Search
```bash
# Search the web
/search Python Docker best practices
```

### Document Processing
```bash
# Process documents
/query /tmp/document.pdf
```

## Computer as Your Linux Development Machine

GOB transforms your computer into a **Linux development environment** through Docker containers. Each tool provides:

- **Complete Linux environment** with full command-line interface
- **Isolated execution** preventing system conflicts
- **Consistent behavior** across different operating systems
- **User-friendly interface** with emoji-based error messages
- **Secure sandboxing** protecting your host system

**Your computer becomes a powerful Linux development machine through GOB's Docker container system!**
