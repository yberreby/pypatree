import importlib
import importlib.metadata as meta
import json
import logging
import os
import pkgutil

log = logging.getLogger(__name__)


def _get_local_packages() -> list[str]:
    """Find packages installed from current directory via PEP 610 metadata."""
    cwd_url = "file://" + os.getcwd()
    packages = []

    log.debug("Looking for packages installed from %s", cwd_url)

    for dist in meta.distributions():
        for f in dist.files or []:
            if f.name == "direct_url.json":
                data = json.loads(f.read_text())
                url = data.get("url", "")
                if url.startswith(cwd_url):
                    name = dist.metadata["Name"]
                    if name:
                        log.debug("Found local package: %s (%s)", name, url)
                        packages.append(name)
                break

    log.debug("Local packages: %s", packages)
    return packages


def get_packages(skip_tests: bool = True) -> dict[str, list[str]]:
    """Find importable packages in CWD and their submodules."""
    result: dict[str, list[str]] = {}

    for pkg_name in _get_local_packages():
        if skip_tests and pkg_name.startswith("test"):
            log.debug("Skipping test package: %s", pkg_name)
            continue
        try:
            pkg = importlib.import_module(pkg_name)
        except ImportError as e:
            log.warning("Skipping %r: %s", pkg_name, e)
            continue

        log.debug("Walking package: %s", pkg_name)
        submods = [pkg_name]
        for _, modname, _ in pkgutil.walk_packages(pkg.__path__, f"{pkg_name}."):
            if skip_tests and ".test" in modname:
                continue
            submods.append(modname)

        result[pkg_name] = submods

    return result
