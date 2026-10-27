# STATE - where the build is right now
**Owner:** Shaela Beard · Understance · Open Agent Hackathon 2026 · Track 2
**Rule:** kept current at the end of every step (part of the done-gate). Logs the questions asked and the answers given, not just outcomes, so a newcomer can reconstruct what was done and why.
**Last updated:** Oct 27, 2026.

## Current position
- **Phase:** 3 (real end-to-end through the sponsors). Phases 0 and 1 complete; Phase 2 complete except 2.6 and 2.6a (governance tests and the capabilities manifest), deferred for time.
- **Step:** Phases 3.2 to 3.4 done. Phase 3.5 code done: run.py and POST /run answer through Zetaris, Nightshift and H-MEM (or offline in sample mode), with a trace file per run and the ask-once decision loop. Step 3.6 done: the capabilities manifest (run.py --capabilities, GET /capabilities, a scope line in every answer) and the 7 evals.
- **Next:** Shaela's live run (GATE 3); the Zetaris write-ups; the untested-dependent risk in the answer; repo public and a fresh-clone check; the video, the deck and the submission; the web page if time allows. Step 3.7 done: README, metadata.json, docs/ZETARIS_SETUP.md, full-suite hook.
- **Settled (Shaela, Oct 26):** docs/CONVENTIONS.md is authoritative for the folder layout and supersedes the start kit (`orchestration/`, `evals/`, `input_examples/`, `output_examples/`, `requirements.txt`). 0B update (Oct 27): Zetaris runs locally and answers SQL (Oct 26); Nightshift is installed and answered a real request (Oct 27); NVIDIA is deferred (Shaela, Oct 27). See the Oct 27 session log entry. The footprint report and the subject-repo-unchanged test are deferred to Phase 2/3.

## What is green
- 0.1 git init: done. Branch `main`.
- 0.2 hygiene baseline: done. `.gitignore`, `.env.example` (placeholders only), `README.md` skeleton.
- 0.3 first commit and remote: done. Commit `71f9131` "Initialize repo and hygiene baseline" (3 files, no attribution trailer), pushed to `origin/main`; verified against GitHub with `git ls-remote` (remote `main` = `71f9131`).
- 0.4 CLAUDE.md and docs/: done. Commit `ac26f06`, pushed; `origin/main` = `ac26f06`.
- 0.5 folder skeleton: done. Commit `dd0bbe9`, pushed; `origin/main` = `dd0bbe9`.
- 0.6 pre-commit hook: ruff-check + ruff-format (ruff-pre-commit v0.17.2) installed at `.git/hooks/pre-commit`. Shown to FAIL on a planted violation (unused `import os` blocked with F401, commit exit 1, HEAD unchanged; planted file removed, never committed). Real tree passes both hooks.
- 0.6 code-health caps: `ruff.toml` adds C901 (`max-complexity = 10`) and PLR0915 (ruff default `max-statements = 50`) to ruff's defaults; recorded in docs/CONVENTIONS.md. Shown to FAIL on a planted violation (one function blocked with `C901 too complex (27 > 10)` and `PLR0915 Too many statements (53 > 50)`, HEAD unchanged; planted file removed, never committed). Real tree passes.
- 0.6 attribution setting: `.claude/settings.json` sets `attribution` to `{"commit": "", "pr": "", "sessionUrl": false}`. Since 2.2 it also denies reading `./.env` (`"permissions": {"deny": ["Read(./.env)"]}`).
- 0A: confirmed. docs/DECISIONS.md is the authoritative in-repo record of the locked decisions (the build spec is private, not in the repo); read in full; ticked in docs/BUILD_ORDER.md.
- Tests: 255 pass (17 graph, 10 finding, 8 ports, 6 architecture, 11 sample_app, 22 ast reader, 3 analyze repo, 5 blast radius, 5 answer, 3 template narrator, 20 agents, 14 orchestrator, 2 read-only fact store, 3 git history, 3 module tests, 3 enriched reader, 4 csv fact store, 21 zetaris fact store, 6 fallback fact store, 25 nightshift narrator, 25 hmem memory, 2 read-only memory store, 16 app, 4 server, 6 capabilities, 9 evals, 2 metadata)

