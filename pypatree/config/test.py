import pytest

from . import Exclusion, select_modules


@pytest.mark.parametrize(
    ("name", "excluded"),
    [
        ("test", True),
        ("tests", True),
        ("test_parser", True),
        ("pkg.test_parser", True),
        ("pkg.tests.helpers", True),
        ("testing", False),
        ("contest", False),
        ("pkg.testable", False),
    ],
)
def test_default_exclusion_matches_test_segments(name: str, excluded: bool) -> None:
    exclude = Exclusion()
    assert exclude(name) is excluded


def test_empty_regex_excludes_nothing() -> None:
    exclude = Exclusion("")
    assert not exclude("test")


def test_repr_round_trips() -> None:
    exclude = Exclusion(r"^(a|b)\.$")
    assert eval(repr(exclude)).regex == exclude.regex


def test_selection_without_scope_skips_excluded_packages() -> None:
    assert select_modules(["beta", "alpha", "test_kit"], None, Exclusion()) == [
        "alpha",
        "beta",
    ]
    with pytest.raises(ValueError, match="Use --exclude ''"):
        select_modules(["test_kit"], None, Exclusion())


def test_scope_must_name_a_module_inside_a_local_package() -> None:
    packages = ["alpha", "test_kit"]
    exclude = Exclusion()
    assert select_modules(packages, "alpha.parsers", exclude) == ["alpha.parsers"]
    # Naming an excluded package explicitly overrides the exclusion.
    assert select_modules(packages, "test_kit", exclude) == ["test_kit"]
    for scope, message in [
        ("alpha..parsers", "Invalid module scope"),
        ("gamma", "not in a local package. Found: alpha, test_kit"),
        ("alpha.tests.fixtures", "excluded by --exclude"),
    ]:
        with pytest.raises(ValueError, match=message):
            select_modules(packages, scope, exclude)
