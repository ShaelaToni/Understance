import pytest
from fakes import FakeFactStore

from understance.domain.graph import DependencyGraph, Module
from understance.orchestration.read_only_fact_store import ReadOnlyFactStore
from understance.ports.interfaces import FactStore


def test_reads_pass_through_to_the_real_store():
    store = FakeFactStore()
    graph = DependencyGraph((Module("a"),), ())
    store.store_graph(graph)
    facts = ReadOnlyFactStore(store)
    assert isinstance(facts, FactStore)
    assert facts.load_graph() == graph


def test_writes_are_refused_and_the_real_store_is_untouched():
    store = FakeFactStore()
    store.store_graph(DependencyGraph((Module("a"),), ()))
    with pytest.raises(PermissionError):
        ReadOnlyFactStore(store).store_graph(DependencyGraph((), ()))
    assert store.load_graph().modules == (Module("a"),)
