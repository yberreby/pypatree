"""Integration tests for pypatree."""

from pypatree.__main__ import run
from pypatree.config import DEFAULT_EXCLUDE, Config, DocstringMode


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


def test_scope_nonexistent_silent(capsys) -> None:  # type: ignore[no-untyped-def]
    """Nonexistent scope produces no output."""
    run(Config(scope="nonexistent.module", docstrings=DocstringMode.none))
    out = capsys.readouterr().out
    assert out == ""
