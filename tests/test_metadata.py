import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
METADATA = json.loads((ROOT / "metadata.json").read_text(encoding="utf-8"))


def test_every_sponsor_location_and_test_exists():
    for name, sponsor in METADATA["sponsor_technology"].items():
        for path in sponsor.get("where", []):
            assert (ROOT / path).exists(), f"{name}: {path}"
        if "test" in sponsor:
            assert (ROOT / sponsor["test"]).is_file(), f"{name}: {sponsor['test']}"


def test_the_h_mem_wording_is_exact():
    engine = METADATA["sponsor_technology"]["meterless_engine"]
    assert engine["engine"] == "H-MEM"
    assert engine["verification"] == (
        "implements the Meterless H-MEM spec, "
        "verified with a pytest port of its core test cases."
    )
