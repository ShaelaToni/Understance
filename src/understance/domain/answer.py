from dataclasses import dataclass
from enum import Enum

from understance.domain.finding import Finding
from understance.domain.graph import OpenQuestion


class AnswerStatus(Enum):
    ANSWERED = "answered"
    NEEDS_INPUT = "needs_input"
    INCOMPLETE = "incomplete"
    NEEDS_DECISION = "needs_decision"


@dataclass(frozen=True)
class Narration:
    text: str
    model: str | None


@dataclass(frozen=True)
class Answer:
    run_id: str
    question: str
    status: AnswerStatus
    target: str | None
    affected: tuple[str, ...]
    text: str
    findings: tuple[Finding, ...]
    blocked: tuple[Finding, ...]
    model: str | None
    open_questions: tuple[OpenQuestion, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "affected", tuple(self.affected))
        object.__setattr__(self, "findings", tuple(self.findings))
        object.__setattr__(self, "blocked", tuple(self.blocked))
        object.__setattr__(self, "open_questions", tuple(self.open_questions))


@dataclass(frozen=True)
class Decision:
    """An open question the owner settled: what they chose, who, and when."""

    question: OpenQuestion
    answer: str
    decided_by: str
    decided_at: str

    def __post_init__(self):
        if not self.answer.strip():
            raise ValueError("a Decision must carry an answer")
        if not self.decided_by.strip():
            raise ValueError("a Decision must name who decided")
