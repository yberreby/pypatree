"""Read local Python source with Griffe, without importing it."""

import inspect
import os
import subprocess
from collections.abc import Iterable
from pathlib import Path
from typing import Optional, Union

import griffe

from pypatree.config import Exclusion, select_modules
from pypatree.layout import TEST_NAME, modules, project_packages
from pypatree.signature import Parameter, Signature
from pypatree.tree import Tree

_PROJECT_FILES = {"pyproject.toml", "setup.py", "setup.cfg"}
_LIST_IGNORED = "ls-files --others --ignored --exclude-standard --directory -z".split()
_ANNOTATED = {"typing.Annotated", "typing_extensions.Annotated"}
_KINDS = {
    griffe.ParameterKind.positional_only: inspect.Parameter.POSITIONAL_ONLY,
    griffe.ParameterKind.positional_or_keyword: inspect.Parameter.POSITIONAL_OR_KEYWORD,
    griffe.ParameterKind.var_positional: inspect.Parameter.VAR_POSITIONAL,
    griffe.ParameterKind.keyword_only: inspect.Parameter.KEYWORD_ONLY,
    griffe.ParameterKind.var_keyword: inspect.Parameter.VAR_KEYWORD,
}
_VARIADIC = {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}


def source_trees(
    root: Path,
    *,
    scope: Optional[str] = None,
    exclude: Exclusion = Exclusion(),
    show_defaults: bool = False,
) -> dict[str, Tree]:
    """Read the packages of root and of the Python projects beneath it."""
    packages = source_packages(root)
    if not packages:
        raise ValueError(
            f"No Python source packages found in {root}. Run pypatree from a "
            "Python project or a repository containing Python subprojects."
        )
    trees = {}
    for name in select_modules(packages, scope, exclude):
        package, *inner = name.split(".")
        path = packages[package]
        module = _load_package(path)
        for part in inner:
            path = _source_modules(path).get(part)
            if path is None:
                raise ValueError(f"Scope {scope!r} does not exist")
            module = _submodule(module, part)
        trees[name] = _source_tree(
            path, module, exclude=exclude, show_defaults=show_defaults
        )
    return trees


def source_packages(root: Path) -> dict[str, Path]:
    """Map the top-level packages of each project under root to their paths."""
    result: dict[str, Path] = {}
    for project in _projects(root):
        for name, path in project_packages(project).items():
            if not _readable(path):
                continue
            if name in result:
                raise ValueError(
                    f"Duplicate source package {name!r}: {result[name]} and {path}. "
                    "Run pypatree from the intended subproject directory."
                )
            result[name] = path
    return result


def _projects(root: Path) -> list[Path]:
    """Root if it is a project, else the outermost projects beneath it, else root.

    The search skips hidden, Git-ignored, and test directories and `node_modules`,
    and does not enter packages or virtual environments.
    """
    if not _PROJECT_FILES.isdisjoint(os.listdir(root)):
        return [root]
    ignored = _git_ignored(root)
    projects = []
    for directory, children, files in os.walk(root):
        here = Path(directory)
        if not _PROJECT_FILES.isdisjoint(files):
            projects.append(here)
            children.clear()
        elif "__init__.py" in files or "pyvenv.cfg" in files:
            children.clear()
        else:
            children[:] = sorted(
                name
                for name in children
                if not name.startswith(".")
                and name != "node_modules"
                and not TEST_NAME.search(name)
                and here / name not in ignored
            )
    return projects or [root]


def _git_ignored(root: Path) -> set[Path]:
    """Paths under root that Git ignores; none outside a Git work tree."""
    try:
        # Hooks export variables that would select another repository.
        local = set(_git(root, "rev-parse", "--local-env-vars").split())
        env = {key: value for key, value in os.environ.items() if key not in local}
        listing = _git(root, *_LIST_IGNORED, env=env)
    except (OSError, subprocess.CalledProcessError):
        return set()
    return {root / entry for entry in listing.split("\0") if entry}


def _git(root: Path, *args: str, env: Optional[dict[str, str]] = None) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, env=env, capture_output=True, check=True
    )
    return os.fsdecode(result.stdout)


def _readable(path: Path) -> bool:
    return path.is_dir() or path.suffix == ".py"


def _source_modules(path: Path) -> dict[str, Path]:
    return {name: child for name, child in modules(path).items() if _readable(child)}


