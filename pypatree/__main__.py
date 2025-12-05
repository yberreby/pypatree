import tyro

from .config import Config
from .discovery import get_packages
from .display import print_tree
from .tree import build_tree


def run(cfg: Config) -> None:
    """Display module tree with public functions/classes."""
    for pkg_name, submods in sorted(get_packages(exclude=cfg.exclude).items()):
        if not submods:
            continue
        print_tree(pkg_name, build_tree(submods, pkg_name, cfg.exclude), cfg)


def main() -> None:
    cfg = tyro.cli(Config, description="Display module tree with public functions/classes.")
    run(cfg)


if __name__ == "__main__":
    main()
