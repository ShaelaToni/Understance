"""What Understance does, does not do, cannot reach, and what stays the owner's call.

Every DOES, DOES NOT and CANNOT REACH line names the test that enforces it;
tests/test_capabilities.py fails if a named test is missing, so this list
cannot drift from the code.
"""

SCOPE_LINE = (
    "Scope: reads the Python imports of sample_app statically, at module level, "
    "and changes nothing. Dynamic imports, reflection, generated code and other "
    "languages are not followed. Full list: run.py --capabilities."
)

MANIFEST = {
    "does": [
        {
            "claim": "Reads a Python project with ast and never imports or runs its code.",
            "enforced_by": "tests/test_ast_source_reader.py::test_reading_never_runs_subject_code",
        },
        {
            "claim": "Lists every module a change could reach, with the file and line of each import link.",
            "enforced_by": "tests/test_compute_blast_radius.py::test_every_edge_into_the_blast_radius_is_an_observed_finding_with_file_and_line",
        },
        {
            "claim": "Blocks any claim the stored facts do not support.",
            "enforced_by": "tests/test_agents.py::test_evaluator_blocks_a_claim_the_facts_do_not_support",
        },
        {
            "claim": "Stops and asks when the code leaves a decision open, instead of guessing.",
            "enforced_by": "tests/test_orchestrator.py::test_an_open_decision_stops_the_agent_and_asks_the_owner",
        },
        {
            "claim": "Keeps the owner's decision in H-MEM memory and does not ask twice.",
            "enforced_by": "tests/test_app.py::test_an_open_decision_is_asked_then_recorded_then_remembered",
        },
        {
            "claim": "Runs a data quality rule in Zetaris before the agents read any fact.",
            "enforced_by": "tests/test_zetaris_fact_store.py::test_the_data_quality_rule_runs_first_and_is_logged",
        },
        {
            "claim": "Answers from the offline facts, and says so, when Zetaris is unreachable.",
            "enforced_by": "tests/test_fallback_fact_store.py::test_an_unreachable_primary_falls_back_and_says_so",
        },
        {
            "claim": "Writes every agent step, query and model request to a trace file.",
            "enforced_by": "tests/test_app.py::test_a_question_is_answered_with_the_proof_and_a_trace",
        },
    ],
    "does_not": [
        {
            "claim": "Change the code it reads: agents hold read-only facts and read-only memory.",
            "enforced_by": "tests/test_orchestrator.py::test_each_agent_holds_only_the_ports_its_role_needs",
        },
        {
            "claim": "Show a model sentence that states a file, a number or a module outside the verified links.",
            "enforced_by": "tests/test_nightshift_narrator.py::test_the_observed_distortion_is_blocked_and_the_proof_stands_alone",
        },
        {
            "claim": "Send files, line numbers or the code's own comments to the model.",
            "enforced_by": "tests/test_nightshift_narrator.py::test_the_model_sees_link_summaries_only_never_files_or_lines",
        },
        {
            "claim": "Read .env in sample mode.",
            "enforced_by": "tests/test_app.py::test_sample_mode_set_in_the_environment_never_reads_the_env_file",
        },
        {
            "claim": "Follow symlinks out of the project.",
            "enforced_by": "tests/test_ast_source_reader.py::test_symlinks_are_not_followed",
        },
        {
            "claim": "Delete a memory: a newer decision supersedes the older one, which stays on the record.",
            "enforced_by": "tests/test_hmem_memory.py::test_a_newer_decision_replaces_the_older_one_and_nothing_is_deleted",
        },
        {
            "claim": "Hide a failed data quality rule behind the offline fallback.",
            "enforced_by": "tests/test_fallback_fact_store.py::test_a_failed_data_quality_rule_is_never_hidden_by_the_fallback",
        },
        {
            "claim": "Act on instructions written into a question: it only reads and answers.",
            "enforced_by": "tests/test_evals.py::test_the_subject_repo_is_unchanged_after_every_eval",
        },
    ],
    "cannot_reach": [
        {
            "claim": "Dynamic imports (import_module, __import__): named in the scope, not followed.",
            "enforced_by": "tests/test_ast_source_reader.py::test_dynamic_imports_are_named_not_followed",
        },
        {
            "claim": "Files that do not parse: skipped and named.",
            "enforced_by": "tests/test_ast_source_reader.py::test_unparseable_file_is_skipped_and_named",
        },
        {
            "claim": "Files over the size limit: skipped and named.",
            "enforced_by": "tests/test_ast_source_reader.py::test_oversize_file_is_skipped_and_named",
        },
        {
            "claim": "The meaning of the model's sentence: the guard blocks stated evidence, not a wrong reading; the proof lines carry the answer.",
            "enforced_by": "tests/test_nightshift_narrator.py::test_the_guard_blocks_what_the_model_must_never_state",
        },
    ],
    "you": [
        "Settle the decisions the code leaves open, such as when a cancellation takes effect.",
        "Decide whether a change goes ahead: Understance shows the impact and the proof, and never edits code.",
        "Choose the mode: sample mode runs offline; live mode uses Zetaris, Nightshift and H-MEM.",
    ],
}
