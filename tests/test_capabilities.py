import ast
import json
import subprocess
import sys
import threading
import urllib.request
from pathlib import Path

from understance.shell.app import App
from understance.shell.capabilities import MANIFEST, SCOPE_LINE
from understance.shell.server import make_server

ROOT = Path(__file__).resolve().parent.parent
LIMITS = ("does", "does_not", "cannot_reach")


def _test_names(path):
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    return {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}


def test_the_manifest_has_the_four_lists():
    assert list(MANIFEST) == ["does", "does_not", "cannot_reach", "you"]
    assert all(MANIFEST[name] for name in MANIFEST)


def test_every_claim_and_limit_names_a_test_that_exists():
    for kind in LIMITS:
        for item in MANIFEST[kind]:
            path, name = item["enforced_by"].split("::")
            assert name in _test_names(path), item["enforced_by"]


def test_the_owner_list_names_what_stays_the_owners_call():
    assert all(isinstance(line, str) and line for line in MANIFEST["you"])


def test_every_answer_carries_the_scope_line(tmp_path):
    app = App({"SAMPLE_MODE": "true"}, ROOT, logs=tmp_path, echo=lambda line: None)
    code, body = app.handle({"question": "What would changing billing affect?"})
    assert (code, body["scope"]) == (200, SCOPE_LINE)


def test_get_capabilities_serves_the_manifest(tmp_path):
    app = App({"SAMPLE_MODE": "true"}, ROOT, logs=tmp_path, echo=lambda line: None)
    server = make_server(app, host="127.0.0.1", port=0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        url = f"http://127.0.0.1:{server.server_address[1]}/capabilities"
        with urllib.request.urlopen(url, timeout=10) as response:
            assert json.loads(response.read()) == MANIFEST
    finally:
        server.shutdown()
        server.server_close()


def test_the_capabilities_flag_prints_the_manifest_without_any_settings():
    result = subprocess.run(
        [sys.executable, str(ROOT / "run.py"), "--capabilities"],
        capture_output=True,
        text=True,
        env={},
        check=True,
    )
    assert json.loads(result.stdout) == MANIFEST
