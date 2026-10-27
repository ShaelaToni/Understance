import io
import json
import urllib.error
from dataclasses import astuple
from pathlib import Path

import pytest
from fakes import FakeFactStore, FakeGitHistory

from understance.adapters.csv_fact_store import CsvFactStore
from understance.adapters.enriched_source_reader import EnrichedSourceReader
from understance.adapters.zetaris_fact_store import (
    ZetarisClient,
    ZetarisFactStore,
    ZetarisQueryError,
    ZetarisTables,
    ZetarisUnavailable,
)
from understance.ports.interfaces import DataQualityError, FactStore, FactsUnavailable

SAMPLE_APP = Path(__file__).resolve().parent.parent / "sample_app"
TOKEN = "test-token-not-real"
BASE = "http://zetaris.test/api/v1.0"
T = ZetarisTables()


# The Zetaris REST answers, in the shape observed on the build machine (Oct 27):
# {"records": [{column: value}], "pageNumber", "pageLimit", "totalCount",
#  "totalPages", "queryToken"}; the USL casts import_line and test_count to INT,
# and the source tables (inferSchema=false) give text, with null for empty.


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeOpener:
    """Answer each request with the next scripted reply; record every request."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.requests = []
        self.timeouts = []

    def __call__(self, request, timeout):
        self.requests.append(request)
        self.timeouts.append(timeout)
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return _Response(json.dumps(reply).encode("utf-8"))


class FakeZetarisClient:
    """Answer SELECTs from tables shaped like Zetaris rows; record every query."""

    def __init__(self, tables, broken=()):
        self.tables = tables
        self.broken = list(broken)
        self.queries = []

    def select(self, sql):
        self.queries.append(sql)
        if "IS NULL" in sql:
            return self.broken
        table = sql.split(" FROM ")[1]
        return self.tables[table]


def _page(records, page=1, pages=1, token="q1"):
    return {
        "records": records,
        "pageNumber": page,
        "pageLimit": 100,
        "totalCount": len(records),
        "totalPages": pages,
        "queryToken": token,
    }


def _http_error(code, body):
    return urllib.error.HTTPError(
        BASE, code, "error", {}, io.BytesIO(json.dumps(body).encode("utf-8"))
    )


def _client(opener):
    return ZetarisClient(BASE, "1", TOKEN, opener=opener, sleep=lambda s: None)


def _graph():
    return EnrichedSourceReader(history=FakeGitHistory()).read_graph(SAMPLE_APP)


def _zetaris_tables(graph):
    """The sample app's facts as Zetaris returns them from the USL and sources."""
    return {
        T.module: [
            {
                "module_name": m.name,
                "file": m.file,
                "last_commit": m.last_commit,
                "last_changed": m.last_changed,
                "test_count": len(m.tested_by),
            }
            for m in reversed(graph.modules)
        ],
        T.dependency: [
            {
                "source_module": d.source,
                "target_module": d.target,
                "import_file": d.file,
                "import_line": d.line,
            }
            for d in reversed(graph.dependencies)
        ],
        T.defines: [
            {"module_name": m.name, "name": n} for m in graph.modules for n in m.defines
        ],
        T.open_questions: [
            {
                "module_name": m.name,
                "file": q.file,
                "line": str(q.line),
                "symbol": q.symbol,
                "text": q.text,
            }
            for m in graph.modules
            for q in m.open_questions
        ],
        T.test_map: [
            {"module_name": m.name, "test_file": f}
            for m in graph.modules
            for f in m.tested_by
        ],
    }


def _everything(graph):
    return [astuple(m) for m in graph.modules], [astuple(d) for d in graph.dependencies]


def _store(client, events=None):
    log = events.append if events is not None else (lambda event: None)
    return ZetarisFactStore(client, FakeFactStore(), log=log)


# The client: one SELECT through the REST API.


def test_select_posts_the_query_with_the_auth_headers_and_closes_it():
    opener = FakeOpener(_page([{"module_name": "a"}]), {})
    assert _client(opener).select("SELECT module_name FROM x") == [{"module_name": "a"}]
    start, close = opener.requests
    assert (start.get_method(), start.full_url) == ("POST", BASE + "/query/sql/start")
    assert json.loads(start.data) == {
        "select": "SELECT module_name FROM x",
        "pageLimit": 100,
    }
    assert start.get_header("Authorization") == f"Bearer {TOKEN}"
    assert start.get_header("X-org-id") == "1"
    assert len(start.get_header("X-request-id")) == 36
    assert (close.get_method(), close.full_url) == (
        "DELETE",
        BASE + "/query/sql/close/q1",
    )


def test_every_page_is_read():
    opener = FakeOpener(
        _page([{"n": 1}], page=1, pages=2), _page([{"n": 2}], page=2), {}
    )
    assert _client(opener).select("SELECT n FROM x") == [{"n": 1}, {"n": 2}]
    page = opener.requests[1]
    assert page.get_method() == "GET"
    assert (
        page.full_url
        == BASE + "/query/sql/page?queryToken=q1&pageLimit=100&pageNumber=2"
    )


def test_each_request_carries_the_timeout():
    opener = FakeOpener(_page([]), {})
    ZetarisClient(BASE, "1", TOKEN, timeout=45, opener=opener).select("SELECT a FROM x")
    assert opener.timeouts == [45, 45]


def test_a_dropped_connection_is_retried_once():
    opener = FakeOpener(urllib.error.URLError("refused"), _page([{"a": 1}]), {})
    assert _client(opener).select("SELECT a FROM x") == [{"a": 1}]


