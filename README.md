# Understance

**Understand before you change.**

You own every line of your software. Do you know which line, if changed, will quietly break three other features?

If an AI wrote most of your app, or the person who built it has moved on, nobody can tell you. Not with proof.

Understance can. Name the change you want ("add customer cancellation"), and it shows you every part of the app that change could reach, with the file and line that prove each link. When the code leaves a real decision open, it stops and asks you instead of guessing. Answer once, and it remembers.

It never changes the code it reads, and never runs it. The reader only parses files, the agents hold read-only views, and a test checks the code it reads is byte-for-byte unchanged after every scenario.

Open Agent Hackathon 2026, Track 2: The Agent That Can Explain Why. Team: Wisdom by Design (solo, Shaela Beard).

---

## See it in 60 seconds (Python 3.11 or newer; no services, no keys)

Sample mode runs the real agents offline, from the facts committed in `facts/`, with no model, no network and no `.env`:

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
SAMPLE_MODE=true .venv/bin/python run.py "Add customer cancellation"
```

You get JSON back. The `answer` reads:

```
Changing sample_app.subscriptions could affect 5 other modules: sample_app.access, sample_app.api, sample_app.billing, sample_app.main, sample_app.notifications.
The proof, one import link at a time (8 links):
- sample_app.access imports sample_app.subscriptions (sample_app/access.py, line 14)
- sample_app.api imports sample_app.access (sample_app/api.py, line 3)
...
Before you change this, a decision is open that the code does not settle:
- Does cancellation take effect immediately, or at the end of the current billing period? The intended timing is not specified here. (sample_app/subscriptions.py, line 16, in cancel_subscription)
Which should it be? Tell me, and I will record your decision.
```

Answer it once:

```
SAMPLE_MODE=true .venv/bin/python run.py "Add customer cancellation" --decide "at the end of the billing period" --by Shaela
```

Ask again, and it says: "A decision recorded earlier settles this, so I am not asking again", with your answer, your name and the time.

Ask it what it can and cannot do:

```
.venv/bin/python run.py --capabilities
```

## The problem, and who it is for

AI made it easy to build software. It did not make it easy to understand what you built. When the builder leaves, the reasoning leaves too, and the next person changes the system one nervous guess at a time. AI assistants make this worse when they answer confidently with details they made up.

Understance is for the owner: the person who has to approve a change and live with the software afterwards, often without reading code.

## How it stays honest

One rule runs the whole tool: **the model proposes, the system verifies, and every claim traces to evidence.**

- **Facts come from reading the code, never from a model.** The reader parses Python files with `ast`. It never imports or runs them, never follows symlinks, and skips oversize or unreadable files by name.
- **Every claim is checked against the stored facts.** A claim with no fact behind it is blocked and logged, never explained.
- **The model gets one job, and a guard.** It writes one or two plain sentences from the verified links. It is given link summaries only, never files or line numbers. A fixed guard blocks any sentence that states a file, any number, or a module outside the verified links, and the model's sentence is labelled as model-written. The proof lines below it always come from the facts.
- **Open decisions stop the run.** A question the code leaves open (marked `# AMBIGUOUS:` in the code) is asked, not answered.
- **Limits are stated, with proof.** `run.py --capabilities` lists what it does, does not do and cannot reach; every line names the test that enforces it, and a test fails if one goes missing.

A real example of why the guard exists. Asked to rephrase a finding, the local model said billing "is located at sample_app/api.py, line 4". That is wrong. Under the guard, that sentence is never shown (Nightshift receipt `rcpt_req_es5lonm2`, Oct 27).

## The four agents

| Agent | Role | Reaches |
|---|---|---|
| Planner | Finds the module the question is about, by name or by the concepts a module defines (for example `cancel_subscription` for "cancellation"). Asks back when the question is unclear. | Facts (read-only) |
| Retriever | Pulls the facts in scope: direct importers first, everything that reaches the target when sent back. | Facts (read-only) |
| Evaluator | Approves only claims a stored fact supports and blocks the rest. Sends the plan back when the answer is not whole. Flags open decisions, and recalls decisions already recorded. | Facts and memory (both read-only) |
| Explainer | Leads with what could be affected, then the proof. The only agent that reaches a model. | Narrator (model) |

