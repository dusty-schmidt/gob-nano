# Mini-Agent-Zero Brainstorming Alignment v3.0

**Created:** 2026-03-29  
**Version:** 3.0 (YAML Agent Config System)  
**Status:** Finalized - Ready to Build

---

## Target Platform

- **Hardware:** Old laptops with 4-8GB RAM
- **OS:** Docker container with full Linux terminal
- **User:** Single user (no multi-user support needed)

---

## Core Objectives

1. Leaner Initial Codebase - Reduce complexity while maintaining 80-90% functionality
2. Docker Container First - Run agent inside container like parent Agent Zero
3. Terminal Access - Agent can execute terminal commands to install dependencies
4. YAML Agent Configs - Agents dynamically loaded from YAML files
5. Expandable Architecture - Start lean, add packages via apt-get/pip on-demand
6. Core Tasks Priority - Agent tasks > advanced integrations

---

## KEY FEATURE: YAML Agent Configuration System

### Concept:
Instead of separate directories for each agent profile (6 folders), agents become YAML config files in a single 'agents/' directory.

### How It Works:

EXAMPLE: agents/default.yaml
```yaml
name: Default Agent
description: General purpose AI assistant
model: qwen/qwen3.5-flash-02-23
context: Your default system prompt here
tools:
  - response
  - search_engine
  - code_execution
  - text_editor
  - document_query
max_tokens: 4096
temperature: 0.7
```

### Benefits:

| Before (Dir-per-profile) | After (YAML Configs) |
|--------------------------|-----------------------|
| 6 separate directories | Single agents/ folder |
| Hard-coded loading logic | Dynamic file discovery |
| Complex inheritance system | Simple flat structure |
| Must modify code to add agents | Just create YAML file |
| ~20 files | 3-5 YAML files |

### Runtime Agent Discovery:

```python
import os
import yaml
import glob

def load_agents():
    agents = []
    for yaml_file in glob.glob('agents/*.yaml'):
        with open(yaml_file, 'r') as f:
            config = yaml.safe_load(f)
            agents.append(config)
    return agents
```

---

## Final Decisions (v3.0) - March 29, 2026

### 1. Docker Container Architecture
Choice: Dockerfile + docker-compose.yml
- Full Linux environment (Debian/Ubuntu base)
- Agent runs like original Agent Zero inside container
- Terminal command execution enabled
- Agent can add features via terminal

### 2. Base Container
Choice: Lightweight Linux base (python:3.12-slim or debian:bookworm-slim)
- No bloat in base image
- Agent installs what it needs at runtime
- Terminal access = full flexibility

### 3. Web Scraping
Choice: playwright (full browser)
- Keep in initial install (can add via terminal if dropped)
- Trade-off: Heavier but more capable
- Agent can apt-get install chromium if needed

### 4. Memory System
Choice: JSON-only file-based memory
- Simple JSON/JSONL files, no FAISS
- No embeddings, no vector DB
- Can add SQLite later via pip install if needed
- Saves ~100MB+ on startup

### 5. LLM Provider
Choice: OpenRouter (qwen/qwen3.5-flash-02-23)
- External API - no local embeddings needed
- Saves ~50MB, simpler architecture
- Can switch to local models via terminal pip install

### 6. Agent Configuration System
Choice: YAML files (not separate directories)
- Single agents/ directory
- YAML config files define each agent
- Runtime auto-discovers YAML files
- User can create/edit agents like text files
- Saves 5+ profile directories, ~15-20 files

### 7. Configuration
Choice: Hardcoded defaults, single config file
- Single config.yaml for system settings
- No usr/ directory separation
- Settings hardcoded as defaults
- Easy to modify via YAML

### 8. Prompt System
Choice: Prompts embedded in YAML
- Single default.yaml defines default agent
- No additional .prompt.md files
- Prompts directly in YAML config
- Simplified structure, easier editing

### 9. WebUI Simplification
Choice: Remove complex settings menu
- No settings menu (all settings hardcoded)
- Simplified UI, no runtime configuration
- User modifies YAML files and restarts

---

## New Structure (YAML-Centric)

```
a0/
|-- Dockerfile              # Full Linux container setup
|-- docker-compose.yml      # Container orchestration
|-- requirements.txt        # 10-15 minimal dependencies
|-- config.yaml             # Main system config
|-- agents/                 # YAML agent configs
|   |-- default.yaml        # Default agent
|   |-- developer.yaml      # Developer agent (example)
|   |-- researcher.yaml     # Researcher agent (example)
|   |-- web-scraper.yaml    # Web scraping agent (example)
|-- tools/                  # 6-8 essential tools
|-- helpers/
|   |-- memory/            # JSON only
|   |-- config_loader.py   # Load YAML configs
|   |-- agent_loader.py    # Auto-discover agents
|   `-- utils/             # Helper functions
|-- workdir/               # User work
`-- tmp/                   # Temp files
```

### Agents Directory Structure:

