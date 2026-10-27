from pathlib import Path

from sample_app_truth import EXPECTED_MODULES, EXPECTED_UNTESTED

from understance.adapters.module_tests import ModuleTests

SAMPLE_APP = Path(__file__).resolve().parent.parent / "sample_app"


def test_every_module_but_the_untested_one_is_linked_to_its_tests():
    found = ModuleTests().map(SAMPLE_APP, set(EXPECTED_MODULES))
    assert set(found) == set(EXPECTED_MODULES) - set(EXPECTED_UNTESTED)
    assert found["sample_app.access"] == ("sample_app/tests/test_access.py",)
    assert found["sample_app.models"] == (
        "sample_app/tests/test_access.py",
        "sample_app/tests/test_billing.py",
        "sample_app/tests/test_models.py",
        "sample_app/tests/test_subscriptions.py",
    )


def test_a_project_without_tests_has_an_empty_map(tmp_path):
    (tmp_path / "pkg").mkdir()
    assert ModuleTests().map(tmp_path / "pkg", {"pkg.a"}) == {}


def test_imports_of_outside_packages_are_not_linked(tmp_path):
    root = tmp_path / "pkg"
    (root / "tests").mkdir(parents=True)
    (root / "a.py").write_text("", encoding="utf-8")
    (root / "tests" / "test_a.py").write_text(
        "import os\nfrom collections import OrderedDict\nfrom pkg import a\n",
        encoding="utf-8",
    )
    assert ModuleTests().map(root, {"pkg.a"}) == {"pkg.a": ("pkg/tests/test_a.py",)}
