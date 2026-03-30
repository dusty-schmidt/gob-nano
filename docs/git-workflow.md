# Git Workflow for Gob-Nano

## Branch Strategy: GitHub Flow (Simple)

```
main ──────────────────────────────────── (always deployable)
     └── task/feature-name              (your work)
```

- `main` is the only permanent branch
- Task branches branch from `main`, merge back to `main`
- One task = one branch = one merge to main

---

## Workflow Steps

### 1. STARTING A NEW TASK

```bash
git checkout main
git pull origin main
git checkout -b task/short-description
```

**Example:**
```bash
git checkout -b task/add-yaml-agent-configs
```

### 2. WHILE WORKING

Commit early and often:

```bash
git add .
git commit -m "Brief description of changes"
```

**Tip:** Small commits with clear messages make debugging easier.

### 3. BEFORE MERGING

**ALWAYS run tests AND lint, fix any issues:**

```bash
# Run the test suite
python scripts/test.py

# Run lint check
python scripts/lint.py

# If tests fail or lint finds issues, fix them before proceeding
```

**Lint issues must be fixed - do not skip or ignore warnings.**

### 4. MERGING TO MAIN

```bash
git checkout main
git pull origin main
git merge task/your-branch-name
git push origin main
git branch -d task/your-branch-name
```

### 5. CLEANING UP

After pushing, delete the local branch:

```bash
git branch -d task/your-branch-name
```

---

## Quick Reference

| Situation | Command |
|----------|---------|
| Start new task | `git checkout -b task/name` |
| Save work | `git add . && git commit -m "message"` |
| Run tests | `python scripts/test.py` |
| Run lint | `python scripts/lint.py` |
| See status | `git status` |
| See history | `git log --oneline` |
| Switch branch | `git checkout branch-name` |
| Update from main | `git pull origin main` |
| Merge to main | `git checkout main && git merge branch-name && git push` |
| Delete branch | `git branch -d branch-name` |

---

---

## Rules

1. **ALWAYS** branch from `main`
2. **ALWAYS** run `python scripts/test.py` before merging
3. **ALWAYS** run `python scripts/lint.py` and fix all issues before merging
4. **ALWAYS** pull `main` before creating a new branch
5. **ALWAYS** delete task branches after merging
6. **NEVER** push directly to `main` (always use a task branch)
7. **NEVER** skip or ignore lint warnings

---

## Branch Naming

Use `task/` prefix with a short description:

| Good | Bad |
|------|-----|
| `task/add-yaml-configs` | `my-work` |
| `task/fix-memory-bug` | `branch1` |
| `task/update-dockerfile` | `latest` |

---

## If Something Goes Wrong

**Accidentally worked on main:**
```bash
git stash
git checkout -b task/fix-mistake
git stash pop
```

**Need to undo last commit:**
```bash
git reset --soft HEAD~1  # keep changes staged
git reset HEAD~1         # discard changes
```
