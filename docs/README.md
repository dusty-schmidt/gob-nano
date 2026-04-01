# gob Documentation

These docs cover the current state of GOB v1.0.0 — a minimal AI agent framework with built-in safety.

## Contents

- [Architecture](architecture.md) — How the pieces fit together
- [Development](development.md) — How to work on GOB safely
- [Tools](tools.md) — Available tool reference
- [Configuration](configuration.md) — Config file reference

## Philosophy

gob is a **template** — a minimal, working starting point that you build from in any direction. Two GOB installs should never look the same because each one evolves to suit its owner's needs.

Core principles:
- **Computer as a tool** — Full Linux environment, install what you need
- **No framework lock-in** — Standard Python, standard libraries, no magic
- **Grow, don't bloat** — Start minimal, add only what you use
- **Safety by design** — Isolate execution, validate before merge, learn from failure

The last principle means: the agent never writes directly to `main`. Every code change runs in a sandboxed feature branch, passes validation, and only then merges. Failure produces a structured autopsy so the agent adapts instead of repeating mistakes.
