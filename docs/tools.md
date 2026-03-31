# Tools

Core tools:
- `response` - Text responses
- `search_engine` - Web search
- `code_execution` - Run code
- `text_editor` - File operations
- `document_query` - Read docs

## Usage
Tools auto-detected. No manual selection needed.

## Examples
```
"What's the weather?" → search_engine
"Calculate this" → code_execution
"Edit this file" → text_editor
```

## Extend
```bash
pip install pypdf
apt-get install poppler-utils
```

## Check Tools
```bash
python -m gob.main --mode validate
```