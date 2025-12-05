"""Tests for discovery module - uses pypatree itself as test subject."""

import re
from unittest.mock import patch

from pypatree.config import DEFAULT_EXCLUDE

from . import _get_local_packages, _matches_exclude, get_packages


def test_matches_exclude_exact_test() -> None:
    pattern = re.compile(DEFAULT_EXCLUDE)
    assert _matches_exclude("test", pattern) is True


def test_matches_exclude_test_prefixed() -> None:
    pattern = re.compile(DEFAULT_EXCLUDE)
    assert _matches_exclude("test_foo", pattern) is True
    assert _matches_exclude("test_", pattern) is True


def test_matches_exclude_not_testing() -> None:
    pattern = re.compile(DEFAULT_EXCLUDE)
    assert _matches_exclude("testing", pattern) is False
    assert _matches_exclude("testable", pattern) is False
    assert _matches_exclude("tests", pattern) is False


def test_matches_exclude_nested() -> None:
    pattern = re.compile(DEFAULT_EXCLUDE)
    assert _matches_exclude("foo.test", pattern) is True
    assert _matches_exclude("foo.test_bar", pattern) is True
    assert _matches_exclude("foo.testing", pattern) is False


def test_get_local_packages_finds_pypatree() -> None:
    """pypatree is installed from current dir when tests run."""
    packages = _get_local_packages()
    assert "pypatree" in packages


def test_get_packages_finds_submodules() -> None:
    """Finds pypatree and its submodules."""
    result = get_packages(exclude=DEFAULT_EXCLUDE)
    assert "pypatree" in result
    submods = result["pypatree"]
    assert "pypatree" in submods
    assert "pypatree.discovery" in submods
    assert "pypatree.introspection" in submods
    assert "pypatree.display" in submods


def test_get_packages_excludes_test_modules_by_default() -> None:
    """Test modules are excluded with default pattern."""
    result = get_packages(exclude=DEFAULT_EXCLUDE)
    submods = result["pypatree"]
    assert "pypatree.discovery.test" not in submods
    assert "pypatree.display.test" not in submods


def test_get_packages_includes_test_modules_when_no_exclude() -> None:
    """Test modules are included when exclude is None."""
    result = get_packages(exclude=None)
    submods = result["pypatree"]
    assert "pypatree.discovery.test" in submods
    assert "pypatree.display.test" in submods


def test_get_packages_skips_unimportable() -> None:
    """Packages that fail to import are skipped."""
    with patch("pypatree.discovery.safe_import", return_value=None):
        result = get_packages()
    assert result == {}
