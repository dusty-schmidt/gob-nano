# GOB-Nano Makefile - Strict Remote Sync Workflow
#
# Usage:
#   make dev     # Start work (auto-pulls latest from remote)
#   make push    # End work (auto-pulls, then pushes)
#   make test    # Run test suite
#   make lint    # Code linting
#   make clean   # Clean build artifacts
#   make status  # Quick status check

.PHONY: dev test lint clean push status help

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

help:
	@echo "$(BLUE)GOB-Nano Development Commands$(NC)"
	@echo "================================"
	@echo "$(GREEN)dev$(NC)     - Start work (auto-pulls from remote)"
	@echo "$(GREEN)push$(NC)    - End work (auto-pulls, then pushes)"
	@echo "$(GREEN)test$(NC)    - Run test suite"
	@echo "$(GREEN)lint$(NC)    - Run code linting"
	@echo "$(GREEN)clean$(NC)   - Clean build artifacts"
	@echo "$(GREEN)status$(NC)  - Quick status check"

# Internal: Sync with remote (pull with rebase)
.sync:
	@echo "$(BLUE)Syncing with remote...$(NC)"
	@git pull --rebase origin main
	@echo "$(GREEN)✓ Sync complete$(NC)"

# Start work - ALWAYS sync first
dev: .sync
	@echo "$(GREEN)✓ Ready for development$(NC)"
	@echo "$(YELLOW)Work on your changes, then run 'make push' to sync$(NC)"

# Run tests
test:
	@echo "$(BLUE)Running tests...$(NC)"
	@python -m pytest tests/ -v

# Code linting
lint:
	@echo "$(BLUE)Running linting...$(NC)"
	@python -m ruff check src/
	@python -m ruff check scripts/

# Clean build artifacts
clean:
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -type f -delete 2>/dev/null || true
	@find . -name "*.pyo" -type f -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

# End work - auto-sync, then push
push: .sync
	@echo "$(BLUE)Pushing to remote...$(NC)"
	@git push origin main
	@echo "$(GREEN)✓ Push complete$(NC)"

# Quick status check
status:
	@echo "$(BLUE)Repository Status:$(NC)"
	@git status --short