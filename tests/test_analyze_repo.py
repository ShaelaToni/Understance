from pathlib import Path

from fakes import FakeFactStore, FakeSourceReader
from sample_app_truth import EXPECTED_DEPENDENCIES, EXPECTED_MODULES

from understance.adapters.ast_source_reader import ASTSourceReader
from understance.domain.graph import Dependency, DependencyGraph, Module
from understance.usecases.analyze_repo import AnalyzeRepo

SAMPLE_APP = Path(__file__).resolve().parent.parent / "sample_app"


def _small_graph():
    return DependencyGraph(
        modules=(Module("app.a"), Module("app.b")),
        dependencies=(Dependency("app.a", "app.b"),),
    )


def test_reads_the_root_it_is_given():
    reader = FakeSourceReader(_small_graph())
    AnalyzeRepo(reader, FakeFactStore()).run(Path("some/repo"))
    assert reader.roots_read == [Path("some/repo")]


def test_stores_and_returns_the_graph_it_read():
    store = FakeFactStore()
    graph = AnalyzeRepo(FakeSourceReader(_small_graph()), store).run(Path("repo"))
    assert graph == _small_graph()
    assert store.load_graph() == _small_graph()


def test_real_reader_on_sample_app_stores_the_hand_verified_graph():
    store = FakeFactStore()
    AnalyzeRepo(ASTSourceReader(), store).run(SAMPLE_APP)
    stored = store.load_graph()
    assert {m.name for m in stored.modules} == set(EXPECTED_MODULES)
    assert {(d.source, d.target) for d in stored.dependencies} == set(
        EXPECTED_DEPENDENCIES
    )
