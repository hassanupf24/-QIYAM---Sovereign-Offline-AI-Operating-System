.PHONY: install format lint test run docker-build docker-up docker-down clean

# Environment variables
PYTHON = python
PIP = pip
PYTEST = pytest

install:
	$(PIP) install -r requirements.txt
	$(PIP) install -e .[dev]

format:
	black .
	isort .

lint:
	flake8 .
	mypy .
	black --check .
	isort --check-only .

test:
	$(PYTEST)

security:
	bandit -r . -x ./tests,./frontend,./venv,./.venv

test-all: lint test security

run:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker-compose -f docker/docker-compose.yml build

docker-up:
	docker-compose -f docker/docker-compose.yml up -d

docker-down:
	docker-compose -f docker/docker-compose.yml down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/ dist/ *.egg-info/
