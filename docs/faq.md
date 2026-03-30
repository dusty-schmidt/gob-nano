# FAQ

## Common Questions

### How do I use gob?

1. **Install:**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/dusty-schmidt/gob/main/scripts/install.sh | bash
   cd ~/.gob
   ```

2. **Configure:**
   ```bash
   nano .env  # Add OPENROUTER_API_KEY
   ```

3. **Run:**
   ```bash
   source venv/bin/activate
   python -m gob.main --mode tui
   ```

4. **Start chatting!** Type naturally, gob will detect when to use tools.

---

### What API do I need?

**Required:**
- OpenRouter API key ([OpenRouter.ai](https://openrouter.ai))

**Optional:**
- Discord bot token ([Discord Developer Portal](https://discord.com/developers))

---

### Does gob need internet?

**Yes** for:
- LLM calls (via OpenRouter)
- Web search
- Loading documentation

**No for:**
- Local file operations
- Basic text generation (once configured)

---

### Can I run gob locally?

**Currently:** Requires OpenRouter API (cloud)

**Future:** Can add local LLM via:
```bash
pip install ollama
ollama run qwen2.5
```

---

### How does gob handle tasks?

1. **Parse** your input
2. **Detect** tool needs (automatic)
3. **Execute** tools if needed
4. **Format** response
5. **Return** answer

Example:
```
You: "Summarize this PDF"
→ Detects document_query needed
→ Loads PDF
→ Extracts text
→ Summarizes
→ Returns summary
```

---

### Can I create custom agents?

**Yes!** Add YAML files to `config/agents/`:

**config/agents/coder.yaml**
```yaml
name: "Coder Agent"
description: "Specialized for software development"

context: |
  You are a software development assistant...

tools:
  - response
  - code_execution
  - text_editor
```

Gob auto-discovers all YAML files!

---

### How do I add new tools?

1. Create file in `src/gob/tools/my_tool.py`
2. Add to `src/gob/helpers/tool_loader.py` tools set
3. Expose in `src/gob/tools/__init__.py`
4. Enable in `config/config.yaml`

See [Development Guide](development.md) for full details.

---

### Can I disable tools?

Yes, for faster startup:

```yaml
tools:
  enabled:
    - response
    - code_execution
  disabled:
    - search_engine
    - document_query
```

Edit `config/config.yaml` and restart.

---

### How does memory work?

Lightweight JSONL persistence:
- Stores conversation history
- No vector database needed
- Loads on startup (~2 seconds)
- Saves to `src/gob/data/memory.jsonl`

For long-term memory:
```bash
python -m gob.main --mode validate  # Check memory loaded
```

---

### Can I run gob as a Discord bot?

**Yes**, once configured:

```bash
# Add Discord token to .env
DISCORD_BOT_TOKEN=your_token_here

# Run bot mode
python -m gob.main --mode discord
```

Requires bot permissions set up in Discord Developer Portal.

---

### What if a tool is missing?

Gob installs packages on-demand:

```
You: "Parse this PDF"
→ Gob: "Installing pypdf..."
→ Runs: pip install pypdf
→ Completes task
```

Manual installation:
```bash
pip install pypdf
apt-get install -y poppler-utils
```

---

### How to reset memory?

```bash
# Delete memory file
rm src/gob/data/memory.jsonl

# Or clear all
rm -rf src/gob/data/
```

Next run starts fresh.

---

### Can I change the LLM model?

Edit `config/config.yaml`:

```yaml
llm:
  model: qwen/qwen3.5-flash-02-23  # Change here
  temperature: 0.7
  max_tokens: 4096
```

Popular models:
- `qwen/qwen2.5-coder-32b-instruct` - Good for code
- `meta-llama/llama-3.1-8b-instruct` - Fast
- `anthropic/claude-3-haiku` - Concise

---

### How to update gob?

```bash
cd ~/.gob
git pull
pip install -e .
```

Changes are auto-loaded (no restart needed for config).

---

### What platforms are supported?

- Linux (tested)
- macOS (should work)
- Windows (WSL recommended)

Requires Python 3.9+.

---

### Troubleshooting

**"Config file not found"**
```bash
cd ~/.gob  # Ensure you're in project root
python -m gob.main
```

**"API key not configured"**
```bash
nano .env  # Add OPENROUTER_API_KEY
```

**"Module not found"**
```bash
pip install -e .
```

**"Port already in use"**
```bash
# Kill any existing processes
pkill -f gob.main
```

---

**More questions?** Check the [GitHub repo](https://github.com/dusty-schmidt/gob) or open an issue!