## Open threads
1. ~~Em dashes in two planning docs~~ RESOLVED Oct 26: all 5 (4 in DECISIONS.md, 1 in REQUIREMENTS.md) replaced with commas.
2. ~~Folder skeleton: start kit vs CONVENTIONS.md~~ RESOLVED Oct 26: CONVENTIONS.md is authoritative.
3. **BUILD_ORDER.md Phase 0 items not in the start kit:** 0B update (Oct 27): Zetaris and Nightshift are running on the build machine and NVIDIA is deferred (see the Oct 27 session log entry); footprint report/test deferred to Phase 2/3; `evals/` comes with the 0.5 skeleton (CONVENTIONS.md). The coding tool's attribution setting is done at 0.6. 0A: see thread 10.
4. **GOVERNANCE.md and THREAT_MODEL.md are starters** drawn from CLAUDE.md; to be expanded from spec 17/19/23/24 and Shostack + STRIDE at the relevant phase.
5. ~~GitHub email verification~~ RESOLVED Oct 26: Shaela verified `git@shaelabeard.com` on her GitHub account.
6. ~~No `src/understance/__init__.py`~~ RESOLVED Oct 26 (Shaela): empty `src/understance/__init__.py` added, so `understance` is a regular package.
7. ~~requirements.txt unpinned~~ RESOLVED Oct 26 (Shaela): installed into `.venv` and pinned to the installed versions, `pytest==9.1.1`, `ruff==0.17.2`.
8. ~~Import-path wiring for `understance`~~ RESOLVED Oct 26 (Shaela, Phase 1.1): `pytest.ini` with `pythonpath = src` (no pyproject.toml); recorded in docs/CONVENTIONS.md.
9. **Full dependency locking** for fresh-clone reproducibility is to be revisited at Phase 5, when the runtime deps (FastAPI, the sponsor clients) are in; for now only the two top-level dev tools are pinned. Their transitive deps (iniconfig, packaging, pluggy, pygments) are not pinned (Shaela, Oct 26). pre-commit (4.7.0) was added and pinned at 0.6; its transitive deps are not pinned either.
10. ~~0A not ticked~~ RESOLVED Oct 26 (Shaela): docs/DECISIONS.md is the authoritative in-repo record of the locked decisions; the build spec is private and not in the repo. docs/BUILD_ORDER.md header note and the 0A line now point to docs/DECISIONS.md instead of "spec section 18"; 0A ticked.
11. **Pre-commit hook additions at their phases (Shaela, Oct 26):** ~~the architecture fitness test run joins the hook at 1.3~~ RESOLVED: landed in 2a7a6fe. Governance half RESOLVED Oct 27 (step 3.7): the full test suite runs in the hook. Still open: a dedicated dead-code detector.
12. ~~Complexity / function-length cap not active~~ RESOLVED Oct 26 (Shaela): enabled in `ruff.toml` (C901 max 10, PLR0915 default 50 statements), enforced by the hook, recorded in docs/CONVENTIONS.md.
13. ~~DECISIONS.md FOR-THE-DECK item 5 inconsistent~~ RESOLVED Oct 26 (Shaela): now reads "5. Zetaris local now, AWS as the demo-safety fallback, reversible behind the FactStore port (the agnostic seam in action)."
14. **BUILD_ORDER.md header still cites the private build spec for sections 17 (agent roles) and 19 (governance enforcement).** Only the section 18 reference was changed, as directed. Those sections are not in the repo either; docs/GOVERNANCE.md is the in-repo starter for both. Pending Shaela.

## Session log (questions asked, answers given, why)

### Session 1 - Oct 26, 2026 (Phase 0)
**Before 0.1 - observations raised by the helper**
- CLAUDE.md was already in the folder; to keep the kit's order it was left out of the first commit and placed at 0.4.
- The planning docs were not yet in the folder (supplied later, before 0.4).
- The coding tool's default setup adds a co-author trailer; CLAUDE.md forbids it, so it was omitted on every commit.

**0.1 git init**
- Ran `git init` (git 2.50.1). Branch `main`, no commits. No surprises.
- Q: README title? A: the product is named **Understance** ("understand" + "stance": understand before changing). Use `# Understance` with the tagline "Understand before changing." It is the real name, not a placeholder.
- Q: Commit the start kit? A: No. It is setup instructions, not a product file; keep it out of git.
- Q: Private GitHub remote? A: Yes, named `understance`, on Shaela's account; confirm which account `gh` is signed in to first; stop if not signed in. Flip to public before submission.
- Q: Hold the session record until 0.6? A: No. Create docs/STATE.md as soon as docs/ exists (0.4) and log as we go.
- Directive: Python package name is `understance` (`src/understance/...`), recorded in docs/CONVENTIONS.md. (Found already recorded there at 0.4.)
- Domain: understance.dev (recorded in docs/CONVENTIONS.md).

