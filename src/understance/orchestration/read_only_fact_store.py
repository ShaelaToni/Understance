from understance.domain.graph import DependencyGraph
from understance.ports.interfaces import FactStore


class ReadOnlyFactStore(FactStore):
    """Hand agents the facts to read; refuse every write."""

    def __init__(self, store: FactStore):
        self._store = store

    def store_graph(self, graph: DependencyGraph) -> None:
        raise PermissionError("agents read facts; they never write them")

    def load_graph(self) -> DependencyGraph:
        return self._store.load_graph()
