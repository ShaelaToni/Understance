from pathlib import Path

from fakes import FakeGitHistory
from sample_app_truth import EXPECTED_DEPENDENCIES

from understance.adapters.enriched_source_reader import EnrichedSourceReader
from understance.ports.interfaces import SourceReader

SAMPLE_APP = Path(__file__).resolve().parent.parent / "sample_app"


def test_it_plugs_into_the_source_reader_port():
    assert isinstance(EnrichedSourceReader(), SourceReader)


def test_modules_gain_their_file_last_change_and_tests():
    graph = EnrichedSourceReader(history=FakeGitHistory()).read_graph(SAMPLE_APP)
    modules = {m.name: m for m in graph.modules}
    access = modules["sample_app.access"]
    assert access.file == "sample_app/access.py"
    assert (access.last_commit, access.last_changed) == (
        "abc1234",
        "2026-10-27T05:00:00Z",
    )
    assert access.tested_by == ("sample_app/tests/test_access.py",)
    assert modules["sample_app.notifications"].tested_by == ()


def test_the_import_map_is_unchanged():
    graph = EnrichedSourceReader(history=FakeGitHistory()).read_graph(SAMPLE_APP)
    assert {(d.source, d.target) for d in graph.dependencies} == set(
        EXPECTED_DEPENDENCIES
    )
