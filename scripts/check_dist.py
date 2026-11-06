#!/usr/bin/env python
"""Build the distributions, check their contents, and run each one installed."""

import tarfile
import tempfile
from importlib.metadata import version
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

from lib import PYTHON_VERSION, ROOT, run

SDIST_CONTENTS = {
    ".gitignore",
    ".python-version",
    "LICENSE",
    "PKG-INFO",
    "README.md",
    "pypatree",
    "pyproject.toml",
    "scripts",
    "tests",
    "uv.lock",
}
ARGS = ("--flat", "--show-defaults", "--color", "never")
EXPECTED = [
    "example",
    "example.visible(mode: Literal['fast', 'slow'] = 'fast') -> bool",
]


def main() -> None:
    run("uv", "build", cwd=ROOT)
    release = version("pypatree")
    wheels = list((ROOT / "dist").glob(f"pypatree-{release}-*.whl"))
    assert len(wheels) == 1, wheels
    wheel = wheels[0]
    sdist = ROOT / "dist" / f"pypatree-{release}.tar.gz"
    with tarfile.open(sdist) as archive:
        names = archive.getnames()
    contents = {PurePosixPath(name).parts[1] for name in names if "/" in name}
    assert contents == SDIST_CONTENTS, contents
    with ZipFile(wheel) as archive:
        names = archive.namelist()
    assert "pypatree/py.typed" in names
    assert not any(name.endswith("/test.py") for name in names), names

    for artifact in [wheel, sdist]:
        with tempfile.TemporaryDirectory() as temporary:
            check_installed(artifact, Path(temporary))
        print(f"Installed {artifact.name}: qualified output preserved.", flush=True)


def check_installed(artifact: Path, directory: Path) -> None:
    """Inspect an uninstalled project with artifact, installed and through uvx."""
    environment = directory / "venv"
    run("uv", "venv", "--python", PYTHON_VERSION, str(environment))
    python = environment / "bin" / "python"
    run("uv", "pip", "install", "--python", str(python), str(artifact))
    project = directory / "project space é"
    (project / "example").mkdir(parents=True)
    (project / "pyproject.toml").write_text('[project]\nname = "example"\n')
    (project / "example" / "__init__.py").write_text(
        "from typing import Literal\n"
        'def visible(mode: Literal["fast", "slow"] = "fast") -> bool: pass\n'
    )
    installed = run(str(python.with_name("pypatree")), *ARGS, cwd=project).stdout
    assert installed.decode().splitlines() == EXPECTED, installed
    uvx = ["uvx", "--no-cache", "--python", PYTHON_VERSION, "--from", str(artifact)]
    isolated = run(*uvx, "pypatree", *ARGS, cwd=project).stdout
    assert isolated == installed, isolated
    # Run from the project so the checkout's own pypatree cannot shadow the install.
    location = run(
        str(python), "-c", "import pypatree; print(pypatree.__file__)", cwd=project
    )
    module = Path(location.stdout.decode().strip()).resolve()
    assert module.is_relative_to(environment.resolve()), module


if __name__ == "__main__":
    main()
