"""Run Understance from the command line, or serve POST /run.

  .venv/bin/python run.py "What would changing billing affect?"
  .venv/bin/python run.py "Add customer cancellation" --decide "at the end of the billing period" --by Shaela
  .venv/bin/python run.py --serve        (POST /run and GET /health on 0.0.0.0:$PORT, default 8000)

SAMPLE_MODE=true runs offline from facts/ with no model, and never reads .env.
Otherwise the settings come from .env (see .env.example).
"""

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from understance.shell.app import App, load_settings, stderr_echo
from understance.shell.server import make_server


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Understance: what a change could affect"
    )
    parser.add_argument("question", nargs="?", help="a question about the sample app")
    parser.add_argument("--decide", help="your answer to the open decision")
    parser.add_argument("--by", help="who is deciding (needed with --decide)")
    parser.add_argument("--serve", action="store_true", help="serve POST /run")
    parser.add_argument("--logs", type=Path, help="folder for traces and memory")
    args = parser.parse_args(argv)
    env = load_settings(os.environ, ROOT / ".env")
    try:
        app = App(env, ROOT, logs=args.logs, echo=print if args.serve else stderr_echo)
    except ValueError as e:
        message = f"{e}. Set SAMPLE_MODE=true to run offline."
        print(json.dumps({"error": {"type": "configuration", "message": message}}))
        return 2
    if args.serve:
        port = int(env.get("PORT") or 8000)
        print(f"[INFO] serving POST /run on 0.0.0.0:{port} ({app.mode} mode)")
        make_server(app, port=port).serve_forever()
        return 0
    if not args.question or (args.decide and not args.by):
        parser.error("give a question; --decide also needs --by")
    request = {"question": args.question}
    if args.decide:
        request["decision"] = {"answer": args.decide, "decided_by": args.by}
    code, body = app.handle(request)
    print(json.dumps(body, indent=2))
    return 0 if code == 200 else 1


if __name__ == "__main__":
    sys.exit(main())
