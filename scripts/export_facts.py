"""Write the practice app's facts to facts/ (the Zetaris sources and sample mode).

Run from the repo root: PYTHONPATH=src .venv/bin/python scripts/export_facts.py
"""

from pathlib import Path

from understance.adapters.csv_fact_store import CsvFactStore
from understance.adapters.enriched_source_reader import EnrichedSourceReader
from understance.usecases.analyze_repo import AnalyzeRepo

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    store = CsvFactStore(ROOT / "facts")
    graph = AnalyzeRepo(EnrichedSourceReader(), store).run(ROOT / "sample_app")
    print(f"Wrote {len(graph.modules)} modules and {len(graph.dependencies)} links")


if __name__ == "__main__":
    main()
