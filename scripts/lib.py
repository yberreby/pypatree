"""Shared utilities for scripts."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).parent.parent
PYPATREE = f"pypatree@{ROOT}"
PYTHON_VERSION = (ROOT / ".python-version").read_text().strip()


def run(*cmd: str, **kw: Any) -> subprocess.CompletedProcess[bytes]:
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    result = subprocess.run(cmd, capture_output=True, env=env, **kw)
    if result.returncode:
        raise RuntimeError(
            f"{cmd!r} failed in {kw.get('cwd', Path.cwd())} "
            f"(exit {result.returncode}):\n{result.stderr.decode(errors='replace')}"
        )
    return result


def run_pypatree_on_repo(
    repo_url: str,
    timeout: int = 120,
    revision: Optional[str] = None,
    constraints: Optional[Path] = None,
) -> str:
    """Clone repo, install, run pypatree, return output."""
    with tempfile.TemporaryDirectory() as tmp:
        name = repo_url.split("/")[-1].removesuffix(".git")
        dest = f"{tmp}/{name}"

        if revision is None:
            run("git", "clone", "--depth=1", "-q", repo_url, dest)
        else:
            run("git", "init", "-q", dest)
            run("git", "-C", dest, "fetch", "--depth=1", "-q", repo_url, revision)
            run("git", "-C", dest, "checkout", "--detach", "-q", "FETCH_HEAD")
            actual_revision = (
                run("git", "-C", dest, "rev-parse", "HEAD").stdout.decode().strip()
            )
            assert actual_revision == revision, (actual_revision, revision)

        run("uv", "venv", "--python", PYTHON_VERSION, cwd=dest)
        install = ["uv", "pip", "install"]
        if constraints is not None:
            install.extend(["--constraints", str(constraints)])
        run(*install, "-e", ".", PYPATREE, cwd=dest, timeout=timeout)
        return run(
            "uv", "run", "--no-sync", "pypatree", cwd=dest, timeout=timeout
        ).stdout.decode()
