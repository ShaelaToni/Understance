"""H-MEM memory, implemented in Python from the Meterless H-MEM spec (AGENTS.md).

Implemented: the canonical record (source mandatory), the trust ledger, the
feedback deltas, hybrid retrieval ranking and conflict detection with gated
auto-resolve. Not implemented: dreaming, sleep, mining and embeddings (the
semantic term uses word overlap, so no model is needed).
"""

import hashlib
import json
import math
import re
from collections import Counter
from collections.abc import Callable
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

from understance.domain.answer import Decision
from understance.domain.graph import OpenQuestion
from understance.ports.interfaces import MemoryStore

DAY_MS = 24 * 60 * 60 * 1000
FEEDBACK = {"helpful": 0.05, "not_helpful": -0.03, "wrong": -0.20}
LAYER_WEIGHT = {"long_term": 1.0, "working": 0.8, "short_term": 0.6}
RECENCY_MS = 14 * DAY_MS
AUTO_RESOLVE_GATE = 0.70
OPPOSING_WORDS = (
    ("always", "never"),
    ("enable[ds]?", "disable[ds]?"),
    ("prefers?", "avoids?|dislikes?"),
    ("on", "off"),
    ("yes", "no"),
)
OPPOSING = tuple(
    tuple(re.compile(rf"\b(?:{w})\b", re.IGNORECASE) for w in pair)
    for pair in OPPOSING_WORDS
)
WORD = re.compile(r"[a-z0-9]+")


@dataclass
class MemoryRecord:
    """One H-MEM record (spec section 2), with snake_case field names."""

    id: str
    content: str
    source: str
    confidence: float = 0.7
    type: str = "general"
    layer: str = "working"
    timestamp: int = 0
    last_accessed: int = 0
    access_count: int = 0
    tags: list[str] = field(default_factory=list)
    provenance: dict = field(default_factory=dict)
    namespace: str | None = None
    domain: str | None = None
    supersedes: str | None = None
    superseded_by: str | None = None
    derived_from: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Conflict:
    memory_a: str
    memory_b: str
    reason: str
    confidence: float


class HMem:
    """The H-MEM services this product needs: store, ledger, query, conflicts."""

    def __init__(
        self,
        clock: Callable[[], int],
        ledger_path: Path | None = None,
        actor="understance",
    ):
        self._clock = clock
        self._path = Path(ledger_path) if ledger_path else None
        self._actor = actor
        self.records: dict[str, MemoryRecord] = {}
        self.ledger: list[dict] = []
        if self._path and self._path.exists():
            self._replay()

    def add(
        self, content: str, source: str, actor: str | None = None, **fields
    ) -> MemoryRecord:
        if not source or not source.strip():
            raise ValueError("an H-MEM record must carry a source")
        now = self._clock()
        record = MemoryRecord(
            f"mem-{len(self.records) + 1:04d}",
            content,
            source,
            timestamp=now,
            last_accessed=now,
            **fields,
        )
        self.records[record.id] = record
        self._log(record.id, "create", actor, None, record)
        return record

    def feedback(self, memory_id: str, kind: str) -> MemoryRecord:
        before = self.records[memory_id]
        after = replace(
            before,
            confidence=_clamp(before.confidence + FEEDBACK[kind]),
            access_count=before.access_count + (kind == "helpful"),
            tags=before.tags + (["review"] if kind == "wrong" else []),
        )
        self.records[memory_id] = after
        self._log(memory_id, "feedback", None, before, after, {"kind": kind})
        return after

    def supersede(self, old_id: str, new_id: str, actor: str | None = None) -> None:
        before = self.records[old_id]
        after = replace(before, superseded_by=new_id)
        self.records[old_id] = after
        self._log(old_id, "update", actor, before, after, {"superseded_by": new_id})

    def note_read(self, memory_id: str, details: dict) -> None:
        self._log(memory_id, "read", None, None, None, details)

    def history(self, memory_id: str) -> list[dict]:
        return [e for e in self.ledger if e["memoryId"] == memory_id]

    def query(self, text: str, threshold: float = 0.35, top_n: int = 5) -> list[tuple]:
        scored = [(r, self._score(text, r)) for r in self.records.values()]
        kept = sorted((p for p in scored if p[1] >= threshold), key=lambda p: -p[1])
        for record, _ in kept[:top_n]:
            self.note_read(record.id, {"query": text})
        return kept[:top_n]

    def scan_conflicts(self) -> list[Conflict]:
        found = []
        records = list(self.records.values())
        for i, a in enumerate(records):
            for b in records[i + 1 :]:
                conflict = _conflict(a, b)
                if conflict:
                    found.append(conflict)
                    self._log(
                        a.id, "conflict_detected", None, None, None, asdict(conflict)
                    )
        return found

    def auto_resolve(self, conflict: Conflict) -> str:
        a, b = self.records[conflict.memory_a], self.records[conflict.memory_b]
        sa, sb = self._weight(a), self._weight(b)
        margin = abs(sa - sb) / max(sa, sb)
        decision = _clamp(conflict.confidence * 0.6 + margin * 0.8)
        if decision < AUTO_RESOLVE_GATE:
            return "queued"
        winner, loser = (a, b) if sa >= sb else (b, a)
        after = replace(loser, superseded_by=winner.id)
        self.records[loser.id] = after
        details = {"winner": winner.id, "decision_confidence": round(decision, 3)}
        self._log(loser.id, "conflict_resolved", None, loser, after, details)
        return "resolved"

    def _score(self, text: str, record: MemoryRecord) -> float:
        query, memory = _words(text), _words(record.content)
        top = set(sorted(query, key=lambda w: -query[w])[:8])
        keyword = len(top & set(memory)) / len(top | set(memory)) if top else 0.0
        tag = (
            sum(t in query for t in record.tags) / len(record.tags)
            if record.tags
            else 0.0
        )
        age = max(0, self._clock() - record.last_accessed)
        raw = (
            0.35 * _cosine(query, memory)
            + 0.20 * keyword
            + 0.10 * tag
            + 0.05 * LAYER_WEIGHT.get(record.layer, 0.6)
            + 0.05 * math.exp(-age / RECENCY_MS)
            - 0.20 * (record.superseded_by is not None)
        )
        return _clamp(raw) * record.confidence

    def _weight(self, record: MemoryRecord) -> float:
        return (
            0.3 * (record.last_accessed / max(1, self._clock()))
            + 0.2 * min(1, record.access_count / 10)
            + 0.25 * record.confidence
            + 0.1 * min(1, len(record.content) / 200)
            + 0.15
            * (1 if record.provenance.get("origin") == "user_correction" else 0.5)
        )

    def _log(self, memory_id, action, actor, before, after, details=None) -> None:
        entry = {
            "memoryId": memory_id,
            "action": action,
            "actor": actor or self._actor,
            "timestamp": self._clock(),
            "previousState": asdict(before) if before else None,
            "newState": asdict(after) if after else None,
            "details": details or {},
        }
        self.ledger.append(entry)
        if self._path:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, sort_keys=True) + "\n")

    def _replay(self) -> None:
        for line in self._path.read_text(encoding="utf-8").splitlines():
            entry = json.loads(line)
            self.ledger.append(entry)
            if entry["newState"] is not None:
                self.records[entry["memoryId"]] = MemoryRecord(**entry["newState"])


