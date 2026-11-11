"""Package the independently qualified six-component EMC demonstration."""
import hashlib
import json
from pathlib import Path

from atlas.agent_review import approval_entry

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/ingestion/extended-mohr-coulomb-2013/certified-public-backend-v1"


def bundle(destination, engine):
    def read(name):
        return json.loads((PACKET / name).read_text())

    gate = read("recorded-gate.json")
    expected = read("recorded-wasm.json")
    model_id = gate["model"]
    review_path = ROOT / "catalogue/agent-reviews" / f"{model_id}-agent-v1.json"
    approval = approval_entry(review_path, root=ROOT)
    registry = json.loads((ROOT / "catalogue/approved-models.json").read_text())
    if approval not in registry["models"]:
        raise ValueError("Exact certified recorded approval is absent from the registry")
    definition = (ROOT / approval["definition"]["path"]).read_bytes()

    assets = {}
    for line in (PACKET / "WASM.sha256").read_text().splitlines():
        digest, name = line.split()
        if name not in {"certified-return.mjs", "certified-return.wasm", "models.json"}:
            raise ValueError("Unexpected certified engine asset")
        value = (engine / name).read_bytes()
        if hashlib.sha256(value).hexdigest() != digest:
            raise ValueError(f"Unqualified certified engine asset: {name}")
        assets[name] = value
    catalogue = json.loads(assets.pop("models.json"))
    if catalogue["models"] != [json.loads(definition)] or catalogue["sha256"] != expected["catalogue_hash"]:
        raise ValueError("Certified engine model and reviewed definition differ")
    material = {k: v for k, v in expected["integration_settings"].items()
                if k not in {"version", "norm"}}
    preset = {
        "version": "experimental-recorded-run-0.2", "stress_scope": "effective",
        "model": model_id, "parameters": gate["parameters"], "initial": gate["initial"],
        "integration_settings": material, "control_settings": expected["control_settings"],
        "path": {
            "version": "experimental-recorded-path-0.1",
            "coordinate": {"name": "Observation order", "unit": "1", "meaning": "path_order"},
            "initial_strain": gate["initial_strain"],
            "controls": [{"kind": "strain", "coefficients": row[1:]} for row in gate["controls"]],
            "knots": [{"coordinate": row[0], "targets": row[1:]} for row in gate["knots"]],
        },
    }
    target = destination / "engine-certified-return"
    target.mkdir(exist_ok=True)
    for name, raw in assets.items():
        (target / name).write_bytes(raw)
    (target / "model.json").write_bytes(definition)
    (target / "review.json").write_bytes(review_path.read_bytes())
    (target / "approval.json").write_text(json.dumps(approval, indent=2) + "\n")
    (target / "recorded.json").write_text(json.dumps({"catalogue": catalogue, "preset": preset}) + "\n")
    (destination / "certified-recorded-worker.mjs").write_bytes((ROOT / "web/certified-recorded-worker.mjs").read_bytes())
    return model_id
