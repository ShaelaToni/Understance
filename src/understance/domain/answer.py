from dataclasses import dataclass
from enum import Enum

from understance.domain.finding import Finding


class AnswerStatus(Enum):
    ANSWERED = "answered"
    NEEDS_INPUT = "needs_input"
    INCOMPLETE = "incomplete"


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

    def __post_init__(self):
        object.__setattr__(self, "affected", tuple(self.affected))
        object.__setattr__(self, "findings", tuple(self.findings))
        object.__setattr__(self, "blocked", tuple(self.blocked))
