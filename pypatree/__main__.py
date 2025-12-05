import tyro

from . import build_tree, get_packages
from .display import print_tree


def run(skip_tests: bool = True) -> None:
    """Display module tree with public functions/classes."""
    for pkg_name, submods in sorted(get_packages(skip_tests=skip_tests).items()):
        if not submods:
            continue
        print(pkg_name)
        print_tree(build_tree(submods, pkg_name, skip_tests=skip_tests))


def main() -> None:
    tyro.cli(run)


if __name__ == "__main__":
    main()
