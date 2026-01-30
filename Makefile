.PHONY: help install install-dev test lint format clean docker-build docker-run

help:
	@echo "Code Agent - Makefile commands:"
	@echo ""
	@echo "  install         Install production dependencies"
	@echo "  install-dev     Install development dependencies"
	@echo "  test            Run tests with coverage"
	@echo "  lint            Run linters (ruff, mypy)"
	@echo "  format          Format code with black"
	@echo "  clean           Clean build artifacts and caches"
	@echo "  docker-build    Build Docker image"
	@echo "  docker-run      Run in Docker"
	@echo ""

install:
	pip install -r requirements.txt
	pip install -e .

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install -e .

test:
	pytest --cov=code_agent --cov-report=html --cov-report=term-missing -v

lint:
	@echo "Running ruff..."
	ruff check .
	@echo "Running mypy..."
	mypy code_agent --ignore-missing-imports
	@echo "Running black check..."
	black --check .

format:
	@echo "Formatting with black..."
	black .
	@echo "Auto-fixing with ruff..."
	ruff check --fix .

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

docker-build:
	docker-compose build

docker-run:
	docker-compose run code-agent --help

