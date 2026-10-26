# DECISION MAP - the forks, and why
**Owner:** Shaela Beard · Team: Wisdom by Design (solo) · Open Agent Hackathon 2026
**Why this exists:** code is cheap now; judgment is the expensive, differentiating part. This records each build decision, why this way, why not the other (stated fairly), and what would change our mind. It is also living provenance of the build itself, the product's own thesis applied to how it was made.
**Becomes** docs/DECISIONS.md in the repo. The deck pulls the five or six most telling forks as a visual tree.
**Format per entry:** Decision (driving value). Why this. Why not the alternative (steelmanned). Revisit if. [date · reversible?]
**Voice/integrity:** tiny entries, one line per field; only real decisions actually made; mark superseded, do not rewrite; no em dashes.
**Last updated:** Oct 26, 2026.

## QUICK ENTRY TEMPLATE (copy, fill, done; one line per field)
```
**<Decision>** (<driving value>). [DECK] <- add [DECK] only if it is a top fork worth pitching
- Why this: <one line>
- Why not <alternative, stated fairly>: <one line>
- Revisit if: <the trigger that would reopen it>
- [<date> · locked / open / deferred / reversible]
```
Put it under the fitting heading (Strategic, Architecture, Tooling and Infra, Scope, Process). Mark superseded entries, do not rewrite them. The FOR THE DECK list at the bottom tracks the forks to pitch.

---

## STRATEGIC
**Track 2, The Agent That Can Explain Why** (foundation-first).
- Why this: it is the root of the problem, understand and explain before changing; evidence-backed answers are the deliverable.
- Why not Track 1 or 3: a vibe-coder, an inheritor, and an AI-built owner start at different points but converge on "understand the totality before I change it," and only one primary track is allowed; Track 2 is the truest fit.
- Revisit if: the published challenge statements reframe the tracks. [Oct 24 · low reversibility]

**Positioning: a living comprehension-and-provenance layer, not an "AI code audit"** (new-category Innovation).
- Why this: the audit framing files you next to crowded, funded incumbents and you lose the comparison.
- Why not the audit framing: it is the familiar bucket, so it is easier to explain, but it is a losing frame for a judge.
- Revisit if: never for the hackathon; it is the core. [Oct 24 · locked]

**Audience: the non-expert owner, not engineering teams** (under-served, honest fit).
- Why this: the owner who cannot read their own AI-built software is a 2025-2026 phenomenon and is under-served.
- Why not engineering teams: a real market, but already served by funded PR-time tools (CodeRabbit, Greptile, Qodo).
- Revisit if: discovery shows the owner will not pay and teams will. [Oct 24 · reversible as a product, fixed for the demo]

**Product name: Understance (understand + stance)** [DECK] (positioning + memorability).
- Why this: fuses "understand" and "stance", comprehension plus a firm footing before you act, directly on-thesis ("understand before changing"); memorable and its own identity, distinct from the OwnYour brand.
- Why not a generic descriptor or an OwnYour-tied name: generic is forgettable; an OwnYour-tied name risks confusing judges about pre-existing work (this build is all-new-in-window). Understance stands on its own.
- Clearance (not legal advice): known prior use is a Canadian lingerie/bra brand (apparel, roughly Class 25, reportedly closed July 2026), a different trademark class from software (9/42), so unlikely to conflict for a dev tool; fine as the hackathon name. Commercial use later needs a proper trademark search and counsel. There is lingering apparel SEO association to overcome, and domain/GitHub/npm handles should be checked if it goes commercial.
- Package name: `understance` doubles as the Python package name; record it in docs/CONVENTIONS.md at Step 0.4/0.5 so Claude Code uses it at the folder skeleton.
- Domain: `understance.dev` secured Oct 26 (.com is held by the former apparel brand; .dev fits a developer tool and avoids the .com conflict). Brand consistently as understance.dev.
- Revisit if: a commercial trademark clearance surfaces a conflict. [Oct 26 · locked for the hackathon]

## ARCHITECTURE
**Clean architecture, dependency rule, only four ports** (foundation-first, agnostic).
- Why this: it keeps the core independent of model, data layer, and vendor, so resources can swap; it extends into the larger vision without a rewrite.
- Why not a quick script: faster to a demo, but it would not survive a resource change or grow into the product, which is the whole thesis.
- Revisit if: n/a; this is the foundation. [Oct 24 · locked]

