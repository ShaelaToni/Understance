import json

import pytest

from understance.adapters.hmem_memory import HMem, HMemMemoryStore
from understance.domain.answer import Decision
from understance.domain.graph import OpenQuestion
from understance.ports.interfaces import MemoryStore

T0 = 1750000000000
DAY = 24 * 60 * 60 * 1000
QUESTION = OpenQuestion(
    "sample_app/subscriptions.py",
    16,
    "does cancellation take effect immediately, or at the end of the period?",
    "cancel_subscription",
)


def _engine(now=T0):
    return HMem(lambda: now)


# A pytest port of the core cases of the Meterless H-MEM conformance suite
# (engines/hmem/conformance/vectors/vectors.json, version 1): record
# validation, feedback deltas, ranking order, the conflict gate and the ledger
# audit. Sleep and dreaming are not implemented here, so their cases are not
# ported.


@pytest.mark.parametrize(
    ("case", "source", "accepted"),
    [("rv-001", "", False), ("rv-002", "test", True)],
)
def test_record_validation(case, source, accepted):
    engine = _engine()
    if accepted:
        assert engine.add("valid record", source=source).source == source
    else:
        with pytest.raises(ValueError):
            engine.add("no source here", source=source)


@pytest.mark.parametrize(
    ("case", "start", "kind", "confidence", "access_delta", "tag"),
    [
        ("fd-001", 0.7, "helpful", 0.75, 1, None),
        ("fd-002", 0.7, "not_helpful", 0.67, 0, None),
        ("fd-003", 0.7, "wrong", 0.5, 0, "review"),
        ("fd-004", 0.1, "wrong", 0.0, 0, None),
        ("fd-005", 0.98, "helpful", 1.0, 1, None),
    ],
)
def test_feedback_deltas(case, start, kind, confidence, access_delta, tag):
    engine = _engine()
    record = engine.add(
        "feedback target record", source="conformance", confidence=start
    )
    after = engine.feedback(record.id, kind)
    assert after.confidence == pytest.approx(confidence, abs=1e-9)
    assert after.access_count - record.access_count == access_delta
    if tag:
        assert tag in after.tags


def test_ranking_order_ro_001_a_superseded_record_ranks_below_a_fresh_one():
    engine = _engine()
    fresh = engine.add(
        "we deploy the api with docker on mondays",
        source="conformance",
        confidence=0.9,
        layer="long_term",
    )
    old = engine.add(
        "we deploy the api with docker on fridays",
        source="conformance",
        confidence=0.9,
        layer="long_term",
    )
    engine.supersede(old.id, fresh.id)
    order = [
        r.id for r, _ in engine.query("when do we deploy the api with docker", 0, 10)
    ]
    assert order.index(fresh.id) < order.index(old.id)


def test_ranking_order_ro_002_confidence_multiplies_the_whole_score():
    engine = _engine()
    high = engine.add(
        "the deploy window is monday morning", source="conformance", confidence=0.9
    )
    low = engine.add(
        "the deploy window is monday morning", source="conformance", confidence=0.4
    )
    order = [r.id for r, _ in engine.query("deploy window", 0, 10)]
    assert order.index(high.id) < order.index(low.id)


def test_conflict_gate_cg_001_the_loser_is_superseded_and_nothing_is_deleted():
    engine = _engine()
    a = engine.add(
        "always enable telemetry uploads for diagnostics",
        source="conformance",
        confidence=0.95,
    )
    b = engine.add(
        "never enable telemetry uploads for diagnostics",
        source="conformance",
        confidence=0.2,
    )
    found = engine.scan_conflicts()
    assert found
    outcome = engine.auto_resolve(found[0])
    assert outcome in ("resolved", "queued")
    if outcome == "resolved":
        assert any(engine.records[r.id].superseded_by for r in (a, b))
    assert {a.id, b.id} <= set(engine.records)


def test_ledger_audit_la_001_create_then_feedback_reconstructs():
    engine = _engine()
    record = engine.add("audited record", source="conformance", confidence=0.7)
    engine.feedback(record.id, "wrong")
    history = engine.history(record.id)
    assert [h["action"] for h in history] == ["create", "feedback"]
    assert history[-1]["previousState"]["confidence"] == pytest.approx(0.7)
    assert history[-1]["newState"]["confidence"] == pytest.approx(0.5)


# Beyond the vectors: the same rules where insertion order cannot hide them.


def test_the_superseded_penalty_holds_when_the_old_record_came_first():
    engine = _engine()
    old = engine.add(
        "we deploy the api with docker on fridays", source="t", confidence=0.9
    )
    fresh = engine.add(
        "we deploy the api with docker on mondays", source="t", confidence=0.9
    )
    engine.supersede(old.id, fresh.id)
    order = [
        r.id for r, _ in engine.query("when do we deploy the api with docker", 0, 10)
    ]
    assert order.index(fresh.id) < order.index(old.id)


