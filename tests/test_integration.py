"""Run pypatree on itself and on the editable-installed stub projects."""

import subprocess
import sys
from pathlib import Path

import pytest

from pypatree.__main__ import run
from pypatree.config import Config

STUB = Path(__file__).parent / "stubs" / "test_stub"
CLI = Path(sys.executable).with_name("pypatree")


@pytest.mark.parametrize("runtime", [False, True])
def test_inspects_itself_without_test_modules(
    runtime: bool, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(Config(docstrings="none", runtime=runtime))
    out = capsys.readouterr().out
    assert "source_trees(" in out
    assert "test_scope_errors" not in out
    assert run(Config(docstrings="none", exclude="", runtime=runtime))
    assert "test_scope_errors" in capsys.readouterr().out


@pytest.mark.parametrize("runtime", [False, True])
def test_scope_shows_only_that_subtree(
    runtime: bool, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(Config(scope="pypatree.layout", docstrings="none", runtime=runtime))
    out = capsys.readouterr().out
    assert out.startswith("pypatree.layout")
    assert "project_packages" in out
    assert "print_tree" not in out


@pytest.mark.parametrize("runtime", [False, True])
def test_unknown_scope_lists_local_packages(runtime: bool) -> None:
    with pytest.raises(ValueError, match="not in a local package. Found: pypatree"):
        run(Config(scope="nonexistent.module", runtime=runtime))


@pytest.mark.parametrize(
    ("scope", "expected", "exit_code"),
    [
        ("test_stub.branch", "leaf", 1),
        ("test_stub.branch.leaf", "leaf_function", 0),
    ],
)
def test_scoped_cli_avoids_unrelated_imports(
    scope: str, expected: str, exit_code: int
) -> None:
    result = subprocess.run(
        [str(CLI), scope, "--runtime"],
        cwd=STUB,
        text=True,
        capture_output=True,
        timeout=10,
    )
    assert result.stdout.startswith(scope)
    assert expected in result.stdout
    assert "sibling" not in result.stdout
    assert "Unrelated sibling was imported" not in result.stderr
    assert result.returncode == exit_code
    if exit_code:
        assert "missing_dependency_for_pypatree" in result.stderr
        assert "Output is incomplete" in result.stderr


def test_scoped_cli_respects_package_boundaries_and_exclusions() -> None:
    for scope, message in [
        ("test_stubbish.branch", "not in a local package"),
        ("test_stub.branch.missing", "does not exist"),
        ("test_stub.branch.test_ignored", "excluded by --exclude"),
    ]:
        result = subprocess.run(
            [str(CLI), scope, "--runtime"],
            cwd=STUB,
            text=True,
            capture_output=True,
            timeout=10,
        )
        assert result.returncode != 0
        assert message in result.stderr
