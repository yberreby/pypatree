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


@pytest.mark.parametrize(
    ("files", "expected"),
    [
        # A single-module project beside its documentation and release scripts.
        (
            {"mytool.py": "", "docs/conf.py": "", "scripts/release.py": ""},
            {"mytool": "mytool.py"},
        ),
        # Only names that setuptools would pass over: inspect them anyway.
        ({"example/__init__.py": ""}, {"example": "example"}),
        # The project's name selects its module over unrelated directories.
        (
            {
                "pyproject.toml": '[project]\nname = "My-Tool"\n',
                "my_tool.py": "",
                "assets/generate.py": "",
            },
            {"my_tool": "my_tool.py"},
        ),
        # Declarations take precedence, even for test-like names.
        (
            {
                "pyproject.toml": "[tool.hatch.build.targets.wheel]\n"
                'packages = ["lib/core", "test_support"]\n',
                "lib/core/__init__.py": "",
                "other/__init__.py": "",
                "test_support/__init__.py": "",
            },
            {"core": "lib/core", "test_support": "test_support"},
        ),
        # A declared source directory replaces src.
        (
            {
                "pyproject.toml": '[tool.maturin]\npython-source = "python"\n',
                "python/native/__init__.py": "",
                "src/lib.rs": "",
                "docs/conf.py": "",
            },
            {"native": "python/native"},
        ),
        # A declared module that does not exist leaves the conventions in charge.
        (
            {
                "pyproject.toml": '[tool.flit.module]\nname = "missing"\n',
                "present/__init__.py": "",
            },
            {"present": "present"},
        ),
    ],
)
def test_build_configuration_selects_shipped_modules(
    tmp_path: Path, files: dict[str, str], expected: dict[str, str]
) -> None:
    for name, text in files.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(text)
    assert project_packages(tmp_path) == {
        name: tmp_path / path for name, path in expected.items()
    }


def test_package_in_root_and_src_is_ambiguous(tmp_path: Path) -> None:
    touch(tmp_path, "example/__init__.py", "src/example/__init__.py")
    with pytest.raises(ValueError, match="Ambiguous source package 'example'"):
        project_packages(tmp_path)
