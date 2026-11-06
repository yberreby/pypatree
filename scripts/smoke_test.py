#!/usr/bin/env python
"""Run pypatree against the current heads of real-world projects."""

from lib import pypatree_on_repo

SCOPES = {
    "https://github.com/encode/httpx.git": "httpx",
    "https://github.com/Textualize/rich.git": "rich.console",
    "https://github.com/brentyi/tyro.git": "tyro",
}


def main() -> None:
    for url, scope in SCOPES.items():
        print(f"=== {scope} ({url})", flush=True)
        print(pypatree_on_repo(url, scope), flush=True)


if __name__ == "__main__":
    main()
