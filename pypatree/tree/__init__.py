import logging
from typing import Any, Optional

from pypatree.introspection import get_module_items

log = logging.getLogger(__name__)

Tree = dict[str, Any]


def build_tree(
    submods: list[str], pkg_name: str, exclude: Optional[str] = None
) -> Tree:
    """Build nested tree from flat module list."""
    log.debug("Building tree for %s from %d submodules", pkg_name, len(submods))
    tree: Tree = {}

    for modname in sorted(submods):
        if modname == pkg_name:
            tree["__items__"] = get_module_items(modname, exclude=exclude)
            continue

        parts = modname[len(pkg_name) + 1 :].split(".")
        node = tree
        for part in parts:
            node = node.setdefault(part, {})
        node["__items__"] = get_module_items(modname, exclude=exclude)

    log.debug("Tree built with %d top-level entries", len(tree))
    return tree
