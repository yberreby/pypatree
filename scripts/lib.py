"""Shared helpers for development scripts and their tests."""

import os
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Union

ROOT = Path(__file__).parent.parent
PYTHON_VERSION = (ROOT / ".python-version").read_text().strip()
GIT_LOCAL_ENV_VARS = frozenset(
    subprocess.run(
        ["git", "rev-parse", "--local-env-vars"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
)


def run(
    *cmd: str, cwd: Optional[Union[str, Path]] = None, timeout: int = 120
) -> subprocess.CompletedProcess[bytes]:
    """Run cmd, raising with its output on failure and forwarding its stderr."""
    # Git hooks export repository selectors that override a subprocess's cwd.
    env = {
        key: value
        for key, value in os.environ.items()
        if key != "VIRTUAL_ENV" and key not in GIT_LOCAL_ENV_VARS
    }
    result = subprocess.run(cmd, cwd=cwd, timeout=timeout, capture_output=True, env=env)
    if result.returncode:
        raise RuntimeError(
            f"{cmd!r} failed in {cwd or Path.cwd()} "
            f"(exit {result.returncode}):\n"
            f"{result.stdout.decode(errors='replace')}{result.stderr.decode(errors='replace')}"
        )
    if result.stderr:
        sys.stderr.write(result.stderr.decode(errors="replace"))
    return result


def pypatree(*args: str, cwd: Path) -> str:
    """Run this checkout's pypatree with locked dependencies and the project Python.

    The isolated environment leaves the development environment untouched.
    """
    environment = ["--isolated", "--locked", "--no-dev", "--project", str(ROOT)]
    command = ["uv", "run", *environment, "--python", PYTHON_VERSION, "pypatree"]
    return run(*command, *args, cwd=cwd).stdout.decode()


@contextmanager
def checkout(repo_url: str, revision: Optional[str] = None) -> Iterator[Path]:
    """Clone repo_url at revision, or at its default branch head, into a temporary directory."""
    with tempfile.TemporaryDirectory() as tmp:
        dest = str(Path(tmp) / repo_url.split("/")[-1].removesuffix(".git"))
        if revision is None:
            run("git", "clone", "--depth=1", "-q", repo_url, dest)
        else:
            run("git", "init", "-q", dest)
            run("git", "-C", dest, "fetch", "--depth=1", "-q", repo_url, revision)
            run("git", "-C", dest, "checkout", "--detach", "-q", "FETCH_HEAD")
            actual = run("git", "-C", dest, "rev-parse", "HEAD").stdout.decode().strip()
            assert actual == revision, (actual, revision)
        yield Path(dest)


def pypatree_on_repo(repo_url: str, *args: str, revision: Optional[str] = None) -> str:
    with checkout(repo_url, revision) as source:
        output = pypatree(*args, cwd=source)
    if not output.strip():
        raise RuntimeError(f"pypatree produced no tree for {repo_url}")
    return output
