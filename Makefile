# GOB-Nano Makefile - Strict Remote Sync Workflow
#
# Usage:
#   make install     # One-command installation
#   make dev         # Development workflow (pull -> work -> push)
#   make test        # Run tests
#   make lint        # Code linting
#   make clean       # Clean build artifacts
#   make push        # Push with sync check
#   make pull        # Pull with rebase
#   make status      # Quick status check

.PHONY: install dev test lint clean push pull status help

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

help:
	@echo "$(BLUE)GOB-Nano Development Commands$(NC)"
	@echo "================================"
	@echo "$(GREEN)install$(NC) - One-command installation"
	@echo "$(GREEN)dev$(NC) - Development workflow (pull → work → push)"
	@echo "$(GREEN)test$(NC) - Run test suite"
	@echo "$(GREEN)lint$(NC) - Run code linting"
	@echo "$(GREEN)clean$(NC) - Clean build artifacts"
	@echo "$(GREEN)push$(NC) - Push with remote sync check"
	@echo "$(GREEN)pull$(NC) - Pull with rebase"
	@echo "$(GREEN)status$(NC) - Quick status check"

# One-command installation
install:
	@echo "$(BLUE)Installing GOB-Nano...$(NC)"
	@echo "$(YELLOW)Note: Repository is now at 'gob-01' on GitHub$(NC)"
	@bash scripts/install.sh

# Development workflow - ALWAYS sync with remote first
dev:
	@echo "$(BLUE)Starting development workflow...$(NC)"
	@make pull
	@echo "$(GREEN)✓ Ready for development - remote is in sync$(NC)"
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

# Push with strict remote sync check
# Push with strict remote sync check
push:
	@echo "$(BLUE)Checking remote sync...$(NC)"
	@git fetch origin
	@BEHIND=$$(git rev-list HEAD...origin/main --count); \
	if [ "$$BEHIND" != "0" ]; then \
		echo "$(RED)❌ Remote has changes - run 'make pull' first$(NC)"; \
		echo "   Remote is ahead by $$BEHIND commits"; \
		exit 1; \
	fi
	@echo "$(BLUE)Pushing to remote...$(NC)"
	@git push origin main
	@echo "$(GREEN)✓ Push successful - remote is in sync$(NC)"
# Pull with rebase to maintain clean history
pull:
	@echo "$(BLUE)Pulling latest changes...$(NC)"
	@git pull --rebase origin main
	@echo "$(GREEN)✓ Pull complete - local is up to date$(NC)"

# Quick status check
status:
	@echo "$(BLUE)Repository Status:$(NC)"
	@git status --short