from dataclasses import FrozenInstanceError

import pytest

from understance.domain.answer import Answer, AnswerStatus, Narration
from understance.domain.finding import Evidence, Finding, FindingKind


def test_narration_carries_the_text_and_the_model_that_wrote_it():
    narration = Narration(text="plain words", model="template (no model)")
    assert (narration.text, narration.model) == ("plain words", "template (no model)")
    assert Narration(text="no model needed", model=None).model is None


def test_answer_statuses_are_a_fixed_list():
    assert [s.value for s in AnswerStatus] == ["answered", "needs_input", "incomplete"]


def test_answer_is_frozen_and_stores_tuples():
    finding = Finding("a imports b", FindingKind.OBSERVED, [Evidence("a.py", 1, 1)])
    answer = Answer(
        "run-1", "q", AnswerStatus.ANSWERED, "b", ["a"], "text", [finding], [], "m"
    )
    assert answer.affected == ("a",)
    assert answer.findings == (finding,)
    assert answer.blocked == ()
    with pytest.raises(FrozenInstanceError):
        answer.status = AnswerStatus.NEEDS_INPUT
