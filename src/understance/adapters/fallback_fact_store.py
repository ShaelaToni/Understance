from collections.abc import Callable

from understance.domain.graph import DependencyGraph
from understance.ports.interfaces import FactStore, FactsUnavailable


class FallbackFactStore(FactStore):
    """Read from the primary store; if it is unreachable, use the offline one."""

    def __init__(
        self,
        primary: FactStore,
        fallback: FactStore,
        log: Callable[[dict], None] = lambda event: None,
    ):
        self._primary = primary
        self._fallback = fallback
        self._log = log
        self._using_fallback = False

    def store_graph(self, graph: DependencyGraph) -> None:
        self._primary.store_graph(graph)

    def load_graph(self) -> DependencyGraph:
        if not self._using_fallback:
            try:
                return self._primary.load_graph()
            except FactsUnavailable as e:
                self._using_fallback = True
                self._log(
                    {
                        "agent_name": "FallbackFactStore",
                        "action": "fall_back",
                        "input_summary": type(self._primary).__name__,
                        "output_summary": f"{e}; using {type(self._fallback).__name__}",
                        "status": "fallback",
                    }
                )
        return self._fallback.load_graph()
