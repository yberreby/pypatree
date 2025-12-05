from . import build_tree


def test_build_tree_type() -> None:
    tree = build_tree(["pkg"], "pkg", exclude=None)
    assert isinstance(tree, dict)


def test_build_tree_empty() -> None:
    tree = build_tree([], "pkg", exclude=None)
    assert tree == {}


def test_build_tree_root_items() -> None:
    tree = build_tree(["pkg"], "pkg", exclude=None)
    assert "__items__" in tree


def test_build_tree_nested_path() -> None:
    tree = build_tree(["pkg", "pkg.a.b.c"], "pkg", exclude=None)
    assert "a" in tree
    assert "b" in tree["a"]
    assert "c" in tree["a"]["b"]
