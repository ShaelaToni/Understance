from dataclasses import FrozenInstanceError

import pytest

from understance.domain.finding import Evidence, Finding, FindingKind
from understance.domain.graph import (
    BlastRadius,
    Dependency,
    DependencyGraph,
    Module,
    OpenQuestion,
)


def graph(module_names, edges):
    return DependencyGraph(
        modules=[Module(name) for name in module_names],
        dependencies=[Dependency(source, target) for source, target in edges],
    )


def test_module_is_identified_by_its_dotted_name():
    assert Module("app.billing").name == "app.billing"
    assert Module("app.billing") == Module("app.billing")


def test_dependency_records_that_source_imports_target():
    dependency = Dependency("app.main", "app.billing")
    assert dependency.source == "app.main"
    assert dependency.target == "app.billing"


def test_entities_cannot_be_changed_after_construction():
    module = Module("a")
    dependency = Dependency("a", "b")
    built = graph(["a"], [])
    with pytest.raises(FrozenInstanceError):
        module.name = "b"
    with pytest.raises(FrozenInstanceError):
        dependency.target = "c"
    with pytest.raises(FrozenInstanceError):
        built.modules = ()


def test_graph_stores_modules_and_dependencies_as_tuples():
    built = graph(["a", "b"], [("a", "b")])
    assert built.modules == (Module("a"), Module("b"))
    assert built.dependencies == (Dependency("a", "b"),)


def test_only_the_module_no_one_imports_is_an_orphan():
    # main -> billing -> models: only main is not imported by any module.
    built = graph(
        ["main", "billing", "models"], [("main", "billing"), ("billing", "models")]
    )
    assert built.orphans() == [Module("main")]


def test_with_no_imports_every_module_is_an_orphan_in_name_order():
    built = graph(["c", "a", "b"], [])
    assert built.orphans() == [Module("a"), Module("b"), Module("c")]


def test_importing_itself_does_not_stop_a_module_being_an_orphan():
    built = graph(["a"], [("a", "a")])
    assert built.orphans() == [Module("a")]


def test_empty_graph_has_no_orphans():
    assert graph([], []).orphans() == []


def test_dependency_to_a_module_not_in_the_graph_changes_nothing():
    without_dangling = graph(["a", "b"], [("b", "a")])
    with_dangling = graph(["a", "b"], [("b", "a"), ("b", "ghost")])
    assert with_dangling.orphans() == without_dangling.orphans() == [Module("b")]


def test_import_location_is_recorded_but_does_not_change_identity():
    located = Dependency("a", "b", 7, "pkg/a.py")
    assert (located.line, located.file) == (7, "pkg/a.py")
    assert located == Dependency("a", "b")
    assert (Dependency("a", "b").line, Dependency("a", "b").file) == (None, None)


def test_dependents_follow_imports_backwards_through_every_level():
    # main -> api -> billing -> models
    built = graph(
        ["main", "api", "billing", "models"],
        [("main", "api"), ("api", "billing"), ("billing", "models")],
    )
    assert built.dependents_of("models") == ("api", "billing", "main")
    assert built.dependents_of("main") == ()


def test_dependencies_follow_imports_forwards_through_every_level():
    built = graph(
        ["main", "api", "billing", "models"],
        [("main", "api"), ("api", "billing"), ("billing", "models")],
    )
    assert built.dependencies_of("main") == ("api", "billing", "models")
    assert built.dependencies_of("models") == ()


def test_a_cycle_ends_the_walk_and_never_lists_the_target_itself():
    built = graph(["a", "b", "c"], [("a", "b"), ("b", "a"), ("c", "a")])
    assert built.dependents_of("a") == ("b", "c")
    assert built.dependencies_of("a") == ("b",)


def test_reach_ignores_modules_not_in_the_graph_and_unknown_names():
    built = graph(["a", "b"], [("a", "b"), ("a", "ghost")])
    assert built.dependencies_of("a") == ("b",)
    assert built.dependents_of("nobody") == ()


def test_blast_radius_is_frozen_and_stores_tuples():
    finding = Finding("a imports b", FindingKind.OBSERVED, [Evidence("a.py", 1, 1)])
    radius = BlastRadius("b", ["a"], [], [finding])
    assert radius.dependents == ("a",)
    assert radius.dependencies == ()
    assert radius.findings == (finding,)
    with pytest.raises(FrozenInstanceError):
        radius.target = "c"


def test_a_module_records_what_it_defines_and_its_open_questions():
    question = OpenQuestion("app/a.py", 4, "immediately or later?", "cancel")
    module = Module("app.a", ("cancel",), (question,))
    assert module.defines == ("cancel",)
    assert module.open_questions == (question,)
    assert module == Module("app.a")
    assert OpenQuestion("app/a.py", 4, "x").symbol is None