def test_confidence_decides_when_the_low_record_came_first():
    engine = _engine()
    low = engine.add("the deploy window is monday morning", source="t", confidence=0.4)
    high = engine.add("the deploy window is monday morning", source="t", confidence=0.9)
    order = [r.id for r, _ in engine.query("deploy window", 0, 10)]
    assert order.index(high.id) < order.index(low.id)


def test_the_cg_001_pair_resolves_against_the_low_confidence_record():
    engine = _engine()
    a = engine.add(
        "always enable telemetry uploads for diagnostics", source="t", confidence=0.95
    )
    b = engine.add(
        "never enable telemetry uploads for diagnostics", source="t", confidence=0.2
    )
    assert engine.auto_resolve(engine.scan_conflicts()[0]) == "resolved"
    assert engine.records[b.id].superseded_by == a.id
    assert engine.records[a.id].superseded_by is None
    assert engine.history(b.id)[-1]["action"] == "conflict_resolved"


def test_a_weak_conflict_is_queued_for_a_person():
    engine = _engine()
    engine.add(
        "always enable telemetry uploads for diagnostics", source="t", confidence=0.6
    )
    b = engine.add(
        "never enable telemetry uploads for diagnostics", source="t", confidence=0.6
    )
    assert engine.auto_resolve(engine.scan_conflicts()[0]) == "queued"
    assert engine.records[b.id].superseded_by is None


# The product use: the owner's decisions, per repo, append-only.


def _store(folder, repo_id="sample_app", now=T0):
    return HMemMemoryStore(folder, repo_id, lambda: now)


def _decision(answer, at="2026-10-27T16:00:00Z"):
    return Decision(QUESTION, answer, "Shaela", at)


def test_it_plugs_into_the_memory_store_port(tmp_path):
    assert isinstance(_store(tmp_path), MemoryStore)


def test_an_open_question_with_no_decision_recalls_nothing(tmp_path):
    assert _store(tmp_path).decision_for(QUESTION) is None


def test_a_decision_is_recalled_after_reopening(tmp_path):
    _store(tmp_path).record_decision(_decision("at the end of the billing period"))
    reopened = _store(tmp_path, now=T0 + DAY)
    assert reopened.decision_for(QUESTION) == _decision(
        "at the end of the billing period"
    )


def test_a_newer_decision_replaces_the_older_one_and_nothing_is_deleted(tmp_path):
    store = _store(tmp_path)
    store.record_decision(_decision("immediately"))
    store.record_decision(
        _decision("at the end of the billing period", "2026-10-27T17:00:00Z")
    )
    assert store.decision_for(QUESTION).answer == "at the end of the billing period"
    records = list(_store(tmp_path).engine.records.values())
    assert len(records) == 2
    assert records[0].superseded_by == records[1].id
    assert records[1].supersedes == records[0].id


def test_a_decision_survives_the_question_moving_to_another_line(tmp_path):
    _store(tmp_path).record_decision(_decision("at the end of the billing period"))
    moved = OpenQuestion(QUESTION.file, 40, QUESTION.text, QUESTION.symbol)
    recalled = _store(tmp_path).decision_for(moved)
    assert recalled.answer == "at the end of the billing period"


def test_a_reworded_question_is_a_new_question(tmp_path):
    _store(tmp_path).record_decision(_decision("immediately"))
    reworded = OpenQuestion(
        QUESTION.file, 16, "should refunds be prorated?", QUESTION.symbol
    )
    assert _store(tmp_path).decision_for(reworded) is None


def test_the_ledger_is_append_only_and_names_who_decided(tmp_path):
    store = _store(tmp_path)
    store.record_decision(_decision("immediately"))
    ledger = tmp_path / "sample_app.jsonl"
    first = ledger.read_text(encoding="utf-8")
    store.record_decision(_decision("at the end of the billing period"))
    second = ledger.read_text(encoding="utf-8")
    assert second.startswith(first)
    entries = [json.loads(line) for line in second.splitlines()]
    assert [e["action"] for e in entries] == ["create", "create", "update"]
    assert {e["actor"] for e in entries} == {"Shaela"}
    assert entries[0]["newState"]["source"] == "owner"
    assert entries[0]["newState"]["provenance"]["learnedAt"] == "2026-10-27T16:00:00Z"


def test_recall_is_logged_as_a_read(tmp_path):
    store = _store(tmp_path)
    store.record_decision(_decision("immediately"))
    store.decision_for(QUESTION)
    assert store.engine.ledger[-1]["action"] == "read"


def test_each_repo_keeps_its_own_record(tmp_path):
    _store(tmp_path, "repo_a").record_decision(_decision("immediately"))
    assert _store(tmp_path, "repo_b").decision_for(QUESTION) is None
    assert _store(tmp_path, "repo_a").decision_for(QUESTION).answer == "immediately"


def test_a_repo_id_must_be_a_plain_name(tmp_path):
    for bad in ("../escape", "a/b", ".hidden", ""):
        with pytest.raises(ValueError):
            _store(tmp_path, bad)
