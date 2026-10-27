from understance.domain.answer import Decision
from understance.domain.graph import OpenQuestion
from understance.ports.interfaces import MemoryStore


class ReadOnlyMemoryStore(MemoryStore):
    """Let agents recall the owner's decisions; only the owner records them."""

    def __init__(self, memory: MemoryStore):
        self._memory = memory

    def record_decision(self, decision: Decision) -> None:
        raise PermissionError("agents recall decisions; only the owner records them")

    def decision_for(self, question: OpenQuestion) -> Decision | None:
        return self._memory.decision_for(question)
