# GOB

Minimal AI agent framework. A template from which you can build in any direction.

## Philosophy

- **Computer as THE tool** — Rather than building dozens of specific micro-tools, GOB grants the agent broad system access. This is implemented via the `code_execution` module, allowing the agent to dynamically write and run code directly within a Linux container:
  - **Bash:** Executes raw shell commands with full system access. The agent can traverse the file system, install packages, use Git, and make network requests.
  - **Python:** Executes code strings natively via `exec()`, capable of performing data processing, logic, and rapid file manipulation.

- **Safety as THE requirement** - Stop letting your autonomous agents brick themselves in an infinite recursive loop. If your self-modifying code is just one bad hallucination away from a fatal system crash, you are building a time bomb, not an intelligent framework. It is time to treat your agent's brain like a strict production environment: force it to self-branch, sandbox the execution, and make the agent mathematically prove its code works in an automated CI/CD pipeline before it ever touches the main loop

## Quick Start

```bash
git clone https://github.com/dusty-schmidt/gob.git
cd gob
```

Create your `.env` file with your OpenRouter API key:

```bash
echo 'OPENROUTER_API_KEY=sk-or-your-key-here' > .env
```

Get a free key at [openrouter.ai/keys](https://openrouter.ai/keys)

### Run with Docker (recommended)

```bash
docker compose -f docker/docker-compose.yml up --build
```

### Run locally (for tinkering)

```bash
pip install -e .
python -m gob.run_gob --tui
```



## Version

1.0.0

## License

MIT
