"""Configuration types for pypatree."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Optional

import tyro.conf

# Default excludes modules named "test" or starting with "test_"
DEFAULT_EXCLUDE = r"^test$|^test_"


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
    """Regex to exclude module segments (default: test modules). Use '' for none."""

    docstrings: DocstringMode = DocstringMode.short
    """Show module docstrings: none, short (first line), or full."""
