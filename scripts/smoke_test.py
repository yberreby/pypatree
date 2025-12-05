#!/usr/bin/env python
"""Smoke test pypatree against real-world projects."""

import sys

from lib import run_pypatree_on_repo

REPOS = [
    "https://github.com/encode/httpx.git",
    "https://github.com/Textualize/rich.git",
    "https://github.com/brentyi/tyro.git",
]


def main() -> int:
    quiet = "-q" in sys.argv or "--quiet" in sys.argv

    for repo in REPOS:
        name = repo.split("/")[-1].removesuffix(".git")
        print(f"=== {name} ===")

        try:
            output = run_pypatree_on_repo(repo)
        except RuntimeError as e:
            print(f"FAIL: {e}")
            return 1

        if quiet:
            print(f"ok ({output.count(chr(10))} lines)\n")
        else:
            print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
