from dataclasses import FrozenInstanceError

import pytest

from understance.domain.answer import Answer, AnswerStatus, Decision, Narration
from understance.domain.finding import Evidence, Finding, FindingKind
from understance.domain.graph import OpenQuestion


def test_narration_carries_the_text_and_the_model_that_wrote_it():
    narration = Narration(text="plain words", model="template (no model)")
    assert (narration.text, narration.model) == ("plain words", "template (no model)")
    assert Narration(text="no model needed", model=None).model is None


def test_answer_statuses_are_a_fixed_list():
    assert [s.value for s in AnswerStatus] == [
        "answered",
        "needs_input",
        "incomplete",
        "needs_decision",
    ]


def test_answer_is_frozen_and_stores_tuples():
    finding = Finding("a imports b", FindingKind.OBSERVED, [Evidence("a.py", 1, 1)])
    answer = Answer(
        "run-1", "q", AnswerStatus.ANSWERED, "b", ["a"], "text", [finding], [], "m"
    )
    assert answer.affected == ("a",)
    assert answer.findings == (finding,)
    assert answer.blocked == ()
    assert answer.open_questions == ()
    with pytest.raises(FrozenInstanceError):
        answer.status = AnswerStatus.NEEDS_INPUT


QUESTION = OpenQuestion("app/subs.py", 16, "immediately or at period end?", "cancel")


def test_a_decision_carries_the_question_the_answer_who_and_when():
    decision = Decision(QUESTION, "at period end", "Shaela", "2026-10-27T16:00:00Z")
    assert (decision.answer, decision.decided_by) == ("at period end", "Shaela")
    with pytest.raises(FrozenInstanceError):
        decision.answer = "immediately"


def test_a_decision_needs_an_answer_and_a_person():
    with pytest.raises(ValueError):
        Decision(QUESTION, "  ", "Shaela", "2026-10-27T16:00:00Z")
    with pytest.raises(ValueError):
        Decision(QUESTION, "at period end", "", "2026-10-27T16:00:00Z")
