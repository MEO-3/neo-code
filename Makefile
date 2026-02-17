.PHONY: run test lint clean install dev setup

PYTHON = python3
PIP = pip3

# Run the application
run:
	$(PYTHON) -m neo_code

# Install dependencies
install:
	$(PIP) install -r requirements.txt

# Install dev dependencies
dev:
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .

# Setup complete development environment
setup: dev
	@echo "Development environment ready!"

# Run tests
test:
	$(PYTHON) -m pytest tests/ -v --tb=short

# Run tests with coverage
test-cov:
	$(PYTHON) -m pytest tests/ -v --cov=src/neo_code --cov-report=html

# Lint code
lint:
	$(PYTHON) -m ruff check src/ tests/
	$(PYTHON) -m mypy src/neo_code/

# Format code
format:
	$(PYTHON) -m ruff format src/ tests/

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Build package
build:
	$(PYTHON) -m build
