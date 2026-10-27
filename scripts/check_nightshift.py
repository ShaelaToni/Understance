"""Send one real narration request through Nightshift (the live check).

Run from the repo root: PYTHONPATH=src .venv/bin/python scripts/check_nightshift.py
Settings come from .env: METERLESS_BASE_URL, METERLESS_RUNTIME_TOKEN, METERLESS_MODEL.
The key is sent only to Nightshift and is never printed.
"""

import os
import sys
from pathlib import Path

from understance.adapters.csv_fact_store import CsvFactStore
from understance.adapters.nightshift_narrator import (
    NightshiftClient,
    NightshiftNarrator,
)
from understance.usecases.compute_blast_radius import ComputeBlastRadius

ROOT = Path(__file__).resolve().parent.parent
TARGET = "sample_app.subscriptions"


def read_env(path: Path) -> dict[str, str]:
    values = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip("'\"")
    return values


def main() -> int:
    env = {**read_env(ROOT / ".env"), **os.environ}
    events = []

    def show(event: dict) -> None:
        events.append(event)
        print(f"[INFO] {event['action']} {event['status']}: {event['output_summary']}")

    try:
        client = NightshiftClient.from_env(env)
    except ValueError as e:
        print(f"STOPPED: {e}")
        return 1
    findings = ComputeBlastRadius(CsvFactStore(ROOT / "facts")).run(TARGET).findings
    narration = NightshiftNarrator(client, log=show).narrate(findings)
    print(f"Written by: {narration.model}")
    print(narration.text)
    reached = any(e["status"] in ("ok", "blocked") for e in events)
    return 0 if reached else 1


if __name__ == "__main__":
    sys.exit(main())
