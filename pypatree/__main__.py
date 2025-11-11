import tyro

from . import build_tree, get_packages
from .display import render_tree


def main(skip_tests: bool = True):
    """Display module tree with public functions/classes.

    Args:
        skip_tests: Skip test modules and test functions. Default: True.
    """
    grouped_packages = get_packages(skip_tests=skip_tests)
    for pkg_name, submods in sorted(grouped_packages.items()):
        if not submods:
            continue

        print(pkg_name)
        tree = build_tree(submods, pkg_name, skip_tests=skip_tests)
        render_tree(tree)


if __name__ == "__main__":
    tyro.cli(main)
