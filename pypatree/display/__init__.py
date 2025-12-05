from pypatree.tree import Tree


def render_tree(tree: Tree, prefix: str = "") -> list[str]:
    """Render tree to lines with box-drawing characters."""
    lines: list[str] = []
    items = tree.get("__items__", [])
    children = [k for k in tree if k != "__items__"]

    for i, item in enumerate(items):
        last = i == len(items) - 1 and not children
        lines.append(f"{prefix}{'└── ' if last else '├── '}{item}")

    for i, key in enumerate(children):
        last = i == len(children) - 1
        subtree = tree[key]
        sub_items = subtree.get("__items__", [])

        lines.append(f"{prefix}{'└── ' if last else '├── '}{key}")
        ext = "    " if last else "│   "

        for j, item in enumerate(sub_items):
            item_last = j == len(sub_items) - 1
            lines.append(f"{prefix}{ext}{'└── ' if item_last else '├── '}{item}")

        if any(k != "__items__" for k in subtree):
            lines.extend(render_tree(subtree, prefix + ext))

    return lines


def print_tree(tree: Tree) -> None:
    for line in render_tree(tree):
        print(line)