They work in a loop with up to 2 send-backs. Every step is a trace record (timestamp, run_id, agent_name, action, input_summary, output_summary, target_agent, model, confidence, retry_count, status) written to `logs/trace-<run_id>.jsonl`, with an `[INFO] run_id=` line as it happens. A real trace is in `output_examples/03_record_decision.trace.jsonl`.

## Sponsor technology

### Zetaris: the data layer
- Understance exports what it knows as six CSV files (`facts/`), registered in Zetaris as **three sources**: `understance_code` (modules, imports, defined names, open questions), `understance_git` (last change per file) and `understance_tests` (which tests cover which module).
- A **Unified Semantic Layer** joins them: `understance_usl.module` (one row per module with its file, last commit, last change and test count, across all three sources) and `understance_links.dependency` (every import link with its file and line).
- **The agents read through it** (`src/understance/adapters/zetaris_fact_store.py`, over the Zetaris REST API).
- **A data quality rule runs inside Zetaris on every run, before the agents see a fact:** every import link must point at a module that exists, at both ends. A broken link stops the run. It is in the trace each time.
- If Zetaris is unreachable, the run says so in the trace and answers from `facts/`. A failed quality rule is never hidden by that fallback.
- Live check (Oct 27, `scripts/check_zetaris.py`): the rule found 0 broken links, and every fact read through Zetaris matched `facts/` (7 modules, 12 links).

### Meterless: Nightshift and the H-MEM engine
- **Nightshift is the AI provider.** The Explainer's narrator calls the Meterless runtime (`/v1/chat/completions`, model `meterless/auto`, headers `meterless-app` and `meterless-scope`). Each request's receipt is logged: receipt id, routed model, privacy path, egress. On the build machine it routes to **Qwen 2.5 1.5B running locally**; the live check (receipt `rcpt_req_fploapv2`) shows privacy `local-only` and egress `none`: nothing left the Mac.
- **H-MEM (the Meterless engine used).** Understance **implements the Meterless H-MEM spec, verified with a pytest port of its core test cases.** It powers one feature: the owner's decisions, kept per repo in an append-only ledger (`logs/memory/<repo>.jsonl`) so an open question is asked once. A newer decision supersedes the older one; nothing is deleted; every entry records who and when. The port covers 11 of the 13 vectors in the spec's conformance file (record validation, feedback deltas, ranking order, the conflict gate, the ledger audit) in `tests/test_hmem_memory.py`; sleep and dreaming are not implemented. The Meterless TypeScript runner was not run against this Python code.
- **NVIDIA Nemotron:** not used. Nightshift's local model meets the provider requirement.

### Cursor
Not used.

## Run it live (Zetaris, Nightshift, H-MEM)

1. **Python 3.11 or newer**, then the venv and `pip install -r requirements.txt` as above.
2. **Zetaris** (local Docker, signed in): upload the six files in `facts/` to NDP File System `/file-store`; create three File Source & API sources (`understance_code`, `understance_git`, `understance_tests`); in each, Create Table (File store, CSV, NDP File System, `header=true`, `inferSchema=false`) and click **Create** after Preview (stopping at Preview reserves the name). Tables: `modules`, `dependencies_csv`, `defines_csv`, `open_questions` in `understance_code`; `git_history`; `test_map`. Then build the two USL tables above: every statement, in order, is in [`docs/ZETARIS_SETUP.md`](docs/ZETARIS_SETUP.md). Create an API token under Management, API Tokens.
3. **Nightshift** (Mac M1 to M4 edition from meterless.ai): start the local runtime, download a device model (we use Qwen 2.5 1.5B), and copy the Runtime API key from the console (Cmd+5). Keep Hotspot mode off.
4. **`.env`** (gitignored; start from `.env.example`): `ZETARIS_REST_URL=http://localhost:8888/api/v1.0`, `ZETARIS_ORG_ID=1`, `ZETARIS_API_KEY=<token>`, `METERLESS_BASE_URL=http://127.0.0.1:8088/v1`, `METERLESS_RUNTIME_TOKEN=<key>`.
5. Check each sponsor: `PYTHONPATH=src .venv/bin/python scripts/check_zetaris.py` and `PYTHONPATH=src .venv/bin/python scripts/check_nightshift.py`.
6. Run: `.venv/bin/python run.py "Add customer cancellation"`.

