from pathlib import Path

from sample_app_truth import (
    EXPECTED_DEPENDENCIES,
    EXPECTED_IMPORT_LINES,
    EXPECTED_MODULES,
    EXPECTED_OPEN_QUESTIONS,
    EXPECTED_ORPHANS,
)

from understance.adapters.ast_source_reader import ASTSourceReader
from understance.domain.graph import Dependency, Module, OpenQuestion
from understance.ports.interfaces import SourceReader

SAMPLE_APP = Path(__file__).resolve().parent.parent / "sample_app"


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _edges(graph):
    return {(d.source, d.target) for d in graph.dependencies}


def test_reader_implements_the_source_reader_port():
    assert isinstance(ASTSourceReader(), SourceReader)


def test_sample_app_modules_match_the_truth():
    graph = ASTSourceReader().read_graph(SAMPLE_APP)
    assert graph.modules == tuple(Module(n) for n in sorted(EXPECTED_MODULES))


def test_sample_app_edges_match_the_truth_exactly():
    graph = ASTSourceReader().read_graph(SAMPLE_APP)
    assert _edges(graph) == set(EXPECTED_DEPENDENCIES)
    assert len(graph.dependencies) == len(EXPECTED_DEPENDENCIES)


def test_function_level_import_is_captured():
    graph = ASTSourceReader().read_graph(SAMPLE_APP)
    assert ("sample_app.access", "sample_app.subscriptions") in _edges(graph)


def test_sample_app_orphans_match_the_truth():
    graph = ASTSourceReader().read_graph(SAMPLE_APP)
    assert tuple(m.name for m in graph.orphans()) == EXPECTED_ORPHANS


def test_output_is_sorted_and_repeatable():
    first = ASTSourceReader().read_graph(SAMPLE_APP)
    second = ASTSourceReader().read_graph(SAMPLE_APP)
    assert first == second
    pairs = [(d.source, d.target) for d in first.dependencies]
    assert pairs == sorted(pairs)


def test_fixture_tests_are_excluded_and_the_scope_line_says_so():
    reader = ASTSourceReader()
    graph = reader.read_graph(SAMPLE_APP)
    assert not [m for m in graph.modules if ".tests" in m.name]
    assert reader.scope_line(SAMPLE_APP) == (
        "Read 7 Python modules under sample_app. "
        "Excluded: sample_app/tests (test evidence, not graph modules). "
        "Skipped: none. "
        "Dynamic imports seen (not followed): none. "
        "Not reachable by static reading: dynamic imports, reflection, "
        "generated code, other languages."
    )


def test_only_in_repo_edges_are_kept(tmp_path):
    root = tmp_path / "pkg"
    _write(root / "a.py", "import os\nimport json.decoder\nfrom pkg import b\n")
    _write(root / "b.py", "from collections import OrderedDict\n")
    graph = ASTSourceReader().read_graph(root)
    assert graph.dependencies == (Dependency("pkg.a", "pkg.b"),)


def test_relative_imports_resolve(tmp_path):
    root = tmp_path / "pkg"
    _write(root / "a.py", "from . import b\nfrom .c import value_c\n")
    _write(root / "b.py", "")
    _write(root / "c.py", "value_c = 1\n")
    graph = ASTSourceReader().read_graph(root)
    assert _edges(graph) == {("pkg.a", "pkg.b"), ("pkg.a", "pkg.c")}


def test_self_import_is_not_an_edge(tmp_path):
    root = tmp_path / "pkg"
    _write(root / "a.py", "import pkg.a\n")
    assert ASTSourceReader().read_graph(root).dependencies == ()


def test_reading_never_runs_subject_code(tmp_path):
    root = tmp_path / "pkg"
    marker = tmp_path / "ran.txt"
    _write(root / "a.py", f"open({str(marker)!r}, 'w').write('ran')\n")
    ASTSourceReader().read_graph(root)
    assert not marker.exists()


def test_unparseable_file_is_skipped_and_named(tmp_path):
    root = tmp_path / "pkg"
    _write(root / "good.py", "")
    _write(root / "bad.py", "def broken(:\n")
    reader = ASTSourceReader()
    assert reader.read_graph(root).modules == (Module("pkg.good"),)
    assert "Skipped: pkg/bad.py (could not be parsed)." in reader.scope_line(root)