def test_an_unreachable_service_is_reported_as_facts_unavailable():
    opener = FakeOpener(urllib.error.URLError("refused"), TimeoutError())
    with pytest.raises(ZetarisUnavailable) as caught:
        _client(opener).select("SELECT a FROM x")
    assert isinstance(caught.value, FactsUnavailable)
    assert "2 tries" in str(caught.value)


def test_a_server_error_is_retried_then_reported_unavailable():
    opener = FakeOpener(
        _http_error(503, {"msg": "busy"}), _http_error(503, {"msg": "busy"})
    )
    with pytest.raises(ZetarisUnavailable):
        _client(opener).select("SELECT a FROM x")
    assert len(opener.requests) == 2


def test_a_refused_query_fails_at_once_with_the_reason():
    opener = FakeOpener(_http_error(400, {"msg": "Bad Select SQL"}))
    with pytest.raises(ZetarisQueryError, match="HTTP 400: Bad Select SQL"):
        _client(opener).select("COMPILE USL x")
    assert len(opener.requests) == 1


def test_the_token_never_appears_in_an_error():
    for reply in (
        _http_error(401, {"msg": "denied"}),
        urllib.error.URLError("refused"),
    ):
        opener = FakeOpener(reply, reply)
        with pytest.raises(Exception) as caught:
            _client(opener).select("SELECT a FROM x")
        assert TOKEN not in str(caught.value)


def test_settings_come_from_the_environment_and_name_only_what_is_missing():
    client = ZetarisClient.from_env(
        {"ZETARIS_REST_URL": BASE, "ZETARIS_ORG_ID": "1", "ZETARIS_API_KEY": TOKEN}
    )
    assert isinstance(client, ZetarisClient)
    with pytest.raises(ValueError) as caught:
        ZetarisClient.from_env({"ZETARIS_REST_URL": BASE, "ZETARIS_API_KEY": TOKEN})
    assert str(caught.value) == "Zetaris settings missing: ZETARIS_ORG_ID"


# The store: the facts through Zetaris, after the data quality rule.


def test_it_plugs_into_the_fact_store_port():
    assert isinstance(_store(FakeZetarisClient({})), FactStore)


def test_facts_read_through_zetaris_match_the_offline_facts(tmp_path):
    CsvFactStore(tmp_path).store_graph(_graph())
    offline = CsvFactStore(tmp_path).load_graph()
    through_zetaris = _store(FakeZetarisClient(_zetaris_tables(_graph()))).load_graph()
    assert _everything(through_zetaris) == _everything(offline)


def test_the_data_quality_rule_runs_first_and_is_logged():
    events = []
    client = FakeZetarisClient(_zetaris_tables(_graph()))
    _store(client, events).load_graph()
    assert "IS NULL" in client.queries[0]
    assert events[0]["action"] == "data_quality"
    assert (events[0]["output_summary"], events[0]["status"]) == (
        "0 broken links",
        "passed",
    )


def test_the_rule_checks_both_ends_of_every_link():
    client = FakeZetarisClient(_zetaris_tables(_graph()))
    _store(client).load_graph()
    rule = client.queries[0]
    assert f"FROM {T.dependency} d" in rule
    assert "ON s.module_name = d.source_module" in rule
    assert "ON t.module_name = d.target_module" in rule
    assert rule.endswith("WHERE s.module_name IS NULL OR t.module_name IS NULL")


def test_a_broken_link_stops_the_read_and_names_the_link():
    events = []
    broken = [{"source_module": "pkg.a", "target_module": "pkg.gone"}]
    client = FakeZetarisClient(_zetaris_tables(_graph()), broken=broken)
    with pytest.raises(DataQualityError) as caught:
        _store(client, events).load_graph()
    assert str(caught.value) == "1 links point at no module: pkg.a -> pkg.gone"
    assert len(client.queries) == 1
    assert events[-1]["status"] == "failed"


def test_a_broken_link_is_not_a_reason_to_fall_back():
    assert not issubclass(DataQualityError, FactsUnavailable)


def test_every_query_is_logged_with_its_sql_and_row_count():
    events = []
    client = FakeZetarisClient(_zetaris_tables(_graph()))
    _store(client, events).load_graph()
    assert [e["input_summary"] for e in events] == client.queries
    assert len(events) == 6
    assert events[1]["output_summary"] == "7 rows"
    assert all(e["agent_name"] == "ZetarisFactStore" for e in events)


def test_queries_name_their_columns():
    client = FakeZetarisClient(_zetaris_tables(_graph()))
    _store(client).load_graph()
    assert not [q for q in client.queries if "*" in q]


def test_one_read_serves_the_whole_run():
    client = FakeZetarisClient(_zetaris_tables(_graph()))
    store = _store(client)
    assert store.load_graph() is store.load_graph()
    assert len(client.queries) == 6


def test_rows_missing_a_column_are_refused():
    tables = _zetaris_tables(_graph())
    for row in tables[T.module]:
        del row["last_commit"]
    with pytest.raises(ZetarisQueryError, match="lack columns: last_commit"):
        _store(FakeZetarisClient(tables)).load_graph()


def test_table_names_must_be_plain_names():
    with pytest.raises(ValueError):
        ZetarisTables(module="x.module; DROP TABLE y")


def test_storing_writes_the_export_zetaris_registers():
    export = FakeFactStore()
    graph = _graph()
    ZetarisFactStore(FakeZetarisClient({}), export).store_graph(graph)
    assert export.graph is graph
