"""Saved-only exact-row assessment. No imports of the compiler or solver."""
from pathlib import Path
import csv, hashlib, json
packet = Path(__file__).resolve().parent
freeze = json.loads((packet / "pre-build-freeze.json").read_text())
for name, expected_hash in freeze["files"].items():
    assert hashlib.sha256((packet / name).read_bytes()).hexdigest() == expected_hash, name
expected = json.loads((packet / "expected.json").read_text())
with (packet / "native/observed.csv").open() as stream:
    reader = csv.DictReader(stream)
    assert reader.fieldnames == ["id", "phase", "ok", "inputs_unchanged"]
    observed = list(reader)
assert len(observed) == len(expected) == 378
failures = []
for e, o in zip(expected, observed):
    assert (e["id"], e["phase"]) == (o["id"], o["phase"])
    assert o["ok"] in ("0", "1") and o["inputs_unchanged"] in ("0", "1")
    if bool(int(o["ok"])) != e["ok"] or bool(int(o["inputs_unchanged"])) != e["inputs_unchanged"]:
        failures.append({"expected": e, "observed": o})
report = {"outcome": "failed" if failures else "passed", "rows": len(observed),
          "mismatch_count": len(failures),
          "integrator_mismatches": sum("/integrator/" in f["expected"]["id"] for f in failures),
          "failures": failures}
print(json.dumps(report, indent=2))
