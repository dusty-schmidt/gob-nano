# Available Tools

Explore what Gob can do.

## Core Tools (5)

Gob comes with these built-in capabilities:

| Tool | Description | When it's used |
|------|-------------|----------------|
| `response` | Generates text-based responses | Default fallback |
| `search_engine` | Web search via search API | Looking for information, news, facts |
| `code_execution` | Execute Linux/Python code | Data analysis, calculations, automation |
| `text_editor` | Read/write/patch files | Editing code, creating docs, modifying configs |
| `document_query` | Read PDFs, docs, web pages | Analyzing documents, extracting content |

## How Tools Work

### Automatic Detection

Gob detects when a tool is needed. You don't need to request specific tools:

```
User: "What's the current weather in Tokyo?"
→ Gob detects need for info
→ Uses search_engine automatically
→ Returns weather details
```

### Runtime Package Installation

If a task requires a package Gob doesn't have, it will install it:

```
User: "Parse this PDF for me..."
→ Gob detects PyPDF needed
→ Runs: pip install pypdf
→ Completes task
```

## Tool Examples

### Search Engine

**When to use:** Finding current information, news, technical docs

**Automatic in:**
- "What are the top AI trends this year?"
- "Find documentation for Python decorators"
- "Latest news about space exploration"

---

### Code Execution

**When to use:** Data analysis, calculations, automation tasks

**Capabilities:**
- Linux shell commands (bash, curl, grep, etc.)
- Python scripts
- Node.js snippets

**Automatic in:**
- "Calculate statistics from this data"
- "List files in this directory"
- "Convert this CSV to JSON"

---

### Text Editor

**When to use:** Reading, writing, or modifying files

**Capabilities:**
- Read entire files or line ranges
- Create new files
- Patch specific line ranges
- No binary file support

**Automatic in:**
- "What's in this config file?"
- "Create a Python script that does X"
- "Update this function to..."

---

### Document Query

**When to use:** Reading PDFs, Office documents, web pages

**Capabilities:**
- Extract text from PDFs
- Read HTML pages
- Query document contents

**Automatic in:**
- "Summarize this PDF"
- "What's on this webpage?"
- "Extract text from this document"

---

### Response (Base)

**When to use:** Text-based answers, explanations, creative content

**Always available as fallback**

---

## Extending Capabilities

### Install New Tools

Add capabilities at runtime:

```bash
# Install PDF tools
pip install pypdf pdfplumber
apt-get install -y poppler-utils

# Install browser automation
pip install playwright
playwright install chromium

# Install database drivers
pip install sqlite3 psycopg2
```

Gob remembers what's installed and uses it when needed.

### Check Available Tools

```bash
python -m gob.main --mode validate
```

Shows all loaded tools and their status.

---

**Next:** [Development guide](development.md) · [FAQ](faq.md)
