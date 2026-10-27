# CONVENTIONS - names and structure (follow exactly; do not invent)
**Owner:** Shaela Beard · Understance · Open Agent Hackathon 2026 · Track 2
**Rule:** follow these names exactly in the schema, the code, and the user-facing output. Do NOT invent file names, class names, trace fields, id formats, or env-var names. If a name is not covered here, STOP and ask Shaela; do not make one up.
**Last updated:** Oct 26, 2026. Starter set; extend as real decisions are made (record each in docs/DECISIONS.md).

## Product and package
- Product name: **Understance** (user-facing).
- Python package name: **`understance`** (code lives under `src/understance/`). The product name and package name are the same by choice; this is stable even if the brand display name ever changes.
- Domain: understance.dev (brand consistently as understance.dev).

## Ubiquitous language (one glossary, used identically in schema, agents, and output)
- **Fact** - an observed, evidence-backed, deterministically-derived record about the subject repo.
- **Finding** - a conclusion drawn from facts; every Finding is flagged observed vs inferred and carries at least one Evidence id.
- **Evidence** - a concrete pointer that backs a claim (file path, and ideally a line span or hash).
- **Provenance** - the record of entity/activity/agent behind a fact or decision (PROV sense): what produced it, when, from what.
- **Decision** - a fork the user settled; attributed to the user, with options presented neutrally.
- **Dependency** - a directed relationship between modules or symbols (who imports/uses whom).
- **BlastRadius** - the set of things a change to a given target could affect (reverse dependencies and the forward set), with evidence per edge.

## Domain entities (Phase 1.1; pure, no outside imports)
`Module`, `Symbol`, `Dependency`, `DependencyGraph` (exposes `orphans()`), `Finding`, `FindingKind`, `Evidence`, `Provenance`.
A `Finding` is flagged observed vs inferred via `FindingKind` (`OBSERVED`, `INFERRED`) and references its `Evidence` by object (no id fields until Phase 3.1).

## Source and test files
- Cluster per file: entities that belong together live in one module file. `src/understance/domain/graph.py` holds `Module`, `Dependency` (with `line` and `file`, excluded from equality), `DependencyGraph` (exposes `orphans()`, `dependents_of(name)`, `dependencies_of(name)`), and `BlastRadius`. Symbol is deferred past the hackathon (Oct 27).
- Test mirrors module: each source file has one matching test file in `tests/`. `graph.py` is covered by `tests/test_dependency_graph.py` (named for its cluster).
- Domain module files: `graph.py` holds `Module`, `Dependency`, `DependencyGraph`, `BlastRadius`; `answer.py` holds `Answer`, `AnswerStatus`, `Narration`; `finding.py` holds `Evidence`, `Finding`, `FindingKind`, `Provenance`. Tests: `tests/test_dependency_graph.py`, `tests/test_answer.py`, and `tests/test_finding.py`.

## The four ports (Phase 1.2; interfaces only)
`SourceReader`, `FactStore`, `Narrator`, `MemoryStore`. Third-party libraries (ast, SQLite, Zetaris, Nightshift, H-MEM, coverage, pytest) live ONLY inside adapters that implement these ports.

## Adapters (Phase 2.2 on)
- `src/understance/adapters/ast_source_reader.py` holds `ASTSourceReader` (implements `SourceReader`; constructor option `max_file_bytes`, default 1,000,000). Beyond the port it exposes `scope_line(root)`, the plain-language statement of what a read covered and what it could not. Tested by `tests/test_ast_source_reader.py`.

- `src/understance/adapters/template_narrator.py` holds `TemplateNarrator` (implements `Narrator`; sample mode, model "template (no model)"). Tested by `tests/test_template_narrator.py`.

## Use cases (Phase 2.3 on)
- `src/understance/usecases/analyze_repo.py` holds `AnalyzeRepo(reader, store)` with `run(root)`; tested by `tests/test_analyze_repo.py`.
- `src/understance/usecases/compute_blast_radius.py` holds `ComputeBlastRadius(store)` with `run(target)`; tested by `tests/test_compute_blast_radius.py`.
- Shared test doubles: `tests/fakes.py` holds `FakeSourceReader` and `FakeFactStore`.

