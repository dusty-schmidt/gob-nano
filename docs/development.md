# Development Guide

## Project Structure

```
src/gob/
├── main.py              # Entry point
├── orchestrator.py      # Agent orchestration
├── core/                # Core components
│   ├── memory/          # Memory system
│   ├── llm_client.py    # LLM client
│   ├── logger.py        # Logging system
│   ├── setup_wizard.py  # Setup wizard
│   ├── config_loader.py # Configuration loader
│   ├── tool_loader.py   # Tool loader
│   └── agent_loader.py  # Agent loader
├── tools/               # Tool implementations
│   ├── code_execution.py
│   ├── text_editor.py
│   ├── search_engine.py
│   ├── response.py
│   ├── document_query.py
│   └── create_skill.py
├── io/                  # Interfaces
│   ├── tui_chat.py      # TUI interface
│   └── discord_bot.py   # Discord bot
└── plugins/             # Plugin system
    └── test_skill/
        └── SKILL.md
```

## Quick Start

```bash
git clone https://github.com/dusty-schmidt/gob-01.git
cd gob-01
pip install -e .
python -m gob.main --tui
```

## Development Workflow

### 1. Setup Development Environment

```bash
# Clone and install
pip install -e .

# Configure environment
cp .env.example .env  # Add your OLLAMA_CLOUD_API_KEY
```

### 2. Git Workflow & Automated Versioning

The project uses an automated versioning system to prevent conflicts:

```bash
# Create feature branch
git checkout -b micro-task-123-description

# Make changes and test
python -m gob.main --tui --help

# Auto-bump version (prevents conflicts)
./scripts/auto_version_bump_auto.sh patch

# Commit changes
git add .
git commit -m "micro-task-123: description - details"

# Push and create PR
git push origin micro-task-123-description
```

### 3. Testing

```bash
# Run tests
pytest tests/ -v

# Test specific component
python -c "from gob.tools.code_execution import execute; print(execute('print(\"test\")'))"
```

### 4. Version Management

```bash
# Version bump (automated, conflict-free)
./scripts/auto_version_bump_auto.sh patch

# Check version
./scripts/version_manager.sh get

# Sync version files
./scripts/version_manager.sh sync
```

## Configuration

### Environment Variables
Create `.env` file:
```
OLLAMA_CLOUD_API_KEY=your_key_here
```

### Configuration Files
- `config/config.yaml` - Main configuration
- `config/agents/default.yaml` - Agent settings

## Tool Development

### Adding a New Tool

1. Create tool file in `src/gob/tools/`
2. Implement required functions (execute, validate, etc.)
3. Register in `src/gob/core/tool_loader.py`
4. Add documentation in `docs/tools.md`

### Tool Requirements
- All tools must return user-friendly error messages
- Use emoji indicators for different states: 🐛 (bugs), ⏰ (timeouts), ✅ (success)
- Implement proper logging using the project's logger
- Replace print statements with log_to_chat function

## File Structure

```
gob/
├── src/gob/              # Source code
├── config/               # Configuration files
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── tests/                # Test files
├── docker/               # Docker configuration
├── VERSION               # Version file
├── .env                  # Environment variables
├── pyproject.toml        # Python project config
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## Common Commands

```bash
# Run TUI
python -m gob.main --tui

# Run Discord bot
python -m gob.main --discord

# Check version
python -m gob.main --version

# Run tests
pytest tests/ -v

# Version bump (automated)
./scripts/auto_version_bump_auto.sh patch

# Install git hooks
./scripts/git_hooks_installer.sh
```

## Troubleshooting

### Common Issues

1. **Import errors**: Check that all dependencies are installed
2. **Ollama API errors**: Verify your API key in `.env`
3. **Tool errors**: Check that tools are properly registered in tool_loader.py
4. **Memory errors**: Ensure memory directory has proper permissions
5. **Version conflicts**: Use `./scripts/version_manager.sh sync` to fix

### Getting Help

- Check `docs/configuration.md` for configuration details
- Check `docs/tools.md` for tool documentation
- Run `python -m gob.main --help` for CLI help

## Automated Versioning System

The project includes a comprehensive automated versioning system that prevents conflicts when multiple workers contribute:

### Features
- Lock-based conflict prevention
- Branch naming convention validation
- Automated version bumping
- Git hooks for validation
- Comprehensive error handling

### Usage
```bash
# Auto-bump version (prevents conflicts)
./scripts/auto_version_bump_auto.sh patch

# Manual version management
./scripts/version_manager.sh get
./scripts/version_manager.sh set 0.3.0
./scripts/version_manager.sh sync
```
