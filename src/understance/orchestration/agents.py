import re
from dataclasses import dataclass
from enum import Enum

from understance.domain.answer import Narration
from understance.domain.finding import Finding
from understance.ports.interfaces import FactStore, Narrator
from understance.usecases.compute_blast_radius import ComputeBlastRadius, edge_finding

MAX_LISTED = 20
WORD = re.compile(r"[a-z_][a-z0-9_.]*")


class Scope(Enum):
    DIRECT = "direct"
    TRANSITIVE = "transitive"


@dataclass(frozen=True)
class Resolution:
    target: str | None
    question_back: str | None


@dataclass(frozen=True)
class Plan:
    target: str
    scope: Scope


@dataclass(frozen=True)
class Retrieval:
    plan: Plan
    modules: tuple[str, ...]
    findings: tuple[Finding, ...]


@dataclass(frozen=True)
class Verdict:
    approved: tuple[Finding, ...]
    blocked: tuple[Finding, ...]
    missing: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.missing


class Planner:
    """Find the module a question names, then plan narrow and widen on request."""

    def __init__(self, facts: FactStore):
        self.facts = facts

    def resolve(self, question: str) -> Resolution:
        words = set(WORD.findall(question.lower()))
        names = sorted(m.name for m in self.facts.load_graph().modules)
        matches = [
            n for n in names if n.lower() in words or n.split(".")[-1].lower() in words
        ]
        if len(matches) == 1:
            return Resolution(matches[0], None)
        if matches:
            return Resolution(
                None,
                f"Your question names more than one module: {_listing(matches)}. "
                "Which one should I trace?",
            )
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
        if plan.scope is Scope.TRANSITIVE:
            radius = ComputeBlastRadius(self.facts).run(plan.target)
            return Retrieval(plan, radius.dependents, radius.findings)
        edges = sorted(
            (
                d
                for d in self.facts.load_graph().dependencies
                if d.target == plan.target and d.file is not None
            ),
            key=lambda d: d.source,
        )
        modules = tuple(sorted({d.source for d in edges}))
        return Retrieval(plan, modules, tuple(edge_finding(d) for d in edges))


class Evaluator:
    """Approve only claims a stored fact supports; check the answer is closed."""

    def __init__(self, facts: FactStore):
        self.facts = facts

    def evaluate(self, retrieval: Retrieval) -> Verdict:
        dependencies = self.facts.load_graph().dependencies
        supported = {edge_finding(d) for d in dependencies if d.file is not None}
        approved = tuple(f for f in retrieval.findings if f in supported)
        blocked = tuple(f for f in retrieval.findings if f not in supported)
        covered = set(retrieval.modules) | {retrieval.plan.target}
        missing = sorted(
            {d.source for d in dependencies if d.target in covered} - covered
        )
        return Verdict(approved, blocked, tuple(missing))


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


def _listing(names: list[str]) -> str:
    listing = ", ".join(names[:MAX_LISTED])
    if len(names) > MAX_LISTED:
        listing += f", and {len(names) - MAX_LISTED} more"
    return listing
