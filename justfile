# Local dev
default: check dogfood regen-readme

# CI pipeline
ci: check smoke regen-readme

# Run pypatree on itself
dogfood:
    uv run pypatree


# Lint + typecheck + test (100% coverage)
check: lint typecheck test

# Regenerate README.md from template (README.md.in)
regen-readme:
    uv run python scripts/regen_readme.py

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

# Install pre-commit hooks
setup:
    uv run pre-commit install --hook-type pre-push

# Test on external packages
smoke:
    uv run python scripts/smoke_test.py
