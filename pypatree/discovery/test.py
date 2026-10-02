"""Tests for discovery module - uses pypatree itself as test subject."""

import os
import json
import importlib.metadata as metadata
import importlib
import re
import tempfile
from pathlib import Path

import pytest

from pypatree.config import DEFAULT_EXCLUDE

from . import (
    _find_packages_in_dir,
    _get_local_packages,
    _matches_exclude,
    _module_names,
    get_packages,
)


def test_matches_exclude_exact_test() -> None:
    pattern = re.compile(DEFAULT_EXCLUDE)
    assert _matches_exclude("test", pattern) is True


def test_matches_exclude_test_prefixed() -> None:
    pattern = re.compile(DEFAULT_EXCLUDE)
    assert _matches_exclude("test_foo", pattern) is True
    assert _matches_exclude("test_", pattern) is True


def test_matches_exclude_not_testing() -> None:
    pattern = re.compile(DEFAULT_EXCLUDE)
    assert _matches_exclude("testing", pattern) is False
    assert _matches_exclude("testable", pattern) is False
    assert _matches_exclude("tests", pattern) is True


def test_matches_exclude_nested() -> None:
    pattern = re.compile(DEFAULT_EXCLUDE)
    assert _matches_exclude("foo.test", pattern) is True
    assert _matches_exclude("foo.test_bar", pattern) is True
    assert _matches_exclude("foo.testing", pattern) is False


def test_get_local_packages_finds_pypatree() -> None:
    """pypatree is installed from current dir when tests run."""
    packages = _get_local_packages()
    assert "pypatree" in packages


def test_get_packages_finds_submodules() -> None:
    """Finds pypatree and its submodules."""
    result = get_packages(exclude=DEFAULT_EXCLUDE)
    assert "pypatree" in result
    submods = result["pypatree"]
    assert "pypatree" in submods
    assert "pypatree.discovery" in submods
    assert "pypatree.introspection" in submods
    assert "pypatree.display" in submods


def test_get_packages_excludes_test_modules_by_default() -> None:
    """Test modules are excluded with default pattern."""
    result = get_packages(exclude=DEFAULT_EXCLUDE)
    submods = result["pypatree"]
    assert "pypatree.discovery.test" not in submods
    assert "pypatree.display.test" not in submods


def test_get_packages_includes_test_modules_when_no_exclude() -> None:
    """Test modules are included when exclude is None."""
    result = get_packages(exclude=None)
    submods = result["pypatree"]
    assert "pypatree.discovery.test" in submods
    assert "pypatree.display.test" in submods


def test_get_packages_reports_all_imports_failing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(Path(__file__).resolve().parents[2] / "tests/stubs/brokenpkg")
    with pytest.raises(ImportError, match="All discovered packages failed"):
        get_packages()


def test_find_packages_src_as_package() -> None:
    """When src/ itself is a package (has __init__.py), detect it."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(tmpdir, "src")
        os.makedirs(src_dir)
        # src/__init__.py exists -> src IS the package
        with open(os.path.join(src_dir, "__init__.py"), "w") as f:
            f.write("")
        with open(os.path.join(src_dir, "module.py"), "w") as f:
            f.write("")
        packages = _find_packages_in_dir(tmpdir)
        assert "src" in packages


def test_find_packages_src_layout() -> None:
    """Standard src-layout: src/mypkg/ with __init__.py inside."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # src/mypkg/__init__.py (no src/__init__.py)
        mypkg_dir = os.path.join(tmpdir, "src", "mypkg")
        os.makedirs(mypkg_dir)
        with open(os.path.join(mypkg_dir, "__init__.py"), "w") as f:
            f.write("")
        packages = _find_packages_in_dir(tmpdir)
        assert "mypkg" in packages
        assert "src" not in packages


def test_find_packages_flat_layout() -> None:
    """Flat layout: mypkg/ directly in project root."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mypkg_dir = os.path.join(tmpdir, "mypkg")
        os.makedirs(mypkg_dir)
        with open(os.path.join(mypkg_dir, "__init__.py"), "w") as f:
            f.write("")
        packages = _find_packages_in_dir(tmpdir)
        assert "mypkg" in packages


@pytest.mark.parametrize(
    ("files", "expected"),
    [
        (["standalone.py"], ["standalone"]),
        (["namespace/child/module.py"], ["namespace"]),
        (["src/namespace/child/module.py"], ["namespace"]),
        (["src/data.txt", "mypkg/__init__.py"], ["mypkg"]),
        (["mypkg/__init__.py", "build_hook.py", "scripts/tool.py"], ["mypkg"]),
    ],
)
def test_source_layouts(files: list[str], expected: list[str], tmp_path: Path) -> None:
    for filename in files:
        path = tmp_path / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("")
    assert _find_packages_in_dir(str(tmp_path)) == expected


def test_editable_metadata_selects_only_this_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source é"
    source.mkdir()
    distributions = []
    for name, directory, editable in [
        ("local", source, True),
        ("nested", source / "nested", True),
        ("wheel", source, False),
    ]:
        info = tmp_path / f"{name}.dist-info"
        info.mkdir()
        (info / "direct_url.json").write_text(
            json.dumps(
                {
                    "url": directory.as_uri(),
                    "dir_info": {"editable": editable},
                }
            )
        )
        (info / "top_level.txt").write_text(name + "\n")
        distributions.append(metadata.PathDistribution(info))
    monkeypatch.setattr(metadata, "distributions", lambda: distributions)
    monkeypatch.chdir(source)
    assert _get_local_packages() == ["local"]


def test_discovery_continues_after_broken_sibling(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    stub = Path(__file__).resolve().parents[2] / "tests/stubs/test_stub"
    monkeypatch.chdir(stub)
    packages = get_packages(exclude=DEFAULT_EXCLUDE, scope="test_stub")
    assert "test_stub.branch.leaf" in packages["test_stub"]
    assert "test_stub.sibling" not in packages["test_stub"]
    assert "Unrelated sibling was imported" in caplog.text

    root = importlib.import_module("test_stub")
    branch = importlib.import_module("test_stub.branch")
    monkeypatch.setattr(branch, "__path__", root.__path__)
    errors: list[str] = []
    packages = get_packages(
        exclude=DEFAULT_EXCLUDE, scope="test_stub", on_error=errors.append
    )
    assert packages["test_stub"] == ["test_stub", "test_stub.branch"]
    assert any("Recursive package path" in error for error in errors)


def test_scope_without_exclusions_includes_test_module() -> None:
    assert (
        "pypatree.discovery.test"
        in get_packages(scope="pypatree.discovery")["pypatree.discovery"]
    )


def test_excluding_all_packages_has_recovery_hint() -> None:
    with pytest.raises(ValueError, match="Use --exclude ''"):
        get_packages(exclude=".*")


def test_nonexistent_search_paths_and_private_namespaces(tmp_path: Path) -> None:
    private = tmp_path / "_private"
    private.mkdir()
    (private / "leaf.py").write_text("")
    assert _module_names([str(tmp_path), str(tmp_path / "missing")]) == {
        "_private": True
    }
