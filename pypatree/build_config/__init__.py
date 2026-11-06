"""Read what a project's build configuration declares about its top-level modules."""

import configparser
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Optional

if sys.version_info >= (3, 11):  # pragma: no cover
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class BuildConfig:
    name: Optional[str] = None
    """The distribution name, normalized as by `normalize`."""
    include: tuple[str, ...] = ()
    """Glob patterns for the top-level module names the build declares."""
    roots: tuple[PurePosixPath, ...] = ()
    """Directories, relative to the project, that the build reads modules from."""


def normalize(name: str) -> str:
    """Compare distribution and module names, which differ in case and separators."""
    return re.sub(r"[-_.]+", "_", name).lower()


def read_build_config(project: Path) -> BuildConfig:
    """Read pyproject.toml and setup.cfg; unparsable files are logged and skipped.

    Understands the module declarations of hatch, setuptools, flit, uv, poetry,
    pdm, and maturin, and the distribution name of PEP 621 and poetry.
    """
    pyproject = _read(project / "pyproject.toml", tomllib.loads)
    tool = _get(pyproject, "tool")
    setup_cfg = _read(project / "setup.cfg", _parse_cfg)
    options = _get(setup_cfg, "options")
    find = _get(setup_cfg, "options.packages.find")

    names = _strings(_get(pyproject, "project", "name"))
    names += _strings(_get(tool, "poetry", "name"))
    names += _strings(_get(setup_cfg, "metadata", "name"))
    paths = [  # Module paths relative to the project.
        *_strings(_get(tool, "hatch", "build", "packages")),
        *_strings(_get(tool, "hatch", "build", "only-include")),
        *_strings(_get(tool, "hatch", "build", "targets", "wheel", "packages")),
        *_strings(_get(tool, "hatch", "build", "targets", "wheel", "only-include")),
        *_strings(_get(tool, "pdm", "build", "includes")),
    ]
    for package in _list(_get(tool, "poetry", "packages")):
        for include in _strings(_get(package, "include")):
            paths.append(str(PurePosixPath(*_strings(_get(package, "from")), include)))
    dotted = [  # Dotted module names, of which the first part is top-level.
        *_strings(_get(tool, "setuptools", "py-modules")),
        *_strings(_list(_get(tool, "setuptools", "packages"))),
        *_strings(_get(tool, "flit", "module", "name")),
        *_strings(_get(tool, "uv", "build-backend", "module-name")),
        *_strings(_get(tool, "maturin", "module-name")),
        *_lines(_get(options, "py_modules")),
    ]
    if not str(_get(options, "packages") or "").strip().startswith("find"):
        dotted += _lines(_get(options, "packages"))
    roots = [
        *_strings(_get(tool, "setuptools", "packages", "find", "where")),
        *_strings(_get(tool, "setuptools", "package-dir", "")),
        *_strings(_get(tool, "uv", "build-backend", "module-root")),
        *_strings(_get(tool, "pdm", "build", "package-dir")),
        *_strings(_get(tool, "maturin", "python-source")),
        *_lines(_get(find, "where")),
        *_cfg_package_dirs(_get(options, "package_dir")),
    ]
    patterns = [
        *_strings(_get(tool, "setuptools", "packages", "find", "include")),
        *_lines(_get(find, "include")),
    ]
    include = [path.name.removesuffix(".py") for path in map(PurePosixPath, paths)]
    include += [name.split(".")[0] for name in [*dotted, *patterns]]
    roots += [str(path.parent) for path in map(PurePosixPath, paths)]
    return BuildConfig(
        name=normalize(names[0]) if names else None,
        include=tuple(dict.fromkeys(include)),
        roots=tuple(
            dict.fromkeys(
                PurePosixPath(root) for root in roots if root not in ("", ".")
            )
        ),
    )


def _read(path: Path, parse: Callable[[str], Any]) -> Any:
    try:
        return parse(path.read_text())
    except FileNotFoundError:
        return {}
    except Exception as error:
        log.warning("Ignoring unparsable %s: %s", path, error)
        return {}


def _parse_cfg(text: str) -> dict[str, dict[str, str]]:
    parser = configparser.ConfigParser(interpolation=None)
    parser.read_string(text)
    return {section: dict(parser[section]) for section in parser.sections()}


def _get(table: Any, *keys: str) -> Any:
    for key in keys:
        table = table.get(key) if isinstance(table, dict) else None
    return table


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    """A string or list of strings, ignoring values of other types."""
    if isinstance(value, str):
        return [value]
    return [item for item in _list(value) if isinstance(item, str)]


def _lines(value: Any) -> list[str]:
    """A setup.cfg list, separated by newlines or commas."""
    if not isinstance(value, str):
        return []
    return [item.strip() for item in re.split(r"[\n,]", value) if item.strip()]


def _cfg_package_dirs(value: Any) -> list[str]:
    """The root directory from a setup.cfg package_dir mapping such as `=src`."""
    roots = []
    for line in _lines(value):
        package, _, directory = line.partition("=")
        if not package.strip():
            roots.append(directory.strip())
    return roots
