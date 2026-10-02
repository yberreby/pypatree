import pytest
from rich.text import Text

from pypatree.config import Config, DocstringMode
from pypatree.tree import Tree

from . import print_tree, render_tree


def test_tree_renderers_agree(capsys: pytest.CaptureFixture[str]) -> None:
    tree = Tree(
        items=["root()"],
        children={
            "child": Tree(
                items=["child_item()"],
                children={
                    "grandchild": Tree(items=["deep()"]),
                },
            ),
        },
    )
    print_tree("pkg", tree, Config(docstrings=DocstringMode.none))
    output = capsys.readouterr().out.splitlines()
    expected = [
        "pkg",
        "├── root()",
        "└── child",
        "    ├── child_item()",
        "    └── grandchild",
        "        └── deep()",
    ]
    assert output == expected
    assert render_tree(tree) == expected[1:]
    assert render_tree(Tree()) == []
    assert render_tree(Tree(items=["x()"]), prefix="  ") == ["  └── x()"]


@pytest.mark.parametrize("flat", [False, True])
def test_docstrings_are_literal_text(
    flat: bool, capsys: pytest.CaptureFixture[str]
) -> None:
    root_doc = "An array [batch, width]."
    child_doc = "Keep [red]tags[/red] and [/unexpected]."
    tree = Tree(docstring=root_doc, children={"child": Tree(docstring=child_doc)})
    print_tree("literal_docs", tree, Config(flat=flat))
    output = capsys.readouterr().out
    assert root_doc in output
    assert child_doc in output


def test_flat_output_has_qualified_unwrapped_names(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("COLUMNS", "12")
    monkeypatch.setenv("FORCE_COLOR", "1")
    signature = "a_long_function(value: dict[str, list[int]], other: str) -> bool"
    tree = Tree(children={"b": Tree(children={"c": Tree(items=[signature])})})
    print_tree("a", tree, Config(flat=True, color="never"))
    assert capsys.readouterr().out.splitlines() == [
        "a",
        "a.b",
        "a.b.c",
        f"a.b.c.{signature}",
    ]


@pytest.mark.parametrize("flat", [False, True])
def test_color_is_independent_of_format(
    flat: bool, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    tree = Tree(items=["visible(value: int) -> str"])
    print_tree("pkg", tree, Config(flat=flat, color="always"))
    colored = capsys.readouterr().out
    assert "\x1b[" in colored
    print_tree("pkg", tree, Config(flat=flat, color="never"))
    plain = capsys.readouterr().out
    assert "\x1b[" not in plain
    assert Text.from_ansi(colored).plain.splitlines() == plain.splitlines()


@pytest.mark.parametrize("flat", [False, True])
def test_full_docstrings_and_failed_imports(
    flat: bool, capsys: pytest.CaptureFixture[str]
) -> None:
    tree = Tree(
        docstring="First line.\nSecond line.", children={"broken": Tree(failed=True)}
    )
    print_tree("pkg", tree, Config(flat=flat, docstrings=DocstringMode.full))
    output = capsys.readouterr().out
    assert "First line." in output and "Second line." in output
    assert "broken [import failed]" in output
    if flat:
        assert output.splitlines() == [
            r"pkg  First line.\nSecond line.",
            "pkg.broken [import failed]",
        ]
