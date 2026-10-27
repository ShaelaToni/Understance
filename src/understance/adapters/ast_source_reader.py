import ast
from dataclasses import dataclass, field
from pathlib import Path

from understance.domain.graph import Dependency, DependencyGraph, Module
from understance.ports.interfaces import SourceReader

EXCLUDED_REASON = "test evidence, not graph modules"
NOT_REACHABLE = "dynamic imports, reflection, generated code, other languages"
DYNAMIC_IMPORT_CALLS = {"import_module", "__import__"}


@dataclass
class _Scan:
    trees: dict[str, tuple[str, ast.Module]] = field(default_factory=dict)
    excluded: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


class ASTSourceReader(SourceReader):
    """Parse every .py file under root with ast; never import or run subject code."""

    def __init__(self, max_file_bytes: int = 1_000_000):
        self.max_file_bytes = max_file_bytes

    def read_graph(self, root: Path) -> DependencyGraph:
        scan = self._scan(root)
        names = set(scan.trees)
        edges = {
            Dependency(name, target)
            for name, (_, tree) in scan.trees.items()
            for target in _import_targets(tree, name, names)
            if target in names and target != name
        }
        return DependencyGraph(
            modules=tuple(Module(n) for n in sorted(names)),
            dependencies=tuple(sorted(edges, key=lambda d: (d.source, d.target))),
        )

    def scope_line(self, root: Path) -> str:
        scan = self._scan(root)
        dynamic = [rel for rel, tree in scan.trees.values() if _calls_dynamic(tree)]
        return (
            f"Read {len(scan.trees)} Python modules under {root.name}. "
            f"Excluded: {_listing(scan.excluded)}. "
            f"Skipped: {_listing(scan.skipped)}. "
            f"Dynamic imports seen (not followed): {_listing(dynamic)}. "
            f"Not reachable by static reading: {NOT_REACHABLE}."
        )

    def _scan(self, root: Path) -> _Scan:
        scan = _Scan()
        self._walk(root, root.parent, scan)
        return scan

    def _walk(self, directory: Path, base: Path, scan: _Scan) -> None:
        for path in sorted(directory.iterdir()):
            rel = path.relative_to(base).as_posix()
            if path.is_symlink():
                scan.skipped.append(f"{rel} (symlink, not followed)")
            elif path.is_dir():
                if path.name == "tests":
                    scan.excluded.append(f"{rel} ({EXCLUDED_REASON})")
                elif path.name != "__pycache__" and not path.name.startswith("."):
                    self._walk(path, base, scan)
            elif path.suffix == ".py" and path.name != "__init__.py":
                self._read_file(path, rel, scan)

    def _read_file(self, path: Path, rel: str, scan: _Scan) -> None:
        if path.stat().st_size > self.max_file_bytes:
            scan.skipped.append(f"{rel} (over size limit)")
            return
        try:
            tree = ast.parse(path.read_bytes(), filename=rel)
        except (SyntaxError, ValueError):
            scan.skipped.append(f"{rel} (could not be parsed)")
            return
        scan.trees[rel.removesuffix(".py").replace("/", ".")] = (rel, tree)


def _import_targets(tree: ast.Module, name: str, modules: set[str]):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield _longest_module(alias.name, modules)
        elif isinstance(node, ast.ImportFrom):
            base = _from_base(node, name)
            for alias in node.names:
                candidate = f"{base}.{alias.name}" if base else alias.name
                yield candidate if candidate in modules else base


def _longest_module(dotted: str, modules: set[str]) -> str | None:
    parts = dotted.split(".")
    for end in range(len(parts), 0, -1):
        candidate = ".".join(parts[:end])
        if candidate in modules:
            return candidate
    return None


def _from_base(node: ast.ImportFrom, name: str) -> str:
    if not node.level:
        return node.module or ""
    parts = name.split(".")[: -node.level]
    if node.module:
        parts.append(node.module)
    return ".".join(parts)


def _calls_dynamic(tree: ast.Module) -> bool:
    return any(
        isinstance(node, ast.Call) and _called_name(node.func) in DYNAMIC_IMPORT_CALLS
        for node in ast.walk(tree)
    )


def _called_name(func: ast.expr) -> str | None:
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return None


def _listing(items: list[str]) -> str:
    return ", ".join(sorted(items)) or "none"
