from dataclasses import dataclass
from enum import Enum
from typing import Optional

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

    exclude: Optional[str] = DEFAULT_EXCLUDE
    """Regex to exclude module segments (default: test modules). Use '' for none."""

    docstrings: DocstringMode = DocstringMode.short
    """Show module docstrings: none, short (first line), or full."""
