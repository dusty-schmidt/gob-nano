# Development

## Structure
```
src/gob/
├── main.py        # Entry point
├── orchestrator.py
├── tools/         # Tool implementations
├── helpers/       # Config, memory, LLM
└── interfaces/    # TUI, Discord
```

## Setup
```bash
git clone https://github.com/dusty-schmidt/gob.git
cd gob
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Tests
```bash
pytest tests/ -v
```

## Workflow
```bash
git checkout -b task/name
# work
pytest tests/ -v
python -m scripts.lint
git checkout main
git merge task/name
git push
```