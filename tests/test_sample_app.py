import ast
from itertools import pairwise
from pathlib import Path

from sample_app_truth import (
    EXPECTED_BLAST_RADIUS,
    EXPECTED_CHAIN,
    EXPECTED_CYCLE,
    EXPECTED_DEPENDENCIES,
    EXPECTED_IMPORT_LINES,
    EXPECTED_MODULES,
    EXPECTED_OPEN_QUESTIONS,
    EXPECTED_ORPHANS,
    EXPECTED_UNTESTED,
)

SAMPLE_APP = Path(__file__).resolve().parent.parent / "sample_app"
FIXTURE_TESTS = SAMPLE_APP / "tests"


def _module_name(path):
    rel = path.relative_to(SAMPLE_APP.parent).with_suffix("")
    return ".".join(rel.parts)


def _py_files(root):
    return [p for p in root.rglob("*.py") if p.name != "__init__.py"]


def _modules():
    return [p for p in _py_files(SAMPLE_APP) if FIXTURE_TESTS not in p.parents]


def _imported_names(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
        elif isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
    return names


def test_every_sample_app_file_parses():
    files = _py_files(SAMPLE_APP)
    assert files, "sample_app has no modules"
    for path in files:
        ast.parse(path.read_text(encoding="utf-8"))


def test_sample_app_modules_match_the_hand_verified_truth():
    found = {_module_name(p) for p in _modules()}
    assert found == set(EXPECTED_MODULES)


def test_truth_edges_reference_known_modules():
    known = set(EXPECTED_MODULES)
    for source, target in EXPECTED_DEPENDENCIES:
        assert source in known
        assert target in known


def test_truth_orphans_are_never_import_targets():
    targets = {t for _, t in EXPECTED_DEPENDENCIES}
    for orphan in EXPECTED_ORPHANS:
        assert orphan in EXPECTED_MODULES
        assert orphan not in targets


def test_truth_has_exactly_one_orphan():
    targets = {t for _, t in EXPECTED_DEPENDENCIES}
    assert set(EXPECTED_MODULES) - targets == set(EXPECTED_ORPHANS)
    assert len(EXPECTED_ORPHANS) == 1


def test_truth_chain_follows_real_edges():
    edges = set(EXPECTED_DEPENDENCIES)
    for source, target in pairwise(EXPECTED_CHAIN):
        assert (source, target) in edges


def test_truth_cycle_has_both_edges():
    a, b = EXPECTED_CYCLE
    assert (a, b) in EXPECTED_DEPENDENCIES
    assert (b, a) in EXPECTED_DEPENDENCIES


def test_untested_module_is_imported_by_no_fixture_test():
    imported = set()
    for path in _py_files(FIXTURE_TESTS):
        imported |= _imported_names(path)
    tested = set(EXPECTED_MODULES) & imported
    assert set(EXPECTED_MODULES) - tested == set(EXPECTED_UNTESTED)


def test_truth_import_lines_point_at_real_import_statements():
    assert set(EXPECTED_IMPORT_LINES) == set(EXPECTED_DEPENDENCIES)
    for (source, target), line in EXPECTED_IMPORT_LINES.items():
        path = SAMPLE_APP.parent / (source.replace(".", "/") + ".py")
        text = path.read_text(encoding="utf-8").splitlines()[line - 1]
        assert "import" in text
        assert target in text


def _reach(start, edges):
    found, frontier = set(), {start}
    while frontier:
        frontier = {t for s, t in edges if s in frontier} - found - {start}
        found |= frontier
    return tuple(sorted(found))


def test_truth_blast_radius_follows_the_truth_edges():
    reverse = [(t, s) for s, t in EXPECTED_DEPENDENCIES]
    for target, expected in EXPECTED_BLAST_RADIUS.items():
        assert _reach(target, reverse) == expected["dependents"]
        assert _reach(target, EXPECTED_DEPENDENCIES) == expected["dependencies"]


def test_truth_open_questions_point_at_ambiguous_comments():
    for module, questions in EXPECTED_OPEN_QUESTIONS.items():
        assert module in EXPECTED_MODULES
        for file, line, _ in questions:
            text = (SAMPLE_APP.parent / file).read_text(encoding="utf-8")
            assert text.splitlines()[line - 1].strip().startswith("# AMBIGUOUS:")