**0.2 hygiene baseline**
- Created `.gitignore`, `.env.example`, `README.md` from the kit. Only changes from the kit: README title/tagline, and `.gitignore` gained a line ignoring `HACKATHON_PHASE0_START_KIT.md` (Shaela's call). Verified `.env` and the kit are ignored and `.env.example` is not; the three files pass the CLAUDE.md voice rules (no em dashes, no banned words). Shaela reviewed all three files before commit.

**0.3 first commit, remote, push**
- `gh auth status`: `gh` is not installed (`command not found: gh`). Halted per Shaela's rule; nothing installed. Shaela created the private repo herself: `https://github.com/ShaelaToni/Understance.git` (account ShaelaToni).
- Halt: git had no `user.name` / `user.email`, so a commit was impossible. Asked rather than guessed, because the identity is public once the repo flips public.
- First answer: name `ShaelaBeard`, email `loudontheweb@gmail.com`. Committed as `fa21140` (not pushed).
- Halt (surprise): after that commit, CLAUDE.md had disappeared from the folder. The helper had not touched it; a Finder `.DS_Store` write suggested it was moved outside the session. Surfaced, not recreated. Shaela restored it to the repo root before 0.4.
- The helper noted that GitHub's "keep my email private" setting does not change a commit: the email in the commit is visible in public history, and GitHub may reject the push if "Block command line pushes that expose my email" is on.
- Decision (Shaela): re-stamp the commit with her own-domain identity, **Shaela Beard <git@shaelabeard.com>**, to keep the personal email out of the public history. Identity set repo-local only. `git commit --amend --reset-author --no-edit` produced `71f9131`; the old email appears in no commit.
- Push failure 1 (from the helper's shell): `fatal: could not read Username for 'https://github.com': terminal prompts disabled`. Cause: no saved GitHub credentials, and the helper's shell cannot show a password prompt. Not retried.
- Push failure 2 (Shaela via `! git push -u origin main` in the session): `fatal: could not read Username for 'https://github.com': Device not configured`. Cause: the `!` prefix also has no interactive terminal. Not retried.
- Push success: Shaela ran `git push -u origin main` in macOS Terminal with username ShaelaToni and a personal access token (saved in the Keychain). Verified: `git status` up to date with `origin/main`; `origin/main` = `71f9131`; files `.env.example`, `.gitignore`, `README.md`; `git ls-remote` confirms GitHub's `main` = `71f9131`.

**0.4 CLAUDE.md and docs/**
- Shaela placed CLAUDE.md at the repo root and docs/BUILD_ORDER.md, REQUIREMENTS.md, DECISIONS.md, CONVENTIONS.md.
- Directive: create docs/GOVERNANCE.md and docs/THREAT_MODEL.md as starters, headed "Starter; to be expanded from the build spec at the relevant phase," using content already in CLAUDE.md. Done; THREAT_MODEL also notes the Shostack + STRIDE method recorded in docs/DECISIONS.md.
- Created this file (docs/STATE.md).
- Checks: secret scan of CLAUDE.md and docs/ found no secret-shaped strings.
- 0.4 commit `7d37746` (8 files, no trailer). Helper flagged em dashes in DECISIONS.md and REQUIREMENTS.md; first reported as 3 in DECISIONS.md (a line count), corrected to 4 (line 203 has two).
- Directive (Shaela): replace all 5 em dashes with commas and amend them into the 0.4 commit. Done; amended commit `159493f`, same message, no trailer, 0 em dashes in any tracked file.
- Directive (Shaela): CONVENTIONS.md is authoritative for the folder layout (supersedes the start kit); 0B Nightshift + NVIDIA-key setup pending before Phase 3; footprint report/test deferred to Phase 2/3.
- This STATE.md update was folded into the same 0.4 commit (also unpushed) so the push carries a clean tree; then pushed to origin.
- Pushed: `71f9131..ac26f06 main -> main` from the helper's shell (Keychain credentials, no prompt). `git status` up to date with `origin/main`; `git ls-remote` confirms GitHub's `main` = `ac26f06`.

**0.5 folder skeleton**
- Directive (Shaela): skeleton only, no code. `src/understance/` with `domain/`, `ports/`, `usecases/`, `adapters/`, `orchestration/`, each with an empty `__init__.py`; top-level `tests/`, `sample_app/`, `evals/`, `input_examples/`, `output_examples/`, each with a `.gitkeep`; `logs/` not tracked (gitignored, created at runtime); `requirements.txt` with only `pytest` and `ruff` (FastAPI and sponsor SDKs come at their phases); a virtualenv at `.venv`.
- Observation: this Mac has no `python` command, only `python3` (Python 3.14.7, /Library/Frameworks). The venv was created with `python3 -m venv .venv`; its Python is 3.14.7. Nothing installed into it yet.
- Checks: `.venv` ignored (`.gitignore` line 9), `logs/` ignored (line 12).
- Directive (Shaela): GitHub email verification resolved (she verified `git@shaelabeard.com`); 0A and the coding tool's attribution setting assigned to Step 0.6.
- 0.5 commit `05d1a42` (12 files, no trailer), not pushed.
- Directive (Shaela): add an empty `src/understance/__init__.py` (regular package, not namespace). Done.
- Directive (Shaela): install the dev deps and pin them. `.venv/bin/pip install pytest ruff` installed pytest 9.1.1, ruff 0.17.2, plus transitive iniconfig 2.3.1, packaging 26.3, pluggy 1.7.0, pygments 2.21.0. Confirmed with `pytest --version` and `ruff --version`. `requirements.txt` now `pytest==9.1.1` and `ruff==0.17.2`. pip printed a notice that pip 26.2.2 is available (venv has 26.2.1); not upgraded.
- Directive (Shaela): import-path wiring deferred to Phase 1; full dependency locking revisited at Phase 5. Amended into the 0.5 commit with the same message, then pushed.

**0.6 pre-commit hook, 0A, attribution setting**
- Directive (Shaela): pre-commit framework with the official ruff hooks only (lint + format), the checks that exist now. Installed pre-commit 4.7.0 into `.venv` and pinned it (`requirements.txt`: `pre-commit==4.7.0`, `pytest==9.1.1`, `ruff==0.17.2`). Checked the hook names at the official repo's `v0.17.2` tag (matches our ruff): `ruff-check` (lint; `ruff` is a legacy alias) and `ruff-format`. `.pre-commit-config.yaml` uses those two; `pre-commit validate-config` passed; `pre-commit install` wrote `.git/hooks/pre-commit`.
- Proof (planted violation): staged the config, planted `src/understance/_planted_violation.py` containing only `import os`, attempted a commit. Hook output: `ruff check ... Failed`, `F401 os imported but unused`; commit exit 1; HEAD stayed `dd0bbe9`. Unstaged and deleted the planted file; never committed. Then `pre-commit run --all-files`: both hooks Passed on the real tree. (The run printed "Unstaged files detected" because requirements.txt was not yet staged; pre-commit stashed and restored it. Expected, not a failure.)
- 0A: read docs/DECISIONS.md in full. The build spec (section 18) is not reachable, so 0A was NOT ticked; see open thread 10.
- Directive (Shaela): configure the coding tool to omit attribution. Created `.claude/settings.json` (repo-scoped, committed, visible) with `"attribution": {"commit": "", "pr": "", "sessionUrl": false}`. The deprecated `includeCoAuthoredBy` key was not used. JSON validated with `jq`.
- Directive (Shaela): architecture/governance test runs and a dedicated dead-code detector join the hook at 1.3 / 2.6, not now.
- Directive (Shaela): close 0A with docs/DECISIONS.md as the authoritative in-repo record (build spec is private). BUILD_ORDER.md header note and 0A line changed from "spec section 18" to "docs/DECISIONS.md"; 0A ticked.
- Directive (Shaela): add `ruff.toml` (not pyproject) enabling C901 (max-complexity 10) and PLR0915 (ruff default, confirmed via `ruff check --show-settings`: `max_statements = 50`). Recorded in docs/CONVENTIONS.md under "Code health." Proof: planted one function with 27 branches and 53 statements; the hook blocked it with C901 (27 > 10) and PLR0915 (53 > 50); HEAD unchanged; planted file removed, never committed; real tree passes.
- Directive (Shaela): DECISIONS.md FOR-THE-DECK item 5 replaced with her exact wording.
- Helper observation: BUILD_ORDER.md header still points to the private spec for sections 17 and 19 (open thread 14).
- Directive (Shaela): amend the 0.6 commit with the message "Complete Phase 0: pre-commit hook, code-health caps, no-attribution setting, 0A confirmed," then push.

### Phase 1.1, pass 1 (graph entities)
- Directive (Shaela): settle import-path wiring first. Created `pytest.ini` (`[pytest]` / `pythonpath = src`). Verified: pytest reports `configfile: pytest.ini`, collects 0 items (no tests yet), and `understance.domain` imports from `src/`. Recorded in docs/CONVENTIONS.md.
- Halted at the design review before writing tests: the field names and the meaning of an orphan are not in docs/CONVENTIONS.md, so they were put to Shaela as one short list (CLAUDE.md: do not invent names; surface forks before code).
- Design approved by Shaela with three refinements: (1) `DependencyGraph.modules` and `.dependencies` stored as tuples (truly immutable), `orphans()` still returns a sorted list; (2) Symbol dropped from pass 1, added at the step that first uses symbol-level dependencies; (3) a failing test for the dangling-target case. Recorded in docs/DECISIONS.md (Architecture). Note: BUILD_ORDER 1.1 lists Symbol, so the 1.1 box waits for Symbol or an amended BUILD_ORDER (pending Shaela).
- RED: wrote `tests/test_dependency_graph.py` (9 tests) first. Run: `ModuleNotFoundError: No module named 'understance.domain.graph'`, 1 collection error, 0 passed.
- GREEN: wrote `src/understance/domain/graph.py` (frozen dataclasses `Module`, `Dependency`, `DependencyGraph`; only import is `from dataclasses import dataclass`). Run: 9 passed. ruff check and ruff format pass (formatter wrapped one long test line).
- Discrimination check (scratchpad copies, real code untouched): removing the self-import rule, the sorting, or the tuple conversion each makes exactly 1 test fail. The dangling-target test passes without special code (an unknown target never matches a module); it guards against a later change that would, for example, add missing targets as modules.
- File names `src/understance/domain/graph.py` and `tests/test_dependency_graph.py` are not in docs/CONVENTIONS.md; chosen as reversible defaults, pending Shaela.
- Paused at green for Shaela's gate; not committed.
- Directive (Shaela): commit 1.1 pass 1 but do NOT mark 1.1 done or advance to 1.2 (understanding gate open). BUILD_ORDER 1.1 rewritten to two passes (pass 1 Module/Dependency/DependencyGraph; pass 2 Finding/Evidence/Provenance; Symbol deferred to about 2.4, compute_blast_radius); checkbox left unchecked. File names approved and recorded in docs/CONVENTIONS.md ("Source and test files": cluster per file, test mirrors module). `tests/.gitkeep` deleted. The Symbol-deferral entry in docs/DECISIONS.md updated in place (target about 2.4; BUILD_ORDER amended).
- NOT DONE, pending Shaela: a "two-homes-with-relay" DECISIONS entry was requested, but nothing in this session or the repo describes it (searched all .md files for "relay" and "two homes": no hits). Not written, to avoid inventing it. Needs Shaela's content.
- RESOLVED: Shaela supplied the "two homes with a relay rule" decision (project decision map + repo docs/DECISIONS.md; orchestration-window decisions relayed to the build session for the repo, build decisions mirrored back; collapse to the repo when planning winds down). Recorded in docs/DECISIONS.md under Process, after "Reconcile before recording."

### Oct 26, Phase 1.1 pass 2 (Finding, Evidence, Provenance)
- Phase 1.2 design proposal brought first (no code). The Rival flagged the Explainer port/agent name collision. Shaela directed pass 2 before 1.2 and approved the rename: the port is Narrator, the agent stays Explainer (recorded in docs/DECISIONS.md; applied at 1.2).
- RED: `tests/test_finding.py` (10 tests, content supplied by Shaela). Run: `ModuleNotFoundError: No module named 'understance.domain.finding'`.
- GREEN: `src/understance/domain/finding.py` (content supplied by Shaela; imports only `dataclasses` and `enum`). Run: 10 passed.
- Mutation check: removing the empty-evidence check fails only `test_finding_rejects_empty_evidence`; dropping the `tuple()` normalization fails only `test_finding_normalizes_evidence_to_a_tuple`. Restored byte-identical; 10 passed.
- HALT: `pre-commit run --all-files` skips untracked files, so its "Passed" did not cover the new files. Direct ruff showed the test file failing I001 (import order) and ruff-format (four lines over 88). Shaela: her draft's mistake; apply `ruff check --fix` and `ruff format`, diff limited to the import reorder and line wraps (confirmed), then stage before running the hook. Hook passed on the staged files; full suite 19 passed.
- Lesson: stage new files before `pre-commit run --all-files`, or the hook does not see them.
- Names added to docs/CONVENTIONS.md: `FindingKind`, `finding.py`, `tests/test_finding.py`. The ports line is unchanged until 1.2.
- Understanding gate (part 4) for 1.1 closed: Shaela restated both passes. Before recording, the panel flagged that the pass 1 wording ("imports others while nothing imports it") was narrower than the code; Shaela approved the code-accurate definition (nothing else imports it, whether or not it imports anything itself). Recorded in docs/DECISIONS.md; 1.1 ticked in docs/BUILD_ORDER.md.

### Oct 26, Phase 1.2 (the four ports, Narrator rename)
- RED: `tests/test_ports.py` (8 tests, supplied by Shaela): `ModuleNotFoundError: No module named 'understance.ports.interfaces'`. GREEN: `src/understance/ports/interfaces.py` (supplied; imports `abc`, `pathlib`, and the domain only): 8 passed; ruff changed nothing; full suite 27 passed. HALT before the docs: "Explainer" as the port also appeared in CLAUDE.md:41, BUILD_ORDER 1.2 and 2.5 (TemplateExplainer), and older DECISIONS entries. Shaela: rename those to Narrator/TemplateNarrator now; leave older dated DECISIONS entries as written (note added to the 1.2 entry); update FOR THE DECK item 4; GOVERNANCE's only "Explainer" is the agent, unchanged. CLAUDE.md gains ports/ in the dependency rule and the automatic-panel bullet. 1.2 box stays unchecked until Shaela's own-words restatement.
- Understanding gate (part 4) for 1.2 closed by Shaela; 1.2 ticked in docs/BUILD_ORDER.md.
- Sprint speed change (Shaela, Oct 26): done-gate part 4 in CLAUDE.md amended to a recorded plain-language snippet; own-words restatement no longer blocks advancing. Recorded in docs/DECISIONS.md.
- 1.3: a test now reads every file in the inner rings and fails if any imports an adapter or an outside library; inner rings use absolute imports only. Wired into pre-commit so the rule is enforced every commit. Shown failing on a planted forbidden import, then passing when removed.
- 2.1: added sample_app, a tiny subscription-SaaS fixture (seven modules with real import relationships and a deliberately ambiguous cancellation-timing function) plus its hand-verified expected dependency graph (the edges, and that main is the sole orphan). Tests pin the fixture to that truth. It is only ever parsed, never executed.

### Oct 26, Phase 2.1 reopened
- Found: the 2.1 box was checked before comparing the fixture to BUILD_ORDER line 76. Missing: the circular dependency, the in-fixture tests with one untested module, and the access module (auth instead).
- Shaela approved reopening 2.1 and correcting the fixture to match line 76 in full. The corrected-fixture instruction follows as a separate commit.

### Oct 27, tool names removed
- Directive (Shaela): instructions name no tool; nothing in the repo names the coding tool or an AI model except the README AI-usage line. Replaced the mentions in CLAUDE.md, BUILD_ORDER, DECISIONS, REQUIREMENTS, and STATE with neutral wording (substance unchanged; earlier log lines were reworded only to remove the name), redacted one DECISIONS entry about the orchestration window's AI model settings, and added an Instruction style section to CONVENTIONS. File names CLAUDE.md and .claude/settings.json are kept (functional).

### Oct 27, Phase 2.1 corrected fixture
- sample_app now matches BUILD_ORDER line 76: auth renamed to access; a subscriptions <-> access cycle (access imports subscriptions inside has_access so the fixture loads cleanly); sample_app/tests/ covers every module except notifications; pytest.ini testpaths = tests so our suite never runs the fixture's tests. Truth: 7 modules, 12 edges, main the sole orphan, chain, cycle, and untested module recorded in tests/sample_app_truth.py.
- Clarifies the earlier 2.1 note "It is only ever parsed, never executed": our analysis of sample_app is static (it never imports or executes subject code); separately, differential verification at 4.2 runs the trusted fixture's own tests. Two different activities, not a contradiction.
- Snippet (gate part 4): 2.1 gives Understance a small, honest practice repo whose every import is hand-checked, including one real loop between subscriptions and access and one module with no test, so later steps can be graded against known truth.

### Oct 27, README overhaul
- README replaced with the approved overhaul: problem-first story, an honest FAQ, plain-English dated milestones (only what works is checked), and verified Nightshift setup steps (M1 to M4 edition, local Qwen 2.5 1.5B, .env names). Every capability not yet built is marked in progress.

### Oct 27, sponsor setup recorded
- Directive (Shaela): record the Zetaris and Nightshift setup with its evidence, so the README milestones and the project record agree. Older log lines (including the Oct 26 line that calls 0B pending) are kept as written; this entry supersedes them.
- Zetaris (Oct 26): local Docker instance on the build machine (amd64 under Rosetta, about 7 GB while running). `SELECT 1` returned 1 and `SELECT * FROM NY_TAXI.taxi_zones LIMIT 5` returned typed rows; recorded in DECISIONS as the Zetaris characterization finding.
- Nightshift (Oct 27): M1 to M4 edition on the Apple M1 Pro. First real request: receipt rcpt_req_ce9imi24, routed to the local Qwen 2.5 1.5B model, 2284 ms, privacy path local-only, egress none. Evidence: terminal output observed by Shaela; the key was never shown. Not yet wired into the Narrator adapter (Phase 3.3).
- Decisions recorded in DECISIONS: Nightshift installed and answering; Qwen 2.5 1.5B as the local model; NVIDIA deferred; the Zetaris Unified Semantic Layer as required scope. The Oct 24 hosted-Nemotron entry is marked superseded.
- Left open: the 0B Zetaris box stays unchecked until Shaela confirms the Zetaris Cloud registration; the HackOS team box is unchanged.

### Oct 27, Phase 2.2 ast SourceReader
- Directive (Shaela): build the first real adapter as a spec plus a failing test; the test file was supplied, the adapter was written to pass it.
- RED: tests/test_ast_source_reader.py failed to import understance.adapters.ast_source_reader. GREEN: 15 passed; full suite 55 passed. Planted violation: reading only top-level statements made the function-level-import and exact-edges tests fail; restored and green again.
- Also: .claude/settings.json now denies reading ./.env (not tested against the real file, by design). The 0B Zetaris box is checked: Shaela uses the participant account Zetaris provided, with the instance running on local Docker.
- Snippet (gate part 4): Understance can now read a Python project without running any of it and draw its map: which file depends on which, including the hidden import tucked inside a function. On the practice app it matches the hand-checked answer exactly, and it says plainly what it left out and why.

### Oct 27, Phase 2.3 AnalyzeRepo
- RED: tests/test_analyze_repo.py failed to import understance.usecases.analyze_repo. GREEN: 3 passed; full suite 58 passed. Planted violation: removing the store call made the storing tests fail; restored and green again.
- Also corrected the 0.6 status line: .claude/settings.json now holds the attribution setting and the .env read denial (added at 2.2).
- Snippet (gate part 4): Understance now has its first complete action: point it at a project, and it reads the map and files it away as facts, the same way whether the facts go to memory today or to Zetaris tomorrow.

### Oct 27, Phase 2.4 ComputeBlastRadius
- RED: the new tests failed to import BlastRadius and ComputeBlastRadius. GREEN: full suite 73 passed. Planted violation: letting the target appear in its own radius made the radius tests fail; restored and green again.
- Hand trace (sample_app.subscriptions): dependents access, api, billing, main, notifications; it depends on access and models; 8 import edges into it, each an observed finding with file and line (for example sample_app/access.py line 14, the import inside a function).
- Scope: module level only; symbol level deferred past the hackathon (Shaela).
- Snippet (gate part 4): name one part of the app, and Understance now lists everything that would feel a change to it, through every layer, and points to the exact file and line that proves each link.

### Oct 27, Phase 2.5 the four agents
- Directive (Shaela): review the agents' actions, rules and limits with the full panel before any agent code; the review produced 9 fixes, approved. Names approved after the panel resolved two concerns (ReadOnlyFactStore in its own file; Scope as a fixed list).
- RED: the new tests failed to import the agents, the orchestrator and the answer types. GREEN: full suite 104 passed. Planted violation: handing the agents the raw store instead of ReadOnlyFactStore made the least-privilege test fail; restored and green again.
- Trace fields now: timestamp, run_id, agent_name, action, input_summary, output_summary, target_agent, model, confidence, retry_count, status.
- Snippet (gate part 4): ask "what would changing subscriptions affect?" and four agents work it out. The Planner looks at direct importers first; the Evaluator notices main also leads in and sends it back; the widened answer names 5 modules with the file and line for each link; an invented claim is blocked, never explained; and every step is written to the log.

### Oct 27, Phase 2.5b concept words and the policy stop-and-ask
- RED: the new tests failed (no defines, no open questions, no needs_decision). GREEN: full suite 119 passed. Planted violation: never flagging the decision made the stop-and-ask tests fail; restored and green again.
- Snippet (gate part 4): say "add customer cancellation" and Understance works out that subscriptions owns cancellation (it defines cancel_subscription), shows the 5 modules a change would reach with the proof for each link, then stops: the code does not say whether cancellation takes effect immediately or at the end of the billing period, so it asks you instead of guessing.

### Oct 27, Phase 3.1 the facts as CSV files
- Zetaris observed first: a CSV in NDP File System /file-store, registered with Create Table in a File Source & API container, answered SQL (workbench, 7 rows) and the REST API (POST /api/v1.0/query/sql/start: 200, records as JSON objects; close: 200). The API token lives only in .env.
- RED: the new tests failed to import the new adapters; GREEN: full suite 134 passed. Planted violation: dropping the git guard made the command test fail; restored and green again.
- facts/ written by scripts/export_facts.py from sample_app and committed.
- Snippet (gate part 4): Understance now writes what it knows as six small files, the code map, the last change to each file, and which tests cover which module, ready for Zetaris to join them into one view, and usable offline when Zetaris is not there.

### Oct 27, Phase 3.2 the facts through Zetaris
- Directive (Shaela): the data quality rule should run itself; it runs on every read and stops on broken links. A native Zetaris rule was attempted three ways and was not reachable in this version (see DECISIONS); the rule now runs in Zetaris on every agent run.
- RED: tests/test_zetaris_fact_store.py and tests/test_fallback_fact_store.py failed to import the new adapters. GREEN: full suite 161 passed. Planted violation: skipping the rule made test_the_data_quality_rule_runs_first_and_is_logged fail; restored and green again.
- Live check: scripts/check_zetaris.py, run by Shaela after this commit (it reads .env); result recorded when observed.
- Snippet (gate part 4): before the agents answer anything, Understance now asks Zetaris to prove the facts hang together: every import link must point at a module that exists. Then it reads the joined view Zetaris built from three sources. If Zetaris is down, it says so and answers from the offline copy; if the facts are broken, it stops instead of guessing.

### Oct 27, Phase 3.2 live check
- Shaela ran scripts/check_zetaris.py: data quality passed (0 broken links); reads of 7, 12, 15, 1 and 9 rows; MATCH with facts/. One fact through Zetaris: sample_app.notifications imports sample_app.subscriptions (sample_app/notifications.py, line 3), 0 test files, last change 52fe793. Gate met; 3.2 ticked.

### Oct 27, Phase 3.3 the Nightshift narrator
- Directive (Shaela): approved the name nightshift_narrator.py and the guard; the model writes a short summary only, and the proof stays deterministic.
- RED: tests/test_nightshift_narrator.py failed to import the new adapter. GREEN: full suite 186 passed. Planted violation: removing the file-path check made test_the_observed_distortion_is_blocked_and_the_proof_stands_alone fail; restored and green again.
- Live check: scripts/check_nightshift.py, run by Shaela after this commit (it reads .env); result recorded when observed.
- Snippet (gate part 4): Understance now asks a model to say, in plain words, what the verified links mean. It hands the model the links only, never the files or lines, and checks every sentence that comes back. This morning the model claimed billing lives at api.py line 4, which is wrong; that sentence would now be blocked, and the answer would show only the proof, file and line, straight from the facts.

### Oct 27, Phase 3.3 live check
- Shaela ran scripts/check_nightshift.py: receipt rcpt_req_fploapv2, local Qwen 2.5 1.5B, 2069 ms, privacy local-only, egress none, cross-check passed; the model's sentence passed the guard and was shown above the 8 proof lines. Gate met; 3.3 ticked. Limit recorded in DECISIONS: the guard does not judge a sentence's direction or meaning.

### Oct 27, Phase 3.4 H-MEM memory
- Directive (Shaela): H-MEM in Python behind MemoryStore, decisions only for now; README wording exact.
- RED: tests/test_hmem_memory.py failed to import the adapter, and the 2 Decision tests failed to import Decision. GREEN: full suite 213 passed. Planted violation: dropping the superseded penalty made test_the_superseded_penalty_holds_when_the_old_record_came_first fail; restored and green again.
- Snippet (gate part 4): tell Understance once how cancellation should work, and it remembers, in a plain file on your machine that is only ever added to. Change your mind later and the new answer wins, while the old one stays on the record with who decided and when.

### Oct 27, Phase 3.5 the end-to-end run
- Directive (Shaela): one run through Zetaris, Nightshift and H-MEM; POST /run with the standard-library server; label the model's sentence; decisions asked once.
- RED: the new shell, server and read-only memory tests failed to import; the orchestrator, answer and narrator tests failed on the new behavior. GREEN: full suite 238 passed. Planted violation: letting the agents hold the raw memory made test_each_agent_holds_only_the_ports_its_role_needs fail; restored and green again.
- Examples: input_examples/ holds 3 request bodies; output_examples/ holds their sample-mode answers and one trace.
- GATE 3: Shaela's live run, recorded when observed.
- Snippet (gate part 4): ask Understance about adding customer cancellation and it traces the 5 modules a change would reach, with the proof, then stops on the open policy question. Answer it once, and it records your decision in H-MEM; ask again tomorrow and it reminds you what you decided, with who and when, instead of asking twice. Every step is in a trace file, and it runs offline when the sponsors are not there.

### Oct 27, step 3.6 the capabilities manifest and the evals
- Directive (Shaela): keep the evals and the capabilities manifest; Docker and NVIDIA cut; Phase 4 as time allows.
- RED: tests/test_capabilities.py failed to import the manifest. The 7 evals passed from the start: they pin behavior built in 3.5. GREEN: full suite 253 passed. Planted violation: naming a test that does not exist in the manifest made test_every_claim_and_limit_names_a_test_that_exists fail; restored and green again.
- Output examples regenerated in sample mode (every answer now carries the scope line).
- Snippet (gate part 4): ask Understance what it can and cannot do, and it answers from a list where every promise points to the test that proves it. Seven scenarios, written before the answers were seen, run on every commit, and the code it reads is checked unchanged afterwards.

### Oct 27, step 3.7 README, metadata.json, Zetaris setup, full-suite hook
- Directive (Shaela): the README and submission files before the web page; the page last, so it can be dropped without loss.
- 2 new tests (metadata paths and the H-MEM wording); full suite 255 passed. The new pre-commit hook blocked a planted failing test, which was then removed.
- Snippet (gate part 4): anyone can now clone Understance, run it in a minute with no setup beyond Python, read exactly where Zetaris, Nightshift and H-MEM sit, and rebuild the Zetaris layer step by step. Every commit now runs every test.
