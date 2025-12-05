# pypatree

[![CI](https://github.com/yberreby/pypatree/actions/workflows/ci.yml/badge.svg)](https://github.com/yberreby/pypatree/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pypatree)](https://pypi.org/project/pypatree/)
[![Python](https://img.shields.io/pypi/pyversions/pypatree)](https://pypi.org/project/pypatree/)
[![License](https://img.shields.io/pypi/l/pypatree)](https://github.com/yberreby/pypatree/blob/main/LICENSE)

Pretty-print a project's module tree.

```bash
uv add --dev pypatree
uv run pypatree
```

Example output on this very repo:
```
pypatree
├── __main__
│   ├── main() -> None
│   └── run(skip_tests: bool = True) -> None
├── discovery
│   └── get_packages(skip_tests: bool = True) -> dict
├── display
│   ├── print_tree(tree: dict) -> None
│   └── render_tree(tree: dict, prefix: str = '') -> list
├── introspection
│   ├── format_signature(obj: Union[Callable, type]) -> str
│   └── get_module_items(modname: str, skip_tests: bool = True) -> list
└── tree
    └── build_tree(submods: list, pkg_name: str, skip_tests: bool = True) -> dict
```
