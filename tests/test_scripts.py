import inspect
import subprocess
import sys
from enum import Enum
from pathlib import Path

import pytest

from scripts.lib import run, run_pypatree_on_repo


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


def test_showcase_uses_requested_revision_and_project_python(tmp_path: Path) -> None:
    source = tmp_path / "example"
    package = source / "example"
    package.mkdir(parents=True)
    (source / "pyproject.toml").write_text(
        '[build-system]\nrequires = ["hatchling"]\nbuild-backend = "hatchling.build"\n'
        '\n[project]\nname = "example"\nversion = "0.1.0"\nrequires-python = ">=3.9"\n'
    )
    (package / "__init__.py").write_text(
        "from enum import Enum\nclass Flavor(Enum):\n    ONE = 1\n"
        "def first_marker() -> None:\n    pass\n"
    )
    subprocess.run(["git", "init", "-q", str(source)], check=True)
    subprocess.run(
        ["git", "-C", str(source), "config", "user.name", "pypatree test"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(source), "config", "user.email", "test@example.invalid"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(source), "add", "pyproject.toml", "example/__init__.py"],
        check=True,
    )
    subprocess.run(["git", "-C", str(source), "commit", "-qm", "first"], check=True)
    revision = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    (package / "__init__.py").write_text("def second_marker() -> None:\n    pass\n")
    subprocess.run(["git", "-C", str(source), "add", "example/__init__.py"], check=True)
    subprocess.run(["git", "-C", str(source), "commit", "-qm", "second"], check=True)

    output = run_pypatree_on_repo(str(source), revision=revision)

    assert "first_marker" in output
    assert "second_marker" not in output
    enum_keyword_name = tuple(inspect.signature(Enum.__init__).parameters)[-1]
    assert f"**{enum_keyword_name}" in output
