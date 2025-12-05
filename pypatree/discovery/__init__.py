import importlib
import logging
import pkgutil

from setuptools import find_packages

log = logging.getLogger(__name__)


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
