"""Inspection results shared by the source and runtime backends."""

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Optional

from pypatree.signature import Signature


@dataclass
class Tree:
    """A module's docstring, public functions and classes, and submodules."""

    items: list[Signature] = field(default_factory=list)
    """Signatures in definition order."""
    children: dict[str, "Tree"] = field(default_factory=dict)
    docstring: Optional[str] = None
    error: Optional[str] = None
    """Why this module could not be fully inspected."""

    def errors(self, name: str) -> Iterator[tuple[str, str]]:
        """Yield (qualified module name, error) for this module and its submodules."""
        if self.error is not None:
            yield name, self.error
        for child_name, child in sorted(self.children.items()):
            yield from child.errors(f"{name}.{child_name}")
