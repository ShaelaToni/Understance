from pathlib import Path

import pytest
from fakes import FakeFactStore
from sample_app_truth import EXPECTED_BLAST_RADIUS

from understance.adapters.ast_source_reader import ASTSourceReader
from understance.domain.finding import Evidence, FindingKind
from understance.domain.graph import Dependency, DependencyGraph, Module
from understance.usecases.analyze_repo import AnalyzeRepo
from understance.usecases.compute_blast_radius import ComputeBlastRadius

SAMPLE_APP = Path(__file__).resolve().parent.parent / "sample_app"


def _sample_store():
    store = FakeFactStore()
    AnalyzeRepo(ASTSourceReader(), store).run(SAMPLE_APP)
    return store


def test_sample_app_blast_radius_matches_the_hand_trace():
    store = _sample_store()
    for target, expected in EXPECTED_BLAST_RADIUS.items():
        radius = ComputeBlastRadius(store).run(target)
        assert radius.target == target
        assert radius.dependents == expected["dependents"]
        assert radius.dependencies == expected["dependencies"]


def test_every_edge_into_the_blast_radius_is_an_observed_finding_with_file_and_line():
    radius = ComputeBlastRadius(_sample_store()).run("sample_app.subscriptions")
    assert [f.summary for f in radius.findings] == [
        "sample_app.access imports sample_app.subscriptions",
        "sample_app.api imports sample_app.access",
        "sample_app.api imports sample_app.billing",
        "sample_app.api imports sample_app.notifications",
        "sample_app.api imports sample_app.subscriptions",
        "sample_app.billing imports sample_app.subscriptions",
        "sample_app.main imports sample_app.api",
        "sample_app.notifications imports sample_app.subscriptions",
    ]
    assert all(f.kind is FindingKind.OBSERVED for f in radius.findings)
    assert radius.findings[0].evidence == (Evidence("sample_app/access.py", 14, 14),)


def test_unknown_target_is_refused_not_guessed():
    with pytest.raises(ValueError):
        ComputeBlastRadius(_sample_store()).run("sample_app.payments")


def test_works_from_stored_facts_alone():
    store = FakeFactStore()
    store.store_graph(
        DependencyGraph(
            modules=(Module("a"), Module("b")),
            dependencies=(
                Dependency("a", "b", 2, "pkg/a.py"),
                Dependency("b", "a", 5, "pkg/b.py"),
            ),
        )
    )
    radius = ComputeBlastRadius(store).run("b")
    assert radius.dependents == ("a",)
    assert radius.dependencies == ("a",)
    assert [f.evidence for f in radius.findings] == [(Evidence("pkg/a.py", 2, 2),)]


def test_an_edge_without_a_recorded_location_yields_no_finding():
    store = FakeFactStore()
    store.store_graph(
        DependencyGraph(
            modules=(Module("a"), Module("b")),
            dependencies=(Dependency("a", "b"),),
        )
    )
    radius = ComputeBlastRadius(store).run("b")
    assert radius.dependents == ("a",)
    assert radius.findings == ()
