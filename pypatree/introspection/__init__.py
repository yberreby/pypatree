import importlib
import inspect
import logging
import re
from typing import Callable, Union

log = logging.getLogger(__name__)

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


def get_module_items(modname: str, skip_tests: bool = True) -> list[str]:
    """Extract public functions and classes with signatures from a module."""
    try:
        mod = importlib.import_module(modname)
    except ImportError as e:
        log.warning("Could not import %r: %s", modname, e)
        return []

    items = []
    for name in dir(mod):
        if name.startswith("_"):
            continue
        if skip_tests and name.startswith("test"):
            continue
        obj = getattr(mod, name)
        if getattr(obj, "__module__", None) != modname:
            continue
        if inspect.isfunction(obj) or inspect.isclass(obj):
            items.append(format_signature(obj))

    return sorted(items)
