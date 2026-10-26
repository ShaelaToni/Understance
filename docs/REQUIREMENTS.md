# REQUIREMENTS CHECKLIST - find it, check it off
**Owner:** Shaela Beard · Team: Wisdom by Design (solo) · Open Agent Hackathon 2026
**Purpose:** every requirement that must be TRUE to be eligible, scoreable, and complete, as checkboxes, with the rule reference. Check these off as the build satisfies them. Separate from the build ORDER (how to build) in docs/BUILD_ORDER.md.
**Deadline:** 27 October 2026, 23:45 UTC (hard). **Track:** 2, The Agent That Can Explain Why.
**Key dates:** build window 22 Oct 00:00 UTC to 27 Oct 23:45 UTC; judging opens 28 Oct; results 6 Nov 16:00 UTC.
**Last updated:** Oct 25, 2026.

> **Oct 25 reconciliation, confirmed against the authoritative Submission Requirements page (last updated Oct 23).** REQUIRED for eligibility: Zetaris as the data layer; at least one Meterless Engine (H-MEM) in a working feature with a passing test; AND Meterless Nightshift as the primary AI provider (the Submission Requirements page, section 4, bundles Nightshift-as-provider into the Meterless requirement). NVIDIA/Nemotron is OPTIONAL and matters only for the Best-use-of-Nemotron award (DGX Spark); route it through Nightshift and log the model. Cursor is optional. This CORRECTS an earlier same-day over-reading that briefly listed Nightshift-as-provider as optional: the staff note that you may run local models or another cloud provider "inside Nightshift" means the MODEL Nightshift serves can be non-NVIDIA, not that Nightshift itself can be skipped. Our architecture already uses Nightshift as the primary provider (the Explainer calls through it), so this is a label fix, not a build change. Where this and the Official Rules differ, the Official Rules apply.

---

## A. ELIGIBILITY AND ADMIN (missing any = disqualified)
- [x] Registered before 22 Oct 23:45 UTC (done day 1)
- [x] One account; appear on only one team (rules 3, 5.2)
- [x] Solo team created in Team Finder on HackOS, "Wisdom by Design" (team of one), registered and visible (done day 1)
- [ ] Roster final before the FIRST submission is created (locks then) (rules 5.4), solo, so safe
- [ ] Exactly one primary track selected: Track 2 (rules 3, 6); can be changed anytime before the deadline
- [ ] Submitted on HackOS (Submissions in the sidebar) before 27 Oct 23:45 UTC (rules 10). Create early, refine until the deadline; ties break on Impact then submission timestamp

## B. MANDATORY SPONSOR TECH (rules 5, 6, 8.1, 16; Submission Requirements section 4)
**Required to be eligible (missing any = disqualified):**
- [ ] Zetaris integrated as the data layer, running, load-bearing (remove it and the agent breaks). State where Zetaris sits in the README and metadata.json so judges can score Sponsor Tech.
- [ ] At least one Meterless Engine (H-MEM) working in a real feature, with a PASSING test pointed to in the README. State which Engine in the README and metadata.json.
- [ ] Meterless Nightshift is the primary AI provider; a real request passes through it and returns a result. The model Nightshift routes to may be Nemotron or another model/provider, but Nightshift itself is required.

**Optional, scores points but not required for eligibility:**
- [ ] NVIDIA Nemotron via Nightshift, model logged per request. For the Best-use-of-Nemotron award only (DGX Spark), NOT an eligibility gate. No event credits (a key is available on request via the sponsor thread). For the award: README names which agent runs on which Nemotron model and what it does; demo shows it in a real run; a receipt/model log is linked from the README as proof.
- [ ] Cursor: optional coding tool; we use Claude Code instead and state that honestly.

## C. BUILD AND RUNNABLE (Technical 20, Demo 15) (Technical Execution Guide)
- [ ] Runs from a FRESH clone with a documented command, no manual fixing (judges who cannot run it cannot score it)
- [ ] Programmatic entry point (run.py or POST /run), not UI-only; structured JSON in and out
- [ ] Docker build succeeds; API binds 0.0.0.0; host.docker.internal reaches Zetaris and Nightshift
- [ ] No local GPU required (any Nemotron use through Nightshift hosted endpoints)
- [ ] A run finishes in minutes; timeouts on external calls; agent loops bounded
- [ ] No runtime installs or large downloads in the request path
- [ ] SAMPLE_MODE=true runs REAL logic with Zetaris and Nightshift stopped and an empty .env (the page frames this as the fallback when a service is unavailable)
- [ ] Failures return a structured error, not a crash or hang
- [ ] The demo path is not hardcoded or single-use; it works on a real run

## D. AGENT BEHAVIOR AND TRACES (Technical 20) (Strong/Weak examples)
- [ ] At least two named agents with distinct roles that genuinely interact (we have 4)
- [ ] At least one critique, validation, retry, branch, or escalation event
- [ ] Shared state across agents
- [ ] JSONL traces to stdout and logs/, generated at runtime, matching the input processed
- [ ] Traces show Zetaris queries, the Meterless Engine at work, and which model handled each request
- [ ] No hand-written or fabricated traces (integrity)

