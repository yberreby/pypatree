from . import Tree


def test_errors_are_qualified_and_ordered() -> None:
    tree = Tree(
        error="root failed",
        children={
            "b": Tree(error="b failed"),
            "a": Tree(children={"x": Tree(error="x failed"), "y": Tree()}),
        },
    )
    assert list(tree.errors("pkg")) == [
        ("pkg", "root failed"),
        ("pkg.a.x", "x failed"),
        ("pkg.b", "b failed"),
    ]
