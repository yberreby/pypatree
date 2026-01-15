import logging
import sys

import tyro

from .config import Config
from .discovery import get_packages
from .display import print_tree
from .tree import build_tree, get_subtree


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
    for pkg_name, submods in sorted(get_packages(cfg.exclude).items()):
        if not submods:
            continue
        if cfg.scope and not cfg.scope.startswith(pkg_name):
            continue

        tree = build_tree(submods, pkg_name, cfg.exclude, cfg.show_defaults)
        display_name = pkg_name

        if cfg.scope and cfg.scope != pkg_name:
            subtree = get_subtree(tree, cfg.scope[len(pkg_name) + 1 :].split("."))
            if subtree is None:
                continue
            tree, display_name = subtree, cfg.scope

        print_tree(display_name, tree, cfg)


def main() -> None:
    cfg = tyro.cli(
        Config, description="Display module tree with public functions/classes."
    )
    _setup_logging(cfg.verbose)
    run(cfg)


if __name__ == "__main__":
    main()
