from collections.abc import Callable

from understance.domain.answer import Answer, AnswerStatus
from understance.orchestration.agents import (
    Evaluator,
    Explainer,
    Plan,
    Planner,
    Retrieval,
    Retriever,
    Verdict,
)
from understance.orchestration.read_only_fact_store import ReadOnlyFactStore
from understance.ports.interfaces import FactStore, Narrator

MAX_SEND_BACKS = 2
TRACE_FIELDS = (
    "timestamp",
    "run_id",
    "agent_name",
    "action",
    "input_summary",
    "output_summary",
    "target_agent",
    "model",
    "confidence",
    "retry_count",
    "status",
)


class Orchestrator:
    """Run the four agents over one question and trace every step."""

    def __init__(
        self,
        planner: Planner,
        retriever: Retriever,
        evaluator: Evaluator,
        explainer: Explainer,
        trace: Callable[[dict], None],
        clock: Callable[[], str],
    ):
        self.planner = planner
        self.retriever = retriever
        self.evaluator = evaluator
        self.explainer = explainer
        self._trace = trace
        self._clock = clock

    def run(self, question: str, run_id: str) -> Answer:
        log = _Log(self._trace, self._clock, run_id)
        resolution = self.planner.resolve(question)
        if resolution.target is None:
            log(
                "Planner",
                "resolve_target",
                question,
                resolution.question_back,
                "user",
                status="needs_input",
            )
            return Answer(
                run_id,
                question,
                AnswerStatus.NEEDS_INPUT,
                None,
                (),
                resolution.question_back,
                (),
                (),
                None,
            )
        plan = self.planner.plan(resolution.target)
        log("Planner", "plan", question, _plan_summary(plan), "Retriever")
        retrieval, verdict, send_backs = self._loop(plan, log)
        if not verdict.complete:
            text = (
                f"I could not close the answer after {send_backs + 1} passes. "
                f"Not covered: {', '.join(verdict.missing)}."
            )
            log(
                "Evaluator",
                "evaluate",
                _retrieval_summary(retrieval),
                text,
                "user",
                confidence=_confidence(verdict),
                retry=send_backs,
                status="incomplete",
            )
            return Answer(
                run_id,
                question,
                AnswerStatus.INCOMPLETE,
                plan.target,
                (),
                text,
                (),
                verdict.blocked,
                None,
            )
        log(
            "Evaluator",
            "evaluate",
            _retrieval_summary(retrieval),
            f"approved {len(verdict.approved)}, blocked {len(verdict.blocked)}",
            "Explainer",
            confidence=_confidence(verdict),
            retry=send_backs,
            status="approved",
        )
        narration = self.explainer.explain(
            plan.target, retrieval.modules, verdict.approved
        )
        log(
            "Explainer",
            "explain",
            f"{len(verdict.approved)} approved findings",
            f"{len(retrieval.modules)} modules explained",
            "user",
            model=narration.model,
            retry=send_backs,
        )
        return Answer(
            run_id,
            question,
            AnswerStatus.ANSWERED,
            plan.target,
            retrieval.modules,
            narration.text,
            verdict.approved,
            verdict.blocked,
            narration.model,
        )

    def _loop(self, plan: Plan, log: "_Log") -> tuple[Retrieval, Verdict, int]:
        send_backs = 0
        while True:
            retrieval = self.retriever.retrieve(plan)
            log(
                "Retriever",
                "retrieve",
                _plan_summary(plan),
                _retrieval_summary(retrieval),
                "Evaluator",
                retry=send_backs,
            )
            verdict = self.evaluator.evaluate(retrieval)
            if verdict.complete or send_backs >= MAX_SEND_BACKS:
                return retrieval, verdict, send_backs
            log(
                "Evaluator",
                "evaluate",
                _retrieval_summary(retrieval),
                f"not covered: {', '.join(verdict.missing)}",
                "Planner",
                confidence=_confidence(verdict),
                retry=send_backs,
                status="sent_back",
            )
            plan = self.planner.widen(plan)
            send_backs += 1
            log(
                "Planner",
                "widen",
                _plan_summary(retrieval.plan),
                _plan_summary(plan),
                "Retriever",
                retry=send_backs,
            )


class _Log:
    """Write one trace record with exactly TRACE_FIELDS, in order."""

    def __init__(
        self, trace: Callable[[dict], None], clock: Callable[[], str], run_id: str
    ):
        self._trace = trace
        self._clock = clock
        self._run_id = run_id

    def __call__(
        self,
        agent_name,
        action,
        input_summary,
        output_summary,
        target_agent,
        *,
        model=None,
        confidence=None,
        retry=0,
        status="ok",
    ):
        values = (
            self._clock(),
            self._run_id,
            agent_name,
            action,
            input_summary,
            output_summary,
            target_agent,
            model,
            confidence,
            retry,
            status,
        )
        self._trace(dict(zip(TRACE_FIELDS, values, strict=True)))


def _plan_summary(plan: Plan) -> str:
    return f"{plan.target}, {plan.scope.value} scope"


def _retrieval_summary(retrieval: Retrieval) -> str:
    return f"{len(retrieval.modules)} modules, {len(retrieval.findings)} findings"


def _confidence(verdict: Verdict) -> float:
    total = len(verdict.approved) + len(verdict.blocked)
    return round(len(verdict.approved) / total, 2) if total else 1.0


def assemble(
    store: FactStore,
    narrator: Narrator,
    trace: Callable[[dict], None],
    clock: Callable[[], str],
) -> Orchestrator:
    facts = ReadOnlyFactStore(store)
    return Orchestrator(
        Planner(facts),
        Retriever(facts),
        Evaluator(facts),
        Explainer(narrator),
        trace,
        clock,
    )
