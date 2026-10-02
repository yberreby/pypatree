#!/usr/bin/env python
"""Smoke test pypatree against real-world projects."""

import sys
from dataclasses import dataclass

from lib import run_pypatree_on_repo


@dataclass(frozen=True)
class Repo:
    url: str
    scope: str
    extras: tuple[str, ...] = ()


REPOS = [
    Repo("https://github.com/encode/httpx.git", scope="httpx", extras=("cli",)),
    Repo("https://github.com/Textualize/rich.git", scope="rich.console"),
    Repo("https://github.com/brentyi/tyro.git", scope="tyro"),
]


def main() -> int:
    quiet = "-q" in sys.argv or "--quiet" in sys.argv

    for repo in REPOS:
        name = repo.url.split("/")[-1].removesuffix(".git")
        print(f"=== {name}: {repo.scope} ===", flush=True)

        try:
            output = run_pypatree_on_repo(
                repo.url, extras=repo.extras, scope=repo.scope
            )
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