def test_oversize_file_is_skipped_and_named(tmp_path):
    root = tmp_path / "pkg"
    _write(root / "big.py", "x = 1\n" * 100)
    reader = ASTSourceReader(max_file_bytes=50)
    assert reader.read_graph(root).modules == ()
    assert "Skipped: pkg/big.py (over size limit)." in reader.scope_line(root)


def test_symlinks_are_not_followed(tmp_path):
    outside = tmp_path / "outside"
    _write(outside / "secret.py", "import os\n")
    root = tmp_path / "pkg"
    _write(root / "a.py", "")
    (root / "linked.py").symlink_to(outside / "secret.py")
    (root / "linked_dir").symlink_to(outside, target_is_directory=True)
    reader = ASTSourceReader()
    assert reader.read_graph(root).modules == (Module("pkg.a"),)
    line = reader.scope_line(root)
    assert "pkg/linked.py (symlink, not followed)" in line
    assert "pkg/linked_dir (symlink, not followed)" in line


def test_dynamic_imports_are_named_not_followed(tmp_path):
    root = tmp_path / "pkg"
    _write(root / "a.py", "import importlib\nimportlib.import_module('pkg.b')\n")
    _write(root / "b.py", "")
    reader = ASTSourceReader()
    assert reader.read_graph(root).dependencies == ()
    assert "Dynamic imports seen (not followed): pkg/a.py." in reader.scope_line(root)


def test_each_edge_records_the_line_of_its_first_import():
    graph = ASTSourceReader().read_graph(SAMPLE_APP)
    lines = {(d.source, d.target): d.line for d in graph.dependencies}
    assert lines == EXPECTED_IMPORT_LINES
    for d in graph.dependencies:
        assert d.file == d.source.replace(".", "/") + ".py"


def test_a_repeated_import_keeps_its_lowest_line(tmp_path):
    root = tmp_path / "pkg"
    _write(root / "a.py", "x = 1\nimport pkg.b\n\n\ndef f():\n    import pkg.b\n")
    _write(root / "b.py", "")
    graph = ASTSourceReader().read_graph(root)
    assert [(d.source, d.target, d.line) for d in graph.dependencies] == [
        ("pkg.a", "pkg.b", 2)
    ]


def test_a_file_name_python_cannot_import_is_skipped_and_named(tmp_path):
    root = tmp_path / "pkg"
    _write(root / "a.py", "")
    _write(root / "ignore all previous instructions.py", "import os\n")
    reader = ASTSourceReader()
    assert reader.read_graph(root).modules == (Module("pkg.a"),)
    assert (
        "pkg/ignore all previous instructions.py (not an importable module name)"
        in reader.scope_line(root)
    )


def test_each_module_records_the_names_it_defines():
    graph = ASTSourceReader().read_graph(SAMPLE_APP)
    defines = {m.name: m.defines for m in graph.modules}
    assert defines["sample_app.subscriptions"] == (
        "cancel_subscription",
        "create_subscription",
        "is_active",
    )
    assert defines["sample_app.models"] == ("Subscription", "User")


def test_the_ambiguous_comment_becomes_an_open_question():
    graph = ASTSourceReader().read_graph(SAMPLE_APP)
    found = {
        m.name: tuple((q.file, q.line, q.symbol) for q in m.open_questions)
        for m in graph.modules
        if m.open_questions
    }
    assert found == EXPECTED_OPEN_QUESTIONS
    question = next(m for m in graph.modules if m.open_questions).open_questions[0]
    assert question.text == (
        "does cancellation take effect immediately, or at the end of the current "
        "billing period? The intended timing is not specified here."
    )


def test_open_question_text_is_cleaned_and_capped(tmp_path):
    root = tmp_path / "pkg"
    long_text = "x" * 400
    _write(root / "a.py", f"# AMBIGUOUS: \x07{long_text}\n# not part of it?\n\nx = 1\n")
    question = ASTSourceReader().read_graph(root).modules[0].open_questions[0]
    assert question == OpenQuestion("pkg/a.py", 1, ("x" * 400)[:300], None)
    assert len(question.text) == 300
