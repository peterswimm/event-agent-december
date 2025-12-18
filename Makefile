.PHONY: help test lint format run docker-build docker-run docker-stop clean install dev

# Default target
help:
	@echo "EventKit Agent - Available Commands:"
	@echo ""
	@echo "  make install      Install production dependencies"
	@echo "  make dev          Install development dependencies"
	@echo "  make test         Run all tests with coverage"
	@echo "  make lint         Run linting checks (black, isort, pylint)"
	@echo "  make format       Auto-format code with black and isort"
	@echo "  make run          Run the agent server locally"
	@echo "  make docker-build Build Docker image"
	@echo "  make docker-run   Run Docker container"
	@echo "  make docker-stop  Stop Docker container"
	@echo "  make clean        Remove cached files and build artifacts"
	@echo "  make setup        One-time setup (install pre-commit hooks)"

# Installation targets
install:
	pip install --upgrade pip
	pip install -r requirements.txt

dev: install
	pip install -r requirements-dev.txt
	pre-commit install

setup: dev
	@echo "✓ Development environment ready!"
	@echo "  Pre-commit hooks installed"
	@echo "  Run 'make test' to verify setup"

# Testing
test:
	pytest -v --cov=. --cov-report=term-missing --cov-report=html

test-fast:
	pytest -v -x --tb=short

# Linting
lint:
	@echo "Running Black..."
	black --check --diff .
	@echo "\nRunning isort..."
	isort --check-only --diff .
	@echo "\nRunning pylint..."
	pylint --rcfile=.pylintrc $$(git ls-files '*.py')

format:
	black .
	isort .

# Running locally
run:
	python agent.py

run-dev:
	PYTHONUNBUFFERED=1 python agent.py

# Docker commands
docker-build:
	docker build -t eventkit-agent:latest -f deploy/Dockerfile .

docker-run:
	docker-compose -f deploy/docker-compose.yml up -d

docker-stop:
	docker-compose -f deploy/docker-compose.yml down

docker-logs:
	docker-compose -f deploy/docker-compose.yml logs -f

docker-shell:
	docker exec -it eventkit-agent /bin/bash

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -delete 2>/dev/null || true
	rm -rf htmlcov/ .mypy_cache/ .tox/ dist/ build/

# Azure deployment
deploy-dev:
	az deployment group create \
		--resource-group $${AZURE_RESOURCE_GROUP} \
		--template-file infra/main.bicep \
		--parameters infra/dev.bicepparam

deploy-prod:
	az deployment group create \
		--resource-group $${AZURE_RESOURCE_GROUP} \
		--template-file infra/main.bicep \
		--parameters infra/prod.bicepparam

# Utility targets
health:
	curl http://localhost:8010/health

version:
	@python -c "import sys; print(f'Python {sys.version}')"
	@pip show msal msgraph-core pydantic-settings
