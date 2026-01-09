import sys
import types
from typing import Annotated
from unittest.mock import patch

from pypatree.config import DEFAULT_EXCLUDE

from . import format_signature, get_module_docstring, get_module_items, safe_import


def test_format_signature_function() -> None:
    def example(x: str, y: int = 1) -> bool:
        return True

    assert example("a") is True
    assert (
        format_signature(example, show_defaults=True)
        == "example(x: str, y: int = 1) -> bool"
    )
    assert (
        format_signature(example, show_defaults=False)
        == "example(x: str, y: int) -> bool"
    )


def test_format_signature_class() -> None:
    class Example:
        def __init__(self, name: str) -> None:
            self.name = name

    assert Example("test").name == "test"
    assert format_signature(Example, show_defaults=True) == "Example(name: str) -> None"


def test_format_signature_fallback() -> None:
    assert format_signature(print, show_defaults=True) == "print()"


def test_format_signature_unwraps_annotated() -> None:
    def fn(x: Annotated[str, "metadata"]) -> None:
        assert isinstance(x, str)

    fn("test")
    assert format_signature(fn, True) == "fn(x: str) -> None"


def test_format_signature_unwraps_nested_annotated() -> None:
    from typing import List

    def fn(x: List[Annotated[str, "meta"]]) -> None:
        assert x == ["a"]

    fn(["a"])
    assert format_signature(fn, True) == "fn(x: list[str]) -> None"


def test_format_signature_strips_quotes() -> None:
    # Simulates stringified annotations from 'from __future__ import annotations'
    def fn(x: "str", y: "list[int]") -> "None":  # noqa: F821
        assert isinstance(x, str) and isinstance(y, list)

    fn("a", [1])
    assert format_signature(fn, True) == "fn(x: str, y: list[int]) -> None"


def test_get_module_items_import_error() -> None:
    items = get_module_items("nonexistent.module.xyz", None, show_defaults=True)
    assert items == []


def test_get_module_items_excludes_test_functions() -> None:
    items = get_module_items("pypatree.introspection.test", DEFAULT_EXCLUDE, True)
    assert not any("test_" in i for i in items)


def test_get_module_docstring_short() -> None:
    doc = get_module_docstring("pypatree", short=True)
    assert doc is not None
    assert "\n" not in doc


def test_get_module_docstring_full() -> None:
    doc = get_module_docstring("pypatree", short=False)
    assert doc is not None


def test_get_module_docstring_not_found() -> None:
    doc = get_module_docstring("nonexistent.module.xyz")
    assert doc is None


def test_get_module_docstring_no_docstring() -> None:
    mod = types.ModuleType("_test_no_doc")
    mod.__doc__ = None
    sys.modules["_test_no_doc"] = mod
    try:
        doc = get_module_docstring("_test_no_doc")
        assert doc is None
    finally:
        del sys.modules["_test_no_doc"]


def test_format_signature_strips_memory_addresses() -> None:
    sentinel = object()

    def fn(x: object = sentinel) -> None:
        assert x is sentinel

    fn()
    sig = format_signature(fn, show_defaults=True)
    assert "0x" not in sig
    assert "object>" in sig


def test_safe_import_handles_system_exit() -> None:
    with patch("importlib.import_module", side_effect=SystemExit("exit!")):
        assert safe_import("anything") is None


def test_safe_import_handles_unexpected_exception() -> None:
    with patch("importlib.import_module", side_effect=RuntimeError("boom")):
        assert safe_import("anything") is None
