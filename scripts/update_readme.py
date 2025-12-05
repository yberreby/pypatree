#!/usr/bin/env python
"""Generate README.md from README.md.in template."""

import subprocess
import sys

from lib import ROOT, run_pypatree_on_repo

TEMPLATE = ROOT / "README.md.in"
OUTPUT = ROOT / "README.md"

# External repo to showcase (easily configurable)
SHOWCASE_REPO = "https://github.com/encode/httpx.git"


def generate() -> str:
    template = TEMPLATE.read_text()

    # Self output
    self_output = subprocess.run(
        ["uv", "run", "pypatree"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    ).stdout.strip()
    template = template.replace("{{PYPATREE_OUTPUT}}", self_output)

    # External repo showcase
    if "{{SHOWCASE_OUTPUT}}" in template:
        name = SHOWCASE_REPO.split("/")[-1].removesuffix(".git")
        url = SHOWCASE_REPO.removesuffix(".git")
        output = run_pypatree_on_repo(SHOWCASE_REPO).strip()
        template = template.replace("{{SHOWCASE_NAME}}", name)
        template = template.replace("{{SHOWCASE_URL}}", url)
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
