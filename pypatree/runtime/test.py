import importlib
import importlib.metadata as metadata
import json
from pathlib import Path

import pytest

from pypatree.config import Exclusion
from pypatree.tree import Tree

from . import editable_packages, import_module, runtime_trees

STUBS = Path(__file__).resolve().parents[2] / "tests/stubs"
STUB = STUBS / "test_stub"


def items(tree: Tree) -> list[str]:
    return list(map(str, tree.items))


def test_editable_metadata_selects_only_this_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source é %"
    (source / "layout_package").mkdir(parents=True)
    (source / "layout_package" / "__init__.py").write_text("")
    distributions = []
    for name, directory, editable, top_level in [
        ("local", source, True, "local\n"),
        ("hatch", source, True, None),
        ("nested", source / "nested", True, "nested\n"),
        ("wheel", source, False, "wheel\n"),
    ]:
        info = tmp_path / f"{name}.dist-info"
        info.mkdir()
        (info / "direct_url.json").write_text(
            json.dumps({"url": directory.as_uri(), "dir_info": {"editable": editable}})
        )
        if top_level is not None:
            (info / "top_level.txt").write_text(top_level)
        distributions.append(metadata.PathDistribution(info))
    monkeypatch.setattr(metadata, "distributions", lambda: distributions)
    assert editable_packages(source) == ["layout_package", "local"]


def test_scope_imports_only_its_subtree() -> None:
    branch = runtime_trees(STUB, scope="test_stub.branch")["test_stub.branch"]
    assert items(branch) == ["branch_function() -> None"]
    assert sorted(branch.children) == ["deep", "leaf", "needs_missing"]
    assert items(branch.children["deep"].children["inner"]) == [
        "inner_function() -> None"
    ]
    error = branch.children["needs_missing"].error
    assert error is not None and "missing_dependency_for_pypatree" in error
    leaf = runtime_trees(STUB, scope="test_stub.branch.leaf")["test_stub.branch.leaf"]
    assert items(leaf) == ["leaf_function() -> None"]


def test_scope_errors() -> None:
    for scope, message in [
        ("test_stubbish.branch", "not in a local package"),
        ("test_stub.branch.missing", "does not exist"),
        ("test_stub.branch.test_ignored", "excluded by --exclude"),
    ]:
        with pytest.raises(ValueError, match=message):
            runtime_trees(STUB, scope=scope)
    with pytest.raises(ModuleNotFoundError, match="missing_dependency_for_pypatree"):
        runtime_trees(STUB, scope="test_stub.branch.needs_missing")


def test_failed_imports_are_recorded_and_inspection_continues() -> None:
    with pytest.raises(ValueError, match="Use --exclude ''"):
        runtime_trees(STUB)
    tree = runtime_trees(STUB, exclude=Exclusion(""))["test_stub"]
    errors = dict(tree.errors("test_stub"))
    assert sorted(errors) == [
        "test_stub.branch.needs_missing",
        "test_stub.branch.test_ignored",
        "test_stub.sibling",
    ]
    assert "Unrelated sibling was imported" in errors["test_stub.sibling"]
    assert items(tree.children["branch"].children["leaf"]) == [
        "leaf_function() -> None"
    ]
    broken = runtime_trees(STUBS / "brokenpkg")["brokenpkg"]
    assert (
        broken.error == "ModuleNotFoundError: No module named 'nonexistent_module_xyz'"
    )


def test_member_inspection_failure_is_recorded(monkeypatch: pytest.MonkeyPatch) -> None:
    class Unprintable:
        def __repr__(self) -> str:
            raise RuntimeError("repr failed")

    def visible(value: object = Unprintable()) -> None:
        pass

    visible.__module__ = "test_stub.branch.leaf"
    leaf = importlib.import_module("test_stub.branch.leaf")
    monkeypatch.setattr(leaf, "visible", visible, raising=False)
    tree = runtime_trees(STUB, scope="test_stub.branch", show_defaults=True)
    branch = tree["test_stub.branch"]
    assert branch.children["leaf"].error == "RuntimeError: repr failed"
    assert items(branch.children["deep"]) == ["deep_function() -> None"]


def test_recursive_package_path_is_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    root = importlib.import_module("test_stub")
    branch = importlib.import_module("test_stub.branch")
    monkeypatch.setattr(branch, "__path__", root.__path__)
    tree = runtime_trees(STUB, scope="test_stub")["test_stub"]
    error = tree.children["branch"].error
    assert error is not None and error.startswith("Recursive package path")
    assert tree.children["branch"].children == {}


def test_directory_without_editable_install(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="No local editable packages"):
        runtime_trees(tmp_path)


def test_import_keeps_stdout_clean_and_reports_exit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / "chatty.py").write_text("print('import chatter')\n")
    (tmp_path / "exiting.py").write_text("raise SystemExit(3)\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    import_module("chatty")
    assert capsys.readouterr() == ("", "import chatter\n")
    with pytest.raises(ImportError, match=r"'exiting' called sys.exit\(3\)"):
        import_module("exiting")
