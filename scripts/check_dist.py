import tempfile
import tarfile
from importlib.metadata import version
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

from lib import PYTHON_VERSION, ROOT, run


def main() -> None:
    run("uv", "build", cwd=ROOT)
    release = version("pypatree")
    wheels = list((ROOT / "dist").glob(f"pypatree-{release}-*.whl"))
    assert len(wheels) == 1, wheels
    wheel = wheels[0]
    source = ROOT / "dist" / f"pypatree-{release}.tar.gz"
    assert source.is_file(), source
    with tarfile.open(source) as archive:
        names = archive.getnames()
        assert not any(".git" in PurePosixPath(name).parts for name in names), names
    with ZipFile(wheel) as archive:
        names = archive.namelist()
        assert "pypatree/py.typed" in names
        assert not any(name.endswith("/test.py") for name in names), names

    for artifact in [wheel, source]:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            environment = directory / "venv"
            run("uv", "venv", "--python", PYTHON_VERSION, str(environment))
            executable = environment / "bin" / "python"
            run("uv", "pip", "install", "--python", str(executable), str(artifact))
            project = directory / "project space é"
            package = project / "example"
            package.mkdir(parents=True)
            (project / "pyproject.toml").write_text(
                '[build-system]\nrequires = ["hatchling"]\nbuild-backend = "hatchling.build"\n'
                '[project]\nname = "example"\nversion = "0.0.0"\n'
            )
            (package / "__init__.py").write_text(
                "from typing import Literal\n"
                'def visible(mode: Literal["fast", "slow"] = "fast") -> bool: pass\n'
            )
            result = run(
                str(executable.with_name("pypatree")),
                "--flat",
                "--show-defaults",
                "--color",
                "never",
                cwd=project,
            )
            assert result.stdout.decode().splitlines() == [
                "example",
                "example.visible(mode: Literal['fast', 'slow'] = 'fast') -> bool",
            ], result.stdout
            isolated = run(
                "uvx",
                "--no-cache",
                "--python",
                PYTHON_VERSION,
                "--from",
                str(artifact),
                "pypatree",
                "--flat",
                "--show-defaults",
                "--color",
                "never",
                cwd=project,
            )
            assert isolated.stdout == result.stdout, isolated.stdout
            location = (
                run(
                    str(executable),
                    "-c",
                    "import pypatree; print(pypatree.__file__)",
                    cwd=project,
                )
                .stdout.decode()
                .strip()
            )
            assert Path(location).resolve().is_relative_to(environment.resolve()), (
                location
            )
            print(
                f"Installed {artifact.name}: qualified output and literal signatures preserved.",
                flush=True,
            )


if __name__ == "__main__":
    main()
