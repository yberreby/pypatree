"""Command-line options and the module selection they describe."""

import re
from collections.abc import Collection
from dataclasses import dataclass
from typing import Annotated, Literal, Optional

import tyro.conf

from pypatree.layout import TEST_NAME

DEFAULT_EXCLUDE = TEST_NAME.pattern


@dataclass
class Config:
    scope: Annotated[
        Optional[str], tyro.conf.Positional, tyro.conf.arg(metavar="[MODULE]")
    ] = None
    """Dotted module to inspect, such as 'mypkg.parsers'."""

    exclude: str = DEFAULT_EXCLUDE
    """Regex excluding matching module segments and item names. '' disables it."""

    docstrings: Literal["none", "short", "full"] = "short"
    """Module docstrings to show: none, the first line, or all of it."""

    show_defaults: bool = False
    """Show default values in signatures. Otherwise, = ... marks optional parameters."""

    flat: bool = False
    """Print fully qualified names, one item per line, without tree guides or wrapping."""

    color: Literal["auto", "always", "never"] = "auto"
    """Color policy for either output format. Auto detects the terminal."""

    verbose: bool = False
    """Log discovery details and tracebacks to stderr."""

    runtime: bool = False
    """Import editable-installed code in this environment. Default: read local source."""


class Exclusion:
    """Excludes a dotted name when the regex matches any of its segments."""

    def __init__(self, regex: str = DEFAULT_EXCLUDE) -> None:
        self.regex = regex
        self._pattern = re.compile(regex) if regex else None

    def __call__(self, name: str) -> bool:
        pattern = self._pattern
        return pattern is not None and any(map(pattern.search, name.split(".")))

    def __repr__(self) -> str:
        return f"Exclusion({self.regex!r})"


def select_modules(
    packages: Collection[str], scope: Optional[str], exclude: Exclusion
) -> list[str]:
    """The top-level packages to inspect, or the scope if it names a module within one."""
    if scope is None:
        included = sorted(name for name in packages if not exclude(name))
        if not included:
            raise ValueError(
                f"All local packages are excluded by --exclude {exclude.regex!r}. "
                "Use --exclude '' to include them."
            )
        return included
    package, _, inner = scope.partition(".")
    if not all(part.isidentifier() for part in scope.split(".")):
        raise ValueError(f"Invalid module scope {scope!r}: use a dotted Python name")
    if package not in packages:
        raise ValueError(
            f"Scope {scope!r} is not in a local package. Found: {', '.join(sorted(packages))}"
        )
    if inner and exclude(inner):
        raise ValueError(f"Scope {scope!r} is excluded by --exclude {exclude.regex!r}")
    return [scope]
