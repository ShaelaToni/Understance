import csv
from pathlib import Path

from understance.domain.graph import Dependency, DependencyGraph, Module, OpenQuestion
from understance.ports.interfaces import FactStore

TABLES = {
    "modules.csv": ("module_name", "file"),
    "dependencies.csv": ("source", "target", "file", "line"),
    "defines.csv": ("module_name", "name"),
    "open_questions.csv": ("module_name", "file", "line", "symbol", "text"),
    "git_history.csv": ("file", "last_commit", "last_changed"),
    "test_map.csv": ("module_name", "test_file"),
}


class CsvFactStore(FactStore):
    """Keep the facts as six CSV files: code facts, git history and the test map."""

    def __init__(self, folder: Path):
        self.folder = Path(folder)

    def store_graph(self, graph: DependencyGraph) -> None:
        self.folder.mkdir(parents=True, exist_ok=True)
        for name, rows in _rows(graph).items():
            with (self.folder / name).open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, lineterminator="\n")
                writer.writerow(TABLES[name])
                writer.writerows(sorted(rows, key=_as_strings))

    def load_graph(self) -> DependencyGraph:
        return graph_from_tables({name: self._read(name) for name in TABLES})

    def _read(self, name: str) -> list[dict[str, str]]:
        with (self.folder / name).open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))


def graph_from_tables(t: dict[str, list[dict[str, str]]]) -> DependencyGraph:
    """Build the graph from rows shaped like TABLES (text values, "" when empty)."""
    history = {r["file"]: r for r in t["git_history.csv"]}
    modules = tuple(
        Module(
            r["module_name"],
            _defines(t["defines.csv"], r["module_name"]),
            _questions(t["open_questions.csv"], r["module_name"]),
            file=_none(r["file"]),
            last_commit=_none(history.get(r["file"], {}).get("last_commit", "")),
            last_changed=_none(history.get(r["file"], {}).get("last_changed", "")),
            tested_by=_tested_by(t["test_map.csv"], r["module_name"]),
        )
        for r in t["modules.csv"]
    )
    dependencies = tuple(
        Dependency(r["source"], r["target"], _int(r["line"]), _none(r["file"]))
        for r in t["dependencies.csv"]
    )
    return DependencyGraph(modules, dependencies)


def _rows(graph: DependencyGraph) -> dict[str, list[tuple]]:
    ms = graph.modules
    return {
        "modules.csv": [(m.name, m.file) for m in ms],
        "dependencies.csv": [
            (d.source, d.target, d.file, d.line) for d in graph.dependencies
        ],
        "defines.csv": [(m.name, n) for m in ms for n in m.defines],
        "open_questions.csv": [
            (m.name, q.file, q.line, q.symbol, q.text)
            for m in ms
            for q in m.open_questions
        ],
        "git_history.csv": [
            (m.file, m.last_commit, m.last_changed) for m in ms if m.last_commit
        ],
        "test_map.csv": [(m.name, f) for m in ms for f in m.tested_by],
    }


def _as_strings(row: tuple) -> tuple[str, ...]:
    return tuple("" if v is None else str(v) for v in row)


def _none(value: str) -> str | None:
    return value or None


def _int(value: str) -> int | None:
    return int(value) if value else None


def _defines(rows, module: str) -> tuple[str, ...]:
    return tuple(sorted(r["name"] for r in rows if r["module_name"] == module))


def _questions(rows, module: str) -> tuple[OpenQuestion, ...]:
    found = [
        OpenQuestion(r["file"], int(r["line"]), r["text"], _none(r["symbol"]))
        for r in rows
        if r["module_name"] == module
    ]
    return tuple(sorted(found, key=lambda q: q.line))


def _tested_by(rows, module: str) -> tuple[str, ...]:
    return tuple(sorted(r["test_file"] for r in rows if r["module_name"] == module))
