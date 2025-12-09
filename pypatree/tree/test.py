from . import build_tree, get_subtree


def test_get_subtree_empty_path() -> None:
    tree = {"a": {"b": {}}}
    assert get_subtree(tree, []) is tree


def test_get_subtree_single_level() -> None:
    tree = {"a": {"__items__": []}, "b": {}}
    assert get_subtree(tree, ["a"]) == {"__items__": []}


def test_get_subtree_nested() -> None:
    tree = {"a": {"b": {"c": {"__items__": ["x"]}}}}
    assert get_subtree(tree, ["a", "b", "c"]) == {"__items__": ["x"]}


def test_get_subtree_not_found() -> None:
    tree = {"a": {"b": {}}}
    assert get_subtree(tree, ["a", "x"]) is None
    assert get_subtree(tree, ["z"]) is None


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
