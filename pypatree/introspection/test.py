import sys
import types
from operator import or_
from typing import Annotated, Callable, ForwardRef, List, Literal, Optional, Union

import pytest

from pypatree.config import Exclusion

from . import module_items, signature_of


def text(obj: Union[Callable[..., object], type], show_defaults: bool = True) -> str:
    return str(signature_of(obj, show_defaults=show_defaults))


def test_defaults_are_shown_or_marked() -> None:
    def example(x: str, y: int = 1) -> bool:
        return True

    assert text(example) == "example(x: str, y: int = 1) -> bool"
    assert text(example, show_defaults=False) == "example(x: str, y: int = ...) -> bool"


def test_parameter_kinds_survive_inspection() -> None:
    def fn(a: int, /, b, *args: str, k: bool = True, **kwargs) -> None:
        pass

    assert text(fn) == "fn(a: int, /, b, *args: str, k: bool = True, **kwargs) -> None"


def test_class_signature_is_its_call_contract() -> None:
    class Initialized:
        def __init__(self, name: str) -> None:
            self.name = name

    class Constructed:
        def __new__(cls, value: int):
            return super().__new__(cls)

    class Empty:
        pass

    assert text(Initialized) == "Initialized(name: str)"
    assert text(Constructed) == "Constructed(value: int)"
    assert text(Empty) == "Empty()"


def test_unavailable_signature_is_marked(caplog: pytest.LogCaptureFixture) -> None:
    assert text(type) == "type(...)"
    assert "signature" in caplog.text


def test_annotation_wrappers_are_removed() -> None:
    def fn(
        x: Annotated[str, "metadata"],
        y: List[Annotated[str, "meta"]],
        callback: Callable[[Annotated[int, "meta"]], str],
        value: Optional[Annotated[int, "meta"]],
    ) -> None:
        pass

    assert text(fn) == (
        "fn(x: str, y: list[str], callback: Callable[[int], str], value: int | None) -> None"
    )


def test_stringified_annotations_lose_their_quotes() -> None:
    def fn(x: "str", mode: "Literal['fast', 'slow']") -> "None":
        pass

    assert text(fn) == "fn(x: str, mode: Literal['fast', 'slow']) -> None"


@pytest.mark.skipif(sys.version_info < (3, 10), reason="PEP 604 requires Python 3.10")
def test_union_operator_annotation() -> None:
    def fn(value):
        pass

    fn.__annotations__ = {"value": or_(int, str), "return": bool}
    assert text(fn) == "fn(value: int | str) -> bool"


def test_ellipsis_and_forward_references() -> None:
    def fn(items: tuple[int, ...], callback: Callable[..., str]):
        pass

    assert text(fn) == "fn(items: tuple[int, ...], callback: Callable[..., str])"
    fn.__annotations__ = {
        "items": ForwardRef("Missing"),
        "return": ForwardRef("Missing"),
    }
    assert text(fn) == "fn(items: Missing, callback) -> Missing"


@pytest.mark.skipif(
    sys.version_info < (3, 14), reason="Deferred annotations require Python 3.14"
)
def test_unresolved_deferred_annotations_are_displayed() -> None:
    module = types.ModuleType("deferred")
    exec("def fn(value: Missing) -> Missing: pass", module.__dict__)
    assert text(module.fn) == "fn(value: Missing) -> Missing"


def test_default_reprs_omit_memory_addresses_only() -> None:
    sentinel = object()

    def fn(
        x: object = sentinel,
        mode: Literal["fast", "slow"] = "fast",
        label="<x at 0x123>",
        values=["<x at 0x123>"],
    ) -> None:
        pass

    assert text(fn) == (
        "fn(x: object = <object object>, mode: Literal['fast', 'slow'] = 'fast', "
        "label='<x at 0x123>', values=['<x at 0x123>']) -> None"
    )


def test_module_items_are_public_callables_defined_in_the_module() -> None:
    module = types.ModuleType("namespace_probe")
    exec(
        "from os.path import join\n"
        "def _implementation(value: int): pass\n"
        "visible = _implementation\n"
        "def test_helper(): pass\n"
        "class Public: pass\n"
        "CONSTANT = 1\n"
        "def __dir__(): raise RuntimeError('dynamic directory executed')\n"
        "def __getattr__(name): raise RuntimeError('lazy attribute executed')\n",
        module.__dict__,
    )
    items = module_items(module, exclude=Exclusion(), show_defaults=False)
    assert list(map(str, items)) == ["visible(value: int)", "Public()"]
