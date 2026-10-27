# STATE - where the build is right now
**Owner:** Shaela Beard · Understance · Open Agent Hackathon 2026 · Track 2
**Rule:** kept current at the end of every step (part of the done-gate). Logs the questions asked and the answers given, not just outcomes, so a newcomer can reconstruct what was done and why.
**Last updated:** Oct 26, 2026.

## Current position
- **Phase:** 2 (use cases with fakes). Phases 0 and 1 COMPLETE (Oct 26).
- **Step:** Phase 2.1 done: corrected fixture matches BUILD_ORDER line 76 (access module, subscriptions <-> access cycle, in-fixture tests, notifications untested).
- **Next:** Phase 2.2: the ast SourceReader adapter. It must capture every import in a file, including imports inside functions, and must exclude sample_app/tests/ (test evidence, not graph modules) and state that exclusion in its scope line.
- **Settled (Shaela, Oct 26):** docs/CONVENTIONS.md is authoritative for the folder layout and supersedes the start kit (`orchestration/`, `evals/`, `input_examples/`, `output_examples/`, `requirements.txt`). 0B's Nightshift install and NVIDIA-key setup are pending, to be done before Phase 3. The footprint report and the subject-repo-unchanged test are deferred to Phase 2/3.

## What is green
- 0.1 git init: done. Branch `main`.
- 0.2 hygiene baseline: done. `.gitignore`, `.env.example` (placeholders only), `README.md` skeleton.
- 0.3 first commit and remote: done. Commit `71f9131` "Initialize repo and hygiene baseline" (3 files, no attribution trailer), pushed to `origin/main`; verified against GitHub with `git ls-remote` (remote `main` = `71f9131`).
- 0.4 CLAUDE.md and docs/: done. Commit `ac26f06`, pushed; `origin/main` = `ac26f06`.
- 0.5 folder skeleton: done. Commit `dd0bbe9`, pushed; `origin/main` = `dd0bbe9`.
- 0.6 pre-commit hook: ruff-check + ruff-format (ruff-pre-commit v0.17.2) installed at `.git/hooks/pre-commit`. Shown to FAIL on a planted violation (unused `import os` blocked with F401, commit exit 1, HEAD unchanged; planted file removed, never committed). Real tree passes both hooks.
- 0.6 code-health caps: `ruff.toml` adds C901 (`max-complexity = 10`) and PLR0915 (ruff default `max-statements = 50`) to ruff's defaults; recorded in docs/CONVENTIONS.md. Shown to FAIL on a planted violation (one function blocked with `C901 too complex (27 > 10)` and `PLR0915 Too many statements (53 > 50)`, HEAD unchanged; planted file removed, never committed). Real tree passes.
- 0.6 attribution setting: `.claude/settings.json` sets `attribution` to `{"commit": "", "pr": "", "sessionUrl": false}`.
- 0A: confirmed. docs/DECISIONS.md is the authoritative in-repo record of the locked decisions (the build spec is private, not in the repo); read in full; ticked in docs/BUILD_ORDER.md.
- Tests: 40 pass (9 graph, 10 finding, 8 ports, 5 architecture, 8 sample_app)

## Open threads
1. ~~Em dashes in two planning docs~~ RESOLVED Oct 26: all 5 (4 in DECISIONS.md, 1 in REQUIREMENTS.md) replaced with commas.
2. ~~Folder skeleton: start kit vs CONVENTIONS.md~~ RESOLVED Oct 26: CONVENTIONS.md is authoritative.
3. **BUILD_ORDER.md Phase 0 items not in the start kit:** 0B Nightshift + NVIDIA-key setup pending before Phase 3; footprint report/test deferred to Phase 2/3; `evals/` comes with the 0.5 skeleton (CONVENTIONS.md). The coding tool's attribution setting is done at 0.6. 0A: see thread 10.
4. **GOVERNANCE.md and THREAT_MODEL.md are starters** drawn from CLAUDE.md; to be expanded from spec 17/19/23/24 and Shostack + STRIDE at the relevant phase.
5. ~~GitHub email verification~~ RESOLVED Oct 26: Shaela verified `git@shaelabeard.com` on her GitHub account.
6. ~~No `src/understance/__init__.py`~~ RESOLVED Oct 26 (Shaela): empty `src/understance/__init__.py` added, so `understance` is a regular package.
7. ~~requirements.txt unpinned~~ RESOLVED Oct 26 (Shaela): installed into `.venv` and pinned to the installed versions, `pytest==9.1.1`, `ruff==0.17.2`.
8. ~~Import-path wiring for `understance`~~ RESOLVED Oct 26 (Shaela, Phase 1.1): `pytest.ini` with `pythonpath = src` (no pyproject.toml); recorded in docs/CONVENTIONS.md.
9. **Full dependency locking** for fresh-clone reproducibility is to be revisited at Phase 5, when the runtime deps (FastAPI, the sponsor clients) are in; for now only the two top-level dev tools are pinned. Their transitive deps (iniconfig, packaging, pluggy, pygments) are not pinned (Shaela, Oct 26). pre-commit (4.7.0) was added and pinned at 0.6; its transitive deps are not pinned either.
10. ~~0A not ticked~~ RESOLVED Oct 26 (Shaela): docs/DECISIONS.md is the authoritative in-repo record of the locked decisions; the build spec is private and not in the repo. docs/BUILD_ORDER.md header note and the 0A line now point to docs/DECISIONS.md instead of "spec section 18"; 0A ticked.
11. **Pre-commit hook additions at their phases (Shaela, Oct 26):** ~~the architecture fitness test run joins the hook at 1.3~~ RESOLVED: landed in 2a7a6fe. Still open: the governance test run and a dedicated dead-code detector join at 2.6.
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
