import ast
from pathlib import Path

from understance.adapters.ast_source_reader import import_targets


class ModuleTests:
    """Link each module to the test files that import it (parsed, never run)."""

    def map(self, root: Path, modules: set[str]) -> dict[str, tuple[str, ...]]:
        tests = root / "tests"
        if not tests.is_dir() or tests.is_symlink():
            return {}
        linked: dict[str, set[str]] = {}
        for path in sorted(tests.rglob("test_*.py")):
            if path.is_symlink():
                continue
            rel = path.relative_to(root.parent).as_posix()
            try:
                tree = ast.parse(path.read_bytes(), filename=rel)
            except (SyntaxError, ValueError):
                continue
            name = rel.removesuffix(".py").replace("/", ".")
            for target, _ in import_targets(tree, name, modules):
                if target in modules:
                    linked.setdefault(target, set()).add(rel)
        return {m: tuple(sorted(linked[m])) for m in sorted(linked)}
