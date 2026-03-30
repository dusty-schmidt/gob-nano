# Makefile for NANO project – common shortcuts

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
PYTHON ?= python3
PIP ?= pip

# Directories
SRC_DIR := src/gob
SCRIPTS_DIR := scripts
DOCKER_DIR := docker

# -------------------------------------------------------------------
# Targets
# -------------------------------------------------------------------
.PHONY: all install lint test build run setup clean migrate

# Default target – show help
all:
	@echo "Available make commands:"
	@echo "  install   – install package in editable mode"
	@echo "  lint      – run code quality checks (isort, black, flake8)"
	@echo "  test      – run pytest with coverage"
	@echo "  build     – build Docker image (gob-agent)"
	@echo "  run       – start Docker container (background)"
	@echo "  setup     – launch interactive setup wizard"
	@echo "  clean     – remove build artefacts and temporary files"
	@echo "  migrate   – migrate old config/memory to new layout"

# Install package in editable mode (development)
install:
	$(PYTHON) -m $(PIP) install -e .

# Lint code with isort, black, flake8
lint:
	$(PYTHON) -m $(SCRIPTS_DIR)/lint.py

# Run tests (requires pytest & coverage)
test:
	$(PYTHON) -m scripts.test

# Build Docker image
build:
	$(PYTHON) -m $(SCRIPTS_DIR)/build.py

# Run Docker container (background)
run:
	$(PYTHON) -m $(SCRIPTS_DIR)/build.py run

# Interactive setup wizard (creates config.yaml and memory file)
setup:
	$(PYTHON) -m $(SCRIPTS_DIR)/setup.py

# Clean up temporary files, __pycache__, build artefacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf $(SRC_DIR)/__pycache__ $(SCRIPTS_DIR)/__pycache__
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov

# Migrate old config/memory (if any) to new layout
migrate:
	$(PYTHON) -m $(SCRIPTS_DIR)/migrate.py

# -------------------------------------------------
# Push to GitHub via SSH (no password needed)
# -------------------------------------------------
push-ssh:
git push origin main

# -------------------------------------------------
# YOLO install – one‑command setup & start
# -------------------------------------------------
yolo:
	@./scripts/install.sh
