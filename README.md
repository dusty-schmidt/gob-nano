# GOB

Minimal AI agent framework. A template from which you can build in any direction.

## Philosophy

**Computer as THE tool** — Rather than building dozens of specific micro-tools, GOB grants the agent broad system access. This is implemented via the `code_execution` module, allowing the agent to dynamically write and run code directly within a Linux container:
**Bash:** Executes raw shell commands with full system access. The agent can traverse the file system, install packages, use Git, and make network requests.
**Python:** Executes code strings natively via `exec()`, capable of performing data processing, logic, and rapid file manipulation.


## Safety

GOB is built with a self-protecting architecture. It prevents the agent from damaging its own environment by enforcing four pillars:

 **Isolation** — Code execution runs inside a resource-capped Docker container (`512MB RAM`, `1 CPU`). Infinite loops or memory leaks cannot brick the host.
 **Validation** — Every tool is contract-checked (docstrings, signatures) before loading. Merges require syntax and test gates.
 **Autopsy** — Failures produce structured reports (`Exit Code → Classification → Suggested Recovery`) which are injected back into the agent's context, forcing adaptation.
 **Automated Merge** — Code is never written directly to `main`. Changes land on feature branches, pass validation inside the sandbox, and merge only on success.

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
