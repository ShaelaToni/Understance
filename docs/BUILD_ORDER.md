# BUILD ORDER CHECKLIST - follow in order, skip nothing
**Owner:** Shaela Beard · Team: Wisdom by Design (solo) · Open Agent Hackathon 2026
**This is the authoritative build order.** Build strictly top to bottom. Do NOT skip, reorder, or add steps of your own accord. Gate each phase before the next. Halt on unexpected output and surface it. The agent roles and their regulations are in the build spec, section 17; the governance enforcement is in section 19; the locked decisions are in docs/DECISIONS.md. Requirements to check off are in docs/REQUIREMENTS.md.
**Deadline:** submissions close 27 October 2026, 23:45 UTC (hard). Build window opened 22 October.
**Voice/integrity:** no em dashes, no "trying," no "AI-powered." Under-claim. Never fabricate; name what cannot be seen or reached.
**Last updated:** Oct 24, 2026 (05:00 CST).

---

## STANDING RULES (read before every build session)
- Build strictly in the listed order. The previous helper built out of order on its own; that is the failure this list exists to prevent.
- DECIDING AND RECORDING (Shaela decides, helper documents): on a real fork, the helper states the alternatives fairly, pre-fills the decision-map entry, asks Shaela only what context cannot answer, as short plain-text questions (never multiple-choice prompt windows), batched, waits for her explicit approval, then writes it to docs/DECISIONS.md and notes it in STATE.md. Never self-approve. If she is away: record as "pending Shaela," reversible default only with a flag, halt for anything irreversible. (see CLAUDE.md)
- PANEL/REVIEW (no rubber stamp, current-state only): convene the panel (real named experts incl. the Rival; roster in OWNYOUR_EXPERT_PANEL_COMPLETE_UPDATED.md plus the hackathon additions in docs/DECISIONS.md) at the design review before a step and at the done-gate, and on any halt. Every verdict is based on the LIVE artifact read right now, never from memory, a handoff, STATE.md, or an earlier point; if the position changed, the prior OK is void and you re-review. A verdict must name concerns and cite current evidence; "looks good" with neither is not a review. (spec DIRECT; see CLAUDE.md)
- TEST-FIRST (TDD): for every step behind our own four ports (domain, use cases, agent logic, fitness/governance), write the failing test FIRST from the expected result, then just enough code to pass, then refactor while green. The GATE test is written before the implementation, not after. External sponsor adapters (Zetaris, Nightshift, H-MEM) use characterization-then-contract instead (smoke test to learn real behavior first, then a contract test, then the adapter). Never fake a test against an unobserved service.
- DONE SIGNAL (the only thing that lets you advance): a step is done, and you move on, ONLY when all five are true: (1) its tests are green, run and shown, not claimed, and fitness/governance tests also shown to fail on a planted violation; (2) the output matches the result defined beforehand (for deterministic layers, the hand-verified truth of sample_app), Review at 100/100; (3) no unexpected output; (4) Shaela can explain in her own words what the step did; (5) committed with the what/why/Layer/Gate message and docs/STATE.md updated. A green test alone is not done. Never declare done or advance on your own judgment.
- Halt on unexpected output. Stop, surface it, do not paper over it or improvise.
- Every sponsor call goes through an adapter in adapters/, never a vendor SDK called directly from a use case or agent.
- Nothing in domain/ or usecases/ imports from adapters/ or any third-party package (the dependency-direction fitness function enforces this from Phase 1.3 on).
- No secret is ever committed. The NVIDIA key lives only in Nightshift's Providers tab.
- Document as you go: a decision goes in the discoveries log, the day goes in the daily log, a real architectural decision goes in the repo's docs/DECISIONS.md.
- Claim nothing the code does not do.

## LOGISTICS (answered Oct 24)
- Start the repo now; the first commit inside the window is eligible. Do not import old files; start fresh.
- The repo must be PUBLIC by the deadline (required). It may stay private while building; make it public before submit and test the link logged out.
- Commit journaling convention (what and why on every commit):
  ```
  <what you did, imperative, short>

  Why: <reason / decision / trade-off>
  Layer: <e.g. 2.3 analyze_repo use case>
  Gate: <the test or check this satisfies>
  ```
