#!/usr/bin/env python
"""Smoke test pypatree against real-world projects."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPOS = [
    "https://github.com/encode/httpx.git",
    "https://github.com/Textualize/rich.git",
    "https://github.com/pydantic/pydantic-settings.git",
    "https://github.com/brentyi/tyro.git",
]

ROOT = Path(__file__).parent.parent
PYPATREE = f"pypatree@{ROOT}"


def run(*cmd: str, **kw) -> subprocess.CompletedProcess[bytes]:
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    return subprocess.run(cmd, capture_output=True, env=env, **kw)


def main() -> int:
    quiet = "-q" in sys.argv or "--quiet" in sys.argv

    with tempfile.TemporaryDirectory() as tmp:
        for repo in REPOS:
            name = repo.split("/")[-1].removesuffix(".git")
            dest = f"{tmp}/{name}"

            print(f"=== {name} ===")
            run("git", "clone", "--depth=1", "-q", repo, dest)
            result = run(
                "uv", "run", "--with", PYPATREE, "pypatree", cwd=dest, timeout=120
            )

            if result.returncode != 0:
                print(f"FAIL\n{result.stderr.decode()}")
                return 1

            output = result.stdout.decode()
            if quiet:
                print(f"ok ({output.count(chr(10))} lines)\n")
            else:
                print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
