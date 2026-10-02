import sys
from types import ModuleType

import pytest

from . import Tree, build_tree, get_subtree


def test_tree_contains_module_data(monkeypatch: pytest.MonkeyPatch) -> None:
    module = ModuleType("example.child")
    exec(
        '"""Module documentation."""\ndef visible(value: int = 3) -> bool: pass',
        module.__dict__,
    )
    monkeypatch.setitem(sys.modules, module.__name__, module)
    tree = build_tree([module.__name__], "example", exclude=None, show_defaults=True)
    child = get_subtree(tree, ["child"])
    assert child is not None
    assert child.items == ["visible(value: int = 3) -> bool"]
    assert child.docstring == "Module documentation."
    assert not child.failed
    assert get_subtree(tree, []) is tree
    assert get_subtree(tree, ["missing"]) is None


def test_tree_rejects_unrelated_modules() -> None:
    with pytest.raises(ValueError, match="outside package"):
        build_tree(["pkg_other.child"], "pkg", exclude=None, show_defaults=False)


def test_failed_import_runs_once(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    marker = tmp_path / "attempts"
    (tmp_path / "failing_module.py").write_text(
        f"from pathlib import Path\nwith Path({str(marker)!r}).open('a') as file: file.write('attempt\\n')\n"
        "raise RuntimeError('import failed')\n"
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    tree = build_tree(
        ["failing_module"], "failing_module", exclude=None, show_defaults=False
    )
    from pypatree.config import Config
    from pypatree.display import print_tree

    print_tree("failing_module", tree, Config())
    assert tree.failed
    assert marker.read_text() == "attempt\n"


def test_empty_tree() -> None:
    assert build_tree([], "pkg", exclude=None, show_defaults=False) == Tree()
