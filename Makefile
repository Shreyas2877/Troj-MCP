.PHONY: help install test lint format check-coverage clean build docker-build docker-run

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install pre-commit
	pre-commit install

test: ## Run tests with coverage
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

test-fast: ## Run tests without coverage
	pytest tests/ -v

lint: ## Run linting with Ruff
	ruff check src/ tests/

format: ## Format code with Ruff
	ruff format src/ tests/

format-check: ## Check code formatting
	ruff format src/ tests/ --check --diff

check-coverage: ## Check coverage per file (minimum 60%)
	python scripts/check_coverage.py

type-check: ## Run type checking with mypy
	mypy src/ --ignore-missing-imports

security: ## Run security checks
	safety check
	bandit -r src/

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	python -m build

docker-build: ## Build Docker image
	docker build -t macro-man:latest .

docker-run: ## Run Docker container
	docker run --rm -p 8000:8000 macro-man:latest

ci: ## Run all CI checks locally
	@echo "🔍 Running linting..."
	ruff check src/ tests/
	@echo "🎨 Checking formatting..."
	ruff format src/ tests/ --check --diff
	@echo "🔍 Running type checks..."
	mypy src/ --ignore-missing-imports
	@echo "🧪 Running tests..."
	pytest tests/ -v --cov=src --cov-report=xml --cov-report=html --cov-report=term-missing
	@echo "📊 Checking coverage per file..."
	python scripts/check_coverage.py
	@echo "✅ All CI checks passed!"

dev: ## Start development server
	python main.py

dev-stdio: ## Start development server in stdio mode
	python main_stdio.py

setup: install-dev ## Complete setup for development
	@echo "🎉 Setup complete! You can now run:"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Run linting"
	@echo "  make format   - Format code"
	@echo "  make ci       - Run all CI checks"
	@echo "  make dev      - Start development server"
