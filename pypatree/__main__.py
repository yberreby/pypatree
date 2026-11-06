import logging
import re
import sys
import traceback
from pathlib import Path

import tyro

from .config import Config, Exclusion
from .display import print_tree
from .runtime import runtime_trees
from .source import source_trees


def run(cfg: Config) -> bool:
    """Print the selected module trees; return whether inspection was complete."""
    inspect_trees = runtime_trees if cfg.runtime else source_trees
    trees = inspect_trees(
        Path.cwd(),
        scope=cfg.scope,
        exclude=Exclusion(cfg.exclude),
        show_defaults=cfg.show_defaults,
    )
    for name, tree in trees.items():
        print_tree(name, tree, cfg)
    errors = [entry for name, tree in trees.items() for entry in tree.errors(name)]
    for module, error in errors:
        print(f"pypatree: could not inspect {module}: {error}", file=sys.stderr)
    if errors:
        print(
            "Output is incomplete. Fix the reported errors; "
            "narrow inspection with a module scope or --exclude REGEX.",
            file=sys.stderr,
        )
    return not errors


def main() -> int:
    cfg = tyro.cli(
        Config, description="Display module tree with public functions/classes."
    )
    logging.basicConfig(
        level=logging.DEBUG if cfg.verbose else logging.WARNING,
        format="%(name)s: %(message)s",
        stream=sys.stderr,
    )
    if not cfg.verbose:
        # Griffe logs a traceback for each unreadable module, which run() reports.
        logging.getLogger("griffe").setLevel(logging.CRITICAL)
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