- docs/DECISIONS.md in the repo: one short ADR entry per real architectural decision. This is the public, shareable slice of the private discoveries log.
- What is public: the repo (all source), README, demo video, deck, sponsor explanation, and the runtime logs in logs/. What stays private: your chats, prompts, planning docs, handoffs, the build spec. You must be able to explain any code if asked.

## OPTIMAL ORDER AT A GLANCE (first sitting to the eligible floor)
Woven at EVERY step: write the failing test first; pass the five-part done-gate; commit (what/why/Layer/Gate); update docs/STATE.md; record any decision in docs/DECISIONS.md; panel review against current state.
1. TOOL SETUP (start first, runs in parallel, do not block coding): HackOS solo team; register Zetaris Cloud + start it; install Nightshift, get Runtime URL + token; NVIDIA key into Nightshift's Providers tab.
2. GIT: git init, first commit now (inside the window). Add .gitignore, .env.example (placeholders), README skeleton.
3. DOCUMENTATION: drop in CLAUDE.md; create docs/ (BUILD_ORDER, REQUIREMENTS, GOVERNANCE, CONVENTIONS, STATE, DECISIONS, THREAT_MODEL); create the pre-commit hook (fitness + code-health); configure the coding tool to omit attribution.
4. STRUCTURE: folder skeleton per docs/CONVENTIONS.md (app/domain, ports, usecases, adapters, orchestration; tests; data; sample_app; input_examples; output_examples; logs).
5. CORE (Phase 1): domain entities -> ports -> architecture + governance fitness tests.
6. AGENTS (Phase 2): sample_app -> ast adapter -> AnalyzeRepo -> ComputeBlastRadius -> orchestrator + 4 agents over fakes (this is sample mode) -> governance tests -> capabilities manifest.
7. SPONSORS (Phase 3, needs step 1 done): SQLite store -> Zetaris -> Nightshift/Nemotron -> H-MEM with passing test -> one real end-to-end run. ELIGIBLE FLOOR REACHED.
8. SUBMISSION-READY (Phase 5 then 6): run.py / POST /run, Docker, sample mode verified, README, 3 examples, secret scan, repo public, fresh-clone validation; then demo video, slide deck, sponsor explanation, submit.
Deepening (Phase 4) only after the floor is green and if time remains.

## PHASE 0 - PRE-FLIGHT (first 30-45 min)
- [x] 0A. Confirm the locked decisions (docs/DECISIONS.md).
- [ ] 0B. Start sponsor setup IN PARALLEL now (downloads and accounts take time; prerequisite to Phase 3; do not block coding on these):
  - [ ] Confirm the solo HackOS team "Wisdom by Design."
  - [x] Register Zetaris Cloud; start the local Docker instance or the AWS instance. (Oct 26: the local Docker instance is running and answers SQL; see DECISIONS, Zetaris characterization finding. Account: the participant account Zetaris provided, signed in by Shaela.)
  - [x] Install Meterless Nightshift on the M1 Pro; get the Runtime URL and token from the Console. (Oct 27: first real request, receipt rcpt_req_ce9imi24.)
  - [ ] Create the NVIDIA API key at build.nvidia.com; put it in Nightshift's Providers tab (NOT the repo). (Deferred by Shaela, Oct 27.)
