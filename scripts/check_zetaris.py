"""Read the facts through Zetaris and compare them with facts/ (the live check).

Run from the repo root: PYTHONPATH=src .venv/bin/python scripts/check_zetaris.py
Settings come from .env: ZETARIS_REST_URL, ZETARIS_ORG_ID, ZETARIS_API_KEY.
The key is sent only to Zetaris and is never printed.
"""

import os
import sys
from dataclasses import astuple
from pathlib import Path

from understance.adapters.csv_fact_store import CsvFactStore
from understance.adapters.zetaris_fact_store import ZetarisClient, ZetarisFactStore
from understance.ports.interfaces import DataQualityError, FactsUnavailable

ROOT = Path(__file__).resolve().parent.parent
SHOWN = "sample_app.notifications"


def read_env(path: Path) -> dict[str, str]:
    values = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip("'\"")
    return values


def show(event: dict) -> None:
    print(f"[INFO] {event['action']} {event['status']}: {event['output_summary']}")
    print(f"       {event['input_summary']}")


def main() -> int:
    env = {**read_env(ROOT / ".env"), **os.environ}
    offline = CsvFactStore(ROOT / "facts")
    try:
        store = ZetarisFactStore(ZetarisClient.from_env(env), offline, log=show)
        live = store.load_graph()
    except (ValueError, RuntimeError, DataQualityError, FactsUnavailable) as e:
        print(f"STOPPED: {e}")
        return 1
    expected = offline.load_graph()
    for kind in ("modules", "dependencies"):
        got = [astuple(x) for x in getattr(live, kind)]
        want = [astuple(x) for x in getattr(expected, kind)]
        if got != want:
            print(f"MISMATCH in {kind}:")
            print("  only in Zetaris:", [x for x in got if x not in want])
            print("  only in facts/:", [x for x in want if x not in got])
            return 1
    module = next(m for m in live.modules if m.name == SHOWN)
    link = next(d for d in live.dependencies if d.source == SHOWN)
    print(
        f"MATCH: {len(live.modules)} modules and {len(live.dependencies)} links "
        "read through Zetaris equal facts/."
    )
    print(
        f"One fact through Zetaris: {link.source} imports {link.target} "
        f"({link.file}, line {link.line}); test files: {len(module.tested_by)}; "
        f"last change {module.last_commit} on {module.last_changed}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
