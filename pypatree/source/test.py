from pathlib import Path
from typing import Optional

import pytest

from pypatree.config import DEFAULT_EXCLUDE
from pypatree.source import source_packages, source_trees
from pypatree.tree import Tree


def write_sources(root: Path, files: dict[str, str]) -> None:
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def inspect_sources(
    root: Path,
    *,
    scope: Optional[str] = None,
    exclude: Optional[str] = DEFAULT_EXCLUDE,
    max_width: Optional[int] = None,
) -> tuple[dict[str, Tree], list[str]]:
    errors: list[str] = []
    trees = source_trees(
        root=root,
        scope=scope,
        exclude=exclude,
        show_defaults=True,
        max_width=max_width,
        on_error=errors.append,
    )
    return trees, errors


def test_source_signatures_preserve_call_contracts(tmp_path: Path) -> None:
    write_sources(
        tmp_path,
        {
            "example.py": '''
"""Literal [array] documentation."""
from typing import Annotated, Literal
from dataclasses import dataclass, field
from missing_dependency import External, imported_function

def visible(value: Annotated[int, "metadata"], /, *args: str, mode: Literal["a", "b"] = "a", **kwargs) -> bool: pass
def optional(value=None): pass
def annotated() -> list[Annotated[int, "metadata"]]: pass
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
'''
        },
    )
    trees, errors = inspect_sources(tmp_path, scope="example")
    assert errors == []
    assert trees["example"].docstring == "Literal [array] documentation."
    assert trees["example"].items == [
        "Allocator(value: str)",
        "Config(name: str, values: list[int] = list())",
        "Custom(...)",
        "Derived(...)",
        "Explicit(value: int, *, flag=False)",
        "Plain(...)",
        "Variadic(*args, **kwargs)",
        "annotated() -> list[int]",
        "optional(value=None)",
        "visible(value: int, /, *args: str, mode: Literal['a', 'b'] = 'a', **kwargs) -> bool",
    ]


def test_scope_exclusion_and_partial_parse_failure(tmp_path: Path) -> None:
    write_sources(
        tmp_path,
        {
            "example/__init__.py": "",
            "example/branch/__init__.py": "def visible(argument: str, another: int): pass\n",
            "example/branch/leaf.py": "def leaf(): pass\n",
            "example/broken.py": "def invalid(\n",
            "example/test_ignored.py": "def invalid(\n",
            "example/data/value.txt": "not python",
            "example/namespace/leaf.py": "def nested(): pass\n",
        },
    )
    trees, errors = inspect_sources(tmp_path, scope="example.branch", max_width=20)
    assert errors == []
    assert trees["example.branch"].items == [
        "visible(\n    argument: str,\n    another: int,\n)"
    ]
    assert trees["example.branch"].children["leaf"].items == ["leaf()"]
    trees, errors = inspect_sources(tmp_path, scope="example.branch.leaf")
    assert errors == []
    assert trees["example.branch.leaf"].items == ["leaf()"]
    trees, errors = inspect_sources(tmp_path)
    assert len(errors) == 1 and "broken.py" in errors[0]
    assert "Syntax error" in errors[0]
    assert trees["example"].children["broken"].failed
    assert "data" not in trees["example"].children
    assert "test_ignored" not in trees["example"].children
    assert trees["example"].children["namespace"].children["leaf"].items == ["nested()"]
    for scope, message in [
        ("example../elsewhere", "Invalid module scope"),
        ("missing", "not in a local source package"),
        ("example.absent", "does not exist"),
        ("example.test_ignored", "excluded by --exclude"),
    ]:
        with pytest.raises(ValueError, match=message):
            inspect_sources(tmp_path, scope=scope)
    with pytest.raises(ValueError, match="Use --exclude ''"):
        inspect_sources(tmp_path, exclude=".*")


def test_namespace_cycle_is_reported(tmp_path: Path) -> None:
    write_sources(tmp_path, {"namespace/leaf.py": "def visible(): pass\n"})
    (tmp_path / "namespace" / "loop").symlink_to(
        tmp_path / "namespace", target_is_directory=True
    )
    trees, errors = inspect_sources(tmp_path, exclude=None)
    assert len(errors) == 1 and "Recursive source path" in errors[0]
    assert trees["namespace"].children["loop"].failed


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


def test_ambiguous_source_layout_and_empty_directory(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="No Python source packages"):
        inspect_sources(tmp_path)
    write_sources(tmp_path, {"example/__init__.py": "", "src/example/__init__.py": ""})
    with pytest.raises(ValueError, match="Ambiguous source package"):
        source_packages(tmp_path)
