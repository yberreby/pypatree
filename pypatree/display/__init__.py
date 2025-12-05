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
        label = f"[bold blue]{key}[/bold blue]"

        if cfg.docstrings != DocstringMode.none:
            short = cfg.docstrings == DocstringMode.short
            doc = get_module_docstring(child_path, short=short)
            if doc:
                label += f"  [dim]{doc}[/dim]"

        branch = parent.add(label)
        _add_subtree(branch, tree[key], child_path, cfg)


def print_tree(pkg_name: str, tree: Tree, cfg: Config) -> None:
    """Print a package tree using rich."""
    console = Console()

    label = f"[bold yellow]{pkg_name}[/bold yellow]"
    if cfg.docstrings != DocstringMode.none:
        short = cfg.docstrings == DocstringMode.short
        doc = get_module_docstring(pkg_name, short=short)
        if doc:
            label += f"  [dim]{doc}[/dim]"

    rich_tree = RichTree(label)
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