## E. DATA AND SECURITY (missing/violating = disqualification risk) (rules 11, 16; secrets section)
- [ ] No secrets committed (API keys, tokens, .env, .pem, .key, credentials) and none shown on screen in the video or deck
- [ ] Any NVIDIA key (only if obtained) lives in Nightshift's Providers tab, never in the repo
- [ ] .env.example placeholders only; .env gitignored
- [ ] No secrets in README, logs, screenshots, the demo video, or the deck
- [ ] Only permitted data (public/licensed/synthetic, labeled); repo light; data load automated
- [ ] Third-party licenses complied with and attributed
- [ ] Any component or data authored before 22 Oct declared as pre-existing in the submission form (ours: aim to build sample_app and golden-set data fresh in-window; declare anything that predates it)

## F. SUBMISSION COMPONENTS (required) (Submission Requirements sections 2-3)
- [ ] Public GitHub repo (the form accepts github.com links ONLY; public so judges open it without requesting access) with README (setup, usage, dependencies incl. Zetaris and Nightshift)
- [ ] metadata.json present, stating where each sponsor technology sits in the build (helps Sponsor Tech scoring)
- [ ] Demo video 1-4 minutes showing the main workflow on a real run and how Zetaris and Meterless are integrated (agent querying Zetaris, the feature the Engine powers, one real request through Nightshift returning a result)
- [ ] Slide deck covering the 8 points (problem/users, solution, agent workflow/architecture, technical stack, how Zetaris and Meterless were used, what was unique, product visuals, future enhancements)
- [ ] Sponsor technology explanation (Zetaris integration/role; which Meterless Engine, what it does, the test result; how the app connects to Nightshift; where NVIDIA contributes if pursuing the award; Cursor = Claude Code; what was unique)
- [ ] At least 3 sample inputs and matching outputs (recommended; do it)
- [ ] Colab links IF agents run in Google Colab (N/A for us; we run locally/Docker)
- [ ] Pre-existing components declared in the form (ours: none intended; all built in the window)

## G. HONESTY (scored across criteria; integrity) (Honesty Check)
- [ ] Every capability claimed is one the code has
- [ ] Data described accurately (live vs cached)
- [ ] Models claimed match the logs (Nemotron claim honest; meterless/auto not misrepresented)
- [ ] Limitations stated honestly; nothing called production-ready that isn't
- [ ] Track and problem named consistently across README, deck, and demo
- [ ] The "I cannot reach this" honesty behavior is shown, not hidden

## H. OUR OWN BUILD REQUIREMENTS (from the spec)
- [ ] Clean architecture: the dependency-direction fitness function passes (spec 15)
- [ ] Agent governance tests pass (spec 19): no write/credential handle on the wrong agent, unsupported claim rejected, off-list action refused and logged, injected text produces no action
- [ ] Grounding-rate metric computed (spec 18)
- [ ] Change-brief export works (spec 6.1)
- [ ] One-click re-check works, if reached (spec 6.1, Phase 4)

## I. DEMO ACCEPTANCE (reconciled from Chad's acceptance checks A-J)
- [ ] Ingestion works on the fixture repo and names actual files and real relationships
- [ ] Every finding's evidence resolves to a file path and ideally a line span or hash; honest about missing evidence
- [ ] On the ambiguous request (cancellation timing), the agent stops and asks before committing to behavior
- [ ] Each finding distinguishes observed fact from inference and points to a source
- [ ] The plan names affected areas, proposed changes, required verification, and risks/unknowns
- [ ] Decisions survive a fresh session/process (demonstrated reopen)
- [ ] Reopen-and-recover per repo: after external changes, the saved record (what the tool can/cannot do and reach, the options and information given, the decisions made) is intact, keyed to the repo by a readable label, shown without searching, and each saved finding/decision is state-stamped and flagged still-valid / stale / unknown against the current repo (spec 6.2)
- [ ] Sponsors do material workflow work, not a logo or an API ping (the page: mentioning a sponsor or an unused dependency does not meet the requirement)
- [ ] No arbitrary repo execution, secret disclosure, or subject-repo modification
- [ ] At least 3-5 reproducible evaluations and one documented failure/limitation
- [ ] A judge understands the value and can verify the demo in minutes
- [ ] The tool self-describes: a capabilities-and-limits manifest (DOES / DOES NOT / CANNOT REACH / YOU) is queryable (--capabilities, GET /capabilities), shown in run output, the README, and the demo, and each limit references its enforcing test (spec 23)
- [ ] User safeguards (spec 24): never imports or executes subject code (tests only on sample_app); reader hardened (size caps, no symlink escape, no archive expansion); secrets detected and redacted on ingest, value never stored/sent; store is durable (SQLite ACID + integrity_check, portable, versioned, graceful on corruption); facts are deterministic/stable-ordered; decisions attribute the user, options neutral; output states run-specific limits

---
*Check these off as the build satisfies them. Where this and the Official Rules differ, the Official Rules apply. When in doubt about a fact you cannot see or reach: say so, never invent.*
