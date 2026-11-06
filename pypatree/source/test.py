from importlib.machinery import EXTENSION_SUFFIXES
from pathlib import Path

import pytest

from pypatree.tree import Tree
from scripts.lib import run

from . import source_packages, source_trees


def write_sources(root: Path, files: dict[str, str]) -> None:
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def errors(trees: dict[str, Tree]) -> dict[str, str]:
    return {
        module: error
        for name, tree in trees.items()
        for module, error in tree.errors(name)
    }


def test_source_signatures_preserve_call_contracts(tmp_path: Path) -> None:
    write_sources(
        tmp_path,
        {
            "example.py": '''
"""Literal [array] documentation."""
from typing import Annotated, Literal
from dataclasses import dataclass, field
import typing_extensions
from missing_dependency import External, imported_function

def visible(value: Annotated[int, "metadata"], /, *args: str, mode: Literal["a", "b"] = "a", **kwargs) -> bool: pass
def optional(value=None): pass
def annotated() -> list[typing_extensions.Annotated[int, "metadata"]]: pass
def _private(): pass
def test_ignored(): pass

@dataclass
class Config:
    name: str
    values: list[int] = field(default_factory=list)

class Plain: pass
class Derived(External): pass
class Custom(metaclass=External): pass
class Explicit:
    def __init__(self, value: int, *, flag=False): pass
class Allocator:
    def __new__(cls, value: str): pass
class Variadic:
    def __init__(*args, **kwargs): pass
class Assigned:
    __init__ = imported_function
'''
        },
    )
    trees = source_trees(tmp_path, scope="example", show_defaults=True)
    assert errors(trees) == {}
    assert trees["example"].docstring == "Literal [array] documentation."
    assert list(map(str, trees["example"].items)) == [
        "visible(value: int, /, *args: str, mode: Literal['a', 'b'] = 'a', **kwargs) -> bool",
        "optional(value=None)",
        "annotated() -> list[int]",
        "Config(name: str, values: list[int] = list())",
        "Plain(...)",
        "Derived(...)",
        "Custom(...)",
        "Explicit(value: int, *, flag=False)",
        "Allocator(value: str)",
        "Variadic(*args, **kwargs)",
        "Assigned(...)",
    ]


def test_scope_exclusion_and_partial_parse_failure(tmp_path: Path) -> None:
    write_sources(
        tmp_path,
        {
            "example/__init__.py": "",
            "example/branch/__init__.py": "def visible(argument: str): pass\n",
            "example/branch/leaf.py": "def leaf(): pass\n",
            "example/broken.py": "def invalid(\n",
            "example/test_ignored.py": "def invalid(\n",
            "example/data/value.txt": "not python",
            f"example/compiled{EXTENSION_SUFFIXES[0]}": "",
            "example/namespace/leaf.py": "def nested(): pass\n",
        },
    )
    branch = source_trees(tmp_path, scope="example.branch")["example.branch"]
    assert list(map(str, branch.items)) == ["visible(argument: str)"]
    assert list(map(str, branch.children["leaf"].items)) == ["leaf()"]
    leaf = source_trees(tmp_path, scope="example.branch.leaf")["example.branch.leaf"]
    assert list(map(str, leaf.items)) == ["leaf()"]

    trees = source_trees(tmp_path)
    assert list(errors(trees)) == ["example.broken"]
    assert "Syntax error" in errors(trees)["example.broken"]
    assert sorted(trees["example"].children) == ["branch", "broken", "namespace"]
    namespace = trees["example"].children["namespace"]
    assert list(map(str, namespace.children["leaf"].items)) == ["nested()"]
    for scope, message in [
        ("example.absent", "does not exist"),
        ("example.branch.leaf.deeper", "does not exist"),
        ("example.test_ignored", "excluded by --exclude"),
    ]:
        with pytest.raises(ValueError, match=message):
            source_trees(tmp_path, scope=scope)


def test_unreadable_root_keeps_its_submodules(tmp_path: Path) -> None:
    write_sources(
        tmp_path,
        {
            "example/__init__.py": "def invalid(\n",
            "example/leaf.py": "def leaf(): pass\n",
        },
    )
    trees = source_trees(tmp_path)
    assert list(errors(trees)) == ["example"]
    assert list(map(str, trees["example"].children["leaf"].items)) == ["leaf()"]


def test_compiled_top_level_modules_are_skipped(tmp_path: Path) -> None:
    write_sources(
        tmp_path, {"tool.py": "def run(): pass\n", f"fast{EXTENSION_SUFFIXES[0]}": ""}
    )
    assert list(source_trees(tmp_path)) == ["tool"]


def test_namespace_cycle_is_reported(tmp_path: Path) -> None:
    write_sources(tmp_path, {"namespace/leaf.py": "def visible(): pass\n"})
    (tmp_path / "namespace" / "loop").symlink_to(
        tmp_path / "namespace", target_is_directory=True
    )
    trees = source_trees(tmp_path)
    assert list(errors(trees)) == ["namespace.loop"]
    assert errors(trees)["namespace.loop"].startswith("Recursive package path")


def test_duplicate_packages_require_subproject_scope(tmp_path: Path) -> None:
    write_sources(
        tmp_path,
        {
            "first/pyproject.toml": "",
            "first/example/__init__.py": "",
            "second/setup.cfg": "",
            "second/example/__init__.py": "",
        },
    )
    with pytest.raises(ValueError, match="Duplicate source package.*first.*second"):
        source_packages(tmp_path)
    assert source_packages(tmp_path / "first") == {
        "example": tmp_path / "first/example"
    }


def test_dataclass_bases_from_other_modules_contribute_fields(tmp_path: Path) -> None:
    write_sources(
        tmp_path,
        {
            "example/__init__.py": "",
            "example/base.py": (
                "from dataclasses import dataclass\n"
                "@dataclass\nclass Base:\n    x: int\n"
            ),
            "example/derived.py": (
                "from dataclasses import dataclass\nfrom .base import Base\n"
                "@dataclass\nclass Child(Base):\n    y: int = 0\n"
            ),
        },
    )
    for scope in ["example", "example.derived"]:
        tree = source_trees(tmp_path, scope=scope)[scope]
        derived = tree.children["derived"] if scope == "example" else tree
        assert list(map(str, derived.items)) == ["Child(x: int, y: int = ...)"]


def test_project_search_skips_ignored_vendored_and_environment_directories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    projects = {
        "app": "app",
        "scratch/vendored": "vendored",
        "env/lib/site-packages/dependency": "dependency",
        "node_modules/gyp": "gyp",
        "tests/fixture": "fixture",
        ".hidden/tool": "tool",
    }
    files = {".gitignore": "scratch/\n", "env/pyvenv.cfg": ""}
    for directory, package in projects.items():
        files[f"{directory}/pyproject.toml"] = ""
        files[f"{directory}/pkg_{package}/__init__.py"] = ""
    write_sources(tmp_path, files)
    assert sorted(source_packages(tmp_path)) == ["pkg_app", "pkg_vendored"]
    run("git", "init", "-q", str(tmp_path))
    assert sorted(source_packages(tmp_path)) == ["pkg_app"]
    # Git hooks export the hook's repository, which must not replace root's.
    other = tmp_path / "other"
    run("git", "init", "-q", str(other))
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(other))
    assert sorted(source_packages(tmp_path)) == ["pkg_app"]


def test_empty_directory(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="No Python source packages"):
        source_trees(tmp_path)
