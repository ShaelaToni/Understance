import pytest
from fakes import FakeFactStore

from understance.adapters.fallback_fact_store import FallbackFactStore
from understance.domain.graph import DependencyGraph, Module
from understance.ports.interfaces import DataQualityError, FactStore, FactsUnavailable

ONLINE = DependencyGraph((Module("pkg.online"),), ())
OFFLINE = DependencyGraph((Module("pkg.offline"),), ())


class _Failing(FactStore):
    """A primary store that raises the given error and counts its reads."""

    def __init__(self, error):
        self.error = error
        self.reads = 0

    def store_graph(self, graph):
        pass

    def load_graph(self):
        self.reads += 1
        raise self.error


def _holding(graph):
    store = FakeFactStore()
    store.store_graph(graph)
    return store


def test_it_plugs_into_the_fact_store_port():
    assert isinstance(FallbackFactStore(FakeFactStore(), FakeFactStore()), FactStore)


def test_a_reachable_primary_answers_and_nothing_is_logged():
    events = []
    store = FallbackFactStore(_holding(ONLINE), _holding(OFFLINE), events.append)
    assert store.load_graph() == ONLINE
    assert events == []


def test_an_unreachable_primary_falls_back_and_says_so():
    events = []
    primary = _Failing(FactsUnavailable("Zetaris did not answer"))
    store = FallbackFactStore(primary, _holding(OFFLINE), events.append)
    assert store.load_graph() == OFFLINE
    assert events == [
        {
            "agent_name": "FallbackFactStore",
            "action": "fall_back",
            "input_summary": "_Failing",
            "output_summary": "Zetaris did not answer; using FakeFactStore",
            "status": "fallback",
        }
    ]


def test_after_falling_back_the_primary_is_not_asked_again():
    primary = _Failing(FactsUnavailable("down"))
    store = FallbackFactStore(primary, _holding(OFFLINE))
    store.load_graph()
    store.load_graph()
    assert primary.reads == 1


def test_a_failed_data_quality_rule_is_never_hidden_by_the_fallback():
    store = FallbackFactStore(_Failing(DataQualityError("broken")), _holding(OFFLINE))
    with pytest.raises(DataQualityError):
        store.load_graph()


def test_storing_goes_to_the_primary():
    primary, fallback = FakeFactStore(), FakeFactStore()
    FallbackFactStore(primary, fallback).store_graph(ONLINE)
    assert (primary.graph, fallback.graph) == (ONLINE, None)
