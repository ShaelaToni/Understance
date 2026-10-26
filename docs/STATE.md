# STATE - where the build is right now
**Owner:** Shaela Beard · Understance · Open Agent Hackathon 2026 · Track 2
**Rule:** kept current at the end of every step (part of the done-gate). Logs the questions asked and the answers given, not just outcomes, so a newcomer can reconstruct what was done and why.
**Last updated:** Oct 26, 2026.

## Current position
- **Phase:** 0 (setup), following HACKATHON_PHASE0_START_KIT.md (kept out of git).
- **Step:** 0.4 (CLAUDE.md and docs/) committed and pushed; awaiting Shaela's go before 0.5.
- **Next:** 0.5 folder skeleton, using the names in docs/CONVENTIONS.md.
- **Settled (Shaela, Oct 26):** docs/CONVENTIONS.md is authoritative for the folder layout and supersedes the start kit (`orchestration/`, `evals/`, `input_examples/`, `output_examples/`, `requirements.txt`). 0B's Nightshift install and NVIDIA-key setup are pending, to be done before Phase 3. The footprint report and the subject-repo-unchanged test are deferred to Phase 2/3.

## What is green
- 0.1 git init: done. Branch `main`.
- 0.2 hygiene baseline: done. `.gitignore`, `.env.example` (placeholders only), `README.md` skeleton.
- 0.3 first commit and remote: done. Commit `71f9131` "Initialize repo and hygiene baseline" (3 files, no attribution trailer), pushed to `origin/main`; verified against GitHub with `git ls-remote` (remote `main` = `71f9131`).
- No tested code exists yet; no tests have run.

## Open threads
1. ~~Em dashes in two planning docs~~ RESOLVED Oct 26: all 5 (4 in DECISIONS.md, 1 in REQUIREMENTS.md) replaced with commas.
2. ~~Folder skeleton: start kit vs CONVENTIONS.md~~ RESOLVED Oct 26: CONVENTIONS.md is authoritative.
3. **BUILD_ORDER.md Phase 0 items not in the start kit:** 0B Nightshift + NVIDIA-key setup pending before Phase 3; footprint report/test deferred to Phase 2/3; `evals/` comes with the 0.5 skeleton (CONVENTIONS.md). Still unplaced: 0A (confirm locked decisions) and configuring Claude Code to omit attribution.
4. **GOVERNANCE.md and THREAT_MODEL.md are starters** drawn from CLAUDE.md; to be expanded from spec 17/19/23/24 and Shostack + STRIDE at the relevant phase.
5. **GitHub email:** commits link to Shaela's GitHub profile only if `git@shaelabeard.com` is added and verified in GitHub Settings > Emails. Not checked from here.

## Session log (questions asked, answers given, why)

### Session 1 - Oct 26, 2026 (Phase 0)
**Before 0.1 - observations raised by the helper**
- CLAUDE.md was already in the folder; to keep the kit's order it was left out of the first commit and placed at 0.4.
- The planning docs were not yet in the folder (supplied later, before 0.4).
- The helper's default setup adds a "Co-Authored-By: Claude" trailer; CLAUDE.md forbids it, so it was omitted on every commit.

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
