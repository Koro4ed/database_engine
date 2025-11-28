.PHONY: install project lint format build clean

install:
	poetry install

project:
	poetry run project

lint:
	poetry run ruff check .
	poetry run black --check .

format:
	poetry run ruff check --fix .
	poetry run black .

build:
	poetry build

clean:
	rm -rf dist build *.egg-info
	rm -rf data db_meta.json
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

run:
	poetry run project

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make project      - Run the database engine"
	@echo "  make lint         - Run linter checks"
	@echo "  make format       - Format code"
	@echo "  make build        - Build package"
	@echo "  make clean        - Clean build artifacts"
