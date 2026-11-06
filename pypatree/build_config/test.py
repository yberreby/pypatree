from pathlib import Path, PurePosixPath

import pytest

from . import BuildConfig, normalize, read_build_config


@pytest.mark.parametrize(
    ("filename", "text", "expected"),
    [
        ("pyproject.toml", "", BuildConfig()),
        (
            "pyproject.toml",
            '[project]\nname = "My.Tool-Kit"\n',
            BuildConfig(name="my_tool_kit"),
        ),
        (
            "pyproject.toml",
            '[tool.hatch.build.targets.wheel]\npackages = ["src/alpha", "beta.py"]\n'
            '[tool.hatch.build]\nonly-include = ["lib/gamma"]\n',
            BuildConfig(
                include=("gamma", "alpha", "beta"),
                roots=(PurePosixPath("lib"), PurePosixPath("src")),
            ),
        ),
        (
            "pyproject.toml",
            '[tool.setuptools]\npackages = ["alpha", "alpha.sub"]\npy-modules = ["tool"]\n'
            '[tool.setuptools.package-dir]\n"" = "lib"\n',
            BuildConfig(include=("tool", "alpha"), roots=(PurePosixPath("lib"),)),
        ),
        (
            "pyproject.toml",
            '[tool.setuptools.packages.find]\nwhere = ["code"]\ninclude = ["kit*", "kit.*"]\n',
            BuildConfig(include=("kit*", "kit"), roots=(PurePosixPath("code"),)),
        ),
        (
            "pyproject.toml",
            '[tool.flit.module]\nname = "flitmod"\n',
            BuildConfig(include=("flitmod",)),
        ),
        (
            "pyproject.toml",
            '[tool.uv.build-backend]\nmodule-name = ["uvmod.core"]\nmodule-root = ""\n',
            BuildConfig(include=("uvmod",)),
        ),
        (
            "pyproject.toml",
            '[tool.poetry]\nname = "poe-tool"\npackages = [{include = "poe", from = "lib"}, {include = "extra_*"}]\n',
            BuildConfig(
                name="poe_tool",
                include=("poe", "extra_*"),
                roots=(PurePosixPath("lib"),),
            ),
        ),
        (
            "pyproject.toml",
            '[tool.pdm.build]\nincludes = ["pdmpkg"]\npackage-dir = "source"\n',
            BuildConfig(include=("pdmpkg",), roots=(PurePosixPath("source"),)),
        ),
        (
            "pyproject.toml",
            '[tool.maturin]\nmodule-name = "native._core"\npython-source = "python"\n',
            BuildConfig(include=("native",), roots=(PurePosixPath("python"),)),
        ),
        (
            "setup.cfg",
            "[metadata]\nname = cfg-tool\n[options]\npackage_dir =\n    =src\n"
            "packages =\n    cfgpkg\n    cfgpkg.sub\npy_modules = single, other\n",
            BuildConfig(
                name="cfg_tool",
                include=("single", "other", "cfgpkg"),
                roots=(PurePosixPath("src"),),
            ),
        ),
        (
            "setup.cfg",
            "[options]\npackages = find:\n[options.packages.find]\nwhere = lib\ninclude = found*\n",
            BuildConfig(include=("found*",), roots=(PurePosixPath("lib"),)),
        ),
        (
            "pyproject.toml",
            '[tool.hatch.build]\npackages = 3\n[tool.setuptools]\npy-modules = ["ok", 4]\n',
            BuildConfig(include=("ok",)),
        ),
    ],
)
def test_declarations_of_each_build_backend(
    tmp_path: Path, filename: str, text: str, expected: BuildConfig
) -> None:
    (tmp_path / filename).write_text(text)
    assert read_build_config(tmp_path) == expected


def test_unparsable_configuration_is_reported_and_skipped(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    (tmp_path / "pyproject.toml").write_text("[project\n")
    assert read_build_config(tmp_path) == BuildConfig()
    assert "Ignoring unparsable" in caplog.text


def test_normalize_matches_distribution_and_module_names() -> None:
    assert normalize("My.Tool-Kit") == normalize("my_tool__kit") == "my_tool_kit"
