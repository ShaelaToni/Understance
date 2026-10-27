import io
import json
import urllib.error

import pytest

from understance.adapters.nightshift_narrator import (
    NightshiftClient,
    NightshiftError,
    NightshiftNarrator,
    NightshiftReply,
    NightshiftUnavailable,
    blocked_reason,
)
from understance.adapters.template_narrator import TemplateNarrator
from understance.domain.answer import Narration
from understance.domain.finding import Evidence, Finding, FindingKind
from understance.ports.interfaces import Narrator

TOKEN = "test-token-not-real"
BASE = "http://nightshift.test/v1"
MODEL = "webllm/Qwen2.5-1.5B-Instruct-q4f16_1-MLC"


def _observed(content):
    """A Nightshift answer in the shape observed on the build machine (Oct 27),
    receipt rcpt_req_ce9imi24, trimmed to the fields Understance reads."""
    return {
        "id": "chatcmpl-pq0ghjcomvq4c7w1",
        "object": "chat.completion",
        "model": MODEL,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "meterless": {
            "receipt_id": "rcpt_req_ce9imi24",
            "requested_model": "meterless/auto",
            "routed_model": MODEL,
            "winning_route": {"model": MODEL, "provider": "webllm", "kind": "local"},
            "usage": {"input_tokens": 26, "output_tokens": 1, "latency_ms": 2284},
            "privacy": {"path": "local-only", "redaction": {"applied": False}},
            "egress": {"destination": "none"},
            "app": "understance",
            "scope": "user",
        },
        "meterless_cross_check": {
            "status": "passed",
            "recommended_action": "allow",
            "blocking": False,
        },
    }


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


def _client(*replies):
    opener = FakeOpener(*replies)
    client = NightshiftClient(BASE, TOKEN, opener=opener, sleep=lambda s: None)
    return client, opener


def _finding(summary, file, line):
    return Finding(summary, FindingKind.OBSERVED, (Evidence(file, line, line),))


FINDINGS = (
    _finding(
        "sample_app.access imports sample_app.subscriptions", "sample_app/access.py", 14
    ),
    _finding(
        "sample_app.billing imports sample_app.subscriptions",
        "sample_app/billing.py",
        4,
    ),
)
PROOF = TemplateNarrator().narrate(FINDINGS).text
GOOD = "Access control and billing both rely on subscriptions, so change it with care."


def _narrate(*replies):
    events = []
    client, opener = _client(*replies)
    narration = NightshiftNarrator(client, log=events.append).narrate(FINDINGS)
    return narration, events, opener


# The client: one chat request to the Meterless runtime.


def test_the_request_carries_the_model_the_auth_and_the_meterless_headers():
    client, opener = _client(_observed("Ready"))
    client.complete([{"role": "user", "content": "Reply with the single word: ready"}])
    (request,) = opener.requests
    assert (request.get_method(), request.full_url) == (
        "POST",
        BASE + "/chat/completions",
    )
    assert request.get_header("Authorization") == f"Bearer {TOKEN}"
    assert request.get_header("Meterless-app") == "understance"
    assert request.get_header("Meterless-scope") == "user"
    body = json.loads(request.data)
    assert (body["model"], body["max_tokens"]) == ("meterless/auto", 160)
    assert opener.timeouts == [90]


def test_the_reply_carries_the_text_and_the_receipt():
    client, _ = _client(_observed(" Ready "))
    reply = client.complete([])
    assert reply == NightshiftReply(
        text="Ready",
        receipt_id="rcpt_req_ce9imi24",
        routed_model=MODEL,
        route_kind="local",
        latency_ms=2284,
        privacy_path="local-only",
        egress="none",
        cross_check="passed",
        cross_check_blocking=False,
    )
    assert reply.receipt_line() == (
        f"receipt rcpt_req_ce9imi24, {MODEL} (local), 2284 ms, "
        "privacy local-only, egress none, cross-check passed"
    )


def test_a_dropped_connection_is_retried_once():
    client, opener = _client(urllib.error.URLError("refused"), _observed("Ready"))
    assert client.complete([]).text == "Ready"
    assert len(opener.requests) == 2


def test_a_timeout_is_not_retried():
    client, opener = _client(TimeoutError())
    with pytest.raises(NightshiftUnavailable, match="within 90 seconds"):
        client.complete([])
    assert len(opener.requests) == 1


def test_a_connect_timeout_is_not_retried_either():
    client, opener = _client(urllib.error.URLError(TimeoutError()))
    with pytest.raises(NightshiftUnavailable, match="within 90 seconds"):
        client.complete([])
    assert len(opener.requests) == 1


