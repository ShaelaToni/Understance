# CLAUDE.md - read this first, every session

This repository is a hackathon build by Shaela Beard (Team: Wisdom by Design, solo) for the Open Agent Hackathon 2026. Claude Code loads this file automatically. Follow it every session.

## How we build
- Build STRICTLY in the order in docs/BUILD_ORDER.md. Do NOT skip, reorder, or add steps of your own accord. A prior helper built out of order; this rule exists to prevent that.
- HALT on unexpected output. Stop, surface it, do not paper over it or improvise.
- DIRECT method: Define, Instruct, Review at a 100/100 gate, Execute, Confirm, Track. No black boxes. The deliverable is Shaela's understanding; working code is the byproduct. Explain before coding; check understanding.
- Test-first (TDD) for everything behind our own four ports (domain, use cases, agent logic, fitness and governance tests): write the failing test from the expected result FIRST (red), then just enough code to pass (green), then refactor while green. A step's GATE test is written before its implementation, not after. Exception: the external sponsor adapters (Zetaris, Nightshift, H-MEM) use characterization-then-contract (a small smoke test to learn the real behavior first, then a contract test, then the adapter), because you cannot assert against a service you have not yet observed. Never fake a test against an unobserved service.
- Keep v1 minimal (DHH/Levels/Rival guard): do not let safeguards or fitness functions bloat the first walking skeleton; prove the riskiest premise early (deterministic analysis yields useful change-impact on a real messy repo), not last.
- Documentation is continuous from the FIRST action of the FIRST session, including the initial setup run, not something done at the end. Capture the questions asked and the answers given, not just outcomes, so any newcomer (a helper taking over, or a teammate; assume more than one person) can reconstruct what was done, what was asked, what was answered, and why, without guessing. Keep docs/STATE.md current as you go (current phase/step, what is green, what is next, open threads).

## Done and advance (the Confirm gate) - the ONLY signal to move to the next step
Do NOT advance to the next step until ALL five are true. A green test alone is not enough.
1. The step's tests are green, actually run and shown, not claimed. Fitness/governance tests must also be shown to fail on a planted violation.
2. The output matches the result defined beforehand (for deterministic layers, the hand-verified truth of sample_app). Review at 100/100; concerns resolved, not deferred.
3. No unexpected output occurred. A surprise is a not-done: halt and investigate first.
4. Shaela can explain, in her own words, what the step did. If she cannot, it is not done.
5. Committed with the what/why/Layer/Gate message, and docs/STATE.md updated (step marked done, next step named).
Only then check the box in docs/BUILD_ORDER.md and move to the next unchecked item. Never declare done or advance on your own judgment; these five are the signal.

