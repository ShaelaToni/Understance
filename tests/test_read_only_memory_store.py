import pytest

from understance.domain.answer import Decision
from understance.domain.graph import OpenQuestion
from understance.orchestration.read_only_memory_store import ReadOnlyMemoryStore
from understance.ports.interfaces import MemoryStore

QUESTION = OpenQuestion("app/subs.py", 16, "immediately or at period end?", "cancel")
DECISION = Decision(QUESTION, "at period end", "Shaela", "2026-10-27T16:00:00Z")


class _Memory(MemoryStore):
    def __init__(self):
        self.recorded = []

    def record_decision(self, decision):
        self.recorded.append(decision)

    def decision_for(self, question):
        return DECISION if question == QUESTION else None


def test_agents_recall_through_it():
    memory = ReadOnlyMemoryStore(_Memory())
    assert memory.decision_for(QUESTION) == DECISION
    assert memory.decision_for(OpenQuestion("x.py", 1, "other?")) is None


def test_it_refuses_every_write():
    inner = _Memory()
    with pytest.raises(PermissionError):
        ReadOnlyMemoryStore(inner).record_decision(DECISION)
    assert inner.recorded == []
