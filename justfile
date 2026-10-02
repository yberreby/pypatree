# Local dev
default: check dogfood regen-readme

# CI pipeline
ci: check smoke check-readme package-check

# Run pypatree on itself
dogfood:
    uv run pypatree


# Lint + typecheck + test (100% coverage)
check: lint typecheck test

# Regenerate README.md from template (README.md.in)
regen-readme:
    uv run python scripts/regen_readme.py

# Check formatting without modifying the checkout
lint:
    uv run ruff check
    uv run ruff format --check

format:
    uv run ruff check --fix
    uv run ruff format

check-readme:
    uv run python scripts/regen_readme.py --check

package-check:
    uv run python scripts/check_dist.py

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