```
agents/
|-- default.yaml           # Core agent (always available)
|-- developer.yaml         # Code specialist (optional)
|-- researcher.yaml        # Web search specialist (optional)
|-- admin.yaml            # System operations (optional)
```

### How Runtime Works:

1. Agent scans agents/ folder at startup
2. Loads all *.yaml files automatically
3. Presents agent options to user interface
4. Executes with selected agent configuration
5. User can add new agents by creating new YAML files

---

## Dependencies Plan (v3.0)

### Core (keep in Dockerfile - 10 packages)

```yaml
pyyaml>=6.0.1         # YAML parsing (NEW!)
playwright>=1.52.0
beautifulsoup4>=4.12.3
python-dotenv>=1.1.0
pydantic>=2.11.7
nest-asyncio>=1.6.0
watchdog>=6.0.0
pytz>=2024.2
tiktoken>=0.8.0
urllib3>=2.6.0
```

### Optional (install via terminal if needed)

```bash
# PDF processing
apt-get install poppler-utils
pip install pypdf pymupdf

# SQLite memory
pip install sqlalchemy

# Additional packages
pip install any-package-name
```

### Drops (remove entirely)

X faiss-cpu - Vector DB  
X sentence-transformers - Embeddings  
X a2wsgi - If not using Flask  
X docker - Use container, not manage it  
X paramiko - SSH dev tool  
X browser-use - Use playwright directly  
X flask-* - If simplified webui  
X Bluesky integrations  
X YouTube transcription tools  
X Complex task scheduler  

---

## YAML Agent Config Template

```yaml
# agents/default.yaml
name: "Default Agent"
description: "General purpose AI assistant"

model:
  provider: "openrouter"
  name: "qwen/qwen3.5-flash-02-23"
  max_tokens: 4096
  temperature: 0.7

context: |
  You are a helpful AI assistant.
  Execute tasks efficiently.
  Use tools when needed.
  Be concise but thorough.

tools:
  - response
  - search_engine
  - document_query
  - code_execution
  - text_editor

settings:
  max_iterations: 20
  retry_on_error: true
  auto_suggest_tools: true
```

---

## Key Simplifications with YAML Agents

### 1. Memory: FAISS to JSON
| Metric | Old | Lean | Savings |
|--------|-----|------|---------|
| Memory on startup | ~100MB+ | ~5MB | 95% |
| Complexity | Vector DB | JSON files | 80% |
| Loading time | 10-30s | 1-2s | 80% |
| Extendable? | N/A | Yes |

### 2. Agents: Dir-to-YAML
| Metric | Old | Lean | Savings |
|--------|-----|------|---------|
| Profile folders | 6 | 1 | 83% |
| Prompt files | ~20 | 4-5 YAMLs | 80% |
| Configuration | Complex | Simple | 70% |
| Modify agents? | Edit code | Edit YAML |

### 3. Dependencies: 45 packages to 10
| Metric | Old | Lean | Savings |
|--------|-----|------|---------|
| Dependencies | ~45 | ~10 | 78% |
| Disk space | ~500MB | ~150MB | 70% |
| Installation time | 5-10min | 1-2min | 80% |
| Add features? | Rebuild | pip install |

---

## Building the Lean Version (YAML-First)

### Next Steps (Action Plan):

1. [ ] Create Dockerfile - Full Linux container setup
2. [ ] Create docker-compose.yml - Container orchestration
3. [ ] Create requirements.txt - 10 initial dependencies (add pyyaml)
4. [ ] Create agents/default.yaml - Base agent config
5. [ ] Create agents/developer.yaml - Developer profile example
6. [ ] Create helpers/config_loader.py - YAML loading logic
7. [ ] Create helpers/agent_loader.py - Auto-discovery logic
8. [ ] Trim tools/ directory - 6-8 essential tools
9. [ ] Simplify helpers/memory/ - JSON-only, no FAISS
10. [ ] Document YAML format - User guide for creating agents

---

## Expected Outcome

| Metric | Traditional | YAML-First Lean |
|--------|-------------|-----------------|
| Functionality | 80-90% | 80-90% (expandable) |
| Codebase | 100% | ~30-40% |
| Dependencies | ~45 packages | ~10 (plus expandable) |
| Memory footprint | ~200-300MB | ~50-100MB (base) |
| Startup time | 60-90s | 15-30s |
| Flexibility | Build new image | YAML files + terminal |
| Agent customization | Edit code | Edit YAML files |
| Old laptop friendly | Yes | Better |
| Terminal access | No | YES! |
| Dynamic agents | No | YES! |

---

## Notes

- All decisions documented before implementation
- YAML agent configs = major simplification
- Terminal access is key feature for flexibility
- Start lean, expand via terminal commands
- Keep initial dependencies minimal
- Document how to create agents via YAML

---
All decisions confirmed - ready to build lean version with YAML agent configs

End of Mini-Agent-Zero Brainstorming Alignment Document v3.0
