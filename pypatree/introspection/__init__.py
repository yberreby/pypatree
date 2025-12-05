import importlib
import inspect
import logging
import re
from types import ModuleType
from typing import Callable, Optional, Union

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


def format_signature(obj: Union[Callable, type]) -> str:
    """Format function or class with full signature."""
    name = getattr(obj, "__name__", str(obj))
    try:
        if inspect.isclass(obj):
            sig = inspect.signature(obj.__init__)
            params = [p for k, p in sig.parameters.items() if k != "self"]
            sig = sig.replace(parameters=params)
        else:
            sig = inspect.signature(obj)
    except (ValueError, TypeError):
        return f"{name}()"
    return _OBJECT_ADDR_RE.sub(">", f"{name}{sig}")


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


def get_module_items(modname: str, exclude: Optional[str] = None) -> list[str]:
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
            items.append(format_signature(obj))

    return sorted(items)
