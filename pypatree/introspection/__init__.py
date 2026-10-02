import importlib
import inspect
import logging
import re
import sys
import types
from collections import abc
from contextlib import redirect_stdout
from types import ModuleType
from typing import (
    Annotated,
    Callable,
    ForwardRef,
    Literal,
    Optional,
    Union,
    get_args,
    get_origin,
)

log = logging.getLogger(__name__)
ErrorHandler = Callable[[str], None]
log_error: ErrorHandler = log.error


def import_module(modname: str) -> ModuleType:
    try:
        with redirect_stdout(sys.stderr):
            return importlib.import_module(modname)
    except SystemExit as error:
        raise ImportError(f"{modname!r} called sys.exit({error.code!r})") from error


def safe_import(
    modname: str, *, on_error: ErrorHandler = log_error
) -> Optional[ModuleType]:
    """Import a module, logging import failures to stderr."""
    try:
        return import_module(modname)
    except Exception as error:
        on_error(f"Could not import {modname!r}: {type(error).__name__}: {error}")
    return None


_OBJECT_ADDR_RE = re.compile(r" at 0x[0-9a-fA-F]+>")


def _format_annotation(annotation: object) -> str:
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
        return _format_annotation(args[0])
    if origin is Union or (sys.version_info >= (3, 10) and origin is types.UnionType):
        return " | ".join(_format_annotation(arg) for arg in args)
    if origin is abc.Callable and args:
        parameters, result = args
        inputs = (
            "[" + ", ".join(_format_annotation(arg) for arg in parameters) + "]"
            if isinstance(parameters, list)
            else _format_annotation(parameters)
        )
        return f"Callable[{inputs}, {_format_annotation(result)}]"
    if origin is not None and origin is not Literal and args:
        arguments = ", ".join(_format_annotation(arg) for arg in args)
        return f"{inspect.formatannotation(origin)}[{arguments}]"
    return inspect.formatannotation(annotation)


def _format_parameter(parameter: inspect.Parameter, show_defaults: bool) -> str:
    empty = inspect.Parameter.empty
    result = str(parameter.replace(annotation=empty, default=empty))
    if parameter.annotation is not empty:
        result += f": {_format_annotation(parameter.annotation)}"
    if parameter.default is not empty:
        separator = " = " if parameter.annotation is not empty else "="
        default = repr(parameter.default) if show_defaults else "..."
        if show_defaults and not isinstance(parameter.default, str):
            default = _OBJECT_ADDR_RE.sub(">", default)
        result += separator + default
    return result


_MAX_ONELINER = 80


def _format_params(
    params: list[inspect.Parameter], max_len: Optional[int], show_defaults: bool
) -> str:
    """Format parameters, using multiple lines if needed.

    Handles /, *, and *args/**kwargs markers correctly.
    """
    if not params:
        return "()"

    # Build parts with proper markers
    parts: list[str] = []
    saw_var_positional = False
    prev_kind = None
    PK = inspect.Parameter

    for p in params:
        # Insert / after positional-only params
        if prev_kind == PK.POSITIONAL_ONLY and p.kind != PK.POSITIONAL_ONLY:
            parts.append("/")

        # Insert * before keyword-only params (if no *args)
        if (
            p.kind == PK.KEYWORD_ONLY
            and not saw_var_positional
            and prev_kind != PK.KEYWORD_ONLY
        ):
            parts.append("*")

        if p.kind == PK.VAR_POSITIONAL:
            saw_var_positional = True

        parts.append(_format_parameter(p, show_defaults=show_defaults))
        prev_kind = p.kind

    # Trailing / if all positional-only
    if prev_kind == PK.POSITIONAL_ONLY:
        parts.append("/")

    oneliner = f"({', '.join(parts)})"
    if max_len is None or len(oneliner) <= max_len:
        return oneliner
    # One arg per line
    return "(\n    " + ",\n    ".join(parts) + ",\n)"


def format_signature(
    obj: Union[Callable, type],
    show_defaults: bool,
    *,
    max_width: Optional[int] = _MAX_ONELINER,
    name: Optional[str] = None,
) -> str:
    """Format function or class with full signature."""
    if name is None:
        name = getattr(obj, "__name__", type(obj).__name__)
    assert isinstance(name, str)
    try:
        annotations = (
            {
                "annotation_format": importlib.import_module(
                    "annotationlib"
                ).Format.FORWARDREF
            }
            if sys.version_info >= (3, 14)
            else {}
        )
        sig = inspect.signature(obj, **annotations)
    except (ValueError, TypeError) as error:
        log.warning("Could not inspect signature for %s: %s", name, error)
        return f"{name}(...)"

    ret = sig.return_annotation
    ret_str = "" if ret is inspect.Signature.empty else f" -> {_format_annotation(ret)}"

    # Format with proper line breaks for long signatures
    params_str = _format_params(
        list(sig.parameters.values()),
        max_len=None if max_width is None else max_width - len(name) - len(ret_str),
        show_defaults=show_defaults,
    )
    return f"{name}{params_str}{ret_str}"


def get_module_docstring(modname: str, short: bool = True) -> Optional[str]:
    """Get a module's docstring, optionally just the first line."""
    mod = safe_import(modname)
    if mod is None:
        return None
    doc = mod.__doc__
    if not doc:
        return None
    if short:
        return doc.strip().split("\n")[0]
    return doc.strip()


def get_module_items(
    modname: str,
    exclude: Optional[str],
    show_defaults: bool,
    *,
    max_width: Optional[int] = _MAX_ONELINER,
    on_error: ErrorHandler = log_error,
) -> list[str]:
    """Extract public functions and classes with signatures from a module."""
    pattern = re.compile(exclude) if exclude else None
    mod = safe_import(modname, on_error=on_error)
    if mod is None:
        return []

    items = []
    for name, obj in list(vars(mod).items()):
        if name.startswith("_"):
            continue
        if pattern and pattern.search(name):
            continue
        if inspect.isfunction(obj) or inspect.isclass(obj):
            if obj.__module__ == modname:
                items.append(
                    format_signature(
                        obj, show_defaults=show_defaults, max_width=max_width, name=name
                    )
                )

    return sorted(items)
