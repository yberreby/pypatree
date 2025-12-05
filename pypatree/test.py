from . import build_tree, get_module_items, get_packages


def test_get_packages_finds_pypatree() -> None:
    pkgs = get_packages()
    assert "pypatree" in pkgs
    assert "pypatree.display" in pkgs["pypatree"]


def test_get_packages_skips_tests_by_default() -> None:
    pkgs = get_packages()
    submods = pkgs["pypatree"]
    assert not any(".test" in m for m in submods)


def test_get_packages_includes_tests_when_requested() -> None:
    pkgs = get_packages(skip_tests=False)
    submods = pkgs["pypatree"]
    assert any(".test" in m for m in submods)


def test_get_module_items_functions() -> None:
    items = get_module_items("pypatree")
    assert "get_packages()" in items
    assert "build_tree()" in items


def test_get_module_items_classes() -> None:
    items = get_module_items("logging")
    assert "Logger" in items


def test_build_tree_flat() -> None:
    tree = build_tree(["pkg", "pkg.a", "pkg.b"], "pkg", skip_tests=False)
    assert "a" in tree
    assert "b" in tree


def test_build_tree_nested() -> None:
    tree = build_tree(["pkg", "pkg.sub.deep"], "pkg", skip_tests=False)
    assert "sub" in tree
    assert "deep" in tree["sub"]
