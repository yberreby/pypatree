from importlib.machinery import EXTENSION_SUFFIXES
from pathlib import Path

import pytest

from . import modules, project_packages


def touch(root: Path, *files: str) -> None:
    for name in files:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("")


def test_modules_resolve_names_as_imports_do(tmp_path: Path) -> None:
    extension = EXTENSION_SUFFIXES[0]
    touch(
        tmp_path,
        "__init__.py",
        "package/__init__.py",
        "package.py",
        f"compiled_package/__init__{extension}",
        "__main__.py",
        "module.py",
        "module/inner.py",
        "namespace/deep/leaf.py",
        f"both{extension}",
        "both.py",
        f"compiled{extension}",
        "foreign.cpython-27-darwin.so",
        "_private.py",
        "not-a-name.py",
        "data/notes.txt",
        "__pycache__/cached.py",
    )
    assert modules(tmp_path) == {
        "__main__": tmp_path / "__main__.py",
        "_private": tmp_path / "_private.py",
        "both": tmp_path / "both.py",
        "compiled": tmp_path / f"compiled{extension}",
        "compiled_package": tmp_path / "compiled_package",
        "module": tmp_path / "module.py",
        "namespace": tmp_path / "namespace",
        "package": tmp_path / "package",
    }
    assert modules(tmp_path / "missing") == {}


@pytest.mark.parametrize(
    ("files", "expected"),
    [
        (["mypkg/__init__.py"], {"mypkg": "mypkg"}),
        (["src/mypkg/__init__.py"], {"mypkg": "src/mypkg"}),
        (["src/__init__.py", "src/module.py"], {"src": "src"}),
        (["standalone.py"], {"standalone": "standalone.py"}),
        (["namespace/child/module.py"], {"namespace": "namespace"}),
        (["src/namespace/child/module.py"], {"namespace": "src/namespace"}),
        (["src/data.txt", "mypkg/__init__.py"], {"mypkg": "mypkg"}),
        (["mypkg/__init__.py", "build_hook.py", "scripts/tool.py"], {"mypkg": "mypkg"}),
        (["_private/leaf.py", "public.py"], {"public": "public.py"}),
        (["tests/__init__.py", "test_tool.py", "tool.py"], {"tool": "tool.py"}),
        (
            ["venv/pyvenv.cfg", "venv/lib/site/dependency.py", "tool.py"],
            {"tool": "tool.py"},
        ),
    ],
)
def test_project_layouts(
    tmp_path: Path, files: list[str], expected: dict[str, str]
) -> None:
    touch(tmp_path, *files)
    assert project_packages(tmp_path) == {
        name: tmp_path / path for name, path in expected.items()
    }


def test_package_in_root_and_src_is_ambiguous(tmp_path: Path) -> None:
    touch(tmp_path, "example/__init__.py", "src/example/__init__.py")
    with pytest.raises(ValueError, match="Ambiguous source package 'example'"):
        project_packages(tmp_path)
