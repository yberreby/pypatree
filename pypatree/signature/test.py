from inspect import Parameter as Kinds

import pytest

from . import Kind, Parameter, Signature

POSITIONAL_ONLY = Kinds.POSITIONAL_ONLY
POSITIONAL = Kinds.POSITIONAL_OR_KEYWORD
VAR_POSITIONAL = Kinds.VAR_POSITIONAL
KEYWORD_ONLY = Kinds.KEYWORD_ONLY
VAR_KEYWORD = Kinds.VAR_KEYWORD


@pytest.mark.parametrize(
    ("parameters", "expected"),
    [
        ([("a", POSITIONAL_ONLY)], "f(a, /)"),
        ([("a", POSITIONAL_ONLY), ("b", POSITIONAL)], "f(a, /, b)"),
        ([("k", KEYWORD_ONLY)], "f(*, k)"),
        ([("args", VAR_POSITIONAL), ("k", KEYWORD_ONLY)], "f(*args, k)"),
        ([("a", POSITIONAL_ONLY), ("kwargs", VAR_KEYWORD)], "f(a, /, **kwargs)"),
    ],
)
def test_separators_follow_python_syntax(
    parameters: list[tuple[str, Kind]], expected: str
) -> None:
    signature = Signature(
        "f", tuple(Parameter(name, kind) for name, kind in parameters)
    )
    assert str(signature) == expected


def test_annotations_defaults_and_unknown_parameters() -> None:
    signature = Signature(
        "f",
        (
            Parameter("a", POSITIONAL, annotation="int", default="1"),
            Parameter("b", POSITIONAL, default="..."),
            Parameter("args", VAR_POSITIONAL, annotation="str"),
        ),
        returns="bool",
    )
    assert str(signature) == "f(a: int = 1, b=..., *args: str) -> bool"
    assert str(Signature("g", parameters=None)) == "g(...)"


def test_lines_put_one_parameter_per_line_when_too_wide() -> None:
    signature = Signature(
        "f",
        (Parameter("a", POSITIONAL, annotation="int"), Parameter("k", KEYWORD_ONLY)),
        returns="bool",
    )
    text = str(signature)
    assert signature.lines() == signature.lines(len(text)) == [text]
    assert signature.lines(len(text) - 1) == ["f(", "a: int,", "*,", "k,", ") -> bool"]
    assert Signature("g", ()).lines(1) == ["g()"]
    assert Signature("h", None).lines(1) == ["h(...)"]


def test_parameters_must_follow_python_order() -> None:
    with pytest.raises(ValueError, match="out of order"):
        Signature("f", (Parameter("k", KEYWORD_ONLY), Parameter("a", POSITIONAL)))
