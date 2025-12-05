"""Shared utilities for scripts."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent
PYPATREE = f"pypatree@{ROOT}"


def run(*cmd: str, **kw: Any) -> subprocess.CompletedProcess[bytes]:
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    return subprocess.run(cmd, capture_output=True, env=env, **kw)


def run_pypatree_on_repo(repo_url: str, timeout: int = 120) -> str:
    """Clone repo, install, run pypatree, return output."""
    with tempfile.TemporaryDirectory() as tmp:
        name = repo_url.split("/")[-1].removesuffix(".git")
        dest = f"{tmp}/{name}"

        run("git", "clone", "--depth=1", "-q", repo_url, dest)
        run("uv", "venv", cwd=dest)
        run("uv", "pip", "install", "-e", ".", PYPATREE, cwd=dest, timeout=timeout)
        result = run("uv", "run", "pypatree", cwd=dest, timeout=timeout)

        if result.returncode != 0:
            raise RuntimeError(f"pypatree failed on {name}: {result.stderr.decode()}")

        return result.stdout.decode()
