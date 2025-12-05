default: check dogfood

dogfood:
    # Let's print our own tree!
    uv run pypatree

setup:
    uv run pre-commit install --hook-type pre-push

check: lint typecheck test

readme:
    uv run python scripts/update_readme.py

readme-check:
    uv run python scripts/update_readme.py --check

lint:
    uv run ruff check --fix
    uv run ruff format

typecheck:
    uv run basedpyright

test:
    uv run pytest --cov=pypatree --cov-report=term-missing --cov-fail-under=100

test-fast:
    uv run pytest -x -q
