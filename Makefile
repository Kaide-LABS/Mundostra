.PHONY: install dev test lint typecheck run clean \
       frontend-install frontend-dev frontend-build frontend-lint frontend-format frontend-typecheck

install:
	pip install -e .

dev:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest -v

lint:
	ruff check backend/
	ruff format --check backend/

format:
	ruff check --fix backend/
	ruff format backend/

typecheck:
	mypy backend/ --ignore-missing-imports

run:
	uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +

# ── Frontend ────────────────────────────────────────────

frontend-install:
	cd frontend && npm ci

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

frontend-lint:
	cd frontend && npm run lint

frontend-format:
	cd frontend && npm run format:check

frontend-typecheck:
	cd frontend && npm run typecheck