## Agents (Phase 2.5)
`Planner`, `Retriever`, `Evaluator`, `Explainer`. Only the Explainer calls the model (through the Nightshift adapter). Each agent is constructed with only the ports its role needs. (The model-reaching port is Narrator; the Explainer agent reaches the model only through the Narrator port.)
- Files: `src/understance/orchestration/agents.py` (the four agents, `Scope`, `Plan`, `Resolution`, `Retrieval`, `Verdict`), `orchestration/read_only_fact_store.py` (`ReadOnlyFactStore`), `orchestration/orchestrator.py` (`Orchestrator`, `assemble`). Tests: `tests/test_agents.py`, `tests/test_read_only_fact_store.py`, `tests/test_orchestrator.py`.
- Words: **direct scope** (only the modules that import the target), **transitive scope** (everything that reaches it through others), **send back** (the Evaluator returns the plan to the Planner because the answer is not whole), **widen** (the Planner moves from direct to transitive), **blocked** (a claim no stored fact supports; logged, never explained), **incomplete** (the answer could not be closed within 2 send-backs), **needs input** (the agent stops and asks).

## JSONL trace fields (per agent action, to stdout and logs/)
`timestamp`, `run_id`, `agent_name`, `action`, `input_summary`, `output_summary`, `target_agent`, `model`, `confidence`, `retry_count`, `status` (aligned with the Technical Execution Guide, Oct 27). No raw subject-repo source in a trace; summaries and evidence ids only.

## Environment variables (names fixed; values only in a local .env, never committed)
`ZETARIS_REST_URL`, `ZETARIS_ORG_ID`, `ZETARIS_API_KEY`, `METERLESS_BASE_URL`, `METERLESS_RUNTIME_TOKEN`, `METERLESS_MODEL` (default `meterless/auto`), `SAMPLE_MODE`, `LOG_LEVEL`, `PORT`.

## Folder skeleton (Phase 0.5; create exactly these)
```
src/understance/domain/
src/understance/ports/
src/understance/usecases/
src/understance/adapters/
src/understance/orchestration/     (orchestrator + agents; the shell run.py / API lives here or in a shell/ sibling)
tests/
sample_app/            (the trusted subscription-SaaS fixture; its own tests in sample_app/tests/ are test evidence, not graph modules)
evals/                 (the 7 golden-set scenarios + hand-authored expected outputs)
input_examples/
output_examples/
logs/                  (runtime JSONL traces; gitignored)
docs/
```
Dependency management: pip + venv + `requirements.txt`. Web framework: FastAPI.
Test import path: `pytest.ini` at the repo root sets `pythonpath = src`, so tests import `understance...` directly. No `pyproject.toml` (by choice; tool config lives in `pytest.ini` and `ruff.toml`).

## Code health (enforced by the pre-commit hook; config in `ruff.toml`)
- Linter and formatter: ruff (`ruff-check`, `ruff-format`), ruff's default rules plus the caps below. Default rules include unused-import (F401).
- Complexity cap: mccabe C901, `max-complexity = 10` per function.
- Function-length cap: PLR0915 (too-many-statements), ruff default `max-statements = 50` per function. This counts statements, not lines.
- Each cap was shown to block a planted violation (Oct 26, Step 0.6). Architecture and governance test runs join the hook at 1.3 and 2.6, a dedicated dead-code detector at 2.6.

## Instruction style (Oct 27)
- Build instructions are direct, exact, numbered steps. The instruction body names no tool and addresses no one ("do X", not "<tool>, do X"); only the framing around an instruction says where it goes.
- Supersedes the earlier "<tool>, [ACTION] because [REASON]" opening line carried over from a prior project's protocol. That format is retired here.
- The one sanctioned mention of the coding tool in this repo is the README's AI-usage line.

## Pending (not yet decided; STOP and ask before inventing)
- **Evidence / fact id format** - must be stable and deterministic; the exact scheme is set at the FactStore schema step (Phase 3.1). Until then, do not invent an id format.
- Any name not listed above.

---
*One topic, one home. When a new name is decided, add it here and record the decision in docs/DECISIONS.md. Follow exactly; if it is not here, ask.*
