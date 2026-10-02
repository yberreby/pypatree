#!/usr/bin/env python
"""Generate README.md from README.md.in template."""

import sys

import tyro

from lib import PYTHON_VERSION, ROOT, checkout_repo, run, run_pypatree_on_repo

TEMPLATE = ROOT / "README.md.in"
OUTPUT = ROOT / "README.md"

SHOWCASE_REPO = "https://github.com/encode/httpx.git"
SHOWCASE_REVISION = "b5addb64f0161ff6bfe94c124ef76f6a1fba5254"
SHOWCASE_CONSTRAINTS = ROOT / "scripts" / "showcase-constraints.txt"


def lock_showcase() -> None:
    with checkout_repo(SHOWCASE_REPO, revision=SHOWCASE_REVISION) as source:
        run(
            "uv",
            "pip",
            "compile",
            str(ROOT / "pyproject.toml"),
            str(source / "pyproject.toml"),
            "--extra",
            "cli",
            "--python-version",
            PYTHON_VERSION,
            "--no-header",
            "--no-annotate",
            "--no-emit-package",
            "pypatree",
            "--no-emit-package",
            "httpx",
            "--output-file",
            str(SHOWCASE_CONSTRAINTS),
        )


def _pypatree_output(*args: str) -> str:
    return (
        run("uv", "run", "--python", PYTHON_VERSION, "pypatree", *args, cwd=ROOT)
        .stdout.decode()
        .strip()
    )


def generate() -> str:
    template = TEMPLATE.read_text()
    template = template.replace("{{HELP_OUTPUT}}", _pypatree_output("--help"))
    template = template.replace("{{PYPATREE_OUTPUT}}", _pypatree_output())

    template = template.replace(
        "{{FLAT_OUTPUT}}", _pypatree_output("pypatree.introspection", "--flat")
    )

    # External repo showcase
    if "{{SHOWCASE_OUTPUT}}" in template:
        name = SHOWCASE_REPO.split("/")[-1].removesuffix(".git")
        url = SHOWCASE_REPO.removesuffix(".git")
        output = run_pypatree_on_repo(
            SHOWCASE_REPO,
            revision=SHOWCASE_REVISION,
            constraints=SHOWCASE_CONSTRAINTS,
            extras=("cli",),
        ).strip()
        template = template.replace("{{SHOWCASE_NAME}}", name)
        template = template.replace("{{SHOWCASE_URL}}", url)
        template = template.replace("{{SHOWCASE_REVISION}}", SHOWCASE_REVISION)
        template = template.replace("{{SHOWCASE_PYTHON}}", PYTHON_VERSION)
        template = template.replace("{{SHOWCASE_OUTPUT}}", output)

    return "\n".join(line.rstrip() for line in template.splitlines()) + "\n"


def main(check: bool = False, update_constraints: bool = False) -> int:
    if update_constraints:
        lock_showcase()
    generated = generate()

    if check:
        if not OUTPUT.exists():
            print("README.md missing. Run: uv run just regen-readme")
            return 1
        if OUTPUT.read_text() != generated:
            print("README.md is stale. Run: uv run just regen-readme")
            return 1
        return 0

    OUTPUT.write_text(generated)
    print("README.md generated")
    return 0


if __name__ == "__main__":
    sys.exit(tyro.cli(main))