## Usage

- **One question:** `run.py "<question>"`. Add `--decide "<answer>" --by "<name>"` to record a decision. Add `--logs <folder>` to keep traces and memory elsewhere.
- **Server:** `run.py --serve` answers `POST /run`, `GET /capabilities` and `GET /health` on `0.0.0.0:$PORT` (default 8000).
- **Request:** `{"question": "...", "decision": {"answer": "...", "decided_by": "..."}}` (decision optional).
- **Response:** `run_id`, `mode`, `status` (`answered`, `needs_input`, `needs_decision`, `incomplete`), `question`, `target`, `affected`, `answer`, `findings` (summary, file, line), `blocked`, `open_questions`, `decisions`, `model`, `scope`, `trace_file`.
- **Errors** are JSON: `{"error": {"type", "message"}, "run_id"}` with types `bad_request` (400), `nothing_to_decide` (409), `data_quality` (422), `internal` (500, the error's type only), `configuration` (missing settings, with the advice to use sample mode).
- **Examples:** `input_examples/` holds three request bodies; `output_examples/` holds their answers and one trace.

## How we know it works

- **255 automated tests** (Oct 27), run with `.venv/bin/python -m pytest -q`. Every step was built test-first: the new tests were shown failing before the code existed, and defects were planted on purpose to prove the tests catch them.
- **7 evals** (`evals/`): golden scenarios with expected answers written by hand from the sample app's verified truth, including a question that says "delete subscriptions". The code being read is checked byte-for-byte unchanged after all of them.
- **`metadata.json`** names where each sponsor sits and its test; a test fails if a named file goes missing.
- **An architecture test** keeps the agents from ever importing a sponsor adapter, so Zetaris, Nightshift or H-MEM can each be swapped without touching the agents.
- **Pre-commit hooks** run lint (with complexity and length caps), formatting, the architecture test and the full test suite on every commit.

## Architecture

Clean architecture with four ports: `SourceReader`, `FactStore`, `Narrator`, `MemoryStore`.

```
src/understance/
  domain/         pure types: Module, Dependency, DependencyGraph, Finding, Evidence, Answer, Decision
  ports/          the four interfaces
  usecases/       AnalyzeRepo, ComputeBlastRadius
  orchestration/  the four agents, the orchestrator loop, read-only views of facts and memory
  adapters/       ast reader, CSV store, Zetaris store, fallback store, Nightshift narrator, template narrator, H-MEM memory
  shell/          the composition root: run modes, trace files, the HTTP server, the capabilities manifest
```

## Limitations

- Python only, read statically, at module level. Dynamic imports, reflection, generated code and other languages are named, not followed.
- The model guard blocks stated evidence (paths, numbers, unlisted modules); it does not judge a sentence's meaning. In one live run a sentence passed the guard but read as if the dependency ran the other way. That is why the model's sentence is labelled and the proof lines carry the answer.
- H-MEM holds decisions only; sleep, dreaming and mining are not implemented. The ledger is append-only by design, not tamper-proof.
- The server has no login and handles one request at a time. Run it on a trusted machine or network.
- Built and tested against the bundled sample app. Not production-ready.
- Not built: Docker, NVIDIA Nemotron, a change-brief export.

## Data

`sample_app/` is **synthetic**: a small subscription service written for this project inside the build window, with one deliberate import loop, one untested module and one open policy question. No real customer or personal data. `facts/` is generated from it by `scripts/export_facts.py`.

## AI and model usage

**Model (through Meterless Nightshift):** Qwen 2.5 1.5B, local. It writes the short plain-language summary and nothing else; planning, retrieval and verification run without a model, and sample mode uses no model at all.

**Agent framework:** none. The four agents run on a small orchestrator written for this project.

**Development tools:** Built with Claude Code (AI-directed). AI-assisted coding was used for scaffolding, tests, debugging, and documentation. Every change was checked against its tests and the build's review gates before it was committed. This is the single disclosure of the coding tool.

## Pre-existing work

None. Everything in this repository was written inside the build window (Oct 22 to 27, 2026).

## Third-party code and licences

- pytest: MIT
- ruff: MIT
- pre-commit: MIT

Runtime uses the Python standard library only. No third-party code is copied into this repository.
