from pathlib import Path

from understance.domain.graph import DependencyGraph
from understance.ports.interfaces import FactStore, SourceReader


class FakeSourceReader(SourceReader):
    """Return a fixed graph and record which roots were read."""

    def __init__(self, graph: DependencyGraph):
        self.graph = graph
        self.roots_read: list[Path] = []

    def read_graph(self, root: Path) -> DependencyGraph:
        self.roots_read.append(root)
        return self.graph


class FakeFactStore(FactStore):
    """Keep the stored graph in memory."""

    def __init__(self):
        self.graph: DependencyGraph | None = None

    def store_graph(self, graph: DependencyGraph) -> None:
        self.graph = graph

    def load_graph(self) -> DependencyGraph:
        if self.graph is None:
            raise LookupError("no graph has been stored")
        return self.graph
