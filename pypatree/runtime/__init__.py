"""Inspect editable-installed packages by importing them."""

import importlib
import importlib.metadata
import inspect
import json
import logging
import sys
from contextlib import redirect_stdout
from pathlib import Path
from types import ModuleType
from typing import Optional
from urllib.parse import urlsplit
from urllib.request import url2pathname

from pypatree.config import Exclusion, select_modules
from pypatree.introspection import module_items
from pypatree.layout import modules, project_packages
from pypatree.tree import Tree

log = logging.getLogger(__name__)


def runtime_trees(
    root: Path,
    *,
    scope: Optional[str] = None,
    exclude: Exclusion = Exclusion(),
    show_defaults: bool = False,
) -> dict[str, Tree]:
    """Import the packages installed in editable mode from root.

    Importing runs project code, including the parent package initializers of a scope.
    """
    packages = editable_packages(root)
    if not packages:
        raise ValueError(
            f"No local editable packages found in {root}. "
            "Run `uv pip install -e .` from the Python package's project directory, "
            "then rerun pypatree there. Use --verbose for discovery details."
        )
    selected = select_modules(packages, scope, exclude)
    if scope is not None:
        module = _import_scope(scope)
        return {
            scope: _module_tree(module, exclude=exclude, show_defaults=show_defaults)
        }
    return {
        name: _import_tree(name, exclude=exclude, show_defaults=show_defaults)
        for name in selected
    }


def editable_packages(project: Path) -> list[str]:
    """Top-level packages installed in editable mode from project, per PEP 610."""
    project = project.resolve()
    packages: set[str] = set()
    for distribution in importlib.metadata.distributions():
        direct_url = distribution.read_text("direct_url.json")
        if direct_url is None:
            continue
        data = json.loads(direct_url)
        if not data.get("dir_info", {}).get("editable", False):
            continue
        url = urlsplit(data["url"])
        assert url.scheme == "file", f"Expected a local editable URL, got {data['url']}"
        if Path(url2pathname(url.path)).resolve() != project:
            continue
        top_level = distribution.read_text("top_level.txt")
        packages.update(top_level.split() if top_level else project_packages(project))
    log.debug("Editable packages from %s: %s", project, sorted(packages))
    return sorted(packages)


def import_module(name: str) -> ModuleType:
    """Import a module, sending anything it prints to stderr."""
    try:
        with redirect_stdout(sys.stderr):
            return importlib.import_module(name)
    except SystemExit as error:
        raise ImportError(f"{name!r} called sys.exit({error.code!r})") from error


def _import_scope(scope: str) -> ModuleType:
    """Import scope, distinguishing a missing scope from a missing dependency."""
    try:
        return import_module(scope)
    except ModuleNotFoundError as error:
        if error.name and (scope == error.name or scope.startswith(f"{error.name}.")):
            raise ValueError(f"Scope {scope!r} does not exist") from error
        raise


def _import_tree(
    name: str,
    *,
    exclude: Exclusion,
    show_defaults: bool,
    ancestors: frozenset[Path] = frozenset(),
) -> Tree:
    try:
        module = import_module(name)
    except Exception as error:
        return Tree(error=f"{type(error).__name__}: {error}")
    return _module_tree(
        module, exclude=exclude, show_defaults=show_defaults, ancestors=ancestors
    )


def _module_tree(
    module: ModuleType,
    *,
    exclude: Exclusion,
    show_defaults: bool,
    ancestors: frozenset[Path] = frozenset(),
) -> Tree:
    tree = Tree(docstring=inspect.getdoc(module) or None)
    problems = []
    try:
        tree.items = module_items(module, exclude=exclude, show_defaults=show_defaults)
    except Exception as error:  # Such as a default whose __repr__ raises.
        problems.append(f"{type(error).__name__}: {error}")
    paths = {Path(path).resolve() for path in getattr(module, "__path__", ())}
    recursive = sorted(paths & ancestors)
    if recursive:
        problems.append(f"Recursive package path: {', '.join(map(str, recursive))}")
    tree.error = "; ".join(problems) or None
    names = {name for path in paths - ancestors for name in modules(path)}
    names.discard("__main__")  # Importing an entry script runs it.
    for name in sorted(names):
        if exclude(name):
            log.debug("Excluding module: %s.%s", module.__name__, name)
            continue
        tree.children[name] = _import_tree(
            f"{module.__name__}.{name}",
            exclude=exclude,
            show_defaults=show_defaults,
            ancestors=ancestors | paths,
        )
    return tree
