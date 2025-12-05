from . import print_tree, render_tree


def test_empty_tree() -> None:
    assert render_tree({}) == []


def test_items_only() -> None:
    tree = {"__items__": ["foo()", "bar()"]}
    lines = render_tree(tree)
    assert lines == ["├── foo()", "└── bar()"]


def test_nested() -> None:
    tree = {"sub": {"__items__": ["child()"]}}
    lines = render_tree(tree)
    assert lines == ["└── sub", "    └── child()"]


def test_deep_nested() -> None:
    tree = {"a": {"b": {"__items__": ["x()"]}}}
    lines = render_tree(tree)
    assert "a" in lines[0]
    assert "b" in lines[1]
    assert "x()" in lines[2]


def test_print_tree(capsys) -> None:  # type: ignore[no-untyped-def]
    print_tree({"__items__": ["x()"]})
    out = capsys.readouterr().out
    assert "x()" in out
