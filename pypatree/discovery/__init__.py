import importlib.metadata as meta
import json
import logging
import os
import pkgutil
import re
from typing import Optional

from pypatree.introspection import safe_import

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


def _matches_exclude(name: str, pattern: Optional[re.Pattern[str]]) -> bool:
    """Check if any segment of a dotted name matches the exclude pattern."""
    if pattern is None:
        return False
    return any(pattern.search(seg) for seg in name.split("."))


def get_packages(exclude: Optional[str] = None) -> dict[str, list[str]]:
    """Find importable packages in CWD and their submodules."""
    pattern = re.compile(exclude) if exclude else None
    result: dict[str, list[str]] = {}

    for pkg_name in _get_local_packages():
        if _matches_exclude(pkg_name, pattern):
            log.info("Excluding package: %s", pkg_name)
            continue
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