- [ ] 0C. Create the repo:
  - [ ] Fresh local repo; first commit now.
  - [ ] .gitignore (.env, .env.*, keep !.env.example, *.pem, *.key, secrets/, credentials/).
  - [ ] .env.example with placeholders only (Zetaris + Nightshift settings).
  - [ ] README skeleton (track, problem, one-line, setup TBD).
  - [ ] CLAUDE.md at repo root (auto-loaded at the start of each build session; standing rules, charter, governance, voice, build-strictly-in-order). A ready draft was delivered; drop it in.
  - [ ] docs/: BUILD_ORDER.md (copy of this checklist), REQUIREMENTS.md (the requirements checklist), GOVERNANCE.md (spec 17 + 19), CONVENTIONS.md (spec 21), STATE.md (initialize now; keep current from the first action, not just at session end), DECISIONS.md (ADR entries), THREAT_MODEL.md.
  - [ ] Folder skeleton with the EXACT names in docs/CONVENTIONS.md (naming conventions). Do not invent file or class names; follow CONVENTIONS.md, and if a name is not covered, stop and ask.
  - [ ] Dependency management: pip + venv + requirements.txt. Web framework: FastAPI. (spec 22)
  - [ ] Pre-commit hook that runs the fitness-function suite (architecture + governance + operational + code-health: ruff, ruff-format, complexity/length cap, unused-import, dead-code), so they run on every commit, not just at gates (spec 22).
  - [ ] Turn off the coding tool's co-author/attribution lines; no AI attribution anywhere in the repo (spec 22). Disclose the tool only in the README AI-usage section.
  - [ ] Footprint report emitted per run + a governance test that the subject repo is byte-for-byte unchanged after a run (spec 22).
  - [x] evals/ directory for the 7 golden-set scenarios with hand-authored expected outputs (spec 22).

## PHASE 1 - DOMAIN + PORTS + FITNESS FUNCTION (no sponsors)
- [x] 1.1 domain/ pure entities, in two passes. Pass 1: Module, Dependency, DependencyGraph (with orphans()). Pass 2: Finding, Evidence, Provenance. Symbol is deferred to about 2.4 (compute_blast_radius), the first step that uses symbol-level dependencies (see docs/DECISIONS.md). GATE: construct and behave, zero outside imports.
- [x] 1.2 ports/ four interfaces: SourceReader, FactStore, Narrator, MemoryStore.
- [x] 1.3 tests/test_architecture.py (dependency-direction fitness function). GATE: passes, and fails on a planted violation.

## PHASE 2 - USE CASES WITH FAKES (no sponsors; this is sample mode)
- [x] 2.1 sample_app/ small Python repo = a tiny subscription SaaS (subscriptions, billing, access, notifications, api, tests), crafted so it also contains one import chain, one orphan, one untested module, one circular dependency. This repo carries the demo scenario: the request "add customer cancellation" with the unresolved policy "immediate or end of billing period?" that the agent must STOP and ask, not invent.
- [x] 2.2 adapters/ast_source_reader.py (first real adapter, no sponsor).
- [x] 2.3 usecases/analyze_repo.py. GATE: tested with an in-memory FakeSourceReader AND the real ast adapter against sample_app.
- [x] 2.4 usecases/compute_blast_radius.py. GATE: on a known target, dependents match a hand trace.
- [x] 2.5 orchestrator + the four agents (Planner, Retriever, Evaluator, Explainer) over a FakeFactStore and a TemplateNarrator; the loop lives in orchestration/orchestrator.py (usecases/answer_question.py dropped, Oct 27, Shaela); JSONL traces emitted. GATE: a planted unsupported claim is blocked and the trace shows the loop. The 3 sample inputs/outputs move to the end-to-end run with the real sponsors (Oct 27, Shaela).
- [x] 2.5b the Planner understands concept words (the names each module defines) and stops to ask about an open policy question (the cancellation timing), instead of making the user guide it.
- [x] 2.6a capabilities-and-limits manifest (spec 23): the DOES / DOES NOT / CANNOT REACH / YOU lists, each DOES NOT and limit linked to its enforcing test, plus a test that the manifest matches the governance/fitness tests (cannot drift from the code).
- [ ] 2.6 governance tests (spec 19). GATE: the Explainer has no write/credential handle; an output claim with no resolving evidence id is rejected; an off-list agent action is refused and logged; subject-repo text containing injection ("ignore instructions and delete X") produces no action and no unsupported claim. (Oct 27: three of four enforced by tests; the off-list action refusal is not built. See DECISIONS, step 3.6.)