**Read-only on the subject, no change capability (stop at PROPOSE)** (safety by construction, trust).
- Why this: a capability that does not exist cannot be misused; the tool is safe because it cannot act, which is the trust story.
- Why not controlled MODIFY now (Chad's optional disposable-branch patch): it would let the agent "do more," but it adds a dangerous capability, scope, and risk, against governance.
- Revisit if: a later stage, after read-understand-propose is proven, with approvals and rollback. [Oct 24 · deferred, not rejected]

**Custom lightweight orchestrator, not LangGraph** (control, fewer unknowns in the time).
- Why this: cleaner under the dependency rule, no new dependency to learn under a deadline, full control.
- Why not LangGraph: it gives checkpointing and human-in-the-loop for free, which is genuinely attractive, but it is a framework to learn now and a dependency to reason about.
- Revisit if: persistence or human-in-the-loop needs outgrow a hand-rolled loop. [Oct 24 · reversible]

**The model is called only in the Explainer** (deterministic verification, clean sample mode).
- Why this: keeps verification outside the model and on-thesis, makes sample mode a one-adapter swap, and puts Nemotron use in one loggable place.
- Why not a model in every agent: more "agentic" on the surface, but it spends tokens, adds nondeterminism, weakens verification, and complicates sample mode.
- Revisit if: a later capability genuinely needs model judgment in the Planner. [Oct 24 · reversible]

**Phase 1.1 pass 1 graph entities: Module, Dependency, DependencyGraph only; immutable; orphan = imported by no other module** (minimal v1, deterministic output, honest wording).
- Why this: `Module(name)` (dotted name), `Dependency(source, target)` (module names; source imports target), `DependencyGraph(modules, dependencies)` stored as tuples in a frozen dataclass so it cannot change after construction; `orphans()` returns a list sorted by name (stable order). A self-import does not rescue a module from being an orphan; a dependency whose target is not in the graph changes nothing. Symbol is deferred to about 2.4 (compute_blast_radius), the first step that uses symbol-level dependencies (TDD: build only what a test needs). File path and line live with Evidence in pass 2.
- Why not include Symbol now (as BUILD_ORDER 1.1 lists): it keeps 1.1 literally complete, but no pass-1 test uses it, so it would be untested speculative code. Effect: BUILD_ORDER 1.1 amended Oct 26 (Shaela) to two passes (pass 1 Module/Dependency/DependencyGraph; pass 2 Finding/Evidence/Provenance) with Symbol at about 2.4.
- Rival: "orphan" includes entry points such as `main`; it means "not imported by any module," never "unused." User-facing wording must say so (settle at the Explainer step).
- Revisit if: a later step needs symbol-level dependencies or dangling targets reported as findings. [Oct 26 · decided by Shaela; reversible]

## TOOLING AND INFRA
**Hosted LLM through Nightshift on Nemotron, not a local open-source model (Ollama)** (eligibility, no GPU, the prize).
- Why this: Nightshift is the mandatory primary provider, the hosted path needs no local GPU, and Nemotron chases the DGX Spark. Sovereignty is still honored because the Explainer sits behind an adapter and can swap to a local model later.
- Why not local Ollama: it is the owned, offline ideal and you have run it before, but it is not the sponsor path, is not required, and sample mode needs no model at all because the deterministic layer is the truth.
- Revisit if: a post-hackathon offline or fully-owned deployment, a local model behind the same Explainer port. [Oct 24 · reversible by design]

**Zetaris local Docker now, AWS as the demo-safety fallback** (unblock today; reversible behind the port). [supersedes the Oct 24 "AWS leaning" framing]
- Why this: starting local gets building today with no AWS account friction; because Zetaris sits behind the FactStore port and connects by .env config, local vs Zetaris-on-AWS vs sample-mode SQLite are all just connection settings, so the choice is reversible with no rework. Building locally also IS the planned load test.
- Why not AWS-first: AWS free tier needs a brand-new qualifying account plus five credit activities, and sign-up verification could stall the first building hours; its real value is protecting the 16GB machine, which only bites at live-demo time.
- Why not local-forever: Zetaris wants ~8GB RAM and 15GB disk and competes with Nightshift on 16GB; an external SSD eases disk and softens swap but does not add RAM, so the demo-time RAM wall remains the reason to keep AWS ready.
- Revisit if: the machine strains under Zetaris plus Nightshift during build, or before the live demo; then stand up AWS in the background (same adapter, new connection string). [Oct 26 · resolved: local now, AWS fallback; reversible]
- Resolved Oct 26: Zetaris local is amd64 and requires Rosetta emulation on Apple Silicon (their Run Locally page: enable Use Rosetta, give Docker 8GB + 4 CPUs). Fine for building, because Zetaris and Nightshift are used in different phases rather than all at once, but it confirms the demo-time RAM wall on the 16GB machine, so the AWS fallback stays warranted before the live demo.
- Operational (Oct 26, logged at Shaela's direction): Zetaris holds ~7GB while running. When not actively using it, run `docker compose stop` from inside the zetaris-platform folder in Terminal to free the memory, and `docker compose start` to resume; containers and data persist and nothing re-downloads. Use stop/start, not `down`, so the data volumes are kept. Manages the 16GB constraint during build phases that do not need Zetaris live.

**Zetaris FactStore adapter uses REST, not JDBC** (light, Python, matches our env vars).
- Why this: REST needs only an API key plus the REST URL and org ID (already our ZETARIS_REST_URL / ZETARIS_ORG_ID / ZETARIS_API_KEY) and fits Python with no extra runtime.
- Why not JDBC: it needs Java and a driver JAR, heavier and against keep-v1-light. JDBC stays available for ad-hoc Claude Code exploration if ever wanted, but the shipped adapter is REST.
- Revisit if: REST proves insufficient for a query we need and JDBC is the only path. [Oct 26 · locked]

**Zetaris characterization finding (Oct 26): result shape + select explicit columns** (observed live; informs the adapter). Observed by running `SELECT 1` (returned `1`) and `SELECT * FROM NY_TAXI.taxi_zones LIMIT 5` against the running local instance. What we learned: Zetaris answers SQL end to end; addressing is two-part `catalog.table` (e.g. `NY_TAXI.taxi_zones`, catalog straight to tables, no schema layer in the sample); results are ordinary typed tabular rows (numeric and text columns) and can include large fields (a geometry column, `the_geom`, too big to paste). Build implication: the FactStore adapter selects explicit, needed columns, never `SELECT *`, to keep payloads small, deterministic, and aligned with our minimal-data and stable-order safeguards. This is the observe-first step of characterization-then-contract; it feeds the Phase 3 Zetaris contract test and adapter. [Oct 26 · finding, logged at Shaela's direction]

**Python for v1** (fluency, tooling).
- Why this: it is the language you are learning and can read line by line, and its standard library (ast) gives most of the deterministic layer for free.
- Why not another language: less familiarity under a deadline and weaker standard-library parsing for this job.
- Revisit if: n/a for v1. [Oct 24 · locked for v1]

**SQLite as the facts store** (boring, light, Zetaris-readable).
- Why this: zero setup, tiny footprint, and Zetaris can read it.
- Why not Postgres: heavier to stand up; only needed if the Zetaris smoke test shows it cannot read a local SQLite, then a minimal database.
- Revisit if: the Phase 3.2 Zetaris-ingest smoke test requires it. [Oct 24 · backing may change, port will not]

**Claude Code, not Cursor** (zero ramp).
- Why this: a year of fluency, no learning curve, and Cursor is optional per the rules.
- Why not Cursor: it is the recommended workshop tool, but it is a new environment to learn under a deadline for no required gain.
- Revisit if: a specific Cursor-only step proved necessary, which it has not. [Oct 24 · locked]

**Central orchestration window runs on Opus 5.5 at Medium effort (its tuned default); Extra only for isolated hard reasoning; Fable 5.1 as the sanctioned step-up** (capability for the role without wasting limits or the routing quirk). [verified against Anthropic's official model docs + the in-app effort guidance, Oct 26]
- Why this: Anthropic's official guidance starts with Opus 5.5 for long-running agentic and knowledge work, and Medium is its tuned default. The in-app note says Extra often does not improve results, is much slower, and uses limits faster, which matters on a Max plan during a sprint. Quality and hallucination control in this role come from the grounding discipline (cite evidence, verify, current-state-only, never fabricate), not from raw effort.
- Extra effort: reserve for a specific, genuinely hard reasoning moment (a thorny design fork or a deep panel review), switched per task if the app allows, not left on by default.
- Why not Fable 5.1 by default: top reasoning option but slowest, heaviest on Max usage, and can redirect some queries to Opus 4.8; reserve for when Opus 5.5 genuinely falls short (Anthropic's own stated trigger).
- Why not Sonnet/Haiku: tuned for speed and high-volume work, not the deep-reasoning orchestration role.
- Revisit if: Opus 5.5 at Medium (with occasional Extra) falls short on the hardest reasoning, then step up to Fable 5.1. [Oct 26 · decided; corrected same day from an earlier "higher effort default" note]

**Dedicated "Understance Tutor" helper (silent mentor window)** (comprehension so Shaela can explain the tool, inside and out).
- Why this: Shaela must be able to explain Understance to judges and stakeholders without needing to write every line herself; a separate window turns code she pastes into short, over-the-shoulder lessons and keeps the build and orchestration windows uncluttered.
- Why not have the orchestration window also tutor: it would crowd the build thread and blur roles; a silent, read-only tutor is cleaner and can be consulted on its own.
- Roster (real frameworks, no fabricated quotes): Al Sweigart (Automate the Boring Stuff), Felienne Hermans (The Programmer's Brain), Neal Ford and Robert C. Martin (architecture reasoning), Angela Yu (100 Days of Code).
- Style: one concept per lesson, plain words first, tie each snippet to its role in the architecture, end with a teach-back so understanding is provable, not recited. Reads the canonical claude/ docs so lessons are Understance-specific.
- Onboarding saved at claude/HACKATHON_TUTOR_ONBOARDING.md. [Oct 26 · decided]

**Pursue the NVIDIA Nemotron award: open, default-yes-if-time** (bonus prize, zero rework to defer). [DECK candidate]
- Why this: it is swappable behind the Explainer port, so choosing Nemotron is config (pin the model string + per-request logging), not architecture; Nightshift is meterless so no NVIDIA credits are needed; the award is large (our notes: an NVIDIA DGX Spark, about $4,699) and there is no separate application.
- Why not commit-now or drop-now: committing now gains nothing because the award work is pure configuration plus a README line, a demo beat, and a linked receipt log, all addable as late as the day before submission; dropping it forfeits a large prize for no effort saved.
- Scope guard: Nemotron powers the Explainer ONLY; the Evaluator stays deterministic (do not move verification onto the model to chase a two-agent "researcher + critic" story, that would undercut the core differentiator and the Rival would flag it).
- Integrity: pin and log the model; claim Nemotron only if the receipts prove it handled the request; keep the timeout + fallback to another Nightshift model so an outage during judging degrades, not kills.
- Revisit if: time runs short at the end (drop with zero rework) or Nemotron is unreachable (fallback keeps eligibility). [Oct 25 · open, default-yes-if-time, reversible behind the Explainer port]

## SCOPE
**One capability (change-impact with evidence), not many skills** (depth over breadth).
- Why this: the scorecard rewards one capability done with real agent interaction and evidence; breadth is penalized as padding.
- Why not many skills: it looks impressive and some winners have many, but shallow skills read as prompt wrappers and break under a judge's own input.
- Revisit if: never for this event; breadth is a post-hackathon question. [Oct 24 · locked for the event]

**v1 is Python repos at module-and-symbol blast radius, not a full call graph** (achievable, honest).
- Why this: it is buildable in the time and honest about its precision.
- Why not full call-graph, multi-language: more impressive, but too large for the window and easy to overclaim.
- Revisit if: time remains after the eligibility path and the core demo. [Oct 24 · deferred]

**UI deferred; programmatic endpoint plus CLI first** (eligibility before polish).
- Why this: Technical and eligibility come first; a programmatic path is required and a UI is not. Product & UX is 10 points, a known, chosen cost.
- Why not a UI now: Product and UX is ten points, but a polished UI over a thin system is the classic weak submission.
- Revisit if: the core is solid and time remains; then a light output renderer recoups some of those 10 points. [Oct 24 · deferred]

## PROCESS AND STANDARDS
**Test-first (TDD) behind our ports; characterization-then-contract for sponsors** (anti-bloat, honest).
- Why this: writing only enough code to pass prevents slop, and you cannot assert against a service you have not observed.
- Why not test-after: faster per step, but it invites bloat and weaker design, and it is how AI smell creeps in.
- In practice (Oct 26, logged at Shaela's direction): for each sponsor, Zetaris first, OBSERVE its real responses live before writing any test or adapter; write the contract test to the observed behavior, then the adapter. Concrete instance: run SELECT 1 and real queries against the running Zetaris and watch what it returns before coding the FactStore adapter. Empirical before hypothesis.
- Revisit if: n/a. [Oct 24 · locked; observe-first practice instance added Oct 26]

**Sponsors wired thin end-to-end by day two** (protect eligibility against the clock).
- Why this: all mandatory sponsors must work, and leaving them to the end is the most likely way to end with an ineligible submission.
- Why not build the core fully first, sponsors last: cleaner in theory, but the clock makes it the top risk.
- Revisit if: n/a; this is the risk control. [Oct 24 · locked]

**No AI attribution in the repo; disclose the tool once in the README** (clean ownership, honest disclosure).
- Why this: the repo reads as yours, and the rules only require disclosing the coding tool once.
- Why not attribution trailers: harmless, but noise, and not the ownership signal you want.
- Revisit if: n/a. [Oct 24 · locked]

## ADDED OCT 24 (second pass, bringing the map current after a documentation backlog was caught)
These were decided across the planning session and not yet recorded. Pending items are flagged.

### Process and standards
**Five-part done-and-advance gate** (no premature advance). Why this: an objective "done" (tests shown, output matches pre-defined, no surprise, Shaela can explain, committed + STATE updated) stops helpers advancing on their own judgment. Why not "green test = done": a green test alone misses understanding and stale review. [Oct 24 · locked]
**Panel review: current-state-only, no rubber stamp.** Why this: a verdict must read the live artifact now and name concerns with evidence, or it is the stale-approval failure from OwnYour. Why not trust a prior OK: the position may have changed since. [Oct 24 · locked]
**Decide-and-record protocol, record-when-made.** Why this: Shaela decides, the helper documents immediately, flagging open sub-parameters pending, so no undocumented backlog. Why not helper-documents-at-end or holds-whole-batch: both lose decisions (this was caught happening). [Oct 24 · locked]
**Questions as plain text, never multiple-choice prompt windows.** Why this: Shaela finds the widgets limiting and easy to misclick. Why not the widget: faster to render, but worse for her. [Oct 24 · locked]
**Documentation from the first action, capturing questions and answers.** Why this: any newcomer (assume several) reconstructs what was done and why without guessing. Why not document-at-end: the answers given are lost. [Oct 24 · locked]
**Continuous fitness functions (pre-commit) + code-health checks.** Why this: clean stays clean and "no AI smell" is measured, not hoped. Why not check-once: the architecture rots silently. [Oct 24 · locked]
**Footprint proven, not claimed** (read-only checksum test + per-run footprint report). Why this: evidence over assertion; it is also the "measure something" metric. Why not claim lightweight: that is what weak founders do. [Oct 24 · locked]

### Architecture and product features
**Transparency: a self-describing capabilities-and-limits manifest** (DOES / DOES NOT / CANNOT REACH / YOU), queryable, each limit backed by its test. Why this: a user should never assume what the tool can or cannot do; it serves both the "what can I do" and "confirm it cannot" users. Why not leave it implicit: that is a black box and invites overclaim. [Oct 24 · locked]
**Per-repo owned-workspace recovery**: by-repo identity + readable label + workspace listing; the record is the recovery log (what the tool can/cannot do, options and info given, decisions made); append-only; state-stamped and re-validated on reopen; local-only private store; verifiable (evidence ids). Why this: "life happened, what did we do again" must be answerable two weeks later without searching or losing the last-good baseline. Why not re-upload/recompute each time: slow, and it loses history. [Oct 24 · locked; identity key scheme pending]
**Auto-capture of decisions in the tool** (the product version of our own protocol). Why this: users will not stop to document and many would not know how; because the tool frames the fork it owns an exact record, so the user only answers. Features: records the question, options, evidence, answer, date, repo state; append-only; readable back in plain language; captures deferrals and supersessions. Guardrails (the Rival): capture forks and evidence, not keystrokes; transparent and consensual via the manifest; local and private. Why not ask the user to document: they will not, and a model summarizing after the fact would guess. [Oct 24 · locked; approve to write into spec 6.2 + manifest]
**Reportable provenance / audit trail** (accountability beyond personal recall). Why this: a user checking the system for their company will not remember the when and why later and may have to report to a manager, shareholders, or due-diligence; the record must export as an honest report, not just a personal memory. Features: assembled from the recorded decisions, evidence, dates, and state-stamps (accurate by construction; the model only phrases, not a free-form summary); plain-language + evidence-linked; distinguishes observed fact from inference; states limits and open/pending items; user controls what is included; no secrets or raw code (references/hashes only); export is a deliberate, consensual act. Why not a model-written summary: it could fabricate or overclaim, a liability in a report someone relies on. [Oct 24 · data support locked; export/report UX scope PENDING v1-vs-stretch; candidate [DECK] pending Shaela]
**Observed-vs-inferred flag on every finding** (from Chad). Why this: a user must see what is fact versus interpretation, each pointing to a source. Why not one undifferentiated list: it hides uncertainty. [Oct 24 · locked]
**What-if branch: data model locked, full UX a stretch.** Why this: let a user explore "what if I decided X" labeled hypothetical, without touching real history; the model (parent + label) supports it cheaply now. Why not build the full UX now: scope; it is not the core. [Oct 24 · model locked, UX deferred]

### User safeguards (approved Oct 24, panel-reviewed)
**Never execute untrusted code.** v1 parses with ast statically and NEVER imports or runs subject code (no import, no setup.py, no conftest). Differential verification runs tests only on the bundled trusted sample_app. Arbitrary-repo test execution is a future capability: sandboxed (separate process, no network, resource/time caps), explicitly opt-in; default is static impact only. Why: running a stranger's or hostile repo is a malware/exfiltration path. [Oct 24 · locked]
**Harden the reader against malicious inputs.** File-size caps, no following symlinks outside the root, path-traversal safe, no archive expansion. Why: a hostile repo attacks the reader, not only via execution. [Oct 24 · locked]
**Detect and redact secrets on ingest.** Flag a likely secret's presence as a finding; never store, log, send, or display the value, even partially; redact before anything leaves. Honest: flags LIKELY secrets, does not guarantee none found. [Oct 24 · locked]
**Durable, portable history store.** Lean on SQLite's ACID transactions and integrity_check; a single portable/exportable file; a versioned schema for forward migration; graceful handling of a corrupt store (detect, tell the user, never silently lose). Single-writer. Why: the memory is the promise; losing it breaks trust. [Oct 24 · locked]
**Disclose and minimize what leaves the machine.** The Explainer sends derived references (file:line, symbol, hash), not raw source; the manifest states plainly what leaves and what does not; a "what leaves" preview and a fully-local mode are future for privacy-critical users; default uses hosted Nightshift, stated plainly. [Oct 24 · locked]
**Attribute decisions to the user; present options neutrally.** The record marks the user as the actor and that the tool surfaced the fork and did not recommend. v1 presents options with no steering default; any default/ranking, if ever shown, is labeled as the tool's and recorded. Why: a user must never be shown as having been advised by the tool. [Oct 24 · locked]
**Run-specific limits, not boilerplate.** The brief and output state the actual blind spots of THIS run (files not reached, which findings are inference), not a generic disclaimer, so limits get read. [Oct 24 · locked]
**Deterministic, stable-ordered fact output.** Facts are emitted in a stable order so diffs and re-checks reflect real change, not ordering noise. Why: nondeterministic output would produce false "changes" in the broken-code diagnosis and re-check. [Oct 24 · locked]

### Scope
**Rebuild-clean guidance: v1 gives the incremental path; full REPAIR mode is future.** Why this: a messy-system owner who wants to rebuild clean needs guidance to hand their LLM, because they cannot instruct what they do not understand (the gap Shaela crossed with books). v1 surfaces structural violations (layering breaks, cycles, god modules) as findings, names the clean target, and the change brief guides a scoped, layer-ordered INCREMENTAL refactor the user's LLM executes one verified step at a time (re-check confirms each). Same output path, no new v1 machinery. Full one-button whole-system rebuild = REPAIR mode, future. Why not a big-bang rebuild plan in v1: a confident whole-rewrite plan that is wrong is the overclaim/harm we guard against; incremental-behind-tests is safer and is correct engineering (strangler-fig). Confirmed build-with-it-in-mind: v1's FactStore, findings, change brief, and re-check are the foundation REPAIR extends, so no rebuild is needed to add it later. Direction: understand + change-safety (v1) -> incremental REPAIR -> CONTINUOUS. [Oct 24 · v1 = incremental refactor guidance; full REPAIR future]
**Sample app = a tiny subscription SaaS with the cancellation-timing ambiguity** (from Chad). Why this: a comprehensible demo that stages the stop-and-ask beat. Why not a generic repo: a clean repo makes a dull demo. [Oct 24 · locked]
**Golden set = Chad's 7 evaluation scenarios.** Why this: ready, and it showcases governance and honesty. [Oct 24 · locked]
**Broken-code cross-session diagnosis.** Why this: diff the broken repo against the last healthy state to show what changed and what broke, with evidence. [Oct 24 · PENDING: v1-if-time vs stretch; data model (per-state health, diff-against-last-healthy) locked now]

### Tooling and infra (pending)
**Git history as a second source, federated through Zetaris** (approved Oct 24). Why this: one addition pays three ways: it makes Zetaris do real federation (impresses Hay, the Zetaris CTO judge), it powers the broken-code diagnosis (which change broke it), and it enriches provenance (who/when/why from commits). How it affects the build: no structural change, git history is a new source behind the existing FactStore port, added AFTER the core breathes so it does not eat the foundation. Why not an arbitrary second source: it would read as padding; git history is triple-leverage. Pluses (full): real federation across differently-shaped sources through one access point (merit, not padding); triple-leverage (Hay + broken-code diagnosis + provenance who/when/why); lifts Track 2's "across multiple data sources, connect findings" and Impact; agnostic preserved with the sample-mode SQLite swap as live proof; governed least-privilege access aligns with our safeguards and with Zetaris's own "safe access" positioning. [Oct 24 · decided; sequenced after Gate 3]
**Agnostic by design, Zetaris by choice** (the flip, so agnostic AND Hay impressed). Why this: the FactStore PORT is the agnostic seam; Zetaris is load-bearing BY CHOICE as the chosen adapter, not by lock-in. Sample mode's SQLite adapter is the LIVE PROOF of agnosticism, the same swap that makes it judge-runnable shows it is not welded to Zetaris. If Zetaris changes or offers something different, re-implement one adapter; the core never moves. Why it still lands with Hay: a CTO respects clean boundaries and no lock-in, and this matches how Zetaris itself wins (chosen on merit, not a cage). [Oct 24 · locked]
**Impress by substance, not flattery** (Shaela's standard). Why this: the Zetaris integration earns respect only by being genuinely good data engineering, real federation across differently-shaped sources (facts + git history) reconciled through one access point, governed least-privilege read-only access, and honest limits about what could not be reconciled. We do NOT tailor the build or the pitch to please a judge; we build what a data expert would independently rate as competent, and the sponsor explanation states facts, never praise. [Oct 24 · locked]
**Indexing: lazy from the target vs full-index-first.** Candidate: lazy by default (fast answers, coverage builds in background). [Oct 24 · PENDING Shaela]
**License: permissive vs source-available/copyleft**, and verify what the rules require. Why it matters: a public repo is copyable; the license decides whether a funded competitor can lift it commercially before the moat exists. [Oct 24 · PENDING Shaela]

### Process (added Oct 24)
**Reconcile before recording** (no reworded duplicates). Why this: "new" information is often a reworded revision; duplicates cause drift and contradiction. Rule: search first, judge by substance; same = clarify in place, revision = supersede in place (dated, old marked superseded, kept visible), new = add; one topic, one home. [Oct 24 · locked]

**Decision-record homes: two for now (the project decision map + repo docs/DECISIONS.md), with a relay rule** (no drift while planning is still live).
- Why this: planning decisions are still being settled in the orchestration window, so the project decision map stays live there, while the repo docs/DECISIONS.md is the build's record.
- Relay rule: a decision settled in the orchestration window is recorded in the project map and relayed to CeeCee to add to docs/DECISIONS.md; a decision made during the build goes into docs/DECISIONS.md and is mirrored back to the project map.
- Why not one home now: one topic, one home is the standing rule (entry above), but collapsing early would cut the live planning window off from its own record; the relay is the deliberate, temporary exception that keeps both in step.
- Revisit if: planning winds down; then collapse to the repo as the single source. [Oct 26 · decided by Shaela]

## OPEN QUESTIONS, gating the move to build (answer these to start Phase 0; this Q&A is part of the gate)
Architecture: (1) SETTLED Oct 25, FactStore schema (see Settled section below and spec 22); (2) SETTLED Oct 25, Planner deterministic decomposition (see Settled section); (3) the Evaluator's exact "claim resolves to a fact" test; (4) what H-MEM holds vs the SQLite Zetaris reads.
Sponsor: (5) which Nemotron model (name) for the Explainer. [Known unknowns resolved at first contact: Zetaris SQLite ingest; H-MEM API.]
User and story: (6) the one named demo user; (7) the before-to-after transformation in a line; (8) the first-run flow (point at repo → result).
Output and positioning: (9) the literal output format + a concrete example; (10) the exact one-sentence positioning, verbatim.
Demo: (11) the single turn/star moment; (12) the three sample inputs.
Metric and integrity: (13) the grounding-rate formula; (14) the correction/feedback path when a user disputes a finding.
Data and consent: (15) where the SQLite + H-MEM stores live on disk, and how "what leaves" consent is obtained.
Still pending from before: broken-code diagnosis scope; last-known-good definition; lazy-vs-full indexing; license direction; report-export scope; MCP surface.
Note: none of these block Phase 0 (git, CLAUDE.md, docs, hook, skeleton) or Phase 1 (pure domain). Q3/Q4 gate the agent and H-MEM work; Q6-Q12 gate Phase 2+ and the demo. Resolve each at the phase that needs it.

### Settled Oct 25 (Q1 + roster-review additions)
**Q1 FactStore schema / what a fact is** (settled). An observed, evidence-backed, deterministically-derived record. Entities: File, Symbol, Dependency, Evidence, Finding, Run/StateStamp (TestLink Phase 4). Append-only observations, current graph derived (Kleppmann); normalized stable keys, no blobs (Hay); DB-level referential integrity (Celko); entity/activity/agent provenance (PROV); no column holds a secret value; every Finding observed-vs-inferred and renders to a plain evidence-linked sentence (Cagan/Montessori); no fact without a source. [Oct 25 · locked]
**Ubiquitous language** (Evans): one glossary used in schema, agents, and user output; in docs/CONVENTIONS.md. [Oct 25 · locked]
**Threat model** (Manico): docs/THREAT_MODEL.md maps each threat to its safeguard. [Oct 25 · locked]
**Open-format export** (Naval): provenance/record exports as SQLite or JSON, never a proprietary blob. [Oct 25 · locked]
**Q2 Planner decomposition** (settled). Deterministic, rule-based: resolve target (exact/id-based, not fuzzy on attacker-controlled strings, Shostack) then fixed tasks, reverse deps/blast radius, forward deps, evidence per edge, unknowns, behavior-at-risk (Feathers), and for a change the affected set + fitness functions. Graph-driven, no model. Missing or ambiguous target stops and asks, never guesses. Evaluator can send back to widen, bounded. [Oct 25 · locked]
**Feathers characterization-test: recommend-only in v1** (smallest eligible scale). The change brief recommends a characterization test and names what to cover from the static blast radius, labeled a starting skeleton the user runs; the tool does not generate-and-run it. Scaffolding + running = stretch, running stays sandboxed + opt-in. Why: real and on-thesis, keeps read-only, fits the minimal-v1 guard. [Oct 25 · decided recommend-only]
**Guard: keep v1 minimal, prove the premise early** (DHH/Levels/Rival dissent): do not let safeguards or fitness functions bloat the first skeleton; test the riskiest assumption (deterministic analysis yields useful change-impact on a real messy repo) early, not last. [Oct 25 · locked]

### Documentation and voice (Oct 25, directed)
**Living TAYA FAQ + product voice** in HACKATHON_FAQ_TAYA.md: honest answers to the questions users and judges will ask, seeded now and appended as new ones occur; plus how the tool and its content speak (plain, guide-not-hero, under-claim, reveals-not-certifies, no hype). [Oct 25 · locked]
**README leads with problem + benefit** (StoryBrand), then setup/usage/etc. [Oct 25 · locked]
**Repo visibility**: a repo is all-public or all-private, no per-file visibility. The submission repo is public (code, README, examples, shareable docs: ADR/DECISIONS, CONVENTIONS, THREAT_MODEL). Private strategy stays OUT of it (OY Store project, gitignored docs/private/, or a separate private repo). [Oct 25 · locked]

### Sponsor requirements reconciliation (Oct 25)
**[SUPERSEDED Oct 25 by the corrected entry below.]** The earlier same-day entry read "Required = Zetaris + a Meterless Engine only; NVIDIA optional; Nightshift provider is swappable." That wording wrongly implied Nightshift-as-provider was optional. Kept visible per the mark-superseded rule.

**Required = Zetaris + a Meterless Engine + Nightshift as primary provider; NVIDIA optional (award only)** (eligibility clarity; confirmed against the authoritative Submission Requirements page, last updated Oct 23). Why this: section 4 of that page requires Zetaris as the data layer, at least one Meterless Engine in a working feature with a passing test, AND Meterless Nightshift as the primary AI provider; NVIDIA matters only for the DGX Spark award (route Nemotron through Nightshift, log the model), with no event credits (a key is available on request). The staff note that local models or another cloud provider may run "inside Nightshift" means the MODEL Nightshift serves can be non-NVIDIA, not that Nightshift can be skipped. Effect on build: none; the Explainer already calls through Nightshift, and Nemotron stays a bonus behind that port. Why not the superseded reading: it mislabeled a required provider as optional, which could have led a newcomer to skip it. Revisit if: the Official Rules on the event page differ (they govern). [Oct 25 · locked, corrected]

### User journey (Oct 25, directed)
**User journey mapped backward (end to start)** in HACKATHON_USER_JOURNEY_MAP.md. Surfaced for the eligible floor: the clarifying-question loop (ask -> user answers -> recorded) is first-class, not an edge case; the output must carry notices (blind spots, scope-and-limits, decision-recorded), not just the answer; first-run vs reopen is a real branch, both in v1 (reopen even minimal). Why: backward mapping catches missed steps, states, and notifications before code. [Oct 25 · locked]

### Build panel additions (Oct 25, directed), fields the OwnYour roster (creator-commerce) lacks for a dev tool
Supplement the 95-member roster for this build only.
- Michael Feathers (legacy code / safe change / characterization tests): most on-thesis. Insight: pin current behavior with a characterization test over the blast radius before a change. Proposed feature: the change brief scaffolds/recommends a characterization test. [Oct 25 · member added; characterization-test feature PENDING Shaela]
- Felienne Hermans (code comprehension / developer cognition): design output for comprehension (progressive disclosure, chunking, name unfamiliar concepts); the tool partly teaches the owner to read their own code. [Oct 25 · added]
- Simon Willison (LLM grounding / prompt injection): the Explainer receives only verified findings, never raw source that could carry injection. [Oct 25 · added, confirms governance]
- Chip Huyen (AI evaluation): the grounding-rate metric runs in CI as a continuous check, not a one-time demo number (ties Q13). [Oct 25 · added]
- Adam Shostack (threat modeling): docs/THREAT_MODEL.md uses a structured method (his 4 questions + STRIDE), not ad hoc. [Oct 25 · added, sharpens threat model]
- Daniele Procida / Diátaxis (technical docs, optional): the report and README separate explanation / how-to / reference. [Oct 25 · offered]

## FOR THE DECK (pull these forks for the decision-tree slide and investor answers)
The five or six strongest "thinking" forks, each one a chosen path plus the road not taken:
1. Positioning: a living comprehension-and-provenance layer, not an "AI code audit."
2. Read-only, no change capability: safe because it cannot act, not because it promises to.
3. The model is called only in the Explainer: verification stays deterministic, the model only narrates.
4. Hosted Nightshift/Nemotron over a local model, with the Explainer behind an adapter so sovereignty is preserved.
5. Zetaris local now, AWS as the demo-safety fallback, reversible behind the FactStore port (the agnostic seam in action).
6. One capability done deeply, not many shallow skills: depth scores, breadth is padding.
Add or swap as better forks appear. Keep each to the chosen path and one fair line on the alternative.

---
*Tiny entries, real decisions only. Mark superseded rather than rewriting. When in doubt about a fact you cannot see or reach: say so, never invent. This map is the build's own provenance.*
