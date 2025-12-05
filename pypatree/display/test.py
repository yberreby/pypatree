from pypatree.config import Config, DocstringMode

from . import _highlight, print_tree, render_tree


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
    cfg = Config(docstrings=DocstringMode.none)
    print_tree("testpkg", {"__items__": ["x()"]}, cfg)
    out = capsys.readouterr().out
    assert "x()" in out


def test_print_tree_with_docstrings(capsys) -> None:  # type: ignore[no-untyped-def]
    cfg = Config(docstrings=DocstringMode.short)
    # config module has a docstring, so this exercises the docstring label path
    print_tree("pypatree", {"config": {"__items__": ["x()"]}}, cfg)
    out = capsys.readouterr().out
    assert "pypatree" in out
    assert "config" in out


def test_items_not_duplicated_with_nested_children() -> None:
    """Items should appear once, not twice when module has both items AND children."""
    tree = {
        "__items__": ["root()"],
        "child": {
            "__items__": ["child_item()"],
            "grandchild": {"__items__": ["deep()"]},
        },
    }
    lines = render_tree(tree)
    # child_item() should appear exactly once
    assert (
        lines.count("    ├── child_item()") + lines.count("    └── child_item()") == 1
    )


def test_highlight_preserves_signature() -> None:
    """_highlight wraps in 'def' for syntax coloring but returns original signature."""
    cases = [
        "foo()",
        "foo(x: int)",
        "foo(x: int) -> None",
        "foo(a: str, b: int = 1) -> bool",
        "MyClass(name: str) -> None",
    ]
    for sig in cases:
        result = _highlight(sig)
        assert result.plain == sig, f"Expected {sig!r}, got {result.plain!r}"
