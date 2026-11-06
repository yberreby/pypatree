"""Locate Python modules on disk without importing them."""

import inspect
import re
from pathlib import Path

TEST_NAME = re.compile(r"^tests?$|^test_")
"""Names of test modules and directories."""


def modules(directory: Path) -> dict[str, Path]:
    """Map each module importable from directory to its package directory or file.

    As in imports, a regular package shadows a module, which shadows a namespace
    package. Unlike imports, a source file shadows a compiled module so that its
    source can be read.
    """
    if not directory.is_dir():
        return {}
    entries = sorted(directory.iterdir(), key=lambda path: (path.suffix != ".py", path))
    directories = [
        path for path in entries if path.is_dir() and path.name.isidentifier()
    ]
    found: dict[str, Path] = {}
    for path in directories:
        if is_package(path):
            found[path.name] = path
    for path in entries:
        name = inspect.getmodulename(path.name)
        if name and name.isidentifier() and name != "__init__" and path.is_file():
            found.setdefault(name, path)
    for path in directories:
        if path.name != "__pycache__" and any(path.rglob("*.py")):
            found.setdefault(path.name, path)
    return found


def is_package(directory: Path) -> bool:
    """Whether directory has an `__init__` module, in source or compiled form."""
    return any(
        inspect.getmodulename(path.name) == "__init__"
        for path in directory.glob("__init__.*")
    )


def project_packages(project: Path) -> dict[str, Path]:
    """Map a project's public top-level modules to their paths.

    Searches the project root and a `src` directory that is not itself a package,
    ignoring tests and virtual environments. Prefers regular packages, then
    namespace packages, then single modules, so build scripts beside a package
    are not mistaken for the project's API.
    """
    src = project / "src"
    directories = [project]
    if src.is_dir() and not is_package(src):
        directories.append(src)
    found: dict[str, Path] = {}
    for directory in directories:
        for name, path in modules(directory).items():
            if (
                name.startswith("_")
                or TEST_NAME.search(name)
                or path in directories
                or (path / "pyvenv.cfg").is_file()
            ):
                continue
            if name in found:
                raise ValueError(
                    f"Ambiguous source package {name!r}: {found[name]} and {path}"
                )
            found[name] = path
    rank = {name: _rank(path) for name, path in found.items()}
    best = min(rank.values(), default=None)
    return {name: path for name, path in sorted(found.items()) if rank[name] == best}


def _rank(path: Path) -> int:
    if path.is_file():
        return 2
    return 0 if is_package(path) else 1
