import ast
import io
import tokenize
from dataclasses import dataclass, field
from pathlib import Path

from understance.domain.graph import Dependency, DependencyGraph, Module, OpenQuestion
from understance.ports.interfaces import SourceReader

EXCLUDED_REASON = "test evidence, not graph modules"
NOT_REACHABLE = "dynamic imports, reflection, generated code, other languages"
DYNAMIC_IMPORT_CALLS = {"import_module", "__import__"}
OPEN_QUESTION_MARK = "AMBIGUOUS:"
MAX_QUESTION_CHARS = 300
DEFINITIONS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


@dataclass
class _Scan:
    trees: dict[str, tuple[str, ast.Module]] = field(default_factory=dict)
    excluded: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    questions: dict[str, tuple[OpenQuestion, ...]] = field(default_factory=dict)


class ASTSourceReader(SourceReader):
    """Parse every .py file under root with ast; never import or run subject code."""

    def __init__(self, max_file_bytes: int = 1_000_000):
        self.max_file_bytes = max_file_bytes

    def read_graph(self, root: Path) -> DependencyGraph:
        scan = self._scan(root)
        names = set(scan.trees)
        lines: dict[tuple[str, str], int] = {}
        for name, (_, tree) in scan.trees.items():
            for target, line in _import_targets(tree, name, names):
                if target in names and target != name:
                    lines[(name, target)] = min(line, lines.get((name, target), line))
        return DependencyGraph(
            modules=tuple(
                Module(n, _defines(scan.trees[n][1]), scan.questions.get(n, ()))
                for n in sorted(names)
            ),
            dependencies=tuple(
                Dependency(source, target, line, scan.trees[source][0])
                for (source, target), line in sorted(lines.items())
            ),
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
        if not path.stem.isidentifier():
            scan.skipped.append(f"{rel} (not an importable module name)")
            return
        if path.stat().st_size > self.max_file_bytes:
            scan.skipped.append(f"{rel} (over size limit)")
            return
        source = path.read_bytes()
        try:
            tree = ast.parse(source, filename=rel)
        except (SyntaxError, ValueError):
            scan.skipped.append(f"{rel} (could not be parsed)")
            return
        name = rel.removesuffix(".py").replace("/", ".")
        scan.trees[name] = (rel, tree)
        scan.questions[name] = _open_questions(source, rel, tree)


def _import_targets(tree: ast.Module, name: str, modules: set[str]):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield _longest_module(alias.name, modules), node.lineno
        elif isinstance(node, ast.ImportFrom):
            base = _from_base(node, name)
            for alias in node.names:
                candidate = f"{base}.{alias.name}" if base else alias.name
                yield (candidate if candidate in modules else base), node.lineno


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


def _defines(tree: ast.Module) -> tuple[str, ...]:
    return tuple(sorted(n.name for n in tree.body if isinstance(n, DEFINITIONS)))


def _open_questions(
    source: bytes, rel: str, tree: ast.Module
) -> tuple[OpenQuestion, ...]:
    groups: list[tuple[int, list[str]]] = []
    last = 0
    for line, text, whole_line in _comments(source):
        if text.startswith(OPEN_QUESTION_MARK):
            groups.append((line, [text.removeprefix(OPEN_QUESTION_MARK)]))
            last = line
        elif groups and whole_line and line == last + 1:
            groups[-1][1].append(text)
            last = line
    return tuple(
        OpenQuestion(rel, line, _question_text(parts), _enclosing(tree, line))
        for line, parts in groups
    )


def _comments(source: bytes) -> list[tuple[int, str, bool]]:
    try:
        tokens = list(tokenize.tokenize(io.BytesIO(source).readline))
    except (tokenize.TokenError, SyntaxError):
        return []
    return [
        (t.start[0], t.string.lstrip("#").strip(), t.line.lstrip().startswith("#"))
        for t in tokens
        if t.type == tokenize.COMMENT
    ]


def _question_text(parts: list[str]) -> str:
    cleaned = ("".join(c for c in part if c.isprintable()).strip() for part in parts)
    return " ".join(part for part in cleaned if part)[:MAX_QUESTION_CHARS]


def _enclosing(tree: ast.Module, line: int) -> str | None:
    return next(
        (
            n.name
            for n in tree.body
            if isinstance(n, DEFINITIONS) and n.lineno <= line <= n.end_lineno
        ),
        None,
    )
