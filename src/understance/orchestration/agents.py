import re
from dataclasses import dataclass
from enum import Enum

from understance.domain.answer import Narration
from understance.domain.finding import Finding
from understance.domain.graph import Module, OpenQuestion
from understance.ports.interfaces import FactStore, Narrator
from understance.usecases.compute_blast_radius import ComputeBlastRadius, edge_finding

MAX_LISTED = 20
MIN_STEM = 4
WORD = re.compile(r"[a-z_][a-z0-9_.]*")


class Scope(Enum):
    DIRECT = "direct"
    TRANSITIVE = "transitive"


@dataclass(frozen=True)
class Resolution:
    target: str | None
    question_back: str | None
    reason: str | None = None


@dataclass(frozen=True)
class Plan:
    target: str
    scope: Scope


@dataclass(frozen=True)
class Retrieval:
    plan: Plan
    modules: tuple[str, ...]
    findings: tuple[Finding, ...]
    open_questions: tuple[OpenQuestion, ...] = ()


@dataclass(frozen=True)
class Verdict:
    approved: tuple[Finding, ...]
    blocked: tuple[Finding, ...]
    missing: tuple[str, ...]
    decisions_needed: tuple[OpenQuestion, ...] = ()

    @property
    def complete(self) -> bool:
        return not self.missing


class Planner:
    """Find the module a question names, then plan narrow and widen on request."""

    def __init__(self, facts: FactStore):
        self.facts = facts

    def resolve(self, question: str) -> Resolution:
        words = {w.strip(".") for w in WORD.findall(question.lower())}
        modules = self.facts.load_graph().modules
        names = sorted(m.name for m in modules)
        matches = [
            n for n in names if n.lower() in words or n.split(".")[-1].lower() in words
        ]
        if len(matches) == 1:
            return Resolution(matches[0], None, "the question names this module")
        if matches:
            return Resolution(
                None,
                f"Your question names more than one module: {_listing(matches)}. "
                "Which one should I trace?",
            )
        concept = _resolve_concept(words, modules)
        if concept is not None:
            return concept
        return Resolution(
            None,
            "I could not match a module in your question. Which one do you mean? "
            f"Modules: {_listing(names)}.",
        )

    def plan(self, target: str) -> Plan:
        return Plan(target, Scope.DIRECT)

    def widen(self, plan: Plan) -> Plan:
        return Plan(plan.target, Scope.TRANSITIVE)


class Retriever:
    """Turn the stored facts in a plan's scope into findings."""

    def __init__(self, facts: FactStore):
        self.facts = facts

    def retrieve(self, plan: Plan) -> Retrieval:
        graph = self.facts.load_graph()
        questions = _open_questions_of(graph.modules, plan.target)
        if plan.scope is Scope.TRANSITIVE:
            radius = ComputeBlastRadius(self.facts).run(plan.target)
            return Retrieval(plan, radius.dependents, radius.findings, questions)
        edges = sorted(
            (
                d
                for d in graph.dependencies
                if d.target == plan.target and d.file is not None
            ),
            key=lambda d: d.source,
        )
        modules = tuple(sorted({d.source for d in edges}))
        findings = tuple(edge_finding(d) for d in edges)
        return Retrieval(plan, modules, findings, questions)


class Evaluator:
    """Approve only claims a stored fact supports; check the answer is closed."""

    def __init__(self, facts: FactStore):
        self.facts = facts

    def evaluate(self, retrieval: Retrieval) -> Verdict:
        graph = self.facts.load_graph()
        dependencies = graph.dependencies
        supported = {edge_finding(d) for d in dependencies if d.file is not None}
        approved = tuple(f for f in retrieval.findings if f in supported)
        blocked = tuple(f for f in retrieval.findings if f not in supported)
        covered = set(retrieval.modules) | {retrieval.plan.target}
        missing = sorted(
            {d.source for d in dependencies if d.target in covered} - covered
        )
        held = _open_questions_of(graph.modules, retrieval.plan.target)
        decisions = tuple(q for q in retrieval.open_questions if q in held)
        return Verdict(approved, blocked, tuple(missing), decisions)


class Explainer:
    """Lead with what could be affected, then the proof; the only model user."""

    def __init__(self, narrator: Narrator):
        self.narrator = narrator

    def explain(
        self, target: str, affected: tuple[str, ...], findings: tuple[Finding, ...]
    ) -> Narration:
        if not affected:
            return Narration(
                f"Nothing else in this project imports {target}, "
                "so a change to it stays inside it.",
                None,
            )
        headline = (
            f"Changing {target} could affect {len(affected)} other modules: "
            f"{', '.join(affected)}."
        )
        if not findings:
            return Narration(
                headline + " No file and line were recorded for these links.", None
            )
        narration = self.narrator.narrate(findings)
        return Narration(headline + "\n" + narration.text, narration.model)


def decision_text(questions: tuple[OpenQuestion, ...]) -> str:
    lines = [
        "Before you change this, a decision is open that the code does not settle:"
    ]
    for q in questions:
        where = f"{q.file}, line {q.line}"
        if q.symbol is not None:
            where += f", in {q.symbol}"
        lines.append(f"- {q.text[:1].upper()}{q.text[1:]} ({where})")
    lines.append("Which should it be? Tell me, and I will record your decision.")
    return "\n".join(lines)


def _open_questions_of(modules, target: str) -> tuple[OpenQuestion, ...]:
    return next((m.open_questions for m in modules if m.name == target), ())


def _resolve_concept(words: set[str], modules) -> Resolution | None:
    found = {}
    for module in modules:
        hits = _concept_hits(words, module)
        if hits:
            found[module.name] = hits
    if not found:
        return None
    leading = [name for name, hits in found.items() if any(hits.values())]
    if len(found) == 1 or len(leading) == 1:
        target = next(iter(found)) if len(found) == 1 else leading[0]
        return Resolution(
            target, None, f"it defines {', '.join(sorted(found[target]))}"
        )
    options = ", ".join(
        f"{name} ({', '.join(sorted(found[name]))})" for name in sorted(found)
    )
    return Resolution(
        None, f"Your question could mean: {options}. Which one should I trace?"
    )


def _concept_hits(words: set[str], module: Module) -> dict[str, bool]:
    """Map each defined name a question word matches to whether it matched first."""
    hits = {}
    for name in module.defines:
        parts = [p for p in name.lower().split("_") if p]
        matched = [i for i, part in enumerate(parts) if _stem_match(words, part)]
        if matched:
            hits[name] = matched[0] == 0
    return hits


def _stem_match(words: set[str], part: str) -> bool:
    for word in words:
        short, long = sorted((word, part), key=len)
        if len(short) >= MIN_STEM and long.startswith(short):
            return True
    return False


def _listing(names: list[str]) -> str:
    listing = ", ".join(names[:MAX_LISTED])
    if len(names) > MAX_LISTED:
        listing += f", and {len(names) - MAX_LISTED} more"
    return listing
