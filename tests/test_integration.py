"""Integration tests using real stub packages."""

import logging

from pypatree.__main__ import run


def test_finds_testpkg_when_skip_tests_false(capsys) -> None:
    """testpkg is found when skip_tests=False."""
    run(skip_tests=False)
    out = capsys.readouterr().out
    assert "testpkg" in out


def test_skips_testpkg_by_default(capsys) -> None:
    """testpkg is skipped when skip_tests=True (starts with 'test')."""
    run(skip_tests=True)
    out = capsys.readouterr().out
    assert "testpkg" not in out


def test_broken_package_skipped(caplog, capsys) -> None:
    """brokenpkg (which fails to import) is logged and skipped."""
    with caplog.at_level(logging.WARNING):
        run(skip_tests=False)
    assert "brokenpkg" not in capsys.readouterr().out
    assert "Skipping" in caplog.text
