from . import build_tree


def test_build_tree_type() -> None:
    tree = build_tree(["pkg"], "pkg", skip_tests=False)
    assert isinstance(tree, dict)


def test_build_tree_empty() -> None:
    tree = build_tree([], "pkg", skip_tests=False)
    assert tree == {}


def test_build_tree_root_items() -> None:
    tree = build_tree(["pkg"], "pkg", skip_tests=False)
    assert "__items__" in tree


def test_build_tree_nested_path() -> None:
    tree = build_tree(["pkg", "pkg.a.b.c"], "pkg", skip_tests=False)
    assert "a" in tree
    assert "b" in tree["a"]
    assert "c" in tree["a"]["b"]