class HMemMemoryStore(MemoryStore):
    """The owner's decisions for one repo, kept as H-MEM records in an append-only ledger."""

    def __init__(self, folder: Path, repo_id: str, clock: Callable[[], int]):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", repo_id) or repo_id.startswith("."):
            raise ValueError(f"not a plain repo id: {repo_id!r}")
        self.repo_id = repo_id
        self.engine = HMem(clock, Path(folder) / f"{repo_id}.jsonl")

    def record_decision(self, decision: Decision) -> None:
        key = _key(decision.question)
        current = self._current(key)
        record = self.engine.add(
            f"Decided for {_where(decision.question)}: {decision.answer}",
            source="owner",
            actor=decision.decided_by,
            confidence=1.0,
            type="factual",
            layer="long_term",
            tags=["decision", key],
            namespace=self.repo_id,
            supersedes=current.id if current else None,
            provenance={
                "origin": "user",
                "learnedAt": decision.decided_at,
                "label": decision.decided_by,
                "refs": {"question": decision.question.text, "answer": decision.answer},
            },
        )
        if current:
            self.engine.supersede(current.id, record.id, actor=decision.decided_by)

    def decision_for(self, question: OpenQuestion) -> Decision | None:
        record = self._current(_key(question))
        if record is None:
            return None
        self.engine.note_read(record.id, {"recall": _key(question)})
        p = record.provenance
        return Decision(question, p["refs"]["answer"], p["label"], p["learnedAt"])

    def _current(self, key: str) -> MemoryRecord | None:
        found = [
            r
            for r in self.engine.records.values()
            if key in r.tags and r.superseded_by is None
        ]
        return found[0] if found else None


def _key(question: OpenQuestion) -> str:
    """Key by file, symbol and wording, so a question that moves lines keeps its answer."""
    wording = hashlib.sha256(question.text.encode("utf-8")).hexdigest()[:12]
    return f"decision:{question.file}:{question.symbol or ''}:{wording}"


def _where(question: OpenQuestion) -> str:
    where = f"{question.file}, line {question.line}"
    return where + (f", in {question.symbol}" if question.symbol else "")


def _conflict(a: MemoryRecord, b: MemoryRecord) -> Conflict | None:
    if b.id in (a.supersedes, a.superseded_by) or a.id in (
        b.supersedes,
        b.superseded_by,
    ):
        return None
    similarity = _cosine(_words(a.content), _words(b.content))
    for p, q in OPPOSING:
        opposed = (p.search(a.content) and q.search(b.content)) or (
            q.search(a.content) and p.search(b.content)
        )
        if opposed and similarity > 0.5:
            reason = "opposing phrase pair on similar content"
            same_domain = 0.05 if a.domain == b.domain else 0.0
            confidence = _clamp(0.5 + 0.3 * similarity + same_domain)
            return Conflict(a.id, b.id, reason, confidence)
    return None


def _words(text: str) -> Counter:
    return Counter(WORD.findall(text.lower()))


def _cosine(a: Counter, b: Counter) -> float:
    dot = sum(a[w] * b[w] for w in a)
    norm = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(
        sum(v * v for v in b.values())
    )
    return dot / norm if norm else 0.0


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
