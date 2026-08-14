# wDVC MCP Makefile

.PHONY: help install test test-cov lint format typecheck build publish clean

help:
	@echo "wDVC MCP - Available targets:"
	@echo "  install      - Install package in development mode"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run ruff and pylint"
	@echo "  format       - Format code with ruff"
	@echo "  typecheck    - Run mypy type checking"
	@echo "  build        - Build package (sdist + wheel)"
	@echo "  publish      - Publish to PyPI"
	@echo "  clean        - Clean build artifacts"

install:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ --cov=wdvc_mcp --cov-report=term-missing --cov-report=html

lint:
	python -m ruff check src/ tests/
	python -m pylint src/ --rcfile=pylintrc

format:
	python -m ruff format src/ tests/
	python -m ruff check src/ tests/ --fix

typecheck:
	python -m mypy src/ --ignore-missing-imports

build:
	python -m build --no-isolation

publish: build
	twine upload dist/*

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .ruff_cache/ .mypy_cache/ htmlcov/ .coverage