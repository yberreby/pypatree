import sys
from pathlib import Path

import pytest

from scripts.lib import PYTHON_VERSION, run, run_pypatree_on_repo


def test_run_reports_subprocess_failure(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError) as error:
        run(
            sys.executable,
            "-c",
            "import sys; sys.stderr.write('broken input'); sys.exit(7)",
            cwd=tmp_path,
        )

    assert "exit 7" in str(error.value)
    assert "broken input" in str(error.value)
    assert str(tmp_path) in str(error.value)


def test_run_preserves_successful_stderr(capsys: pytest.CaptureFixture[str]) -> None:
    run(
        sys.executable,
        "-c",
        "import sys; sys.stderr.write('partial inspection warning')",
    )
    assert "partial inspection warning" in capsys.readouterr().err


def test_run_failure_preserves_stdout() -> None:
    with pytest.raises(RuntimeError, match="diagnostic on stdout"):
        run(sys.executable, "-c", "print('diagnostic on stdout'); raise SystemExit(1)")


def test_showcase_uses_requested_revision_and_project_python(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("UV_PYTHON", str(tmp_path / "missing-interpreter"))
    caller = tmp_path / "caller"
    run("git", "init", "-q", str(caller))
    run("git", "-C", str(caller), "config", "user.name", "caller fixture")
    run("git", "-C", str(caller), "config", "user.email", "caller@example.invalid")
    run("git", "-C", str(caller), "commit", "--allow-empty", "-qm", "caller")
    caller_revision = run("git", "-C", str(caller), "rev-parse", "HEAD").stdout
    monkeypatch.setenv("GIT_DIR", str(caller / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(caller))
    monkeypatch.setenv("GIT_INDEX_FILE", str(caller / ".git/index"))
    source = tmp_path / "example"
    package = source / "example"
    package.mkdir(parents=True)
    (source / "pyproject.toml").write_text(
        '[build-system]\nrequires = ["hatchling"]\nbuild-backend = "hatchling.build"\n'
        '\n[project]\nname = "example"\nversion = "0.1.0"\nrequires-python = ">=3.9"\n'
    )
    (package / "__init__.py").write_text(
        "import platform\n__doc__ = 'Python ' + platform.python_version()\n"
        "def first_marker() -> None:\n    pass\n"
    )
    run("git", "init", "-q", str(source))
    run("git", "-C", str(source), "config", "user.name", "pypatree test")
    run("git", "-C", str(source), "config", "user.email", "test@example.invalid")
    run("git", "-C", str(source), "add", "pyproject.toml", "example/__init__.py")
    run("git", "-C", str(source), "commit", "-qm", "first")
    revision = (
        run("git", "-C", str(source), "rev-parse", "HEAD").stdout.decode().strip()
    )
    (package / "__init__.py").write_text("def second_marker() -> None:\n    pass\n")
    run("git", "-C", str(source), "add", "example/__init__.py")
    run("git", "-C", str(source), "commit", "-qm", "second")

    output = run_pypatree_on_repo(str(source), revision=revision)

    assert "first_marker" in output
    assert "second_marker" not in output
    assert f"Python {PYTHON_VERSION}" in output
    assert run("git", "-C", str(caller), "rev-parse", "HEAD").stdout == caller_revision
    assert (
        run("git", "-C", str(caller), "config", "user.name").stdout.strip()
        == b"caller fixture"
    )
