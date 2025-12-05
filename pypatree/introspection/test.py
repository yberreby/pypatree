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


def test_get_module_items_skips_test_functions() -> None:
    items = get_module_items("pypatree.introspection.test", skip_tests=True)
    assert not any("test_" in i for i in items)
