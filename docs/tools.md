# Tools (Early Phase)

## Quick Tool Selection

**Need to run code?** Use `/execute`  
**Need to edit files?** Use `/edit`  
**Need to search web?** Use `/search`  
**Need to read documents?** Use `/query`  

## What Each Tool Actually Does

### `/execute` - Code Runner
```
/execute print("hello")
/execute ls -la /tmp
```
**What could break:** Docker might be slow, code might crash

### `/edit` - File Editor  
```
/edit /tmp/test.txt
```
**What could break:** File permissions, Docker container limits

### `/search` - Web Search
```
/search python docker containers
```
**What could break:** Network issues, rate limits

### `/query` - Document Reader
```
/query /tmp/document.pdf "what is this about"
```
**What could break:** File format not supported, extraction fails

## Tool Limitations (We Know These Are Broken)
- All tools run in Docker - might be slow
- File size limits in containers
- Network access might be blocked
- Memory usage might leak

## When Tools Don't Work
1. Try the command without Docker: `python src/gob/tools/code_execution.py`
2. Check if Docker is running: `docker ps`
3. Report what broke: [GitHub issues link]