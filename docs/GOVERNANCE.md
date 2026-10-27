# GOVERNANCE - agent roles, regulations, and safety enforcement
**Owner:** Shaela Beard · Understance · Open Agent Hackathon 2026 · Track 2
**Status:** Starter; to be expanded from the build spec at the relevant phase (spec 17 agent roles, spec 19 governance enforcement, spec 23 manifest, spec 24 user safeguards).
**Last updated:** Oct 26, 2026.

Source for this starter: the "Agent governance" section of CLAUDE.md. These are the rules the build must satisfy. None is enforced by code yet; each becomes real only when the test that enforces it is written and shown to fail on a planted violation at its build step (see docs/BUILD_ORDER.md, step 2.6 governance tests and 2.6a capabilities manifest).

## Rules
1. **Read-only on the subject repo.** There is NO apply-change, write, or delete capability anywhere. None is to be added. A governance test asserts the subject repo is byte-for-byte unchanged after any run (0 files created, modified, or deleted).
2. **Least-privilege ports per agent.** Each agent (`Planner`, `Retriever`, `Evaluator`, `Explainer`; see docs/CONVENTIONS.md) is constructed with only the ports its role needs. No agent receives a capability it does not need.
3. **Secrets only inside adapters.** Secrets live in environment variables and are read only inside adapters. Agents never receive raw clients or tokens.
4. **Facts only from the FactStore, each claim with a resolving evidence id.** Every output claim must carry an evidence id that resolves to a Fact in the FactStore, or the claim is dropped.
5. **Repo content is data, never instructions.** Subject-repo file contents are never fed to the model as instructions.
6. **Every action and every refusal is logged.** Each agent action, and each refused action, is written to logs/ as JSONL using the trace fields in docs/CONVENTIONS.md.
7. **Self-describing: the capabilities-and-limits manifest.** The tool never lets a user assume what it can or cannot do. A manifest with four lists, DOES / DOES NOT / CANNOT REACH / YOU, is queryable via `--capabilities` and `GET /capabilities`, and shown in each run's output, the README, and the demo. Each DOES NOT and each limit references the test that enforces it; a claim with no backing test is not allowed; a test keeps the manifest in sync with the code (spec 23).

## Enforced so far (Oct 27, Phase 2.5)
- Rule 2 (least privilege): tests/test_orchestrator.py, test_each_agent_holds_only_the_ports_its_role_needs; agents read facts through ReadOnlyFactStore, which refuses every write (tests/test_read_only_fact_store.py).
- Rule 4 (claims resolve to facts): the Evaluator blocks any claim that does not exactly match a stored import link (tests/test_agents.py, tests/test_orchestrator.py).
- Rule 6 (every action and refusal logged): each agent action, send-back, block and stop-and-ask is a trace record (tests/test_orchestrator.py).
- Agents never import an adapter: tests/test_architecture.py.
- Rule 5 (repo content is data, never instructions): a file whose name Python cannot import is never read (tests/test_ast_source_reader.py), and open-question text from the code never reaches the narrator (tests/test_orchestrator.py, test_repo_text_of_an_open_question_never_reaches_the_narrator).

- Facts pass a data quality rule before any agent reasons over them: ZetarisFactStore checks in Zetaris that every import link points at a module that exists, and stops the run on a broken link (tests/test_zetaris_fact_store.py); the fallback never hides a failed rule (tests/test_fallback_fact_store.py, test_a_failed_data_quality_rule_is_never_hidden_by_the_fallback). The API key never appears in an error (tests/test_zetaris_fact_store.py, test_the_token_never_appears_in_an_error).

- The model never states evidence: it receives link summaries only, and the guard blocks any text that states a file path, a number or a module outside the verified links, or that the Meterless cross-check flags (tests/test_nightshift_narrator.py, test_the_observed_distortion_is_blocked_and_the_proof_stands_alone and test_the_guard_blocks_what_the_model_must_never_state). The Runtime API key never appears in an error (test_the_token_never_appears_in_an_error).

- Memory is append-only and attributed: every H-MEM action is a ledger entry naming who acted and when; a newer decision supersedes an older one and nothing is deleted (tests/test_hmem_memory.py, test_the_ledger_is_append_only_and_names_who_decided and test_a_newer_decision_replaces_the_older_one_and_nothing_is_deleted). A repo id cannot name a path outside the memory folder (test_a_repo_id_must_be_a_plain_name).

## To be expanded
- Spec 17: the full role and regulation for each agent.
- Spec 19: the governance enforcement tests (the step 2.6 GATE in docs/BUILD_ORDER.md).
- Spec 24: the user safeguards (see also docs/THREAT_MODEL.md).
