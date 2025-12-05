# pypatree

[![CI](https://github.com/yberreby/pypatree/actions/workflows/ci.yml/badge.svg)](https://github.com/yberreby/pypatree/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pypatree)](https://pypi.org/project/pypatree/)
[![Python](https://img.shields.io/pypi/pyversions/pypatree)](https://pypi.org/project/pypatree/)
[![License](https://img.shields.io/pypi/l/pypatree?v=2)](https://github.com/yberreby/pypatree/blob/main/LICENSE)

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
│   └── get_packages(skip_tests: bool = True) -> dict[str, list[str]]
├── display
│   ├── print_tree(tree: dict[str, typing.Any]) -> None
│   └── render_tree(tree: dict[str, typing.Any], prefix: str = '') -> list[str]
├── introspection
│   ├── format_signature(obj: Union[Callable, type]) -> str
│   └── get_module_items(modname: str, skip_tests: bool = True) -> list[str]
└── tree
    └── build_tree(submods: list[str], pkg_name: str, skip_tests: bool = True) -> dict[str, typing.Any]
```
