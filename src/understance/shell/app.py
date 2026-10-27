"""The composition root: wire the adapters to the agents and answer one request."""

import json
import secrets
import sys
import time
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path

from understance.adapters.csv_fact_store import CsvFactStore
from understance.adapters.fallback_fact_store import FallbackFactStore
from understance.adapters.hmem_memory import HMemMemoryStore
from understance.adapters.nightshift_narrator import (
    NightshiftClient,
    NightshiftNarrator,
)
from understance.adapters.template_narrator import TemplateNarrator
from understance.adapters.zetaris_fact_store import ZetarisClient, ZetarisFactStore
from understance.domain.answer import Answer, AnswerStatus, Decision
from understance.orchestration.orchestrator import TRACE_FIELDS, Orchestrator, assemble
from understance.ports.interfaces import DataQualityError
from understance.shell.capabilities import SCOPE_LINE

SUBJECT = "sample_app"
MAX_QUESTION_CHARS = 500
MAX_ANSWER_CHARS = 500
MAX_NAME_CHARS = 100
TRACE_DEFAULTS = {"retry_count": 0, "status": "ok"}


def load_settings(environ: Mapping[str, str], env_file: Path) -> dict[str, str]:
    """Sample mode set in the environment never reads .env; otherwise .env fills gaps."""
    if _is_sample(environ):
        return dict(environ)
    return {**read_env_file(env_file), **environ}


def read_env_file(path: Path) -> dict[str, str]:
    values = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip("'\"")
    return values


def utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_run_id() -> str:
    return f"run-{datetime.now(UTC):%Y%m%dT%H%M%SZ}-{secrets.token_hex(3)}"


class TraceFile:
    """Write each trace record, with every field in order, to logs/trace-<run_id>.jsonl."""

    def __init__(self, folder: Path, run_id: str, clock: Callable[[], str], echo):
        self.path = Path(folder) / f"trace-{run_id}.jsonl"
        self._run_id = run_id
        self._clock = clock
        self._echo = echo

    def __call__(self, record: dict) -> None:
        full = {
            name: record.get(name, TRACE_DEFAULTS.get(name)) for name in TRACE_FIELDS
        }
        full["timestamp"] = record.get("timestamp") or self._clock()
        full["run_id"] = self._run_id
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(full) + "\n")
        self._echo(
            f"[INFO] run_id={self._run_id} agent={full['agent_name']} "
            f"action={full['action']} status={full['status']}"
        )


