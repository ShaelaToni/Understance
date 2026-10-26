import ast
from pathlib import Path

from sample_app_truth import (
    EXPECTED_DEPENDENCIES,
    EXPECTED_MODULES,
    EXPECTED_ORPHANS,
)

SAMPLE_APP = Path(__file__).resolve().parent.parent / "sample_app"


def _module_name(path):
    rel = path.relative_to(SAMPLE_APP.parent).with_suffix("")
    return ".".join(rel.parts)


def _modules():
    return [p for p in SAMPLE_APP.rglob("*.py") if p.name != "__init__.py"]


def test_every_sample_app_module_parses():
    files = _modules()
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
