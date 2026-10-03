import inspect
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

import griffe

from pypatree.discovery import _find_packages_in_dir, _matches_exclude
from pypatree.introspection import ErrorHandler, format_inspected_signature
from pypatree.tree import Tree

_SKIP_DIRECTORIES = {
    "__pycache__",
    "node_modules",
    "venv",
    "build",
    "dist",
    "outputs",
    "throwaway",
    "tests",
}


def _projects(root: Path) -> list[Path]:
    projects = []
    for directory, children, files in os.walk(root):
        children[:] = sorted(
            name
            for name in children
            if not name.startswith(".") and name not in _SKIP_DIRECTORIES
        )
        if "pyproject.toml" in files or "setup.py" in files or "setup.cfg" in files:
            projects.append(Path(directory))
            children.clear()
        elif "__init__.py" in files:
            children.clear()
    return projects or [root]


def source_packages(root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for project in _projects(root):
        for name in _find_packages_in_dir(str(project)):
            candidates = [
                path
                for directory in [project, project / "src"]
                for path in [directory / name, directory / f"{name}.py"]
                if path.is_dir() or path.is_file()
            ]
            if len(candidates) != 1:
                raise ValueError(f"Ambiguous source package {name!r}: {candidates}")
            if name in result:
                raise ValueError(
                    f"Duplicate source package {name!r}: {result[name]} and {candidates[0]}. "
                    "Run pypatree from the intended subproject directory."
                )
            result[name] = candidates[0]
    return result


@dataclass(frozen=True)
class _SourceDefault:
    expression: str

    def __repr__(self) -> str:
        return self.expression


_PARAMETER_KINDS = {
    griffe.ParameterKind.positional_only: inspect.Parameter.POSITIONAL_ONLY,
    griffe.ParameterKind.positional_or_keyword: inspect.Parameter.POSITIONAL_OR_KEYWORD,
    griffe.ParameterKind.var_positional: inspect.Parameter.VAR_POSITIONAL,
    griffe.ParameterKind.keyword_only: inspect.Parameter.KEYWORD_ONLY,
    griffe.ParameterKind.var_keyword: inspect.Parameter.VAR_KEYWORD,
}


def _annotation(annotation: Union[str, griffe.Expr]) -> str:
    if isinstance(annotation, griffe.ExprName):
        return annotation.name
    if (
        isinstance(annotation, griffe.ExprSubscript)
        and annotation.canonical_path == "typing.Annotated"
    ):
        assert isinstance(annotation.slice, griffe.ExprTuple)
        return _annotation(annotation.slice.elements[0])
    if isinstance(annotation, griffe.Expr):
        return "".join(_annotation(part) for part in annotation.iterate(flat=False))
    return annotation


def _parameter(parameter: griffe.Parameter) -> inspect.Parameter:
    assert parameter.kind is not None, parameter
    variadic = parameter.kind in {
        griffe.ParameterKind.var_positional,
        griffe.ParameterKind.var_keyword,
    }
    return inspect.Parameter(
        parameter.name,
        kind=_PARAMETER_KINDS[parameter.kind],
        annotation=inspect.Parameter.empty
        if parameter.annotation is None
        else _annotation(parameter.annotation),
        default=inspect.Parameter.empty
        if variadic or parameter.default is None
        else _SourceDefault(str(parameter.default)),
    )


def _signature(
    item: Union[griffe.Function, griffe.Class],
    *,
    show_defaults: bool,
    max_width: Optional[int],
) -> str:
    callable_item = item
    is_class = isinstance(item, griffe.Class)
    if is_class:
        constructor = item.members.get("__init__") or item.members.get("__new__")
        if constructor is None:
            return f"{item.name}(...)"
        assert isinstance(constructor, griffe.Function), constructor
        callable_item = constructor
    assert isinstance(callable_item, griffe.Function)
    parameters = list(callable_item.parameters)
    if (
        is_class
        and parameters
        and parameters[0].kind
        in {
            griffe.ParameterKind.positional_only,
            griffe.ParameterKind.positional_or_keyword,
        }
    ):
        parameters = parameters[1:]
    empty = inspect.Signature.empty
    signature = inspect.Signature(
        parameters=[_parameter(parameter) for parameter in parameters],
        return_annotation=(
            empty
            if is_class or callable_item.returns is None
            else _annotation(callable_item.returns)
        ),
    )
    return format_inspected_signature(
        signature, name=item.name, show_defaults=show_defaults, max_width=max_width
    )


def _source_tree(
    path: Path,
    *,
    pattern: Optional[re.Pattern[str]],
    show_defaults: bool,
    max_width: Optional[int],
    on_error: ErrorHandler,
    ancestors: frozenset[Path] = frozenset(),
) -> Tree:
    tree = Tree()
    resolved = path.resolve()
    if resolved in ancestors:
        on_error(f"Recursive source path: {path}")
        tree.failed = True
        return tree
    try:
        if path.is_file() or (path / "__init__.py").is_file():
            module = griffe.load(
                path.stem if path.is_file() else path.name,
                search_paths=[path.parent],
                try_relative_path=False,
                submodules=False,
                allow_inspection=False,
            )
            assert isinstance(module, griffe.Module), module
            tree.docstring = module.docstring.value if module.docstring else None
            tree.items = sorted(
                _signature(item, show_defaults=show_defaults, max_width=max_width)
                for name, item in module.members.items()
                if not name.startswith("_")
                and not _matches_exclude(name, pattern)
                and isinstance(item, (griffe.Function, griffe.Class))
            )
    except Exception as error:
        on_error(f"Could not read {path}: {type(error).__name__}: {error}")
        tree.failed = True
    if path.is_dir():
        for child in sorted(path.iterdir()):
            name = child.stem if child.is_file() else child.name
            if (
                not name.isidentifier()
                or name in {"__init__", "__pycache__"}
                or _matches_exclude(name, pattern)
            ):
                continue
            if (child.is_dir() and any(child.rglob("*.py"))) or child.suffix == ".py":
                tree.children[name] = _source_tree(
                    child,
                    pattern=pattern,
                    show_defaults=show_defaults,
                    max_width=None if max_width is None else max_width - 4,
                    on_error=on_error,
                    ancestors=ancestors | {resolved},
                )
    return tree


def source_trees(
    *,
    root: Path,
    scope: Optional[str],
    exclude: Optional[str],
    show_defaults: bool,
    max_width: Optional[int],
    on_error: ErrorHandler,
) -> dict[str, Tree]:
    pattern = re.compile(exclude) if exclude else None
    packages = source_packages(root)
    if scope:
        parts = scope.split(".")
        if not all(part.isidentifier() for part in parts):
            raise ValueError(
                f"Invalid module scope {scope!r}: use a dotted Python name"
            )
        if parts[0] not in packages:
            raise ValueError(f"Scope {scope!r} is not in a local source package")
        if _matches_exclude(".".join(parts[1:]), pattern):
            raise ValueError(f"Scope {scope!r} is excluded by --exclude {exclude!r}")
        path = packages[parts[0]].joinpath(*parts[1:])
        if not path.is_dir() and not path.is_file():
            path = path.with_suffix(".py")
        if not path.exists():
            raise ValueError(f"Scope {scope!r} does not exist")
        packages = {scope: path}
    else:
        included = {
            name: path
            for name, path in packages.items()
            if not _matches_exclude(name, pattern)
        }
        if packages and not included:
            raise ValueError(
                f"All local packages are excluded by --exclude {exclude!r}. Use --exclude '' to include them."
            )
        packages = included
    if not packages:
        raise ValueError(
            f"No Python source packages found in {root}. Run pypatree from a Python project or a repository containing Python subprojects."
        )
    return {
        name: _source_tree(
            path,
            pattern=pattern,
            show_defaults=show_defaults,
            max_width=None if max_width is None else max_width - 4,
            on_error=on_error,
        )
        for name, path in sorted(packages.items())
    }
