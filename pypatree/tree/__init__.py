from dataclasses import dataclass, field
from typing import Optional

from pypatree.introspection import (
    ErrorHandler,
    get_module_items,
    log_error,
    safe_import,
)


@dataclass
class Tree:
    items: list[str] = field(default_factory=list)
    children: dict[str, "Tree"] = field(default_factory=dict)
    docstring: Optional[str] = None
    failed: bool = False


def get_subtree(tree: Tree, path: list[str]) -> Optional[Tree]:
    node = tree
    for part in path:
        if part not in node.children:
            return None
        node = node.children[part]
    return node


def build_tree(
    submods: list[str],
    pkg_name: str,
    exclude: Optional[str],
    show_defaults: bool,
    *,
    max_width: Optional[int] = None,
    on_error: ErrorHandler = log_error,
) -> Tree:
    tree = Tree()
    for modname in sorted(set(submods)):
        if modname != pkg_name and not modname.startswith(f"{pkg_name}."):
            raise ValueError(f"Module {modname!r} is outside package {pkg_name!r}")
        parts = [] if modname == pkg_name else modname[len(pkg_name) + 1 :].split(".")
        node = tree
        for part in parts:
            node = node.children.setdefault(part, Tree())
        module = safe_import(modname, on_error=on_error)
        if module is None:
            node.failed = True
            continue
        node.docstring = module.__doc__.strip() if module.__doc__ else None
        node.items = get_module_items(
            modname,
            exclude=exclude,
            show_defaults=show_defaults,
            max_width=None if max_width is None else max_width - 4 * (len(parts) + 1),
            on_error=on_error,
        )
    return tree
