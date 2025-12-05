from dataclasses import dataclass
from enum import Enum


class DocstringMode(Enum):
    """How to display module docstrings."""

    none = "none"
    short = "short"  # first line only
    full = "full"


@dataclass
class Config:
    """Configuration for pypatree output."""

    skip_tests: bool = True
    docstrings: DocstringMode = DocstringMode.short
