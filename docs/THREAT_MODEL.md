# THREAT MODEL - each threat mapped to the safeguard that mitigates it
**Owner:** Shaela Beard · Understance · Open Agent Hackathon 2026 · Track 2
**Status:** Starter; to be expanded from the build spec at the relevant phase. The expansion uses a structured method, Adam Shostack's four questions plus STRIDE, per docs/DECISIONS.md.
**Last updated:** Oct 26, 2026.

Source for this starter: the "Agent governance," "Secrets," and user-safeguards (spec 24) rules in CLAUDE.md. These are planned safeguards. None is enforced by code yet; each becomes real only when its test is written and shown to fail on a planted violation at its build step.

| Threat | What could go wrong | Safeguard |
|---|---|---|
| Hostile repo | A subject repo is crafted to run code, escape the folder, or exhaust resources when read. | Never import or execute subject code: `ast` static parse only, no import, no `setup.py`, no `conftest`. Hardened reader: file-size caps, no symlink escape, path-traversal safe, no archive expansion. Read-only on the subject repo, proven by the byte-for-byte unchanged governance test. |
| Prompt injection | Text in the subject repo (comments, docstrings, strings) tells the model to do something. | Repo content is data, never instructions; it is never fed to the model as instructions. The tool has no write, apply-change, or delete capability for an injection to trigger. Every output claim must carry an evidence id resolving to a Fact, or it is dropped. Every action and refusal is logged as JSONL. |
| Secret exposure | A key or token in the subject repo, or the tool's own credentials, leaks into storage, logs, the model, or output. | Secrets in the subject repo are detected and redacted on ingest; the value is never stored, logged, sent, or displayed; presence is flagged as "likely," not "guaranteed." The tool's own secrets live in environment variables, read only inside adapters; agents never receive raw clients or tokens. No key, token, .env, .pem, or .key is ever committed. |
| History store as a target | The local per-repo history/recovery store is read, tampered with, or corrupted. | Local-only; holds references and hashes, never secrets or raw code contents; never synced to a cloud without explicit consent. SQLite ACID transactions plus `integrity_check`; a corrupt store is detected and the user is told, never silently lost. FK constraints enforce referential integrity. Saved findings are state-stamped and re-validated on reopen (still-valid / stale / unknown). |
| Untrusted test execution | Running a subject repo's tests runs arbitrary code. | Tests run only on the trusted `sample_app`. Arbitrary-repo execution is sandboxed, opt-in, and future work; the default is static-impact-only. |

## To be expanded
- Shostack's four questions (what are we working on, what can go wrong, what are we going to do about it, did we do a good job) and STRIDE per component.
- Link each safeguard to the test that enforces it, once that test exists.
