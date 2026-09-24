import importlib
import importlib.metadata as meta
import json
import logging
import os
import pkgutil
import re
from collections.abc import Iterable
from typing import Optional

from pypatree.introspection import safe_import

log = logging.getLogger(__name__)


def _find_packages_in_dir(source_path: str) -> list[str]:
    """Find top-level Python packages in a source directory.

    Handles three layouts:
    1. src-as-package: src/__init__.py exists -> src IS the package
    2. src-layout: src/mypkg/__init__.py -> search inside src/
    3. flat-layout: mypkg/__init__.py -> search in root
    """
    src_dir = os.path.join(source_path, "src")
    src_init = os.path.join(src_dir, "__init__.py")

    # Case 1: src itself is a package
    if os.path.isfile(src_init):
        log.debug("src/__init__.py found - treating 'src' as package")
        return ["src"]

    # Case 2: src-layout (src/ exists but no __init__.py)
    # Case 3: flat-layout (no src/ directory)
    search_dir = src_dir if os.path.isdir(src_dir) else source_path
    log.debug("Searching for packages in %s", search_dir)

    packages = []
    for name in os.listdir(search_dir):
        if name.startswith((".", "_")):
            continue
        pkg_path = os.path.join(search_dir, name)
        init_path = os.path.join(pkg_path, "__init__.py")
        if os.path.isdir(pkg_path) and os.path.isfile(init_path):
            packages.append(name)

    return packages


def _get_local_packages() -> list[str]:
    """Find packages installed from current directory via PEP 610 metadata."""
    cwd_url = "file://" + os.getcwd()
    packages = []

    log.debug("Looking for packages installed from %s", cwd_url)

    for dist in meta.distributions():
        for f in dist.files or []:
            if f.name == "direct_url.json":
                data = json.loads(f.read_text())
                url = data.get("url", "").rstrip("/")
                # Must be EXACTLY cwd, not a subdirectory
                if url == cwd_url and data.get("dir_info", {}).get("editable"):
                    assert url.startswith("file://"), f"Expected file:// URL, got {url}"
                    source_path = url.removeprefix("file://")
                    for pkg in _find_packages_in_dir(source_path):
                        log.debug("Found local package: %s", pkg)
                        packages.append(pkg)
                break

    log.debug("Local packages: %s", packages)
    return packages


def _matches_exclude(name: str, pattern: Optional[re.Pattern[str]]) -> bool:
    """Check if any segment of a dotted name matches the exclude pattern."""
    if pattern is None:
        return False
    return any(pattern.search(seg) for seg in name.split("."))


def _scoped_submodules(pkg_name: str, pattern: Optional[re.Pattern[str]]) -> list[str]:
    pkg = importlib.import_module(pkg_name)
    submods = [pkg_name]
    if not hasattr(pkg, "__path__"):
        return submods

    def walk(package_name: str, paths: Iterable[str]) -> None:
        for module in pkgutil.iter_modules(paths, f"{package_name}."):
            if _matches_exclude(module.name[len(pkg_name) + 1 :], pattern):
                log.debug("Excluding module: %s", module.name)
                continue
            submods.append(module.name)
            if module.ispkg:
                child = importlib.import_module(module.name)
                walk(module.name, child.__path__)

    walk(pkg_name, pkg.__path__)
    return submods


def get_packages(
    exclude: Optional[str] = None, scope: Optional[str] = None
) -> dict[str, list[str]]:
    """Find importable packages in CWD and their submodules."""
    pattern = re.compile(exclude) if exclude else None
    result: dict[str, list[str]] = {}
    local_packages = _get_local_packages()

    if scope:
        roots = [
            name
            for name in local_packages
            if scope == name or scope.startswith(f"{name}.")
        ]
        if not roots:
            raise ValueError(f"Scope {scope!r} is not in a local editable package")
        root = max(roots, key=len)
        if _matches_exclude(scope[len(root) + 1 :], pattern) and scope != root:
            raise ValueError(f"Scope {scope!r} is excluded by --exclude {exclude!r}")
        try:
            result[scope] = _scoped_submodules(scope, pattern)
        except ModuleNotFoundError as error:
            if error.name and (
                scope == error.name or scope.startswith(f"{error.name}.")
            ):
                raise ValueError(f"Scope {scope!r} does not exist") from error
            raise
        return result

    for pkg_name in local_packages:
        pkg = safe_import(pkg_name)
        if pkg is None:
            continue

        log.debug("Walking package: %s", pkg_name)
        submods = [pkg_name]
        for _, modname, _ in pkgutil.walk_packages(pkg.__path__, f"{pkg_name}."):
            if _matches_exclude(modname, pattern):
                log.debug("Excluding module: %s", modname)
                continue
            submods.append(modname)

        result[pkg_name] = submods

    return result
