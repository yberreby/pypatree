# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Read @README.md.in for key information; the more verbose README.md is generated from this file using a script, no need to read it, it includes verbose example outputs.

We use `uv` for package management. See @pyproject.toml, @.python-version

We use `just` for task automation. See @justfile - this is the reference for all development commands.

See @.pre-commit-config.yaml

See @pypatree directory for core code

Architecture: `uv run pypatree` (dogfood). Each module = dir with `__init__.py` + `test.py`.

We have GitHub Actions, see @.github/workflows

No matter what, the command `uv run just` is always good to run to ensure the repo is in a good state.
