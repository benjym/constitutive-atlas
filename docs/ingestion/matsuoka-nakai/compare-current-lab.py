"""Check current-run physical outputs against the five frozen NH2004 lab runs."""
import gzip
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SAVED = ROOT / "working-v1/laboratory-responses.json.gz"
FIELDS = ("model", "parameters", "initial", "protocol", "target",
          "steps", "cycles", "integration_settings")
CHANNELS = ("control", "strain", "state", "p", "q", "q_signed", "u")
PROTOCOLS = ("oedometric", "drained", "undrained", "stress-controlled", "isotropic")


def scalars(x):
    return x if isinstance(x, list) else [x]


def main(directory, prefix):
    results = {}
    with gzip.open(SAVED, "rt") as source:
        saved = json.load(source)
    for name, reference in zip(PROTOCOLS, saved, strict=True):
        raw = (Path(directory) / f"{prefix}{name}.json").read_bytes()
        actual = json.loads(raw)
        errors = [f"input mismatch: {k}" for k in FIELDS
                  if actual.get(k) != reference[k]]
        if not actual["ok"] or len(actual.get("points", [])) != 101:
            errors.append(f"run failed or wrong point count: {actual['message']}")
        scoped = prefix == "wasm-"
        pore_available = reference["protocol"] in (2, 3)
        if scoped and actual.get("stress", {}).get("scope") != "effective":
            errors.append("scope-aware response did not declare effective stress")
        if scoped and actual.get("pore_pressure", {}).get("availability") != (
            "reconstructed" if pore_available else "unavailable"
        ):
            errors.append("incorrect pore-pressure availability")
        worst = (0., "")
        count = 0
        if not errors:
            for i, (a, b) in enumerate(zip(actual["points"], reference["points"], strict=True)):
                for k in CHANNELS:
                    if k == "u" and scoped and not pore_available:
                        if a[k] is not None:
                            errors.append(f"{i}: unavailable pore pressure is not null")
                        continue
                    for j, (u, v) in enumerate(zip(scalars(a[k]), scalars(b[k]), strict=True)):
                        err = abs(u - v) / max(1, abs(v)) if math.isfinite(u) else math.inf
                        worst = max(worst, (err, f"{i}:{k}:{j}"))
                        count += 1
            if worst[0] > 1e-8:
                errors.append("scaled physical component error exceeded 1e-8")
        results[name] = dict(compared=count, max_scaled_error=worst[0],
                             worst_location=worst[1], errors=errors,
                             response_sha256=hashlib.sha256(raw).hexdigest())
    passed = all(not row["errors"] for row in results.values())
    print(json.dumps({"status": "pass" if passed else "fail", "runs": results}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