def test_a_refused_request_fails_at_once():
    client, opener = _client(urllib.error.HTTPError(BASE, 401, "no", {}, io.BytesIO()))
    with pytest.raises(NightshiftError, match="HTTP 401"):
        client.complete([])
    assert len(opener.requests) == 1


def test_an_answer_without_text_is_refused():
    client, _ = _client({"meterless": {}})
    with pytest.raises(NightshiftError):
        client.complete([])


def test_the_token_never_appears_in_an_error():
    for reply in (
        urllib.error.HTTPError(BASE, 401, "no", {}, io.BytesIO()),
        urllib.error.URLError("refused"),
    ):
        client, _ = _client(reply, reply)
        with pytest.raises(Exception) as caught:
            client.complete([])
        assert TOKEN not in str(caught.value)


def test_settings_come_from_the_environment_and_name_only_what_is_missing():
    client = NightshiftClient.from_env(
        {"METERLESS_BASE_URL": BASE, "METERLESS_RUNTIME_TOKEN": TOKEN}
    )
    assert client.model == "meterless/auto"
    with pytest.raises(ValueError) as caught:
        NightshiftClient.from_env({"METERLESS_BASE_URL": BASE})
    assert str(caught.value) == "Nightshift settings missing: METERLESS_RUNTIME_TOKEN"


# The narrator: the model writes a short summary; the proof stays deterministic.


def test_it_plugs_into_the_narrator_port():
    client, _ = _client()
    assert isinstance(NightshiftNarrator(client), Narrator)


def test_the_model_writes_the_summary_and_the_proof_lines_follow():
    narration, events, _ = _narrate(_observed(GOOD))
    assert narration == Narration(
        "In plain words (written by the model; the proof below is from the code): "
        f"{GOOD}\n{PROOF}",
        MODEL,
    )
    assert events[0]["status"] == "ok"
    assert events[0]["model"] == MODEL
    assert events[0]["output_summary"].startswith("receipt rcpt_req_ce9imi24")


def test_the_model_sees_link_summaries_only_never_files_or_lines():
    _, _, opener = _narrate(_observed(GOOD))
    sent = json.dumps(json.loads(opener.requests[0].data)["messages"])
    assert "sample_app.access imports sample_app.subscriptions" in sent
    assert ".py" not in sent
    assert not any(ch.isdigit() for ch in sent)


def test_the_observed_distortion_is_blocked_and_the_proof_stands_alone():
    wrong = "The billing module is located at sample_app/api.py, line 4."
    narration, events, _ = _narrate(_observed(wrong))
    assert narration == Narration(PROOF, "template (no model)")
    assert events[0]["status"] == "blocked"
    assert events[0]["output_summary"].startswith(
        "model claim blocked (it states a file path); receipt rcpt_req_ce9imi24"
    )


def test_an_unreachable_nightshift_falls_back_to_the_template():
    narration, events, _ = _narrate(
        urllib.error.URLError("refused"), urllib.error.URLError("refused")
    )
    assert narration == Narration(PROOF, "template (no model)")
    assert events[0]["status"] == "fallback"
    assert events[0]["model"] is None


def test_no_findings_means_no_model_call():
    client, opener = _client()
    narration = NightshiftNarrator(client).narrate(())
    assert narration == TemplateNarrator().narrate(())
    assert opener.requests == []


# The guard: what the model may never say.


def _reply(text, cross_check="passed", blocking=False):
    return NightshiftReply(
        text, "r", MODEL, "local", 1, "local-only", "none", cross_check, blocking
    )


ALLOWED = {"sample_app.access", "sample_app.subscriptions"}


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        (GOOD, None),
        ("sample_app.access relies on sample_app.subscriptions.", None),
        ("", "empty text"),
        ("x" * 501, "longer than a short summary"),
        ("See access.py for the details.", "it states a file path"),
        ("It sits in the sample_app/billing folder.", "it states a file path"),
        (
            "Access imports it on line seven or line 14.",
            "it states a number, such as a line",
        ),
        ("Four modules, 4 links.", "it states a number, such as a line"),
        (
            "sample_app.payments also depends on it.",
            "it names modules outside the verified links: sample_app.payments",
        ),
    ],
)
def test_the_guard_blocks_what_the_model_must_never_state(text, reason):
    assert blocked_reason(_reply(text), ALLOWED) == reason


def test_the_guard_honors_the_meterless_cross_check():
    flagged = "the Meterless cross-check flagged it"
    assert blocked_reason(_reply(GOOD, cross_check="failed"), ALLOWED) == flagged
    assert blocked_reason(_reply(GOOD, blocking=True), ALLOWED) == flagged
