import sys
import types
from operator import or_
from typing import Annotated, Callable, ForwardRef, Literal, Optional
from unittest.mock import patch

import pytest

from pypatree.config import DEFAULT_EXCLUDE

from . import format_signature, get_module_docstring, get_module_items, safe_import


def test_format_signature_function() -> None:
    def example(x: str, y: int = 1) -> bool:
        return True

    assert (
        format_signature(example, show_defaults=True)
        == "example(x: str, y: int = 1) -> bool"
    )
    assert (
        format_signature(example, show_defaults=False)
        == "example(x: str, y: int = ...) -> bool"
    )


def test_format_signature_class() -> None:
    class Example:
        def __init__(self, name: str) -> None:
            self.name = name

    assert format_signature(Example, show_defaults=True) == "Example(name: str) -> None"


def test_format_signature_unavailable(caplog: pytest.LogCaptureFixture) -> None:
    assert format_signature(type, show_defaults=True) == "type(...)"
    assert "signature" in caplog.text


def test_format_signature_unwraps_annotated() -> None:
    def fn(x: Annotated[str, "metadata"]) -> None:
        pass

    assert format_signature(fn, True) == "fn(x: str) -> None"


def test_format_signature_unwraps_nested_annotated() -> None:
    from typing import List

    def fn(x: List[Annotated[str, "meta"]]) -> None:
        pass

    assert format_signature(fn, True) == "fn(x: list[str]) -> None"


def test_format_signature_strips_quotes() -> None:
    # Simulates stringified annotations from 'from __future__ import annotations'
    def fn(x: "str", y: "list[int]") -> "None":  # noqa: F821
        pass

    assert format_signature(fn, True) == "fn(x: str, y: list[int]) -> None"


def test_format_signature_keyword_only() -> None:
    def fn(*, x: int, y: str) -> None:
        pass

    assert format_signature(fn, True) == "fn(*, x: int, y: str) -> None"


def test_format_signature_positional_only() -> None:
    def fn(x: int, /, y: str) -> None:
        pass

    assert format_signature(fn, True) == "fn(x: int, /, y: str) -> None"


def test_format_signature_all_positional_only() -> None:
    def fn(x: int, y: str, /) -> None:
        pass

    assert format_signature(fn, True) == "fn(x: int, y: str, /) -> None"


def test_format_signature_var_positional() -> None:
    def fn(*args: int, x: str) -> None:
        pass

    assert format_signature(fn, True) == "fn(*args: int, x: str) -> None"


def test_get_module_items_import_error() -> None:
    items = get_module_items("nonexistent.module.xyz", None, show_defaults=True)
    assert items == []


def test_get_module_items_excludes_test_functions() -> None:
    items = get_module_items("pypatree.introspection.test", DEFAULT_EXCLUDE, True)
    assert not any("test_" in i for i in items)


def test_get_module_docstring_modes(monkeypatch: pytest.MonkeyPatch) -> None:
    module = types.ModuleType("docstring_modes")
    module.__doc__ = "First line.\nSecond line."
    monkeypatch.setitem(sys.modules, module.__name__, module)
    assert get_module_docstring(module.__name__, short=True) == "First line."
    assert get_module_docstring(module.__name__, short=False) == module.__doc__


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
        pass

    sig = format_signature(fn, show_defaults=True)
    assert "0x" not in sig
    assert "object>" in sig


def test_safe_import_handles_system_exit() -> None:
    with patch("importlib.import_module", side_effect=SystemExit("exit!")):
        assert safe_import("anything") is None


def test_safe_import_handles_unexpected_exception() -> None:
    with patch("importlib.import_module", side_effect=RuntimeError("boom")):
        assert safe_import("anything") is None


def test_signature_preserves_literal_values_and_defaults() -> None:
    def fn(mode: Literal["fast", "slow"] = "fast", label="<x at 0x123>") -> None:
        pass

    signature = format_signature(fn, show_defaults=True)
    assert "Literal['fast', 'slow']" in signature
    assert "= 'fast'" in signature
    assert "label='<x at 0x123>'" in signature


def test_signature_preserves_stringified_literal() -> None:
    def fn(mode: "Literal['fast', 'slow']") -> None:
        pass

    assert format_signature(fn, False) == "fn(mode: Literal['fast', 'slow']) -> None"


def test_signature_nested_callable_annotation() -> None:
    def fn(callback: Callable[[Annotated[int, "meta"]], str]) -> None:
        pass

    assert format_signature(fn, False) == "fn(callback: Callable[[int], str]) -> None"


def test_signature_optional_annotation() -> None:
    def fn(value: Optional[Annotated[int, "meta"]]) -> None:
        pass

    assert format_signature(fn, False) == "fn(value: int | None) -> None"


@pytest.mark.skipif(sys.version_info < (3, 10), reason="PEP 604 requires Python 3.10")
def test_signature_union_annotation() -> None:
    def fn(value):
        pass

    fn.__annotations__ = {"value": or_(int, str), "return": bool}
    assert format_signature(fn, False) == "fn(value: int | str) -> bool"


def test_signature_uses_class_call_contract() -> None:
    class Constructed:
        def __new__(cls, value: int):
            return super().__new__(cls)

    class Empty:
        pass

    assert format_signature(Constructed, False) == "Constructed(value: int)"
    assert format_signature(Empty, False) == "Empty()"


def test_signature_preserves_ellipsis_and_forward_references() -> None:
    def fn(items: tuple[int, ...], callback: Callable[..., str]):
        pass

    assert (
        format_signature(fn, True)
        == "fn(items: tuple[int, ...], callback: Callable[..., str])"
    )
    fn.__annotations__ = {
        "items": ForwardRef("Missing"),
        "return": ForwardRef("Missing"),
    }
    assert format_signature(fn, True) == "fn(items: Missing, callback) -> Missing"


@pytest.mark.skipif(
    sys.version_info < (3, 14), reason="Deferred annotations require Python 3.14"
)
def test_unresolved_deferred_annotations_are_displayed() -> None:
    module = types.ModuleType("deferred")
    exec("def fn(value: Missing) -> Missing: pass", module.__dict__)
    assert format_signature(module.fn, True) == "fn(value: Missing) -> Missing"


def test_module_namespace_uses_bound_names_without_lazy_lookup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = types.ModuleType("namespace_probe")
    exec(
        "def _implementation(value: int): pass\nvisible = _implementation\n"
        "def __dir__(): raise RuntimeError('dynamic directory executed')\n",
        module.__dict__,
    )
    monkeypatch.setitem(sys.modules, module.__name__, module)
    assert get_module_items(module.__name__, None, False) == ["visible(value: int)"]
