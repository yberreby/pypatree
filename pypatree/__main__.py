import logging
import sys

import tyro

from .config import Config
from .discovery import get_packages
from .display import print_tree
from .tree import build_tree


def _setup_logging(verbose: bool) -> None:
    """Configure logging to stderr if verbose."""
    if verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(name)s: %(message)s",
            stream=sys.stderr,
        )


def run(cfg: Config) -> None:
    """Display module tree with public functions/classes."""
    packages = get_packages(cfg.exclude, scope=cfg.scope)
    if not packages:
        print(
            "No packages found. Ensure you're in a directory with an editable install.",
            file=sys.stderr,
        )
        print("Run with --verbose for debug output.", file=sys.stderr)
        return

    for pkg_name, submods in sorted(packages.items()):
        if not submods:
            continue
        tree = build_tree(submods, pkg_name, cfg.exclude, cfg.show_defaults)
        print_tree(pkg_name, tree, cfg)


def main() -> None:
    cfg = tyro.cli(
        Config, description="Display module tree with public functions/classes."
    )
    _setup_logging(cfg.verbose)
    run(cfg)


if __name__ == "__main__":
    main()
