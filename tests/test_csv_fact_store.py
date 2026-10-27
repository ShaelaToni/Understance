import csv
from dataclasses import astuple
from pathlib import Path

from fakes import FakeGitHistory

from understance.adapters.csv_fact_store import TABLES, CsvFactStore
from understance.adapters.enriched_source_reader import EnrichedSourceReader
from understance.ports.interfaces import FactStore

REPO = Path(__file__).resolve().parent.parent
SAMPLE_APP = REPO / "sample_app"
CODE_TABLES = (
    "modules.csv",
    "dependencies.csv",
    "defines.csv",
    "open_questions.csv",
    "test_map.csv",
)


def _graph():
    return EnrichedSourceReader(history=FakeGitHistory()).read_graph(SAMPLE_APP)


def _everything(graph):
    modules = [astuple(m) for m in graph.modules]
    dependencies = [astuple(d) for d in graph.dependencies]
    return modules, dependencies


def test_it_plugs_into_the_fact_store_port(tmp_path):
    assert isinstance(CsvFactStore(tmp_path), FactStore)


def test_every_fact_survives_a_round_trip(tmp_path):
    store = CsvFactStore(tmp_path)
    store.store_graph(_graph())
    assert _everything(store.load_graph()) == _everything(_graph())


def test_each_table_is_a_csv_file_with_its_header(tmp_path):
    CsvFactStore(tmp_path).store_graph(_graph())
    for name, header in TABLES.items():
        with (tmp_path / name).open(newline="", encoding="utf-8") as f:
            assert tuple(next(csv.reader(f))) == header


def test_the_committed_facts_match_a_fresh_export(tmp_path):
    CsvFactStore(tmp_path).store_graph(_graph())
    for name in CODE_TABLES:
        fresh = (tmp_path / name).read_text(encoding="utf-8")
        assert (REPO / "facts" / name).read_text(encoding="utf-8") == fresh, name
    with (REPO / "facts" / "git_history.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    modules_files = {m.file for m in _graph().modules}
    assert {r["file"] for r in rows} <= modules_files
