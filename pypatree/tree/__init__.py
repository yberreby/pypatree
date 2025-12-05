from typing import Any

from pypatree.introspection import get_module_items

Tree = dict[str, Any]


def build_tree(submods: list[str], pkg_name: str, skip_tests: bool = True) -> Tree:
    """Build nested tree from flat module list."""
    tree: Tree = {}

    for modname in sorted(submods):
        if modname == pkg_name:
            tree["__items__"] = get_module_items(modname, skip_tests=skip_tests)
            continue

        parts = modname[len(pkg_name) + 1 :].split(".")
        node = tree
        for part in parts:
            node = node.setdefault(part, {})
        node["__items__"] = get_module_items(modname, skip_tests=skip_tests)

    return tree
