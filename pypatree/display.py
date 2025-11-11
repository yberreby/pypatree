from typing import Any, Dict


def render_tree(tree: Dict[str, Any], prefix: str = "") -> None:
    """Recursively render tree structure with box-drawing characters."""
    # Render root-level items first
    root_items = tree.get("__items__", [])
    keys = [k for k in tree.keys() if k != "__items__"]

    for i, item in enumerate(root_items):
        is_last_item = i == len(root_items) - 1 and not keys
        connector = "└── " if is_last_item else "├── "
        print(f"{prefix}{connector}{item}")

    for i, key in enumerate(keys):
        is_last = i == len(keys) - 1
        items = tree[key].get("__items__", [])

        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{key}")

        extension = "    " if is_last else "│   "
        for j, item in enumerate(items):
            item_connector = "└── " if j == len(items) - 1 else "├── "
            print(f"{prefix}{extension}{item_connector}{item}")

        if [k for k in tree[key].keys() if k != "__items__"]:
            render_tree(tree[key], prefix + extension)
