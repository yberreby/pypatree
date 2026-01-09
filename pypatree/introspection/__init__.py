import importlib
import inspect
import logging
import re
from types import ModuleType
from typing import Annotated, Callable, Optional, Union, get_args, get_origin

log = logging.getLogger(__name__)


def safe_import(modname: str) -> Optional[ModuleType]:
    """Import a module, returning None on any failure."""
    try:
        return importlib.import_module(modname)
    except ImportError as e:
        log.warning("Could not import %r: %s", modname, e)
    except SystemExit as e:
        log.error("Skipping %r (module called sys.exit): %s", modname, e)
    except Exception as e:
        log.error(
            "Skipping %r (unexpected error): %s: %s", modname, type(e).__name__, e
        )
    return None


_OBJECT_ADDR_RE = re.compile(r" at 0x[0-9a-fA-F]+>")
_QUOTED_TYPE_RE = re.compile(r"'([^']+)'")


def _unwrap_annotated(annotation: type) -> type:
    """Recursively strip Annotated wrappers from a type.

    Annotated[T, meta...] -> T
    List[Annotated[T, meta]] -> List[T]
    Dict[K, Annotated[V, meta]] -> Dict[K, V]
    """
    origin = get_origin(annotation)

    # Annotated[T, ...] -> recurse into T
    if origin is Annotated:
        args = get_args(annotation)
        assert args, "Annotated must have at least one arg"
        return _unwrap_annotated(args[0])

    # Generic like List[X], Dict[K, V] -> rebuild with unwrapped args
    if origin is not None:
        args = get_args(annotation)
        if args:
            return origin[tuple(_unwrap_annotated(a) for a in args)]

    # Plain type like str, int -> return as-is
    return annotation


def _simplify_params(
    params: list[inspect.Parameter], show_defaults: bool
) -> list[inspect.Parameter]:
    """Unwrap Annotated types and optionally strip defaults."""
    result = []
    for p in params:
        ann = p.annotation
        if ann is not inspect.Parameter.empty:
            ann = _unwrap_annotated(ann)
        default = p.default if show_defaults else inspect.Parameter.empty
        result.append(p.replace(annotation=ann, default=default))
    return result


def format_signature(obj: Union[Callable, type], show_defaults: bool) -> str:
    """Format function or class with full signature."""
    name = getattr(obj, "__name__", str(obj))
    try:
        if inspect.isclass(obj):
            sig = inspect.signature(obj.__init__)
            params = [p for k, p in sig.parameters.items() if k != "self"]
        else:
            sig = inspect.signature(obj)
            params = list(sig.parameters.values())
        sig = sig.replace(parameters=_simplify_params(params, show_defaults))
    except (ValueError, TypeError):
        return f"{name}()"
    s = _OBJECT_ADDR_RE.sub(">", f"{name}{sig}")
    return _QUOTED_TYPE_RE.sub(r"\1", s)


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
    modname: str, exclude: Optional[str], show_defaults: bool
) -> list[str]:
    """Extract public functions and classes with signatures from a module."""
    pattern = re.compile(exclude) if exclude else None
    mod = safe_import(modname)
    if mod is None:
        return []

    items = []
    for name in dir(mod):
        if name.startswith("_"):
            continue
        if pattern and pattern.search(name):
            continue
        obj = getattr(mod, name)
        if getattr(obj, "__module__", None) != modname:
            continue
        if inspect.isfunction(obj) or inspect.isclass(obj):
            items.append(format_signature(obj, show_defaults=show_defaults))

    return sorted(items)
