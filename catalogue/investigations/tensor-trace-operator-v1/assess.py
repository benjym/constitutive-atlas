"""Re-audit retained trace observations; never builds or executes artifacts."""
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[3]
STUDY = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bits(value):
    return struct.pack(">d", value).hex()


def assess_observation(observed, corpus):
    errors = []
    supported = observed.get("rounding_mode_test_supported")
    if type(supported) is not bool:
        errors.append("rounding-mode status must be boolean")
    if observed.get("version") != "trace-three-binary64-certified-eft-fixed34-v1-candidate":
        errors.append("wrong probe identity")
    if observed.get("checks") != 751 + (2 if supported is True else 0):
        errors.append("incomplete check count")
    if observed.get("failures") != 0 or observed.get("errors") != []:
        errors.append("probe failure")
    expected = [{"id": f["id"], "ok": f["ok"],
                 "result_bits": f["expected_bits"] if f["ok"] else bits(123.25)}
                for f in corpus["records"]]
    if len(expected) != 97 or observed.get("records") != expected:
        errors.append("fixture identities/status/result bits differ from independent corpus")
    derivative = [bits(-1e-130 if j % 2 else 1e-130) for j in range(38)]
    if observed.get("jet_derivative_bits") != derivative:
        errors.append("Jet derivative bits differ")
    return errors


def assess():
    errors = []
    protocol = json.loads((STUDY / "protocol.json").read_text())
    freeze = json.loads((STUDY / "prospective-freeze.json").read_text())
    for name, expected in freeze["files"].items():
        if digest(STUDY / name) != expected:
            errors.append("prospective document changed: " + name)
    for name, expected in protocol["inputs"].items():
        if digest(ROOT / name) != expected:
            errors.append("study input changed: " + name)
    corpus = json.loads((ROOT / "docs/reviews/tensor-trace-accuracy-v1/corpus.json").read_text())
    observations = {}
    backends = {}
    receipts = {}
    for backend in ("native", "wasm"):
        directory = STUDY / backend
        receipt = json.loads((directory / "receipt.json").read_text())
        receipts[backend] = digest(directory / "receipt.json")
        if receipt["inputs"] != protocol["inputs"] or receipt["backend"] != backend:
            errors.append(backend + ": wrong build source receipt")
        commands = receipt["commands"]
        if [c["label"] for c in commands] != ["configure", "build", "observe"] or any(c["exit_code"] != 0 for c in commands):
            errors.append(backend + ": failed or missing invocation")
        build = commands[1]["argv"]
        if build[-4:] != ["--target", "atlas_trace_probe", "--parallel", "1"]:
            errors.append(backend + ": serial explicit-target contract violated")
        if (directory / "observe.stderr.txt").read_bytes():
            errors.append(backend + ": observation stderr")
        observed = json.loads((directory / "observe.stdout.txt").read_text())
        local = assess_observation(observed, corpus)
        errors.extend(backend + ": " + e for e in local)
        observations[backend] = observed
        backends[backend] = {"checks": observed["checks"], "failures": observed["failures"],
            "fixture_rows": len(observed["records"]), "Jet_columns": len(observed["jet_derivative_bits"]),
            "rounding_mode_test_supported": observed["rounding_mode_test_supported"], "pass": not local}
    parity = all(observations["native"][key] == observations["wasm"][key]
                 for key in ("records", "jet_derivative_bits"))
    if not parity:
        errors.append("native/Wasm result bits differ")
    return {"version": "tensor-trace-operator-assessment-v1", "backends": backends,
            "native_wasm_bit_parity": parity, "receipt_sha256": receipts,
            "errors": errors, "pass": not errors,
            "scope": "generic C++ scalar/Jet operator only; no generated DSL/model-rate/integration/admission claim"}


if __name__ == "__main__":
    result = assess()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["pass"] else 1)