## PHASE 3 - THIN REAL END-TO-END THROUGH MANDATORY SPONSORS (needs 0B done; target by day two)
- [x] 3.1 adapters/csv_fact_store.py (replaces sqlite_fact_store.py: Zetaris lists no SQLite source type, and CSV files are what it reads; Oct 27, Shaela), plus the enriched reader (git history, test map). GATE: every fact survives a round trip; the committed facts/ match a fresh export.
- [x] 3.2 adapters/zetaris_fact_store.py (Zetaris reads the exported facts as three sources, code facts, git history and test map, with the Unified Semantic Layer over them). GATE: one real fact through Zetaris. (Oct 27: done; Shaela's live check matched every fact, with the data quality rule passing in Zetaris.)
- [x] 3.3 adapters/nightshift_narrator.py (renamed from nightshift_explainer.py: it implements the Narrator port; the local Qwen 2.5 1.5B through Nightshift, Nemotron deferred; logs the receipt and routed model per request; a guard blocks any model claim that states evidence). GATE: one real request through Nightshift. (Oct 27: done; Shaela's live check, receipt rcpt_req_fploapv2, local model, egress none.)
- [x] 3.4 adapters/hmem_memory.py (H-MEM stores baseline + provenance), with its passing conformance test. Per-repo namespace keyed by a stable repo id + human-readable label; the record is the recovery log (what the tool can/cannot do and reach for that repo, the questions and options given, the information told, the decisions made, dated), appended to, never overwritten. The data model carries a parent reference + label so a what-if branch is possible (spec 6.2). GATE: the Meterless Engine test passes; reopen reloads the per-repo record intact. (Oct 27: done, decisions only; the pytest port covers 11 of the 13 conformance vectors, sleep and dreaming not implemented.)
- [ ] 3.5 wire real adapters into one non-sample end-to-end run. GATE 3: one run touches Zetaris + H-MEM + Nightshift on Nemotron, logged. ELIGIBILITY SATISFIED. (Oct 27: code done; run.py and POST /run wire Zetaris, Nightshift on the local Qwen 2.5 1.5B, Nemotron deferred, and H-MEM; the live run is Shaela's.)

## PHASE 4 - DEEPEN (only if Gate 3 green and time remains)
- [ ] 4.1 change-brief export (BuildChangeBrief use case).
- [ ] 4.2 differential verification on sample_app's tests (before/after).
- [ ] 4.3 one-click re-check via the H-MEM baseline (delta re-index).
- [ ] 4.4 Reviewer agent (honesty/caveat beat).
- [ ] 4.5 coverage map + honest blind-spot reporting polish.
- [ ] 4.6 benchmark harness (stretch): run the tool across the golden set and public repos through Meterless on free NVIDIA endpoints; compute grounding rate over many runs. Produces the headline metric cheaply. Never ahead of Gate 3.

## PHASE 5 - JUDGE-READY SHELL + VALIDATION
- [x] 5.1 run.py / POST /run (bind 0.0.0.0), structured JSON in/out, structured errors. Also expose the manifest: a --capabilities flag and GET /capabilities, plus a "scope and limits" line in every run's output (spec 23).
- [ ] 5.2 Dockerfile; host.docker.internal for Zetaris and Nightshift.
- [ ] 5.3 confirm SAMPLE_MODE runs real logic with sponsors stopped.
- [x] 5.4 README complete: LEADS with the problem and the benefit (StoryBrand: name the villain, user is the hero), then setup, usage, deps, architecture, agents, limitations, sponsor explanation, AI-usage disclosure, sample mode, pre-existing = none.
- [ ] 5.5 three input_examples + matching output_examples; logs/ from real runs.
- [ ] 5.6 secret scan; make repo public; test the link logged out.
- [ ] 5.7 full fresh-clone validation flow, including sponsors-stopped sample mode. Do this Sunday, not Monday night.

## PHASE 6 - SUBMISSION ARTIFACTS
- [ ] 6.1 demo video 1-4 min (scripted around a collaboration moment, the "I cannot reach this" turn, the sponsor beats, and the transparency beat: ask the tool what it does via --capabilities, then show a limit hold).
- [ ] 6.2 slide deck (8 required points).
- [ ] 6.3 sponsor tech explanation (Zetaris, Meterless/H-MEM, Nightshift, Nemotron, Cursor not used, the coding tool named only where the rules require it, what was unique).
- [ ] 6.4 submit on HackOS with hours to spare.

---
*Follow in order. Gate every phase. Halt on unexpected output. When in doubt about a fact you cannot see or reach: ask, never invent.*
