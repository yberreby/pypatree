import importlib.metadata as meta
import json
import logging
import pkgutil
import re
from collections.abc import Iterable
from pathlib import Path
from types import ModuleType
from typing import Optional
from urllib.parse import unquote, urlsplit

from pypatree.introspection import ErrorHandler, import_module, log_error, safe_import

log = logging.getLogger(__name__)


def _module_names(paths: Iterable[str]) -> dict[str, bool]:
    paths = list(paths)
    names = {module.name: module.ispkg for module in pkgutil.iter_modules(paths)}
    for directory in paths:
        if not Path(directory).is_dir():
            continue
        for child in Path(directory).iterdir():
            if (
                child.name not in names
                and child.name.isidentifier()
                and child.name != "__pycache__"
                and child.is_dir()
                and any(child.rglob("*.py"))
            ):
                names[child.name] = True
    return names


def _find_packages_in_dir(source_path: str) -> list[str]:
    source = Path(source_path)
    source_dirs = [source]
    src = source / "src"
    if src.is_dir() and not (src / "__init__.py").is_file():
        source_dirs.append(src)
    packages = {
        module.name
        for module in pkgutil.iter_modules([str(path) for path in source_dirs])
        if module.ispkg and not module.name.startswith("_")
    }
    if packages:
        return sorted(packages)
    names = _module_names(str(path) for path in source_dirs)
    if len(source_dirs) > 1:
        names.pop("src", None)
    names = {
        name: package for name, package in names.items() if not name.startswith("_")
    }
    # A package project may also contain build scripts beside its packages.
    packages = [name for name, package in names.items() if package]
    return sorted(packages or names)


def _get_local_packages() -> list[str]:
    """Find packages installed from current directory via PEP 610 metadata."""
    cwd = Path.cwd().resolve()
    packages = []

    log.debug("Looking for packages installed from %s", cwd)

    for dist in meta.distributions():
        direct_url = dist.read_text("direct_url.json")
        if direct_url is None:
            continue
        data = json.loads(direct_url)
        if not data.get("dir_info", {}).get("editable", False):
            continue
        url = urlsplit(data["url"])
        assert url.scheme == "file", f"Expected local editable URL, got {data['url']}"
        source_path = Path(unquote(url.path)).resolve()
        if source_path == cwd:
            top_level = dist.read_text("top_level.txt")
            packages.extend(
                top_level.split()
                if top_level
                else _find_packages_in_dir(str(source_path))
            )

    log.debug("Local packages: %s", packages)
    return sorted(set(packages))


def _matches_exclude(name: str, pattern: Optional[re.Pattern[str]]) -> bool:
    """Check if any segment of a dotted name matches the exclude pattern."""
    if pattern is None:
        return False
    return any(pattern.search(seg) for seg in name.split("."))


def _submodules(
    pkg: ModuleType, pattern: Optional[re.Pattern[str]], on_error: ErrorHandler
) -> list[str]:
    pkg_name = pkg.__name__
    submods = [pkg_name]
    if not hasattr(pkg, "__path__"):
        return submods

    def walk(
        package_name: str, paths: Iterable[str], *, ancestors: frozenset[Path]
    ) -> None:
        fresh_paths: dict[Path, str] = {}
        for path in paths:
            resolved = Path(path).resolve()
            if resolved in ancestors:
                on_error(
                    f"Recursive package path while inspecting {package_name!r}: {resolved}"
                )
            else:
                fresh_paths[resolved] = path
        ancestors = ancestors.union(fresh_paths)
        for name, is_package in sorted(_module_names(fresh_paths.values()).items()):
            modname = f"{package_name}.{name}"
            if pattern and pattern.search(name):
                log.debug("Excluding module: %s", modname)
                continue
            if is_package:
                child = safe_import(modname, on_error=on_error)
                if child is None:
                    continue
                submods.append(modname)
                walk(modname, child.__path__, ancestors=ancestors)
            else:
                submods.append(modname)

    walk(pkg_name, pkg.__path__, ancestors=frozenset())
    return submods


def get_packages(
    exclude: Optional[str] = None,
    scope: Optional[str] = None,
    *,
    on_error: ErrorHandler = log_error,
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
            result[scope] = _submodules(
                import_module(scope), pattern, on_error=on_error
            )
        except ModuleNotFoundError as error:
            if error.name and (
                scope == error.name or scope.startswith(f"{error.name}.")
            ):
                raise ValueError(f"Scope {scope!r} does not exist") from error
            raise
        return result

    included = [name for name in local_packages if not _matches_exclude(name, pattern)]
    if local_packages and not included:
        raise ValueError(
            f"All local packages are excluded by --exclude {exclude!r}. "
            "Use --exclude '' to include them."
        )
    for pkg_name in included:
        pkg = safe_import(pkg_name, on_error=on_error)
        if pkg is None:
            continue

        log.debug("Walking package: %s", pkg_name)
        result[pkg_name] = _submodules(pkg, pattern, on_error=on_error)

    if included and not result:
        raise ImportError(
            "All discovered packages failed to import. Install the missing dependencies "
            "in the environment running pypatree."
        )
    return result
