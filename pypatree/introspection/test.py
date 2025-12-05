from . import format_signature, get_module_items


def test_format_signature_function() -> None:
    def example(x: str, y: int = 1) -> bool:
        return True

    assert example("a") is True
    assert format_signature(example) == "example(x: str, y: int = 1) -> bool"


def test_format_signature_class() -> None:
    class Example:
        def __init__(self, name: str) -> None:
            self.name = name

    assert Example("test").name == "test"
    assert format_signature(Example) == "Example(name: str) -> None"


def test_format_signature_fallback() -> None:
    result = format_signature(print)
    assert result == "print()"


def test_get_module_items_import_error() -> None:
    items = get_module_items("nonexistent.module.xyz")
    assert items == []


def test_get_module_items_excludes_test_functions() -> None:
    from pypatree.config import DEFAULT_EXCLUDE

    items = get_module_items("pypatree.introspection.test", exclude=DEFAULT_EXCLUDE)
    assert not any("test_" in i for i in items)


def test_format_signature_strips_memory_addresses() -> None:
    sentinel = object()

    def fn(x: object = sentinel) -> None:
        assert x is sentinel

    fn()
    sig = format_signature(fn)
    assert "0x" not in sig
    assert "object>" in sig
