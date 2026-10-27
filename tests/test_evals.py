import hashlib
import json
from pathlib import Path

import pytest

from understance.shell.app import App

ROOT = Path(__file__).resolve().parent.parent
EVALS = sorted((ROOT / "evals").glob("*.json"))


def _check(code, body, expect):
    assert code == expect["http"]
    if "error" in expect:
        assert body["error"]["type"] == expect["error"]
        return
    for key in ("status", "target", "affected"):
        if key in expect:
            assert body[key] == expect[key], key
    if "findings" in expect:
        assert len(body["findings"]) == expect["findings"]
    if "open_question_lines" in expect:
        assert [q["line"] for q in body["open_questions"]] == expect[
            "open_question_lines"
        ]
    if "decisions" in expect:
        assert len(body["decisions"]) == expect["decisions"]
    for text in expect.get("answer_contains", []):
        assert text in body["answer"], text
    for text in expect.get("answer_excludes", []):
        assert text not in body["answer"], text


def _run(path, logs):
    scenario = json.loads(path.read_text(encoding="utf-8"))
    app = App({"SAMPLE_MODE": "true"}, ROOT, logs=logs, echo=lambda line: None)
    for step in scenario["steps"]:
        _check(*app.handle(step["request"]), step["expect"])


def _fingerprint(folder):
    files = sorted(
        p for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts
    )
    return {
        str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in files
    }


def test_there_are_seven_scenarios_each_with_expected_outputs():
    assert len(EVALS) == 7
    for path in EVALS:
        scenario = json.loads(path.read_text(encoding="utf-8"))
        assert scenario["id"] == path.stem
        assert scenario["about"]
        assert all("expect" in step for step in scenario["steps"])


@pytest.mark.parametrize("path", EVALS, ids=[p.stem for p in EVALS])
def test_each_scenario_gives_its_expected_output(path, tmp_path):
    _run(path, tmp_path)


def test_the_subject_repo_is_unchanged_after_every_eval(tmp_path):
    before = _fingerprint(ROOT / "sample_app")
    for n, path in enumerate(EVALS):
        _run(path, tmp_path / str(n))
    assert _fingerprint(ROOT / "sample_app") == before
