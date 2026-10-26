from dataclasses import dataclass
from enum import Enum


class FindingKind(Enum):
    OBSERVED = "observed"
    INFERRED = "inferred"


@dataclass(frozen=True)
class Evidence:
    file: str
    line_start: int | None = None
    line_end: int | None = None
    content_hash: str | None = None


@dataclass(frozen=True)
class Provenance:
    entity: str
    activity: str
    agent: str


@dataclass(frozen=True)
class Finding:
    summary: str
    kind: FindingKind
    evidence: tuple[Evidence, ...]

    def __post_init__(self):
        object.__setattr__(self, "evidence", tuple(self.evidence))
        if not self.evidence:
            raise ValueError("a Finding must carry at least one Evidence")
