import json
from pathlib import Path

from fakes import FakeFactStore

from understance.adapters.ast_source_reader import ASTSourceReader
from understance.adapters.template_narrator import TemplateNarrator
from understance.domain.answer import AnswerStatus
from understance.domain.finding import Evidence, Finding, FindingKind
from understance.orchestration.agents import (
    Evaluator,
    Explainer,
    Plan,
    Planner,
    Retrieval,
    Retriever,
    Scope,
)
from understance.orchestration.orchestrator import (
    MAX_SEND_BACKS,
    TRACE_FIELDS,
    Orchestrator,
    assemble,
)
from understance.orchestration.read_only_fact_store import ReadOnlyFactStore
from understance.ports.interfaces import Narrator
from understance.usecases.analyze_repo import AnalyzeRepo

SAMPLE_APP = Path(__file__).resolve().parent.parent / "sample_app"
CLOCK = "2026-10-27T00:00:00Z"
QUESTION = "What would changing subscriptions affect?"


def _store():
    store = FakeFactStore()
    AnalyzeRepo(ASTSourceReader(), store).run(SAMPLE_APP)
    return store


def _run(question):
    records = []
    orchestrator = assemble(_store(), TemplateNarrator(), records.append, lambda: CLOCK)
    return orchestrator.run(question, "run-1"), records


def _steps(records):
    return [
        (r["agent_name"], r["action"], r["target_agent"], r["status"]) for r in records
    ]


def _orchestrator(retriever_class, records):
    facts = ReadOnlyFactStore(_store())
    return Orchestrator(
        Planner(facts),
        retriever_class(facts),
        Evaluator(facts),
        Explainer(TemplateNarrator()),
        records.append,
        lambda: CLOCK,
    )


def test_evaluator_sends_the_planner_back_and_the_trace_shows_the_loop():
    answer, records = _run(QUESTION)
    assert answer.status is AnswerStatus.ANSWERED
    assert answer.run_id == "run-1"
    assert answer.target == "sample_app.subscriptions"
    assert answer.affected == (
        "sample_app.access",
        "sample_app.api",
        "sample_app.billing",
        "sample_app.main",
        "sample_app.notifications",
    )
    assert len(answer.findings) == 8
    assert _steps(records) == [
        ("Planner", "plan", "Retriever", "ok"),
        ("Retriever", "retrieve", "Evaluator", "ok"),
        ("Evaluator", "evaluate", "Planner", "sent_back"),
        ("Planner", "widen", "Retriever", "ok"),
        ("Retriever", "retrieve", "Evaluator", "ok"),
        ("Evaluator", "evaluate", "Explainer", "approved"),
        ("Explainer", "explain", "user", "ok"),
    ]
    assert [r["retry_count"] for r in records] == [0, 0, 0, 1, 1, 1, 1]
    assert "sample_app.main" in records[2]["output_summary"]


def test_answer_leads_with_the_affected_modules_and_cites_file_and_line():
    answer, records = _run(QUESTION)
    assert answer.text.startswith(
        "Changing sample_app.subscriptions could affect 5 other modules:"
    )
    assert "(sample_app/access.py, line 14)" in answer.text
    assert answer.model == "template (no model)"
    assert records[-1]["model"] == "template (no model)"


def test_a_module_nothing_imports_is_answered_without_a_send_back_or_a_model():
    answer, records = _run("What would changing main affect?")
    assert answer.status is AnswerStatus.ANSWERED
    assert answer.findings == ()
    assert answer.model is None
    assert [r["status"] for r in records] == ["ok", "ok", "approved", "ok"]


def test_an_unknown_module_stops_and_asks_instead_of_guessing():
    answer, records = _run("What would changing payments affect?")
    assert answer.status is AnswerStatus.NEEDS_INPUT
    assert answer.target is None
    assert answer.text.startswith("I could not match a module in your question.")
    assert _steps(records) == [("Planner", "resolve_target", "user", "needs_input")]


class _InventingRetriever(Retriever):
    """Adds one claim the facts do not support (the planted violation)."""

    def retrieve(self, plan):
        found = super().retrieve(plan)
        invented = Finding(
            "sample_app.main imports sample_app.billing",
            FindingKind.OBSERVED,
            [Evidence("sample_app/main.py", 3, 3)],
        )
        return Retrieval(found.plan, found.modules, found.findings + (invented,))


def test_a_planted_unsupported_claim_is_blocked_and_never_explained():
    records = []
    answer = _orchestrator(_InventingRetriever, records).run(QUESTION, "run-2")
    assert answer.status is AnswerStatus.ANSWERED
    assert [f.summary for f in answer.blocked] == [
        "sample_app.main imports sample_app.billing"
    ]
    assert "sample_app.main imports sample_app.billing" not in answer.text
    approved = next(r for r in records if r["status"] == "approved")
    assert approved["output_summary"] == "approved 8, blocked 1"
    assert approved["confidence"] == 0.89


class _NeverWidens(Retriever):
    """Ignores the widened plan, so the answer can never close."""

    def retrieve(self, plan):
        return super().retrieve(Plan(plan.target, Scope.DIRECT))


def test_the_send_back_loop_is_bounded():
    records = []
    answer = _orchestrator(_NeverWidens, records).run(QUESTION, "run-3")
    assert answer.status is AnswerStatus.INCOMPLETE
    assert "sample_app.main" in answer.text
    assert len([r for r in records if r["status"] == "sent_back"]) == MAX_SEND_BACKS
    assert records[-1]["status"] == "incomplete"


def test_every_trace_record_has_exactly_the_agreed_fields_and_is_json():
    _, records = _run(QUESTION)
    for record in records:
        assert tuple(record) == TRACE_FIELDS
        assert record["timestamp"] == CLOCK
        assert record["run_id"] == "run-1"
        json.dumps(record)


def test_each_agent_holds_only_the_ports_its_role_needs():
    store = _store()
    orchestrator = assemble(store, TemplateNarrator(), lambda record: None, str)
    for agent in (orchestrator.planner, orchestrator.retriever, orchestrator.evaluator):
        assert vars(agent).keys() == {"facts"}
        assert isinstance(agent.facts, ReadOnlyFactStore)
        assert agent.facts is not store
    assert vars(orchestrator.explainer).keys() == {"narrator"}
    assert isinstance(orchestrator.explainer.narrator, Narrator)
