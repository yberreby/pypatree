"""Tests for discovery module - uses pypatree itself as test subject."""

from . import _get_local_packages, get_packages


def test_get_local_packages_finds_pypatree() -> None:
    """pypatree is installed from current dir when tests run."""
    packages = _get_local_packages()
    assert "pypatree" in packages


def test_get_packages_finds_submodules() -> None:
    """Finds pypatree and its submodules."""
    result = get_packages()
    assert "pypatree" in result
    submods = result["pypatree"]
    assert "pypatree" in submods
    assert "pypatree.discovery" in submods
    assert "pypatree.introspection" in submods
    assert "pypatree.display" in submods


def test_get_packages_skips_test_modules_by_default() -> None:
    """Test modules are skipped by default."""
    result = get_packages(skip_tests=True)
    submods = result["pypatree"]
    assert not any(".test" in m for m in submods)


def test_get_packages_includes_test_modules_when_requested() -> None:
    """Test modules are included when skip_tests=False."""
    result = get_packages(skip_tests=False)
    submods = result["pypatree"]
    assert any(".test" in m for m in submods)
