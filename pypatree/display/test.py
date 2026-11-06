from inspect import Parameter as Kinds

import pytest
from rich.text import Text

from pypatree.config import Config
from pypatree.signature import Parameter, Signature
from pypatree.tree import Tree

from . import print_tree


def call(name: str, *parameters: Parameter, returns: str = "None") -> Signature:
    return Signature(name, parameters, returns)


def test_tree_lists_sorted_items_before_submodules(
    capsys: pytest.CaptureFixture[str],
) -> None:
    tree = Tree(
        items=[call("second"), call("first")],
        children={
            "zeta": Tree(),
            "alpha": Tree(items=[call("deep")], children={"leaf": Tree()}),
        },
    )
    print_tree("pkg", tree, Config(docstrings="none"))
    assert capsys.readouterr().out.splitlines() == [
        "pkg",
        "├── first() -> None",
        "├── second() -> None",
        "├── alpha",
        "│   ├── deep() -> None",
        "│   └── leaf",
        "└── zeta",
    ]


def test_wrapped_parameters_stay_indented(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("COLUMNS", "40")
    long = "OutT | NonpropagatingMissingType | PropagatingMissingType"
    signature = call(
        "cli",
        Parameter("f", Kinds.POSITIONAL_OR_KEYWORD, annotation="int"),
        Parameter("default", Kinds.KEYWORD_ONLY, annotation=long, default="..."),
        returns="OutT",
    )
    print_tree("pkg", Tree(items=[signature]), Config(color="never"))
    lines = capsys.readouterr().out.splitlines()
    assert lines[:3] == ["pkg", "└── cli(", "        f: int,"]
    assert lines[-1] == "    ) -> OutT"
    wrapped = lines[3:-1]
    assert len(wrapped) > 2 and all(line.startswith(" " * 8) for line in wrapped)
    assert " ".join(line.strip() for line in wrapped) == f"*, default: {long} = ...,"


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
    signature = call(
        "a_long_function",
        Parameter(
            "value", Kinds.POSITIONAL_OR_KEYWORD, annotation="dict[str, list[int]]"
        ),
        Parameter("text", Kinds.POSITIONAL_OR_KEYWORD, default='"""two\nlines"""'),
        returns="bool",
    )
    tree = Tree(children={"b": Tree(children={"c": Tree(items=[signature])})})
    print_tree("a", tree, Config(flat=True, color="never"))
    assert capsys.readouterr().out.splitlines() == [
        "a",
        "a.b",
        "a.b.c",
        "a.b.c.a_long_function(value: dict[str, list[int]], "
        r'text="""two\nlines""") -> bool',
    ]


@pytest.mark.parametrize("flat", [False, True])
def test_color_is_independent_of_format(
    flat: bool, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    tree = Tree(items=[call("visible", returns="str")])
    print_tree("pkg", tree, Config(flat=flat, color="always"))
    colored = capsys.readouterr().out
    assert "\x1b[" in colored
    print_tree("pkg", tree, Config(flat=flat, color="never"))
    plain = capsys.readouterr().out
    assert "\x1b[" not in plain
    assert Text.from_ansi(colored).plain.splitlines() == plain.splitlines()


@pytest.mark.parametrize("flat", [False, True])
def test_full_docstrings_and_failed_modules(
    flat: bool, capsys: pytest.CaptureFixture[str]
) -> None:
    tree = Tree(
        docstring="First line.\nSecond line.",
        children={"broken": Tree(docstring="Unread.", error="SyntaxError")},
    )
    print_tree("pkg", tree, Config(flat=flat, docstrings="full"))
    output = capsys.readouterr().out
    assert "First line." in output and "Second line." in output
    assert "broken [inspection failed]" in output
    assert "Unread." not in output
    if flat:
        assert output.splitlines() == [
            r"pkg  First line.\nSecond line.",
            "pkg.broken [inspection failed]",
        ]
