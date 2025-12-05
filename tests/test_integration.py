"""Integration tests using real stub packages."""

import logging

from pypatree.__main__ import run
from pypatree.config import Config, DocstringMode


def test_finds_testpkg_when_skip_tests_false(capsys) -> None:  # type: ignore[no-untyped-def]
    """testpkg is found when skip_tests=False."""
    run(Config(skip_tests=False, docstrings=DocstringMode.none))
    out = capsys.readouterr().out
    assert "testpkg" in out


def test_skips_testpkg_by_default(capsys) -> None:  # type: ignore[no-untyped-def]
    """testpkg is skipped when skip_tests=True (starts with 'test')."""
    run(Config(skip_tests=True, docstrings=DocstringMode.none))
    out = capsys.readouterr().out
    assert "testpkg" not in out


def test_broken_package_skipped(caplog, capsys) -> None:  # type: ignore[no-untyped-def]
    """brokenpkg (which fails to import) is logged and skipped."""
    with caplog.at_level(logging.WARNING):
        run(Config(skip_tests=False, docstrings=DocstringMode.none))
    assert "brokenpkg" not in capsys.readouterr().out
    assert "Skipping" in caplog.text
