import pytest

from understance.domain.graph import DependencyGraph
from understance.ports.interfaces import FactStore, MemoryStore, Narrator, SourceReader


class _FakeSourceReader(SourceReader):
    def read_graph(self, root):
        return DependencyGraph(modules=(), dependencies=())


class _FakeFactStore(FactStore):
    def store_graph(self, graph):
        self._graph = graph

    def load_graph(self):
        return DependencyGraph(modules=(), dependencies=())


class _FakeNarrator(Narrator):
    def narrate(self, findings):
        return "explanation"


class _FakeMemoryStore(MemoryStore):
    def save_finding(self, finding):
        self._finding = finding

    def load_findings(self):
        return ()


def test_complete_source_reader_instantiates():
    assert isinstance(_FakeSourceReader(), SourceReader)


def test_complete_fact_store_instantiates():
    assert isinstance(_FakeFactStore(), FactStore)


def test_complete_narrator_instantiates():
    assert isinstance(_FakeNarrator(), Narrator)


def test_complete_memory_store_instantiates():
    assert isinstance(_FakeMemoryStore(), MemoryStore)


def test_incomplete_source_reader_cannot_instantiate():
    class _Missing(SourceReader):
        pass

    with pytest.raises(TypeError):
        _Missing()


def test_incomplete_fact_store_cannot_instantiate():
    class _Missing(FactStore):
        def store_graph(self, graph):
            pass

    with pytest.raises(TypeError):
        _Missing()


def test_incomplete_narrator_cannot_instantiate():
    class _Missing(Narrator):
        pass

    with pytest.raises(TypeError):
        _Missing()


def test_incomplete_memory_store_cannot_instantiate():
    class _Missing(MemoryStore):
        def save_finding(self, finding):
            pass

    with pytest.raises(TypeError):
        _Missing()
