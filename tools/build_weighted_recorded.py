"""Package the approved fixed-plane Mašín six-component demonstration."""
import hashlib
import json
from pathlib import Path

from atlas.agent_review import approval_entry

ROOT = Path(__file__).resolve().parents[1]
MODEL = "clay2014-trace-calibrated-igs-fixed-plane-v1"
GATE = ROOT / ("docs/ingestion/hypoplastic-clay-2014/delivery-20261111/"
               "generic-boundary-v1/radius-bounded-v2/production/reversal-v4")
ASSETS = ("weighted-history.mjs", "weighted-history.wasm")
EXPECTED = GATE / "strain-wasm/synthetic-NCL-H0--mixed-six-components.json"


def bundle(destination, engine):
    manifest = json.loads((ROOT / "catalogue/manifest.json").read_text())
    if not any(entry["id"] == MODEL for entry in manifest["models"]):
        return None
    review = ROOT / "catalogue/agent-reviews" / f"{MODEL}-agent-v1.json"
    approval = approval_entry(review, root=ROOT)
    registry = json.loads((ROOT / "catalogue/approved-models.json").read_text())
    if approval not in registry["models"]:
        raise ValueError("Exact weighted-history approval is absent from the registry.")
    definition = (ROOT / approval["definition"]["path"]).read_bytes()
    spec = (GATE / "recorded.json").read_bytes()
    fixture = json.loads(spec)
    if fixture["catalogue"]["models"] != [json.loads(definition)] or fixture["preset"]["model"] != MODEL:
        raise ValueError("Weighted-history catalogue differs from the approved definition.")
    hashes = {Path(path).name: digest for digest, path in
              (line.split(maxsplit=1) for line in (GATE / "wasm-solver.sha256").read_text().splitlines())}
    if set(hashes) != set(ASSETS):
        raise ValueError("Unexpected weighted-history engine asset set.")
    assets = {name: (engine / name).read_bytes() for name in ASSETS}
    for name, content in assets.items():
        if hashlib.sha256(content).hexdigest() != hashes[name]:
            raise ValueError(f"Unqualified weighted-history engine asset: {name}")
    target = destination / "engine-weighted-history"
    target.mkdir(exist_ok=True)
    for name, content in assets.items():
        (target / name).write_bytes(content)
    (target / "model.json").write_bytes(definition)
    (target / "recorded.json").write_bytes(spec)
    (target / "review.json").write_bytes(review.read_bytes())
    (target / "approval.json").write_text(json.dumps(approval, indent=2) + "\n")
    return MODEL
