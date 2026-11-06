# Local dev
default: check dogfood regen-readme

# CI pipeline
ci: check smoke check-readme package-check

# Lint + typecheck + test (100% coverage)
check: lint typecheck test

# Check formatting without modifying the checkout
lint:
    uv run ruff check
    uv run ruff format --check

# Fix and format with ruff
format:
    uv run ruff check --fix
    uv run ruff format

# Type check with basedpyright
typecheck:
    uv run basedpyright

# Run tests with coverage
test:
    uv run pytest --cov=pypatree --cov-report=term-missing --cov-fail-under=100

# Run pypatree on itself
dogfood:
    uv run pypatree

# Regenerate README.md from template (README.md.in)
regen-readme:
    uv run python scripts/regen_readme.py

# Fail if README.md is stale
check-readme:
    uv run python scripts/regen_readme.py --check

# Build, inspect, and run the wheel and sdist
package-check:
    uv run python scripts/check_dist.py

# Test on external packages
smoke:
    uv run python scripts/smoke_test.py

# Install pre-commit hooks
setup:
    uv run pre-commit install --hook-type pre-push
