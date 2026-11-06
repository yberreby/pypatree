"""Locate Python modules on disk without importing them."""

import inspect
import re
from fnmatch import fnmatchcase
from pathlib import Path

from pypatree.build_config import normalize, read_build_config

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
    """Map the public top-level modules that a project's build ships to their paths.

    In order of preference: the modules its build configuration declares; the
    contents of its source directory, `src` or a declared one; the module named
    after the project; and, as in setuptools' flat layout, the packages, else
    namespace packages, else modules, passing over names such as `docs`.
    Tests and virtual environments are never part of the result.
    """
    config = read_build_config(project)
    src = project / "src"
    sources = [project / root for root in config.roots]
    if not sources and src.is_dir() and not is_package(src):
        sources = [src]
    found: dict[str, Path] = {}
    for directory in [project, *sources]:
        for name, path in modules(directory).items():
            if (
                name.startswith("_")
                or path in sources
                or (path / "pyvenv.cfg").is_file()
            ):
                continue
            if name in found and found[name] != path:
                raise ValueError(
                    f"Ambiguous source package {name!r}: {found[name]} and {path}"
                )
            found[name] = path
    declared = {
        name: path
        for name, path in found.items()
        if any(fnmatchcase(name, pattern) for pattern in config.include)
    }
    public = {name: path for name, path in found.items() if not TEST_NAME.search(name)}
    in_sources = {name: path for name, path in public.items() if path.parent in sources}
    named = {
        name: path for name, path in public.items() if normalize(name) == config.name
    }
    for chosen in [declared, in_sources, named]:
        if chosen:
            return dict(sorted(chosen.items()))
    rank = {name: _rank(name, path) for name, path in public.items()}
    best = min(rank.values(), default=None)
    return {name: path for name, path in sorted(public.items()) if rank[name] == best}


# Names that setuptools' flat layout does not ship (setuptools.discovery, 84.2).
_UNSHIPPED_PACKAGES = frozenset(
    "benchmark benchmarks bin build changelog ci debian dist doc docs documentation "
    "env example examples exercise exercises fabfile htmlcov manpages news "
    "newsfragments python requirements scripts site_scons tasks tools util utils "
    "venv".split()
)
_UNSHIPPED_MODULES = frozenset(
    "benchmark benchmarks build conanfile conftest dodo example examples exercise "
    "exercises fabfile manage noxfile pavement setup tasks toxfile".split()
)


def _rank(name: str, path: Path) -> tuple[bool, int]:
    if path.is_file():
        return name in _UNSHIPPED_MODULES, 2
    return name in _UNSHIPPED_PACKAGES, 0 if is_package(path) else 1
