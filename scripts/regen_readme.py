#!/usr/bin/env python
"""Generate README.md from README.md.in template."""

import sys

from lib import PYTHON_VERSION, ROOT, run, run_pypatree_on_repo

TEMPLATE = ROOT / "README.md.in"
OUTPUT = ROOT / "README.md"

SHOWCASE_REPO = "https://github.com/encode/httpx.git"
SHOWCASE_REVISION = "b5addb64f0161ff6bfe94c124ef76f6a1fba5254"
SHOWCASE_CONSTRAINTS = ROOT / "scripts" / "showcase-constraints.txt"


def generate() -> str:
    template = TEMPLATE.read_text()

    # Help output
    help_output = (
        run("uv", "run", "pypatree", "--help", cwd=ROOT).stdout.decode().strip()
    )
    template = template.replace("{{HELP_OUTPUT}}", help_output)

    # Self output
    self_output = run("uv", "run", "pypatree", cwd=ROOT).stdout.decode().strip()
    template = template.replace("{{PYPATREE_OUTPUT}}", self_output)

    # External repo showcase
    if "{{SHOWCASE_OUTPUT}}" in template:
        name = SHOWCASE_REPO.split("/")[-1].removesuffix(".git")
        url = SHOWCASE_REPO.removesuffix(".git")
        output = run_pypatree_on_repo(
            SHOWCASE_REPO,
            revision=SHOWCASE_REVISION,
            constraints=SHOWCASE_CONSTRAINTS,
        ).strip()
        template = template.replace("{{SHOWCASE_NAME}}", name)
        template = template.replace("{{SHOWCASE_URL}}", url)
        template = template.replace("{{SHOWCASE_REVISION}}", SHOWCASE_REVISION)
        template = template.replace("{{SHOWCASE_PYTHON}}", PYTHON_VERSION)
        template = template.replace("{{SHOWCASE_OUTPUT}}", output)

    return template


def main() -> int:
    generated = generate()

    if "--check" in sys.argv:
        if not OUTPUT.exists():
            print("README.md missing. Run: just readme")
            return 1
        if OUTPUT.read_text() != generated:
            print("README.md is stale. Run: just readme")
            return 1
        return 0

    OUTPUT.write_text(generated)
    print("README.md generated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
