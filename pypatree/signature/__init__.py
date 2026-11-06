"""Call signatures, independent of how they were inspected."""

import inspect
from dataclasses import dataclass
from typing import Optional

Kind = inspect._ParameterKind

_POSITIONAL_ONLY = inspect.Parameter.POSITIONAL_ONLY
_VAR_POSITIONAL = inspect.Parameter.VAR_POSITIONAL
_KEYWORD_ONLY = inspect.Parameter.KEYWORD_ONLY
_PREFIXES = {_VAR_POSITIONAL: "*", inspect.Parameter.VAR_KEYWORD: "**"}


@dataclass(frozen=True)
class Parameter:
    name: str
    kind: Kind
    annotation: Optional[str] = None
    default: Optional[str] = None
    """Default as displayed, such as a source expression or `...`; None if required."""

    def __str__(self) -> str:
        text = _PREFIXES.get(self.kind, "") + self.name
        if self.annotation is not None:
            text += f": {self.annotation}"
        if self.default is not None:
            text += (
                f" = {self.default}"
                if self.annotation is not None
                else f"={self.default}"
            )
        return text


@dataclass(frozen=True)
class Signature:
    """How to call a function or class. Unknown parameters display as `name(...)`."""

    name: str
    parameters: Optional[tuple[Parameter, ...]]
    returns: Optional[str] = None

    def __post_init__(self) -> None:
        kinds = [parameter.kind for parameter in self.parameters or ()]
        if kinds != sorted(kinds):
            raise ValueError(f"Parameters of {self.name!r} are out of order: {kinds}")

    @property
    def parts(self) -> list[str]:
        """Parameters with the `/` and `*` separators that Python syntax requires."""
        parts: list[str] = []
        previous: Optional[Kind] = None
        for parameter in self.parameters or ():
            if previous == _POSITIONAL_ONLY and parameter.kind != _POSITIONAL_ONLY:
                parts.append("/")
            if parameter.kind == _KEYWORD_ONLY and previous not in (
                _VAR_POSITIONAL,
                _KEYWORD_ONLY,
            ):
                parts.append("*")
            parts.append(str(parameter))
            previous = parameter.kind
        if previous == _POSITIONAL_ONLY:
            parts.append("/")
        return parts

    def lines(self, width: Optional[int] = None) -> list[str]:
        """The signature on one line, or one parameter per line if wider than width."""
        text = str(self)
        if width is None or len(text) <= width or not self.parameters:
            return [text]
        return [
            f"{self.name}(",
            *(f"{part}," for part in self.parts),
            f"){self._returns}",
        ]

    @property
    def _returns(self) -> str:
        return "" if self.returns is None else f" -> {self.returns}"

    def __str__(self) -> str:
        parameters = "..." if self.parameters is None else ", ".join(self.parts)
        return f"{self.name}({parameters}){self._returns}"
