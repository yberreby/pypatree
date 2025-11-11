"""Display module tree with public functions/classes."""

import importlib
import inspect
import pkgutil
from typing import Any, Dict, List

from setuptools import find_packages


def get_packages(skip_tests: bool = True) -> Dict[str, List[str]]:
    """Get all packages and their submodules using setuptools + pkgutil."""
    top_level_packages = [pkg for pkg in find_packages() if "." not in pkg]

    grouped = {}
    for pkg_name in top_level_packages:
        pkg = importlib.import_module(pkg_name)

        # Walk the package to find all submodules (including .py files)
        submods = []
        for _importer, modname, _ispkg in pkgutil.walk_packages(
            pkg.__path__, prefix=f"{pkg_name}."
        ):
            # Skip test modules if requested
            if skip_tests and (".test" in modname or modname.startswith("test")):
                continue
            submods.append(modname)

        # Include the top-level package itself
        grouped[pkg_name] = [pkg_name] + submods

    return grouped


def get_module_items(modname: str, skip_tests: bool = True) -> List[str]:
    """Extract public functions and classes from a module."""
    items = []
    try:
        mod = importlib.import_module(modname)
        for name in dir(mod):
            if name.startswith("_"):
                continue
            # Skip test functions/classes if requested
            if skip_tests and name.startswith("test"):
                continue
            obj = getattr(mod, name)
            if getattr(obj, "__module__", None) == modname:
                if inspect.isfunction(obj):
                    items.append(f"{name}()")
                elif inspect.isclass(obj):
                    items.append(name)
    except Exception:
        pass
    return sorted(items)


def build_tree(
    submods: List[str], pkg_name: str, skip_tests: bool = True
) -> Dict[str, Any]:
    """Build nested tree structure from flat module list."""
    tree = {}
    for modname in sorted(submods):
        if modname == pkg_name:
            tree["__items__"] = get_module_items(modname, skip_tests=skip_tests)
            continue

        short_name = modname[len(pkg_name) + 1 :]
        parts = short_name.split(".")

        current = tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]

        current["__items__"] = get_module_items(modname, skip_tests=skip_tests)
    return tree
