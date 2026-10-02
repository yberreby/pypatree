from rich.console import Console
from rich.syntax import Syntax
from rich.text import Text
from rich.tree import Tree as RichTree

from pypatree.config import Config, DocstringMode
from pypatree.introspection import get_module_docstring
from pypatree.tree import Tree

_SYNTAX = Syntax("", "python", theme="one-dark", background_color="default")


def _highlight(sig: str) -> Text:
    """Highlight a Python signature with syntax coloring."""
    wrapper = f"def {sig}: ..."
    text = _SYNTAX.highlight(wrapper)
    text.rstrip()
    # Slice based on actual positions in plain text
    start = len("def ")
    end = text.plain.rfind(": ...")
    return text[start:end]


def _module_label(name: str, modpath: str, style: str, cfg: Config) -> Text:
    label = Text(name, style=style)
    if cfg.docstrings != DocstringMode.none:
        doc = get_module_docstring(modpath, short=cfg.docstrings == DocstringMode.short)
        if doc:
            label.append(f"  {doc}", style="dim")
    return label


def _add_subtree(
    parent: RichTree,
    tree: Tree,
    modpath: str,
    cfg: Config,
) -> None:
    """Recursively add nodes to a rich tree."""
    items = tree.get("__items__", [])
    children = sorted(k for k in tree if k != "__items__")

    for item in items:
        parent.add(_highlight(item))

    for key in children:
        child_path = f"{modpath}.{key}"
        branch = parent.add(_module_label(key, child_path, style="bold blue", cfg=cfg))
        _add_subtree(branch, tree[key], child_path, cfg)


def print_tree(pkg_name: str, tree: Tree, cfg: Config) -> None:
    """Print a package tree using rich."""
    console = Console()

    rich_tree = RichTree(
        _module_label(pkg_name, pkg_name, style="bold yellow", cfg=cfg)
    )
    _add_subtree(rich_tree, tree, pkg_name, cfg)
    console.print(rich_tree)


def render_tree(tree: Tree, prefix: str = "") -> list[str]:
    """Render tree to lines with box-drawing characters (plain text)."""
    lines: list[str] = []
    items = tree.get("__items__", [])
    children = sorted(k for k in tree if k != "__items__")

    for i, item in enumerate(items):
        last = i == len(items) - 1 and not children
        lines.append(f"{prefix}{'└── ' if last else '├── '}{item}")

    for i, key in enumerate(children):
        last = i == len(children) - 1
        subtree = tree[key]

        lines.append(f"{prefix}{'└── ' if last else '├── '}{key}")
        ext = "    " if last else "│   "
        lines.extend(render_tree(subtree, prefix + ext))

    return lines
