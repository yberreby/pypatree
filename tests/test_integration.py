"""Integration tests for pypatree."""

import subprocess
import sys
from pathlib import Path

import pytest

from pypatree.__main__ import run
from pypatree.config import DEFAULT_EXCLUDE, Config, DocstringMode
from pypatree.discovery import get_packages


def test_finds_pypatree_package(capsys) -> None:  # type: ignore[no-untyped-def]
    """pypatree finds itself when run from its own directory."""
    run(Config(exclude=DEFAULT_EXCLUDE, docstrings=DocstringMode.none))
    out = capsys.readouterr().out
    assert "pypatree" in out
    assert "get_packages" in out


def test_excludes_test_modules_by_default(capsys) -> None:  # type: ignore[no-untyped-def]
    """Test modules are excluded with default exclude pattern."""
    run(Config(exclude=DEFAULT_EXCLUDE, docstrings=DocstringMode.none))
    out = capsys.readouterr().out
    assert "test_format_signature" not in out


def test_includes_test_modules_when_no_exclude(capsys) -> None:  # type: ignore[no-untyped-def]
    """Test modules are included when exclude is None."""
    run(Config(exclude=None, docstrings=DocstringMode.none))
    out = capsys.readouterr().out
    assert "test_format_signature" in out


def test_scope_to_submodule(capsys) -> None:  # type: ignore[no-untyped-def]
    """Scoping to a submodule shows only that subtree."""
    run(Config(scope="pypatree.discovery", docstrings=DocstringMode.none))
    out = capsys.readouterr().out
    assert "pypatree.discovery" in out
    assert "get_packages" in out
    assert "print_tree" not in out  # from display module


def test_scope_nonexistent_reports_error() -> None:
    with pytest.raises(ValueError, match="not in a local editable package"):
        run(Config(scope="nonexistent.module", docstrings=DocstringMode.none))


@pytest.mark.parametrize(
    ("scope", "expected"),
    [
        ("test_stub.branch", "leaf"),
        ("test_stub.branch.leaf", "leaf_function"),
    ],
)
def test_scoped_cli_avoids_unrelated_imports(scope: str, expected: str) -> None:
    stub = Path(__file__).parent / "stubs" / "test_stub"
    cli = Path(sys.executable).with_name("pypatree")
    result = subprocess.run(
        [str(cli), scope], cwd=stub, text=True, capture_output=True, check=True
    )
    assert result.stdout.startswith(scope)
    assert expected in result.stdout
    assert "sibling" not in result.stdout


def test_scoped_cli_respects_package_boundaries_and_exclusions() -> None:
    stub = Path(__file__).parent / "stubs" / "test_stub"
    cli = Path(sys.executable).with_name("pypatree")
    for scope, message in [
        ("test_stubbish.branch", "not in a local editable package"),
        ("test_stub.branch.missing", "does not exist"),
        ("test_stub.branch.test_ignored", "excluded by --exclude"),
    ]:
        result = subprocess.run(
            [str(cli), scope], cwd=stub, text=True, capture_output=True
        )
        assert result.returncode != 0
        assert message in result.stderr


def test_scoped_discovery_is_relative_to_local_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stub = Path(__file__).parent / "stubs" / "test_stub"
    monkeypatch.chdir(stub)

    assert get_packages(exclude=DEFAULT_EXCLUDE, scope="test_stub.branch") == {
        "test_stub.branch": [
            "test_stub.branch",
            "test_stub.branch.deep",
            "test_stub.branch.deep.inner",
            "test_stub.branch.leaf",
            "test_stub.branch.needs_missing",
        ]
    }
    assert get_packages(exclude=DEFAULT_EXCLUDE, scope="test_stub.branch.leaf") == {
        "test_stub.branch.leaf": ["test_stub.branch.leaf"]
    }
    with pytest.raises(ValueError, match="excluded by --exclude"):
        get_packages(exclude=DEFAULT_EXCLUDE, scope="test_stub.branch.test_ignored")
    with pytest.raises(ValueError, match="does not exist"):
        get_packages(exclude=DEFAULT_EXCLUDE, scope="test_stub.branch.missing")
    with pytest.raises(ModuleNotFoundError, match="missing_dependency_for_pypatree"):
        get_packages(exclude=DEFAULT_EXCLUDE, scope="test_stub.branch.needs_missing")
