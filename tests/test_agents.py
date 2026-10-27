from pathlib import Path

from fakes import FakeFactStore

from understance.adapters.ast_source_reader import ASTSourceReader
from understance.adapters.template_narrator import TemplateNarrator
from understance.domain.finding import Evidence, Finding, FindingKind
from understance.domain.graph import Dependency, DependencyGraph, Module, OpenQuestion
from understance.orchestration.agents import (
    Evaluator,
    Explainer,
    Plan,
    Planner,
    Retrieval,
    Retriever,
    Scope,
)
from understance.orchestration.read_only_fact_store import ReadOnlyFactStore
from understance.usecases.analyze_repo import AnalyzeRepo

SAMPLE_APP = Path(__file__).resolve().parent.parent / "sample_app"


def _facts():
    store = FakeFactStore()
    AnalyzeRepo(ASTSourceReader(), store).run(SAMPLE_APP)
    return ReadOnlyFactStore(store)


def _facts_of(modules, dependencies=()):
    store = FakeFactStore()
    built = tuple(m if isinstance(m, Module) else Module(m) for m in modules)
    store.store_graph(DependencyGraph(built, dependencies))
    return ReadOnlyFactStore(store)


def test_planner_resolves_a_module_named_in_the_question():
    resolution = Planner(_facts()).resolve("What would changing subscriptions affect?")
    assert resolution.target == "sample_app.subscriptions"
    assert resolution.question_back is None


def test_planner_stops_and_asks_when_no_module_matches():
    resolution = Planner(_facts()).resolve("What would changing payments affect?")
    assert resolution.target is None
    assert resolution.question_back.startswith(
        "I could not match a module in your question."
    )
    assert "sample_app.subscriptions" in resolution.question_back


def test_planner_stops_and_asks_when_several_modules_match():
    facts = _facts_of(["app.models", "lib.models"])
    resolution = Planner(facts).resolve("change models")
    assert resolution.target is None
    assert "app.models, lib.models" in resolution.question_back


def test_planner_lists_at_most_twenty_modules_when_it_asks():
    facts = _facts_of([f"m{i:02d}" for i in range(25)])
    question_back = Planner(facts).resolve("change payments").question_back
    assert "m19" in question_back
    assert "m20" not in question_back
    assert question_back.endswith("m19, and 5 more.")


def test_planner_starts_narrow_and_widens_when_sent_back():
    planner = Planner(_facts())
    plan = planner.plan("sample_app.subscriptions")
    assert plan == Plan("sample_app.subscriptions", Scope.DIRECT)
    assert planner.widen(plan) == Plan("sample_app.subscriptions", Scope.TRANSITIVE)


def test_direct_retrieval_returns_only_the_modules_that_import_the_target():
    retrieval = Retriever(_facts()).retrieve(
        Plan("sample_app.subscriptions", Scope.DIRECT)
    )
    assert retrieval.modules == (
        "sample_app.access",
        "sample_app.api",
        "sample_app.billing",
        "sample_app.notifications",
    )
    assert len(retrieval.findings) == 4


def test_evaluator_finds_the_direct_answer_incomplete():
    facts = _facts()
    retrieval = Retriever(facts).retrieve(
        Plan("sample_app.subscriptions", Scope.DIRECT)
    )
    verdict = Evaluator(facts).evaluate(retrieval)
    assert not verdict.complete
    assert verdict.missing == ("sample_app.main",)


def test_evaluator_approves_the_widened_answer():
    facts = _facts()
    retrieval = Retriever(facts).retrieve(
        Plan("sample_app.subscriptions", Scope.TRANSITIVE)
    )
    verdict = Evaluator(facts).evaluate(retrieval)
    assert verdict.complete
    assert len(verdict.approved) == 8
    assert verdict.blocked == ()


def test_evaluator_blocks_a_claim_the_facts_do_not_support():
    facts = _facts()
    retrieval = Retriever(facts).retrieve(Plan("sample_app.api", Scope.TRANSITIVE))
    invented = Finding(
        "sample_app.main imports sample_app.billing",
        FindingKind.OBSERVED,
        [Evidence("sample_app/main.py", 3, 3)],
    )
    planted = Retrieval(
        retrieval.plan, retrieval.modules, retrieval.findings + (invented,)
    )
    verdict = Evaluator(facts).evaluate(planted)
    assert invented in verdict.blocked
    assert invented not in verdict.approved


