default: check

check: lint typecheck test

lint:
    uv run ruff check --fix
    uv run ruff format

typecheck:
    uv run basedpyright

test:
    uv run pytest --cov=pypatree --cov-report=term-missing --cov-fail-under=100

test-fast:
    uv run pytest -x -q
