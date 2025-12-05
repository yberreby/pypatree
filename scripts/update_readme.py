#!/usr/bin/env python
"""Generate README.md from README.md.in template."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
TEMPLATE = ROOT / "README.md.in"
OUTPUT = ROOT / "README.md"
PLACEHOLDER = "{{PYPATREE_OUTPUT}}"


def generate() -> str:
    template = TEMPLATE.read_text()
    output = subprocess.run(
        ["uv", "run", "pypatree"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    ).stdout.strip()
    return template.replace(PLACEHOLDER, output)


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
