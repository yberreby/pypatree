import logging
import re
import sys
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


class _Diagnostics(logging.Handler):
    failed: bool = False

    def emit(self, record: logging.LogRecord) -> None:
        self.failed = True


def run(cfg: Config) -> None:
    """Display module tree with public functions/classes."""
    packages = get_packages(cfg.exclude, scope=cfg.scope)
    if not packages:
        raise ValueError(
            f"No local editable packages found in {Path.cwd()}. "
            "Run `uv pip install -e .` from the Python package's project directory, "
            "then rerun pypatree there. Use --verbose for discovery details."
        )

    for pkg_name, submods in sorted(packages.items()):
        if not submods:
            continue
        tree = build_tree(
            submods,
            pkg_name=pkg_name,
            exclude=cfg.exclude,
            show_defaults=cfg.show_defaults,
            max_width=None if cfg.flat else Console().width,
        )
        print_tree(pkg_name, tree, cfg)


def main() -> int:
    cfg = tyro.cli(
        Config, description="Display module tree with public functions/classes."
    )
    _setup_logging(cfg.verbose)
    diagnostics = _Diagnostics(level=logging.ERROR)
    logger = logging.getLogger("pypatree")
    logger.addHandler(diagnostics)
    try:
        run(cfg)
    except re.error as error:
        logger.error(
            "Invalid --exclude regular expression: %s. Check the pattern; see --help.",
            error,
        )
    except Exception as error:
        logger.error("%s: %s", type(error).__name__, error, exc_info=cfg.verbose)
        logger.error("Use --verbose for the traceback and --help for usage.")
    else:
        if diagnostics.failed:
            logger.error(
                "Output is incomplete. Fix the reported imports, or narrow inspection "
                "with a module scope or --exclude REGEX. Use --verbose for details."
            )
    finally:
        logger.removeHandler(diagnostics)
    return int(diagnostics.failed)


if __name__ == "__main__":
    sys.exit(main())
