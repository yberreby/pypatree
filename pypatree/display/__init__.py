"""Render module trees as Rich trees or as qualified lines."""

from collections.abc import Iterator
from typing import Any

from rich.console import Console, Group, RenderableType
from rich.padding import Padding
from rich.syntax import Syntax
from rich.text import Text
from rich.tree import Tree as RichTree

from pypatree.config import Config
from pypatree.signature import Signature
from pypatree.tree import Tree

_SYNTAX = Syntax("", "python", theme="one-dark", background_color="default")
_GUIDE_WIDTH = 4
"""Columns that each level of Rich's tree guides occupies."""
_PARAMETER_INDENT = 4
_CONSOLE_OPTIONS: dict[str, dict[str, Any]] = {
    "auto": {},
    # An explicit no_color overrides the NO_COLOR environment variable.
    "always": {"force_terminal": True, "no_color": False},
    "never": {"color_system": None},
}


def print_tree(name: str, tree: Tree, cfg: Config) -> None:
    console = Console(**_CONSOLE_OPTIONS[cfg.color])
    if cfg.flat:
        for line in _flat_lines(name, tree, cfg):
            console.print(line, soft_wrap=True)
        return
    root = RichTree(_label(name, tree, cfg, style="bold yellow"))
    _add_contents(root, tree, cfg, width=console.width - _GUIDE_WIDTH)
    console.print(root)


def _add_contents(parent: RichTree, tree: Tree, cfg: Config, *, width: int) -> None:
    for signature in sorted(tree.items, key=_name):
        parent.add(_wrapped(signature, width))
    for name, child in sorted(tree.children.items()):
        branch = parent.add(_label(name, child, cfg, style="bold blue"))
        _add_contents(branch, child, cfg, width=width - _GUIDE_WIDTH)


def _flat_lines(name: str, tree: Tree, cfg: Config) -> Iterator[Text]:
    yield _label(name, tree, cfg, style="bold blue")
    for signature in sorted(tree.items, key=_name):
        yield _highlight(_escape(f"{name}.{signature}"))
    for child_name, child in sorted(tree.children.items()):
        yield from _flat_lines(f"{name}.{child_name}", child, cfg)


def _label(name: str, tree: Tree, cfg: Config, *, style: str) -> Text:
    if tree.error is not None:
        return Text.assemble((name, style), (" [inspection failed]", "red"))
    note = ""
    if tree.docstring and cfg.docstrings != "none":
        docstring = tree.docstring
        if cfg.docstrings == "short":
            docstring = docstring.splitlines()[0]
        note = f"  {_escape(docstring) if cfg.flat else docstring}"
    return Text.assemble((name, style), (note, "dim"))


def _wrapped(signature: Signature, width: int) -> RenderableType:
    """Highlighted signature; wrapped parameters stay indented under their call."""
    first, *rest = _highlight("\n".join(signature.lines(width))).split("\n")
    if not rest:
        return first
    *parameters, last = rest
    return Group(
        first,
        *(
            Padding(line, (0, 0, 0, _PARAMETER_INDENT), expand=False)
            for line in parameters
        ),
        last,
    )


def _highlight(code: str) -> Text:
    text = _SYNTAX.highlight(f"def {code}: ...")
    return text[len("def ") : text.plain.rfind(": ...")]


def _escape(text: str) -> str:
    return text.replace("\n", r"\n")


def _name(signature: Signature) -> str:
    return signature.name
