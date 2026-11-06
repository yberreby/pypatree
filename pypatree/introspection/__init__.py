"""Signatures of live functions and classes."""

import importlib
import inspect
import logging
import sys
import types
from collections import abc
from types import ModuleType
from typing import (
    Annotated,
    Any,
    Callable,
    ForwardRef,
    Literal,
    Optional,
    Union,
    get_args,
    get_origin,
)

from pypatree.config import Exclusion
from pypatree.signature import Parameter, Signature

log = logging.getLogger(__name__)

_EMPTY = inspect.Parameter.empty
# Python 3.14 defers annotations; FORWARDREF keeps unresolvable names instead of raising.
_SIGNATURE_OPTIONS: dict[str, Any] = (
    {"annotation_format": importlib.import_module("annotationlib").Format.FORWARDREF}
    if sys.version_info >= (3, 14)
    else {}
)


def module_items(
    module: ModuleType, *, exclude: Exclusion, show_defaults: bool
) -> list[Signature]:
    """Signatures of the public functions and classes defined in module."""
    return [
        signature_of(obj, name=name, show_defaults=show_defaults)
        # vars() skips module __getattr__ and __dir__ hooks; the copy tolerates
        # inspection that binds new module globals.
        for name, obj in list(vars(module).items())
        if not name.startswith("_")
        and not exclude(name)
        and (inspect.isfunction(obj) or inspect.isclass(obj))
        and obj.__module__ == module.__name__
    ]


def signature_of(
    obj: Union[Callable[..., object], type],
    *,
    name: Optional[str] = None,
    show_defaults: bool,
) -> Signature:
    """The call signature of a function or class, named by its binding if given."""
    name = obj.__name__ if name is None else name
    try:
        signature = inspect.signature(obj, **_SIGNATURE_OPTIONS)
    except (ValueError, TypeError) as error:
        log.warning("Could not inspect signature for %s: %s", name, error)
        return Signature(name, parameters=None)
    parameters = tuple(
        Parameter(
            parameter.name,
            parameter.kind,
            annotation=_declared(parameter.annotation),
            default=None
            if parameter.default is _EMPTY
            else _default(parameter.default, show_defaults),
        )
        for parameter in signature.parameters.values()
    )
    # Calling a class returns an instance, whatever __init__ declares.
    returns = None if inspect.isclass(obj) else _declared(signature.return_annotation)
    return Signature(name, parameters, returns)


def _declared(annotation: object) -> Optional[str]:
    return None if annotation is _EMPTY else _annotation(annotation)


def _default(value: object, show_defaults: bool) -> str:
    if not show_defaults:
        return "..."
    text = repr(value)
    # Object addresses change between runs and carry no API information.
    address = f" at {id(value):#x}>"
    return text[: -len(address)] + ">" if text.endswith(address) else text


def _annotation(annotation: object) -> str:
    if isinstance(annotation, str):
        return annotation
    if isinstance(annotation, ForwardRef):
        return annotation.__forward_arg__
    if annotation is Ellipsis:
        return "..."
    if annotation is type(None):
        return "None"
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is Annotated:
        return _annotation(args[0])
    if origin is Union or (sys.version_info >= (3, 10) and origin is types.UnionType):
        return " | ".join(map(_annotation, args))
    if origin is abc.Callable and args:
        parameters, result = args
        inputs = (
            f"[{', '.join(map(_annotation, parameters))}]"
            if isinstance(parameters, list)
            else _annotation(parameters)
        )
        return f"Callable[{inputs}, {_annotation(result)}]"
    if origin is not None and origin is not Literal and args:
        return (
            f"{inspect.formatannotation(origin)}[{', '.join(map(_annotation, args))}]"
        )
    return inspect.formatannotation(annotation)
