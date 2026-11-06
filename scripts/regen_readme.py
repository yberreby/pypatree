#!/usr/bin/env python
"""Generate README.md from the README.md.in template."""

import re
import sys

import tyro

from lib import PYTHON_VERSION, ROOT, pypatree, pypatree_on_repo

TEMPLATE = ROOT / "README.md.in"
OUTPUT = ROOT / "README.md"

SHOWCASE_REPO = "https://github.com/encode/httpx.git"
SHOWCASE_REVISION = "b5addb64f0161ff6bfe94c124ef76f6a1fba5254"


def generate() -> str:
    replacements = {
        "{{PYPATREE_OUTPUT}}": pypatree(cwd=ROOT),
        "{{FLAT_OUTPUT}}": pypatree("pypatree.introspection", "--flat", cwd=ROOT),
        "{{HELP_OUTPUT}}": pypatree("--help", cwd=ROOT),
        "{{SHOWCASE_NAME}}": SHOWCASE_REPO.split("/")[-1].removesuffix(".git"),
        "{{SHOWCASE_URL}}": SHOWCASE_REPO.removesuffix(".git"),
        "{{SHOWCASE_REVISION}}": SHOWCASE_REVISION,
        "{{SHOWCASE_PYTHON}}": PYTHON_VERSION,
        "{{SHOWCASE_OUTPUT}}": pypatree_on_repo(
            SHOWCASE_REPO, revision=SHOWCASE_REVISION
        ),
    }
    readme = TEMPLATE.read_text()
    for placeholder, value in replacements.items():
        assert placeholder in readme, placeholder
        readme = readme.replace(placeholder, value.strip())
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", readme)
    assert not leftover, leftover
    return "\n".join(line.rstrip() for line in readme.splitlines()) + "\n"


def main(check: bool = False) -> int:
    """Write README.md, or with --check, fail if it differs from the generated text."""
    generated = generate()
    if not check:
        OUTPUT.write_text(generated)
        print("README.md generated")
        return 0
    if not OUTPUT.exists() or OUTPUT.read_text() != generated:
        print("README.md is stale or missing. Run: uv run just regen-readme")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(tyro.cli(main))
