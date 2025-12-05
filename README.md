# pypatree

[![CI](https://github.com/yberreby/pypatree/actions/workflows/ci.yml/badge.svg)](https://github.com/yberreby/pypatree/actions/workflows/ci.yml)

Pretty-print a project's module tree.

```bash
uv add --dev pypatree
uv run pypatree
```

Example output on this very repo:
```
pypatree
├── build_tree()
├── get_module_items()
├── get_packages()
├── __main__
│   ├── main()
│   └── run()
└── display
    ├── print_tree()
    └── render_tree()
```
