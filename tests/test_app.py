import io
import json
import urllib.error
from pathlib import Path

import pytest

from understance.adapters.nightshift_narrator import NightshiftClient
from understance.adapters.zetaris_fact_store import ZetarisClient
from understance.orchestration.orchestrator import TRACE_FIELDS
from understance.shell.app import App, load_settings

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = {"SAMPLE_MODE": "true"}
CANCEL = "Add customer cancellation"
DECISION = {"answer": "at the end of the billing period", "decided_by": "Shaela"}


def _app(tmp_path, env=SAMPLE, **options):
    ids = iter(f"run-{n}" for n in range(1, 10))
    return App(
        env,
        ROOT,
        logs=tmp_path,
        clock=lambda: "2026-10-27T16:00:00Z",
        run_id=lambda: next(ids),
        echo=lambda line: None,
        **options,
    )


def _trace(tmp_path, run_id):
    path = tmp_path / f"trace-{run_id}.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


# Settings and modes.


def test_sample_mode_set_in_the_environment_never_reads_the_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("ZETARIS_API_KEY=must-not-be-read\n", encoding="utf-8")
    assert "ZETARIS_API_KEY" not in load_settings(SAMPLE, env_file)
    live = load_settings({}, env_file)
    assert live["ZETARIS_API_KEY"] == "must-not-be-read"
    assert load_settings({"ZETARIS_API_KEY": "from-env"}, env_file)[
        "ZETARIS_API_KEY"
    ] == ("from-env")


def test_live_mode_without_settings_names_what_is_missing(tmp_path):
    with pytest.raises(ValueError, match="Zetaris settings missing"):
        _app(tmp_path, env={})


# One request, answered from the facts.


def test_a_question_is_answered_with_the_proof_and_a_trace(tmp_path):
    code, body = _app(tmp_path).handle(
        {"question": "What would changing billing affect?"}
    )
    assert code == 200
    assert (body["run_id"], body["mode"], body["status"]) == (
        "run-1",
        "sample",
        "answered",
    )
    assert body["target"] == "sample_app.billing"
    assert body["affected"] == ["sample_app.api", "sample_app.main"]
    assert body["findings"][0] == {
        "summary": "sample_app.api imports sample_app.billing",
        "file": "sample_app/api.py",
        "line": 4,
    }
    assert body["model"] == "template (no model)"
    assert body["trace_file"] == "trace-run-1.jsonl"
    records = _trace(tmp_path, "run-1")
    assert all(list(r) == list(TRACE_FIELDS) for r in records)
    assert {r["run_id"] for r in records} == {"run-1"}


def test_an_open_decision_is_asked_then_recorded_then_remembered(tmp_path):
    app = _app(tmp_path)
    code, first = app.handle({"question": CANCEL})
    assert (code, first["status"]) == (200, "needs_decision")
    assert first["open_questions"][0]["line"] == 16
    code, second = app.handle({"question": CANCEL, "decision": DECISION})
    assert (code, second["status"]) == (200, "answered")
    assert second["decisions"] == [
        {
            "file": "sample_app/subscriptions.py",
            "line": 16,
            "answer": "at the end of the billing period",
            "decided_by": "Shaela",
            "decided_at": "2026-10-27T16:00:00Z",
        }
    ]
    assert ("Owner", "record_decision", "recorded") in [
        (r["agent_name"], r["action"], r["status"]) for r in _trace(tmp_path, "run-2")
    ]
    code, third = _app(tmp_path).handle({"question": CANCEL})
    assert (code, third["status"]) == (200, "answered")
    assert "not asking again" in third["answer"]
    assert (tmp_path / "memory" / "sample_app.jsonl").exists()


def test_a_decision_with_nothing_to_decide_is_refused(tmp_path):
    request = {"question": "What would changing billing affect?", "decision": DECISION}
    code, body = _app(tmp_path).handle(request)
    assert (code, body["error"]["type"]) == (409, "nothing_to_decide")
    assert not (tmp_path / "memory" / "sample_app.jsonl").exists()


@pytest.mark.parametrize(
    "request_body",
    [
        None,
        [],
        {},
        {"question": "   "},
        {"question": "x" * 501},
        {"question": CANCEL, "decision": "now"},
        {"question": CANCEL, "decision": {"answer": "now"}},
        {"question": CANCEL, "decision": {"answer": "", "decided_by": "Shaela"}},
    ],
)
def test_bad_requests_get_a_structured_error(tmp_path, request_body):
    code, body = _app(tmp_path).handle(request_body)
    assert code == 400
    assert body["error"]["type"] == "bad_request"


# Live mode, with the sponsors simulated at the HTTP edge.


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _down(request, timeout):
    raise urllib.error.URLError("refused")


def _nightshift(request, timeout):
    body = {
        "model": "webllm/Qwen",
        "choices": [{"message": {"content": "Several modules lean on billing."}}],
        "meterless": {"receipt_id": "rcpt_test", "routed_model": "webllm/Qwen"},
        "meterless_cross_check": {"status": "passed", "blocking": False},
    }
    return _Response(json.dumps(body).encode("utf-8"))


def _live(tmp_path, nightshift_opener):
    zetaris = ZetarisClient(
        "http://z.test", "1", "k", opener=_down, sleep=lambda s: None
    )
    nightshift = NightshiftClient("http://n.test/v1", "k", opener=nightshift_opener)
    return _app(tmp_path, env={}, clients=(zetaris, nightshift))


def test_live_mode_falls_back_to_the_facts_and_narrates_through_nightshift(tmp_path):
    code, body = _live(tmp_path, _nightshift).handle(
        {"question": "What would changing billing affect?"}
    )
    assert (code, body["mode"], body["status"]) == (200, "live", "answered")
    assert body["model"] == "webllm/Qwen"
    assert "Several modules lean on billing." in body["answer"]
    records = _trace(tmp_path, "run-1")
    assert all(list(r) == list(TRACE_FIELDS) for r in records)
    steps = [(r["agent_name"], r["status"]) for r in records]
    assert ("FallbackFactStore", "fallback") in steps
    assert ("NightshiftNarrator", "ok") in steps


def test_an_unexpected_failure_is_a_structured_error(tmp_path):
    def broken(request, timeout):
        raise RuntimeError("boom")

    code, body = _live(tmp_path, broken).handle(
        {"question": "What would changing billing affect?"}
    )
    assert (code, body["error"]["type"]) == (500, "internal")
    assert body["run_id"] == "run-1"
    assert "boom" not in json.dumps(body)


def test_broken_facts_in_zetaris_stop_the_run_with_a_data_quality_error(tmp_path):
    def broken_links(request, timeout):
        if request.get_method() == "DELETE":
            return _Response(b"{}")
        page = {
            "records": [{"source_module": "sample_app.api", "target_module": "gone"}],
            "pageNumber": 1,
            "totalPages": 1,
            "queryToken": "q1",
        }
        return _Response(json.dumps(page).encode("utf-8"))

    zetaris = ZetarisClient("http://z.test", "1", "k", opener=broken_links)
    nightshift = NightshiftClient("http://n.test/v1", "k", opener=_nightshift)
    app = _app(tmp_path, env={}, clients=(zetaris, nightshift))
    code, body = app.handle({"question": "What would changing billing affect?"})
    assert (code, body["error"]["type"]) == (422, "data_quality")
    assert "sample_app.api -> gone" in body["error"]["message"]
