.PHONY: help install dev lint format test test-cov typecheck serve docker-build docker-up clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -e .

dev: ## Install dev + production dependencies & pre-commit hooks
	pip install -e ".[dev]"
	pre-commit install

lint: ## Run ruff linter
	ruff check .

format: ## Auto-format code with ruff
	ruff format .
	ruff check --fix .

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage report
	pytest --cov=expert_spork --cov-report=term-missing

typecheck: ## Run mypy type-checker
	mypy src/

serve: ## Start dev server with hot reload
	SPORK_DEBUG=true uvicorn expert_spork.main:app --reload --host 0.0.0.0 --port 8000

docker-build: ## Build Docker image
	docker build -t expert-spork .

docker-up: ## Start services via docker-compose
	docker compose up -d

clean: ## Remove build artifacts
	rm -rf dist build *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
