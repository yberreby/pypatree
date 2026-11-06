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


def write(source: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def install_project(
    *, cli: Path, source: Path, package: str, files: dict[str, str]
) -> None:
    """Install files as an editable project into the CLI's environment."""
    write(source, files)
    (source / "pyproject.toml").write_text(
        '[build-system]\nrequires = ["hatchling"]\nbuild-backend = "hatchling.build"\n'
        '[project]\nname = "pypatree-fixture"\nversion = "0.0.0"\n'
        f"[tool.hatch.build.targets.wheel]\npackages = [{json.dumps(package)}]\n"
    )
    python = str(cli.with_name("python"))
    run("uv", "pip", "install", "--python", python, "-e", str(source))


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
        write(
            tmp_path / project,
            {
                "pyproject.toml": f'[project]\nname = "{project}"\nversion = "0.0.0"\n',
                f"src/{package}/__init__.py": (
                    "import unavailable_pypatree_fixture_dependency\n"
                    "raise RuntimeError('source inspection must not execute this')\n"
                    "def visible(value: int = 3) -> int: return value\n"
                ),
            },
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
def test_backends_agree_on_editable_layouts_and_escaped_paths(
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
    runtime = invoke(cli, source, "--flat", "--runtime")
    assert runtime.returncode == 0, runtime.stderr
    module = {
        "src/example": "example",
        "example.py": "example",
        "namespace": "namespace._private.leaf",
    }.get(package, package)
    assert f"{module}.visible(value: int) -> int" in runtime.stdout.splitlines()
    assert runtime.stderr == ""
    assert invoke(cli, source, "--flat").stdout == runtime.stdout


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
    result = invoke(cli, physical, "--runtime")
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
            "example/__main__.py": "raise RuntimeError('entry script executed')\n",
        },
    )
    for args in [(), ("example",)]:
        result = invoke(cli, tmp_path, "--runtime", *args)
        assert result.returncode == 0, result.stderr
        assert "visible()" in result.stdout
        assert "test_bomb" not in result.stdout
        assert "__main__" not in result.stdout


@pytest.mark.parametrize(
    "failure",
    [
        "raise SystemExit(0)",
        "raise RuntimeError('broken child')",
        "import missing_pypatree_dependency",
    ],
)
def test_import_failure_is_reported_once_after_partial_output(
    cli: Path, tmp_path: Path, failure: str
) -> None:
    attempts = tmp_path / "attempts"
    install_project(
        cli=cli,
        source=tmp_path,
        package="example",
        files={
            "example/__init__.py": "def visible(): pass\n",
            "example/child/__init__.py": (
                f"with open({str(attempts)!r}, 'a') as file: file.write('.')\n{failure}\n"
            ),
        },
    )
    result = invoke(cli, tmp_path, "--runtime")
    assert result.returncode != 0
    assert "visible()" in result.stdout
    assert "child [inspection failed]" in result.stdout
    assert "could not inspect example.child" in result.stderr
    assert "Output is incomplete" in result.stderr
    assert "--exclude" in result.stderr
    assert "Traceback" not in result.stderr
    assert attempts.read_text() == "."


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


def test_source_parse_failure_is_reported_without_traceback(
    cli: Path, tmp_path: Path
) -> None:
    write(
        tmp_path,
        {
            "pyproject.toml": "",
            "example/__init__.py": "def visible(): pass\n",
            "example/broken.py": "def invalid(\n",
        },
    )
    result = invoke(cli, tmp_path, "--flat")
    assert result.returncode != 0
    assert result.stdout.splitlines() == [
        "example",
        "example.visible()",
        "example.broken [inspection failed]",
    ]
    assert (
        "could not inspect example.broken: LoadingError: Syntax error" in result.stderr
    )
    assert "Traceback" not in result.stderr
    assert "Traceback" in invoke(cli, tmp_path, "--verbose").stderr


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
        "example.loop [inspection failed]",
    ]
    assert "Recursive package path" in result.stderr
