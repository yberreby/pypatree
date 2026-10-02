"""Shared utilities for scripts."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Optional, Union

ROOT = Path(__file__).parent.parent
PYPATREE = f"pypatree@{ROOT}"
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


@contextmanager
def checkout_repo(repo_url: str, revision: Optional[str] = None) -> Iterator[Path]:
    with tempfile.TemporaryDirectory() as tmp:
        name = repo_url.split("/")[-1].removesuffix(".git")
        dest = str(Path(tmp) / name)

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

        yield Path(dest)


def run_pypatree_on_repo(
    repo_url: str,
    revision: Optional[str] = None,
    constraints: Optional[Path] = None,
    extras: tuple[str, ...] = (),
    scope: Optional[str] = None,
) -> str:
    """Clone repo, install, run pypatree, return output."""
    with checkout_repo(repo_url, revision=revision) as dest:
        run("uv", "venv", "--python", PYTHON_VERSION, cwd=dest)
        executable = str(dest / ".venv" / "bin" / "python")
        install = ["uv", "pip", "install", "--python", executable]
        if constraints is not None:
            install.extend(["--constraints", str(constraints)])
        package = f".[{','.join(extras)}]" if extras else "."
        run(*install, "-e", package, PYPATREE, cwd=dest)
        command = ["uv", "run", "--python", executable, "--no-sync", "pypatree"]
        if scope is not None:
            command.append(scope)
        output = run(*command, cwd=dest).stdout.decode()
        if not output.strip():
            raise RuntimeError(f"pypatree produced no tree for {repo_url}")
        return output
