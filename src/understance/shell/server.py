"""POST /run over HTTP with the standard library: JSON in, JSON out."""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from understance.shell.app import App

MAX_BODY_BYTES = 10_000


def make_server(app: App, host: str = "0.0.0.0", port: int = 8000) -> HTTPServer:
    """One request at a time, so runs never write the same memory file at once."""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                self._send(200, {"status": "ok", "mode": app.mode})
            else:
                self._send(404, _error("not_found", "use POST /run or GET /health"))

        def do_POST(self):
            if self.path != "/run":
                self._send(404, _error("not_found", "use POST /run or GET /health"))
                return
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_BODY_BYTES:
                self._send(
                    413, _error("too_large", f"body over {MAX_BODY_BYTES} bytes")
                )
                return
            try:
                request = json.loads(self.rfile.read(length) or b"null")
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._send(400, _error("bad_request", "the body is not valid JSON"))
                return
            self._send(*app.handle(request))

        def _send(self, code: int, body: dict) -> None:
            data = json.dumps(body).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, format, *args):
            pass

    return HTTPServer((host, port), Handler)


def _error(kind: str, message: str) -> dict:
    return {"error": {"type": kind, "message": message}}
