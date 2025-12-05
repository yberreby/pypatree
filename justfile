# Local dev
default: check dogfood

# CI pipeline
ci: check smoke readme

# Run pypatree on itself
dogfood:
    uv run pypatree

# Install pre-commit hooks
setup:
    uv run pre-commit install --hook-type pre-push

# Lint + typecheck + test (100% coverage)
check: lint typecheck test

# Regenerate README.md from template
readme:
    uv run python scripts/update_readme.py

# Verify README.md is up to date
readme-check:
    uv run python scripts/update_readme.py --check

# Fix and format with ruff
lint:
    uv run ruff check --fix
    uv run ruff format

# Type check with basedpyright
typecheck:
    uv run basedpyright

# Run tests with coverage
test:
    uv run pytest --cov=pypatree --cov-report=term-missing --cov-fail-under=100

# Quick test run
test-fast:
    uv run pytest -x -q

# Test on external packages
smoke:
    uv run python scripts/smoke_test.py
