import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from understance.shell.app import App
from understance.shell.server import make_server

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def base_url(tmp_path):
    app = App({"SAMPLE_MODE": "true"}, ROOT, logs=tmp_path, echo=lambda line: None)
    server = make_server(app, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def _call(url, data=None):
    request = urllib.request.Request(url, data=data, method="POST" if data else "GET")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_post_run_answers_in_json(base_url):
    data = json.dumps({"question": "What would changing billing affect?"}).encode()
    code, body = _call(base_url + "/run", data)
    assert (code, body["status"], body["mode"]) == (200, "answered", "sample")


def test_health_reports_the_mode(base_url):
    assert _call(base_url + "/health") == (200, {"status": "ok", "mode": "sample"})


def test_a_body_that_is_not_json_is_a_bad_request(base_url):
    code, body = _call(base_url + "/run", b"{not json")
    assert (code, body["error"]["type"]) == (400, "bad_request")


def test_an_unknown_path_is_not_found(base_url):
    code, body = _call(base_url + "/other", b"{}")
    assert (code, body["error"]["type"]) == (404, "not_found")
