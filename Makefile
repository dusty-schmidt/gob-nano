# GOB Makefile
#
# Usage:
#   make run      # Start the TUI
#   make dev      # Pull latest, start working
#   make ship     # Commit, merge to main, push (branch workflow)
#   make push     # Quick add-commit-push on main
#   make test     # Run test suite
#   make clean    # Clean build artifacts
#   make status   # Git status

.PHONY: run dev test clean push ship status help

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

help:
	@echo "$(BLUE)GOB Development Commands$(NC)"
	@echo "========================"
	@echo "$(GREEN)run$(NC)     - Start TUI chat"
	@echo "$(GREEN)dev$(NC)     - Sync with remote, ready for work"
	@echo "$(GREEN)ship$(NC)    - Commit + push (prompts for message)"
	@echo "$(GREEN)test$(NC)    - Run test suite"
	@echo "$(GREEN)clean$(NC)   - Clean build artifacts"
	@echo "$(GREEN)status$(NC)  - Git status"

# Run the TUI
run:
	@python -m gob.run_gob --tui

# Sync with remote
dev:
	@echo "$(BLUE)Syncing with remote...$(NC)"
	@git pull --rebase origin main
	@echo "$(GREEN)✓ Ready for development$(NC)"

# Quick commit and push on main
ship:
	@echo "$(BLUE)Shipping...$(NC)"
	@git add -A
	@read -p "Commit message: " msg; git commit -m "$$msg"
	@git push origin main
	@echo "$(GREEN)✓ Shipped$(NC)"

# Run tests
test:
	@echo "$(BLUE)Running tests...$(NC)"
	@python -m pytest tests/ -v

# Clean build artifacts
clean:
	@echo "$(BLUE)Cleaning...$(NC)"
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -type f -delete 2>/dev/null || true
	@rm -rf build/ *.egg-info/ src/*.egg-info/
	@echo "$(GREEN)✓ Clean$(NC)"

# Git status
status:
	@git status --short
	@echo ""
	@git log --oneline -5