def _load(path: Path, *, submodules: bool) -> griffe.Module:
    module = griffe.load(
        path.stem if path.is_file() else path.name,
        search_paths=[path.parent],
        try_relative_path=False,
        submodules=submodules,
        allow_inspection=False,
    )
    assert isinstance(module, griffe.Module), module
    return module


def _load_package(path: Path) -> Optional[griffe.Module]:
    """Load a package with one Griffe loader, so that its modules can refer to each
    other, as a dataclass does to its bases. Griffe skips unreadable submodules;
    _source_tree reads those, and an unreadable root, alone to report the error.
    """
    try:
        return _load(path, submodules=True)
    except Exception:
        return None


def _submodule(module: Optional[griffe.Module], name: str) -> Optional[griffe.Module]:
    member = None if module is None else module.members.get(name)
    return member if isinstance(member, griffe.Module) else None


def _source_tree(
    path: Path,
    loaded: Optional[griffe.Module],
    *,
    exclude: Exclusion,
    show_defaults: bool,
    ancestors: frozenset[Path] = frozenset(),
) -> Tree:
    resolved = path.resolve()
    if resolved in ancestors:
        return Tree(error=f"Recursive package path: {resolved}")
    tree = Tree()
    module = loaded
    source = path if path.is_file() else path / "__init__.py"
    if source.is_file():
        try:
            module = _read_from(loaded, source) or _load(path, submodules=False)
            tree.docstring = module.docstring.value if module.docstring else None
            tree.items = [
                _signature(item, show_defaults=show_defaults)
                for name, item in module.members.items()
                if not name.startswith("_")
                and not exclude(name)
                and isinstance(item, (griffe.Function, griffe.Class))
            ]
        except Exception as error:
            tree.error = f"{type(error).__name__}: {error}"
    for name, child in _source_modules(path).items():
        if not exclude(name):
            tree.children[name] = _source_tree(
                child,
                _submodule(module, name),
                exclude=exclude,
                show_defaults=show_defaults,
                ancestors=ancestors | {resolved},
            )
    return tree


def _read_from(
    module: Optional[griffe.Module], source: Path
) -> Optional[griffe.Module]:
    """The module if Griffe read it from source, else None."""
    filepath = None if module is None else module.filepath
    if isinstance(filepath, Path) and filepath.resolve() == source.resolve():
        return module
    return None


def _signature(
    item: Union[griffe.Function, griffe.Class], *, show_defaults: bool
) -> Signature:
    if isinstance(item, griffe.Function):
        returns = None if item.returns is None else _annotation(item.returns)
        return Signature(
            item.name, _parameters(item.parameters, show_defaults), returns
        )
    constructor = item.members.get("__init__") or item.members.get("__new__")
    if not isinstance(constructor, griffe.Function):
        return Signature(item.name, parameters=None)
    parameters = list(constructor.parameters)
    if parameters and parameters[0].kind in {
        griffe.ParameterKind.positional_only,
        griffe.ParameterKind.positional_or_keyword,
    }:
        parameters = parameters[1:]  # self or cls
    return Signature(item.name, _parameters(parameters, show_defaults))


def _parameters(
    parameters: Iterable[griffe.Parameter], show_defaults: bool
) -> tuple[Parameter, ...]:
    return tuple(_parameter(parameter, show_defaults) for parameter in parameters)


def _parameter(parameter: griffe.Parameter, show_defaults: bool) -> Parameter:
    assert parameter.kind is not None, parameter
    kind = _KINDS[parameter.kind]
    default = None
    if parameter.default is not None and kind not in _VARIADIC:
        default = str(parameter.default) if show_defaults else "..."
    annotation = parameter.annotation
    return Parameter(
        parameter.name,
        kind,
        annotation=None if annotation is None else _annotation(annotation),
        default=default,
    )


def _annotation(annotation: Union[str, griffe.Expr]) -> str:
    if isinstance(annotation, griffe.ExprName):
        return annotation.name
    if (
        isinstance(annotation, griffe.ExprSubscript)
        and annotation.canonical_path in _ANNOTATED
    ):
        assert isinstance(annotation.slice, griffe.ExprTuple), annotation
        return _annotation(annotation.slice.elements[0])
    if isinstance(annotation, griffe.Expr):
        return "".join(map(_annotation, annotation.iterate(flat=False)))
    return annotation
