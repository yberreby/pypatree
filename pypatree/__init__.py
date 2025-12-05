from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
from typing import Any, Dict

from setuptools import find_packages

log = logging.getLogger(__name__)

Tree = Dict[str, Any]


def get_packages(skip_tests: bool = True) -> dict[str, list[str]]:
    """Find importable packages in CWD and their submodules."""
    result: dict[str, list[str]] = {}

    for pkg_name in find_packages():
        if "." in pkg_name:
            continue
        if skip_tests and pkg_name.startswith("test"):
            continue
        try:
            pkg = importlib.import_module(pkg_name)
        except ImportError as e:
            log.warning("Skipping %r: %s", pkg_name, e)
            continue

        submods = [pkg_name]
        for _, modname, _ in pkgutil.walk_packages(pkg.__path__, f"{pkg_name}."):
            if skip_tests and ".test" in modname:
                continue
            submods.append(modname)

        result[pkg_name] = submods

    return result


def get_module_items(modname: str, skip_tests: bool = True) -> list[str]:
    """Extract public functions and classes defined in a module."""
    try:
        mod = importlib.import_module(modname)
    except ImportError as e:
        log.warning("Could not import %r: %s", modname, e)
        return []

    items = []
    for name in dir(mod):
        if name.startswith("_"):
            continue
        if skip_tests and name.startswith("test"):
            continue
        obj = getattr(mod, name)
        if getattr(obj, "__module__", None) != modname:
            continue
        if inspect.isfunction(obj):
            items.append(f"{name}()")
        elif inspect.isclass(obj):
            items.append(name)

    return sorted(items)


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
