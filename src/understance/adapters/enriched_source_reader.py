from dataclasses import replace
from pathlib import Path

from understance.adapters.ast_source_reader import ASTSourceReader
from understance.adapters.git_history import GitHistory
from understance.adapters.module_tests import ModuleTests
from understance.domain.graph import DependencyGraph
from understance.ports.interfaces import SourceReader


class EnrichedSourceReader(SourceReader):
    """The import map plus each module's last change and the tests that cover it."""

    def __init__(
        self,
        reader: SourceReader | None = None,
        history: GitHistory | None = None,
        tests: ModuleTests | None = None,
    ):
        self.reader = reader or ASTSourceReader()
        self.history = history or GitHistory()
        self.tests = tests or ModuleTests()

    def read_graph(self, root: Path) -> DependencyGraph:
        graph = self.reader.read_graph(root)
        files = [m.file for m in graph.modules if m.file]
        changes = self.history.last_changes(root.parent, files)
        tested = self.tests.map(root, {m.name for m in graph.modules})
        modules = []
        for m in graph.modules:
            commit, date = changes.get(m.file, (None, None))
            modules.append(
                replace(
                    m,
                    last_commit=commit,
                    last_changed=date,
                    tested_by=tested.get(m.name, ()),
                )
            )
        return DependencyGraph(tuple(modules), graph.dependencies)
