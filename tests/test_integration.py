"""Integration tests using real stub packages."""

import logging

from pypatree.__main__ import run
from pypatree.config import DEFAULT_EXCLUDE, Config, DocstringMode


def test_excludes_test_stub_by_default(capsys) -> None:  # type: ignore[no-untyped-def]
    """test_stub is excluded with default exclude pattern."""
    run(Config(exclude=DEFAULT_EXCLUDE, docstrings=DocstringMode.none))
    out = capsys.readouterr().out
    assert "test_stub" not in out


def test_includes_test_stub_when_no_exclude(capsys) -> None:  # type: ignore[no-untyped-def]
    """test_stub is included when exclude is None."""
    run(Config(exclude=None, docstrings=DocstringMode.none))
    out = capsys.readouterr().out
    assert "test_stub" in out


def test_broken_package_skipped(caplog, capsys) -> None:  # type: ignore[no-untyped-def]
    """brokenpkg (which fails to import) is logged and skipped."""
    with caplog.at_level(logging.WARNING):
        run(Config(exclude=None, docstrings=DocstringMode.none))
    assert "brokenpkg" not in capsys.readouterr().out
    assert "brokenpkg" in caplog.text