def test_evaluator_blocks_a_real_link_cited_at_the_wrong_line():
    wrong_line = Finding(
        "sample_app.main imports sample_app.api",
        FindingKind.OBSERVED,
        [Evidence("sample_app/main.py", 9, 9)],
    )
    retrieval = Retrieval(
        Plan("sample_app.api", Scope.TRANSITIVE), ("sample_app.main",), (wrong_line,)
    )
    verdict = Evaluator(_facts()).evaluate(retrieval)
    assert verdict.blocked == (wrong_line,)
    assert verdict.approved == ()


def test_links_without_a_recorded_location_yield_no_finding():
    facts = _facts_of(["a", "b"], (Dependency("a", "b"),))
    assert Retriever(facts).retrieve(Plan("b", Scope.DIRECT)).findings == ()


def test_explainer_leads_with_what_could_be_affected():
    finding = Finding(
        "app.a imports app.b", FindingKind.OBSERVED, [Evidence("app/a.py", 3, 3)]
    )
    narration = Explainer(TemplateNarrator()).explain("app.b", ("app.a",), (finding,))
    assert narration.text.startswith(
        "Changing app.b could affect 1 other modules: app.a.\n"
    )
    assert "app.a imports app.b (app/a.py, line 3)" in narration.text
    assert narration.model == "template (no model)"


class _MustNotBeCalled(TemplateNarrator):
    def narrate(self, findings):
        raise AssertionError("no model call is needed when nothing is affected")


def test_explainer_makes_no_model_call_when_nothing_is_affected():
    narration = Explainer(_MustNotBeCalled()).explain("app.main", (), ())
    assert narration.text == (
        "Nothing else in this project imports app.main, "
        "so a change to it stays inside it."
    )
    assert narration.model is None


def test_planner_finds_the_module_behind_a_concept_word():
    resolution = Planner(_facts()).resolve("Add customer cancellation")
    assert resolution.target == "sample_app.subscriptions"
    assert resolution.reason == "it defines cancel_subscription"


def test_planner_resolves_a_concept_only_one_module_defines():
    resolution = Planner(_facts()).resolve("What if I change the refund rules?")
    assert resolution.target == "sample_app.billing"
    assert resolution.reason == "it defines refund_on_cancel"


def test_planner_ignores_short_words_and_asks_when_nothing_matches():
    resolution = Planner(_facts()).resolve("add a fix")
    assert resolution.target is None
    assert resolution.question_back.startswith("I could not match a module")


def test_planner_asks_with_evidence_when_a_concept_has_two_owners():
    facts = _facts_of(
        [Module("app.a", ("refund_order",)), Module("app.b", ("refund_payment",))]
    )
    resolution = Planner(facts).resolve("change refunds")
    assert resolution.target is None
    assert resolution.question_back == (
        "Your question could mean: app.a (refund_order), app.b (refund_payment). "
        "Which one should I trace?"
    )


def test_retrieval_carries_the_targets_open_questions():
    retrieval = Retriever(_facts()).retrieve(
        Plan("sample_app.subscriptions", Scope.DIRECT)
    )
    assert [(q.file, q.line) for q in retrieval.open_questions] == [
        ("sample_app/subscriptions.py", 16)
    ]


def test_evaluator_passes_on_only_open_questions_the_facts_hold():
    facts = _facts()
    retrieval = Retriever(facts).retrieve(
        Plan("sample_app.subscriptions", Scope.TRANSITIVE)
    )
    invented = OpenQuestion("sample_app/subscriptions.py", 99, "invented?", None)
    planted = Retrieval(
        retrieval.plan,
        retrieval.modules,
        retrieval.findings,
        retrieval.open_questions + (invented,),
    )
    verdict = Evaluator(facts).evaluate(planted)
    assert verdict.decisions_needed == retrieval.open_questions


def test_a_module_name_at_the_end_of_a_sentence_still_matches():
    resolution = Planner(_facts()).resolve("Show me what changing subscriptions.")
    assert resolution.target == "sample_app.subscriptions"