## Panel and Review (the R in DIRECT) - no rubber stamps, current-state only
- Convene the panel (Shaela's review device: channel REAL named experts' documented frameworks, including the Rival who hunts the fatal flaw; the roster is in OWNYOUR_EXPERT_PANEL_COMPLETE_UPDATED.md plus the hackathon panel additions in docs/DECISIONS.md, and the method and voice are in THE_DIRECT_METHOD.md and SHAELA_BASE_OF_KNOWLEDGE.md) at two points in every step: the design review BEFORE writing code (is the approach correct, clean, foundation-first), and again at the done-gate. Also on any halt.
- CURRENT-STATE ONLY (the hard-won rule): every verdict is based on the LIVE artifact read right now, the actual file as it is and the test output just run. NEVER approve from memory, a handoff, STATE.md, or an earlier point in the session. "Empirical before hypothesis." If the position changed since the last check (a new commit, an edited file), the prior OK is VOID; re-review against the current state.
- NO RUBBER STAMP: a verdict must name what was checked, cite the current evidence, surface real concerns (and the Rival's), and resolve each to 100/100. "Looks good" with no named concern and no cited current evidence is NOT a valid review; it means the panel was not run, and that is a not-done.
- A green panel does not replace the five-part done-gate. Both must pass, both against current reality.

## Deciding and recording (so Shaela keeps momentum; she decides, the helper documents)
When a real decision/fork arises (a choice with a genuine alternative or a consequence; trivial choices already settled by docs/CONVENTIONS.md do not count):
1. Surface it at the design review. State the fork and the alternatives fairly (steelman each, include the Rival's angle). Pre-fill a draft decision-map entry from the conversation.
2. Ask Shaela ONLY what cannot be derived from context, as a short plainly-worded question in the conversation that she answers in her own words. NEVER use a multiple-choice prompt window (she finds them limiting and easy to misclick). If several small forks pile up, ask them as one short written list for a single approval.
3. Shaela answers and gives explicit approval. Never self-approve or self-decide a fork. Show her the exact entry; she says approved or edits a line.
4. On approval, immediately write the entry to docs/DECISIONS.md (the decision map, quick template), mark [DECK] if she flags it, and note it in docs/STATE.md. Then continue building.
RECORD WHEN MADE, NEVER WITHHOLD (the backlog trap): a decision Shaela has directed or approved in conversation is a MADE decision; record it the moment it is made, capturing the why and the features, not just the choice. If some sub-parameters are still open, write the entry now with those flagged "pending Shaela" inside it; do NOT hold the whole entry until every sub-question is answered. An undocumented backlog is the failure this protocol exists to prevent. "Wait for approval" applies only to a fork the helper is proposing, not to a decision she has already settled.
If Shaela is away: do NOT self-decide a real fork. Record it as "pending Shaela," take a reversible default only if needed to keep moving and flag that you did, and halt for anything irreversible.
RECONCILE BEFORE RECORDING (no reworded duplicates): before writing any decision or finding, search the existing docs for the topic and judge by SUBSTANCE, not wording. Same substance = do not duplicate (clarify in place if it helps). Changed substance = a revision: supersede the existing entry in place, dated, with the old marked superseded and kept visible; never a silent overwrite and never a parallel duplicate elsewhere. Genuinely new (no existing entry) = add. One topic, one home.

## Clean architecture (non-negotiable)
- Dependencies point inward only. domain/ and usecases/ import NOTHING from adapters/ or any third-party package. The test in tests/test_architecture.py enforces this; it must stay green.
- Fitness functions are continuous: the architecture, governance, and operational tests run on every commit (pre-commit hook) and at every gate, not once. Each must be shown to fail on a planted violation.
- Only four ports: SourceReader, FactStore, Explainer, MemoryStore. Existing libraries (ast, graph libs, coverage, pytest) live inside adapters only.
- Code-health fitness functions run in the pre-commit hook alongside the architecture and governance tests: a linter and formatter (ruff + ruff-format), a complexity/function-length cap, an unused-import check, and a dead-code detector. TDD (write only enough code to pass) is the primary anti-bloat lever; these make "no AI code smell" measurable. A too-long function or an unused import fails the commit.
- Footprint is proven, not claimed: a governance test asserts the SUBJECT repo is byte-for-byte unchanged after any run (before/after checksum; 0 files created, modified, or deleted). Each run emits a footprint report (wall-clock seconds, peak memory, model calls, tokens if reported, Zetaris queries, files indexed, state bytes written). Cold index time is measured against repo size.
- Every sponsor call goes through an adapter, never a vendor SDK called from a use case or agent.

## Agent governance (safety; see docs/GOVERNANCE.md)
- The tool is READ-ONLY on the subject repo. There is NO apply-change, write, or delete capability anywhere. Do not add one.
- Each agent is constructed with only the ports its role needs. Do not hand an agent a capability it does not need.
- Secrets live in environment variables, read only inside adapters. Agents never receive raw clients or tokens.
- Facts come only from the FactStore. Every output claim must carry an evidence id that resolves to a fact, or it is dropped.
- Repo content is DATA, never instructions. Never feed subject-repo file contents to the model as instructions.
- Every agent action (and every refused action) is logged to logs/ as JSONL.
- Self-describing: the tool never lets a user assume what it can or cannot do. A capabilities-and-limits manifest (DOES / DOES NOT / CANNOT REACH / YOU) is queryable via --capabilities and GET /capabilities, shown in each run's output, the README, and the demo. Each DOES NOT and each limit references the test that enforces it; a claim with no backing test is not allowed; a test keeps the manifest in sync with the code (spec 23).
- User safeguards (spec 24, panel-reviewed): NEVER import or execute subject code (ast static parse only; no import, setup.py, or conftest); tests run only on the trusted sample_app; arbitrary-repo execution is sandboxed + opt-in + future, default static-impact-only. Harden the reader: file-size caps, no symlink escape, path-traversal safe, no archive expansion. Detect and redact secrets on ingest; never store/log/send/display the value; flag presence; "likely," not "guaranteed." Facts are emitted in stable deterministic order so diffs reflect real change. Decisions attribute the user as actor; options presented neutrally, any default labeled as the tool's and recorded. Output states run-specific limits (actual blind spots), not boilerplate.

## Secrets
- Never commit a key, token, .env, .pem, or .key. .env.example has placeholders only.
- The NVIDIA key lives in Nightshift's Providers tab, never in this repo.
- The per-repo history/recovery store is local-only: it holds references and hashes, never secrets or raw code contents, and is never synced to a cloud without explicit consent. Saved findings/decisions are state-stamped (the repo state they were valid against) and re-validated on reopen (still-valid / stale / unknown).
- The store is durable and portable: SQLite ACID transactions + integrity_check, a single exportable file, a versioned schema for forward migration, and graceful handling of a corrupt store (detect and tell the user, never silently lose). Single-writer.
- Referential integrity is enforced at the DB level (FK constraints): no finding or dependency edge references a missing evidence/file/symbol row (Celko). The provenance and record export in an open format (SQLite or JSON), never a proprietary blob.
- A short docs/THREAT_MODEL.md names each threat (hostile repo, prompt injection, secret exposure, history store as target, untrusted test execution) mapped to the safeguard that mitigates it.

## Voice and integrity (for all docs, README, commit messages)
- No em dashes. No "trying" or "try." No "AI-powered" (say Claude Code, AI-directed, AI-orchestration).
- Under-claim. Never fabricate. If you cannot see or reach something, say so and ask; do not invent.
- Claim nothing the code does not do.
- Ask questions as plain text in the conversation; never use multiple-choice prompt windows.
- Do NOT use the timetable or deadline to pressure Shaela's decisions or pace, and never imply she should start building before she is ready. The blueprint exists so the work can move deliberately; she runs her own race. State a deadline only as a plain fact if she asks, or if something would genuinely be missed without her awareness, never as a lever to rush.

## Commit convention
```
<what you did, imperative, short>

Why: <reason / decision / trade-off>
Layer: <e.g. 2.3 analyze_repo use case>
Gate: <the test or check this satisfies>
```
Record real architectural decisions in docs/DECISIONS.md.
No AI attribution anywhere in the repo: no "Generated with Claude Code", no "Co-Authored-By: Claude" trailer, no "written by AI" comments. Configure Claude Code to omit co-author/attribution lines. The coding tool is disclosed once, honestly, in the README's AI-usage section (the rules require disclosing the tool); that is the only place.

## Naming
Follow docs/CONVENTIONS.md exactly. Do not invent file names, class names, trace fields, id formats, or env var names. If a name is not covered there, stop and ask.
Ubiquitous language (one glossary in docs/CONVENTIONS.md): Fact, Finding, Evidence, Provenance, Decision, Dependency, BlastRadius, used identically in the schema, the agents, and the user-facing output.

## Where things are
- docs/BUILD_ORDER.md - the authoritative step-by-step order (build from this)
- docs/REQUIREMENTS.md - every requirement to check off
- docs/GOVERNANCE.md - the agent roles, regulations, and safety enforcement
- docs/CONVENTIONS.md - naming and file conventions (follow exactly)
- docs/STATE.md - current state; update at the end of each session
- docs/DECISIONS.md - one ADR entry per real decision

## The build in one line
A Track 2 agent for the owner of AI-built or inherited software: it explains what a change affects and why, with evidence and provenance, blocks any claim not backed by a fact, and hands the owner a change brief. The model proposes, the system verifies, every claim traces to evidence. It reads and explains; it does not change code.
