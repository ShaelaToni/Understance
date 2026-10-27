from pathlib import Path

from understance.domain.graph import DependencyGraph
from understance.ports.interfaces import FactStore, SourceReader


class AnalyzeRepo:
    """Read a repo's dependency graph and store it as facts."""

    def __init__(self, reader: SourceReader, store: FactStore):
        self.reader = reader
        self.store = store

    def run(self, root: Path) -> DependencyGraph:
        graph = self.reader.read_graph(root)
        self.store.store_graph(graph)
        return graph
