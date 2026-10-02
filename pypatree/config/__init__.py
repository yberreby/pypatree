"""Configuration types for pypatree."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Literal, Optional

import tyro.conf

DEFAULT_EXCLUDE = r"^tests?$|^test_"


class DocstringMode(Enum):
    """How to display module docstrings."""

    none = "none"
    short = "short"
    full = "full"


@dataclass
class Config:
    """Configuration for pypatree output."""

    scope: Annotated[
        Optional[str], tyro.conf.Positional, tyro.conf.arg(metavar="[MODULE]")
    ] = None
    """Module path to scope to (e.g., 'mypkg.submodule')."""

    exclude: Optional[str] = DEFAULT_EXCLUDE
    """Regex to exclude module segments and item names (default: tests). Use '' for none."""

    docstrings: DocstringMode = DocstringMode.short
    """Show module docstrings: none, short (first line), or full."""

    show_defaults: bool = False
    """Show default values in signatures. Otherwise, = ... marks optional parameters."""

    flat: bool = False
    """Print fully qualified names, one item per line, without tree guides or wrapping."""

    color: Literal["auto", "always", "never"] = "auto"
    """Color policy for either output format. Auto detects the terminal."""

    verbose: bool = False
    """Enable debug logging to stderr."""

    runtime: bool = False
    """Import editable-installed code in this environment. Default: read local source."""
