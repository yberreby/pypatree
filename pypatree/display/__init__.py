from collections.abc import Iterator

from rich.console import Console
from rich.syntax import Syntax
from rich.text import Text
from rich.tree import Tree as RichTree

from pypatree.config import Config, DocstringMode
from pypatree.tree import Tree

_SYNTAX = Syntax("", "python", theme="one-dark", background_color="default")


def _highlight(signature: str) -> Text:
    text = _SYNTAX.highlight(f"def {signature}: ...")
    return text[len("def ") : text.plain.rfind(": ...")]


def _label(name: str, tree: Tree, cfg: Config) -> str:
    if tree.failed:
        return f"{name} [import failed]"
    if cfg.docstrings == DocstringMode.none or not tree.docstring:
        return name
    docstring = tree.docstring
    if cfg.docstrings == DocstringMode.short:
        docstring = docstring.splitlines()[0]
    return f"{name}  {docstring}"


def _styled_label(name: str, tree: Tree, cfg: Config, *, style: str) -> Text:
    content = _label(name, tree, cfg)
    label = Text(content.replace("\n", r"\n") if cfg.flat else content)
    label.stylize(style, 0, len(name))
    label.stylize("red" if tree.failed else "dim", len(name))
    return label


def _add_subtree(parent: RichTree, tree: Tree, cfg: Config) -> None:
    for item in tree.items:
        parent.add(_highlight(item))
    for name, child in sorted(tree.children.items()):
        branch = parent.add(_styled_label(name, child, cfg, style="bold blue"))
        _add_subtree(branch, child, cfg)


def _flat_lines(name: str, tree: Tree, cfg: Config) -> Iterator[Text]:
    yield _styled_label(name, tree, cfg, style="bold blue")
    for item in tree.items:
        yield _highlight(f"{name}.{item}".replace("\n", r"\n"))
    for child_name, child in sorted(tree.children.items()):
        yield from _flat_lines(f"{name}.{child_name}", child, cfg)


def print_tree(pkg_name: str, tree: Tree, cfg: Config) -> None:
    console = Console(
        force_terminal={"auto": None, "always": True, "never": False}[cfg.color],
        color_system=None if cfg.color == "never" else "auto",
        no_color={"auto": None, "always": False, "never": True}[cfg.color],
    )
    if cfg.flat:
        for line in _flat_lines(pkg_name, tree, cfg):
            console.print(line, soft_wrap=True)
        return
    root = RichTree(_styled_label(pkg_name, tree, cfg, style="bold yellow"))
    _add_subtree(root, tree, cfg)
    console.print(root)


def render_tree(tree: Tree, prefix: str = "") -> list[str]:
    console = Console(color_system=None)
    root = RichTree("")
    _add_subtree(root, tree, Config(docstrings=DocstringMode.none))
    with console.capture() as capture:
        console.print(root)
    return [prefix + line for line in capture.get().splitlines()[1:]]