class App:
    """Answer requests in sample mode (facts/, no model) or live mode (the sponsors)."""

    def __init__(
        self,
        env: Mapping[str, str],
        root: Path,
        logs: Path | None = None,
        clock: Callable[[], str] = utc_now,
        run_id: Callable[[], str] = new_run_id,
        echo: Callable[[str], None] = print,
        clients: tuple[ZetarisClient, NightshiftClient] | None = None,
    ):
        self.sample = _is_sample(env)
        self.mode = "sample" if self.sample else "live"
        self._facts = Path(root) / "facts"
        self._logs = Path(logs) if logs else Path(root) / "logs"
        self._clock = clock
        self._run_id = run_id
        self._echo = echo
        self.memory = HMemMemoryStore(
            self._logs / "memory", SUBJECT, lambda: int(time.time() * 1000)
        )
        if not self.sample:
            self._zetaris, self._nightshift = clients or (
                ZetarisClient.from_env(env),
                NightshiftClient.from_env(env),
            )

    def handle(self, request) -> tuple[int, dict]:
        problem = _problem(request)
        if problem:
            return 400, _error("bad_request", problem)
        run_id = self._run_id()
        trace = TraceFile(self._logs, run_id, self._clock, self._echo)
        try:
            orchestrator = self._assemble(trace)
            answer = orchestrator.run(request["question"].strip(), run_id)
            if "decision" in request:
                return self._decide(orchestrator, answer, request["decision"], trace)
            return 200, self._json(answer, trace)
        except DataQualityError as e:
            return 422, _error("data_quality", str(e), run_id)
        except Exception as e:  # noqa: BLE001 (every other failure is a structured error)
            trace(
                {
                    "agent_name": "App",
                    "action": "error",
                    "status": "error",
                    "output_summary": type(e).__name__,
                }
            )
            return 500, _error(
                "internal", f"the run failed ({type(e).__name__})", run_id
            )

    def _assemble(self, trace: TraceFile) -> Orchestrator:
        offline = CsvFactStore(self._facts)
        if self.sample:
            return assemble(
                offline, TemplateNarrator(), trace, self._clock, self.memory
            )
        zetaris = ZetarisFactStore(self._zetaris, offline, log=trace)
        store = FallbackFactStore(zetaris, offline, log=trace)
        narrator = NightshiftNarrator(self._nightshift, log=trace)
        return assemble(store, narrator, trace, self._clock, self.memory)

    def _decide(self, orchestrator, answer: Answer, decision: dict, trace):
        if (
            answer.status is not AnswerStatus.NEEDS_DECISION
            or len(answer.open_questions) != 1
        ):
            message = "this question has no single open decision to record"
            return 409, _error("nothing_to_decide", message, answer.run_id)
        (question,) = answer.open_questions
        self.memory.record_decision(
            Decision(
                question,
                decision["answer"].strip(),
                decision["decided_by"].strip(),
                self._clock(),
            )
        )
        trace(
            {
                "agent_name": "Owner",
                "action": "record_decision",
                "input_summary": f"{question.file}, line {question.line}",
                "output_summary": "decision recorded in H-MEM memory",
                "target_agent": "Evaluator",
                "status": "recorded",
            }
        )
        return 200, self._json(orchestrator.run(answer.question, answer.run_id), trace)

    def _json(self, answer: Answer, trace: TraceFile) -> dict:
        return {
            "run_id": answer.run_id,
            "mode": self.mode,
            "status": answer.status.value,
            "question": answer.question,
            "target": answer.target,
            "affected": list(answer.affected),
            "answer": answer.text,
            "findings": [
                {
                    "summary": f.summary,
                    "file": f.evidence[0].file,
                    "line": f.evidence[0].line_start,
                }
                for f in answer.findings
            ],
            "blocked": len(answer.blocked),
            "open_questions": [
                {"file": q.file, "line": q.line, "symbol": q.symbol, "text": q.text}
                for q in answer.open_questions
            ],
            "decisions": [
                {
                    "file": d.question.file,
                    "line": d.question.line,
                    "answer": d.answer,
                    "decided_by": d.decided_by,
                    "decided_at": d.decided_at,
                }
                for d in answer.decisions
            ],
            "model": answer.model,
            "scope": SCOPE_LINE,
            "trace_file": trace.path.name,
        }


def _is_sample(env: Mapping[str, str]) -> bool:
    return str(env.get("SAMPLE_MODE", "")).strip().lower() == "true"


def _problem(request) -> str | None:
    if not isinstance(request, dict):
        return "the request must be a JSON object"
    question = request.get("question")
    if not isinstance(question, str) or not question.strip():
        return "question is required: a non-empty string"
    if len(question) > MAX_QUESTION_CHARS:
        return f"question is longer than {MAX_QUESTION_CHARS} characters"
    if "decision" not in request:
        return None
    decision = request["decision"]
    if not isinstance(decision, dict):
        return "decision must be an object with answer and decided_by"
    for name, limit in (("answer", MAX_ANSWER_CHARS), ("decided_by", MAX_NAME_CHARS)):
        value = decision.get(name)
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            return f"decision.{name} is required: a non-empty string of at most {limit} characters"
    return None


def _error(kind: str, message: str, run_id: str | None = None) -> dict:
    body = {"error": {"type": kind, "message": message}}
    if run_id:
        body["run_id"] = run_id
    return body


def stderr_echo(line: str) -> None:
    print(line, file=sys.stderr)
