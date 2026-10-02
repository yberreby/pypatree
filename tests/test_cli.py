import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.lib import ROOT, run


@pytest.fixture(scope="module")
def cli(tmp_path_factory: pytest.TempPathFactory) -> Path:
    environment = tmp_path_factory.mktemp("cli") / "venv"
    run("uv", "venv", "--python", sys.executable, str(environment))
    executable = environment / "bin" / "python"
    run("uv", "pip", "install", "--python", str(executable), "-e", str(ROOT))
    return executable.with_name("pypatree")


def install_project(
    *, cli: Path, source: Path, package: str, files: dict[str, str]
) -> None:
    for name, text in files.items():
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    (source / "pyproject.toml").write_text(
        '[build-system]\nrequires = ["hatchling"]\nbuild-backend = "hatchling.build"\n'
        '[project]\nname = "pypatree-fixture"\nversion = "0.0.0"\n'
        f"[tool.hatch.build.targets.wheel]\npackages = [{json.dumps(package)}]\n"
    )
    run(
        "uv",
        "pip",
        "install",
        "--python",
        str(cli.with_name("python")),
        "-e",
        str(source),
    )


def invoke(cli: Path, source: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(cli), *args],
        cwd=source,
        capture_output=True,
        text=True,
        timeout=10,
        env={**os.environ, "COLUMNS": "32"},
    )


def test_uninstalled_monorepo_and_subproject(cli: Path, tmp_path: Path) -> None:
    for project, package in [("core", "example_core"), ("engine", "example_engine")]:
        directory = tmp_path / project
        module = directory / "src" / package
        module.mkdir(parents=True)
        (directory / "pyproject.toml").write_text(
            f'[project]\nname = "{project}"\nversion = "0.0.0"\n'
        )
        (module / "__init__.py").write_text(
            "import unavailable_pypatree_fixture_dependency\n"
            "raise RuntimeError('source inspection must not execute this')\n"
            "def visible(value: int = 3) -> int: return value\n"
        )
    for directory in [tmp_path, tmp_path / "engine"]:
        result = invoke(cli, directory, "--flat")
        assert result.returncode == 0, result.stderr
        assert "example_engine.visible(value: int = ...) -> int" in result.stdout
        assert ("example_core.visible" in result.stdout) == (directory == tmp_path)
        assert result.stderr == ""


@pytest.mark.parametrize(
    "package", ["example", "src/example", "src", "example.py", "namespace"]
)
def test_editable_layouts_and_escaped_paths(
    cli: Path, tmp_path: Path, package: str
) -> None:
    source = tmp_path / "project space é %"
    filename = package if package.endswith(".py") else f"{package}/__init__.py"
    if package == "namespace":
        filename = "namespace/_private/leaf.py"
    install_project(
        cli=cli,
        source=source,
        package=package,
        files={filename: "def visible(value: int) -> int: return value\n"},
    )
    result = invoke(cli, source, "--flat")
    assert result.returncode == 0, result.stderr
    module = {
        "src/example": "example",
        "example.py": "example",
        "namespace": "namespace._private.leaf",
    }.get(package, package)
    assert f"{module}.visible(value: int) -> int" in result.stdout.splitlines()
    assert result.stderr == ""


def test_symlinked_editable_source(cli: Path, tmp_path: Path) -> None:
    physical = tmp_path / "physical"
    physical.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(physical, target_is_directory=True)
    install_project(
        cli=cli,
        source=alias,
        package="example",
        files={"example/__init__.py": "def visible(): pass\n"},
    )
    result = invoke(cli, physical)
    assert result.returncode == 0, result.stderr
    assert "visible()" in result.stdout


def test_exclusion_prevents_package_execution(cli: Path, tmp_path: Path) -> None:
    install_project(
        cli=cli,
        source=tmp_path,
        package="example",
        files={
            "example/__init__.py": "def visible(): pass\n",
            "example/test_bomb/__init__.py": "raise RuntimeError('excluded package executed')\n",
        },
    )
    for args in [(), ("example",)]:
        result = invoke(cli, tmp_path, *args)
        assert result.returncode == 0, result.stderr
        assert "visible()" in result.stdout
        assert "test_bomb" not in result.stdout


@pytest.mark.parametrize(
    "failure",
    [
        "raise SystemExit(0)",
        "raise RuntimeError('broken child')",
        "import missing_pypatree_dependency",
    ],
)
def test_import_failure_reports_partial_output_and_next_action(
    cli: Path, tmp_path: Path, failure: str
) -> None:
    install_project(
        cli=cli,
        source=tmp_path,
        package="example",
        files={
            "example/__init__.py": "def visible(): pass\n",
            "example/child/__init__.py": failure + "\n",
        },
    )
    result = invoke(cli, tmp_path, "--runtime")
    assert result.returncode != 0
    assert "visible()" in result.stdout
    assert "example.child" in result.stderr
    assert "Output is incomplete" in result.stderr
    assert "--exclude" in result.stderr
    assert "Traceback" not in result.stderr


def test_import_stdout_is_kept_out_of_tree(cli: Path, tmp_path: Path) -> None:
    install_project(
        cli=cli,
        source=tmp_path,
        package="example",
        files={
            "example/__init__.py": "print('import chatter')\ndef visible(): pass\n",
        },
    )
    result = invoke(cli, tmp_path, "--flat", "--runtime")
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ["example", "example.visible()"]
    assert "import chatter" in result.stderr


def test_empty_directory_has_actionable_failure(cli: Path, tmp_path: Path) -> None:
    result = invoke(cli, tmp_path)
    assert result.returncode != 0
    assert result.stdout == ""
    assert str(tmp_path) in result.stderr
    assert "Run pypatree from a Python project" in result.stderr


def test_invalid_regex_has_actionable_failure(cli: Path, tmp_path: Path) -> None:
    result = invoke(cli, tmp_path, "--exclude", "[")
    assert result.returncode != 0
    assert "Invalid --exclude regular expression" in result.stderr
    assert "--help" in result.stderr
    assert "Traceback" not in result.stderr


def test_project_logging_configuration_cannot_hide_import_failure(
    cli: Path, tmp_path: Path
) -> None:
    install_project(
        cli=cli,
        source=tmp_path,
        package="example",
        files={
            "example/__init__.py": "import logging\nlogging.disable(logging.CRITICAL)\ndef visible(): pass\n",
            "example/child/__init__.py": "raise RuntimeError('broken child')\n",
        },
    )
    result = invoke(cli, tmp_path, "--runtime")
    assert result.returncode != 0
    assert "broken child" in result.stderr
    assert "Output is incomplete" in result.stderr


def test_recursive_package_paths_have_a_bounded_failure(
    cli: Path, tmp_path: Path
) -> None:
    install_project(
        cli=cli,
        source=tmp_path,
        package="example",
        files={
            "example/__init__.py": "def visible(): pass\n",
            "example/loop/__init__.py": "from pathlib import Path\n__path__ = [str(Path(__file__).parents[1])]\n",
        },
    )
    result = invoke(cli, tmp_path, "--flat", "--runtime")
    assert result.returncode != 0
    assert result.stdout.splitlines() == [
        "example",
        "example.visible()",
        "example.loop",
    ]
    assert "Recursive package path" in result.stderr
