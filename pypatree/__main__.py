import logging
import re
import sys
import traceback
from pathlib import Path

import tyro
from rich.console import Console

from .config import Config
from .discovery import get_packages
from .display import print_tree
from .tree import build_tree


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING,
        format="%(name)s: %(message)s",
        stream=sys.stderr,
    )


def run(cfg: Config) -> bool:
    """Display module tree with public functions/classes."""
    errors: list[str] = []

    def report_error(message: str) -> None:
        errors.append(message)
        print(f"pypatree: {message}", file=sys.stderr)

    packages = get_packages(cfg.exclude, scope=cfg.scope, on_error=report_error)
    if not packages:
        raise ValueError(
            f"No local editable packages found in {Path.cwd()}. "
            "Run `uv pip install -e .` from the Python package's project directory, "
            "then rerun pypatree there. Use --verbose for discovery details."
        )

    for pkg_name, submods in sorted(packages.items()):
        tree = build_tree(
            submods,
            pkg_name=pkg_name,
            exclude=cfg.exclude,
            show_defaults=cfg.show_defaults,
            max_width=None if cfg.flat else Console().width,
            on_error=report_error,
        )
        print_tree(pkg_name, tree, cfg)
    if errors:
        print(
            "Output is incomplete. Install missing dependencies or fix the reported errors; "
            "narrow inspection with a module scope or --exclude REGEX.",
            file=sys.stderr,
        )
    return not errors


def main() -> int:
    cfg = tyro.cli(
        Config, description="Display module tree with public functions/classes."
    )
    _setup_logging(cfg.verbose)
    try:
        return 0 if run(cfg) else 1
    except re.error as error:
        print(
            f"Invalid --exclude regular expression: {error}. Check the pattern; see --help.",
            file=sys.stderr,
        )
    except Exception as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        if cfg.verbose:
            traceback.print_exc()
        else:
            print(
                "Use --verbose for the traceback and --help for usage.", file=sys.stderr
            )
    return 1


if __name__ == "__main__":
    sys.exit(main())
