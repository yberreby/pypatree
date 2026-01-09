from pypatree.config import DEFAULT_EXCLUDE

from . import build_tree, get_module_items, get_packages


def test_get_packages_finds_pypatree() -> None:
    pkgs = get_packages(exclude=DEFAULT_EXCLUDE)
    assert "pypatree" in pkgs
    assert "pypatree.display" in pkgs["pypatree"]


def test_get_packages_excludes_tests_by_default() -> None:
    pkgs = get_packages(exclude=DEFAULT_EXCLUDE)
    submods = pkgs["pypatree"]
    assert "pypatree.discovery.test" not in submods


def test_get_packages_includes_tests_when_no_exclude() -> None:
    pkgs = get_packages(exclude=None)
    submods = pkgs["pypatree"]
    assert "pypatree.discovery.test" in submods


def test_get_module_items_functions() -> None:
    items = get_module_items("pypatree.discovery", None, True)
    assert any("get_packages" in i for i in items)


def test_get_module_items_classes() -> None:
    items = get_module_items("logging", None, True)
    assert any("Logger(" in i for i in items)


def test_build_tree_flat() -> None:
    tree = build_tree(["pkg", "pkg.a", "pkg.b"], "pkg", None, True)
    assert "a" in tree
    assert "b" in tree


def test_build_tree_nested() -> None:
    tree = build_tree(["pkg", "pkg.sub.deep"], "pkg", None, True)
    assert "sub" in tree
    assert "deep" in tree["sub"]
