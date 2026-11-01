"""Verify this prospective plan without compiled calls or root installation."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import tempfile
P = Path(__file__).resolve().parent
ROOT = P.parents[2]
sys.path.insert(0, str(ROOT))
from atlas.model import validate
from atlas.evidence import validate_record

def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

for rel, expected in read(P / "manifest.json")["files"].items():
    assert sha(P / rel) == expected, f"Packet changed: {rel}"
baseline = read(P / "baseline.json")
for rel, expected in baseline["files"].items():
    assert sha(ROOT / rel) == expected, f"Baseline changed: {rel}; reassess plan before use"
assert len(list((ROOT / "models").glob("*.json"))) == baseline["model_count"] == 11
D = P / "proposed"
model = read(D / "models/mohr-coulomb.json")
validate(model)
assert sha(D / "models/mohr-coulomb.json") == read(P / "checks.json")["model_byte_exact"]
old, new = read(ROOT / "catalogue/manifest.json"), read(D / "catalogue/manifest.json")
without = lambda items: [x for x in items if x["id"] != "mohr-coulomb"]
assert without(old["models"]) == without(new["models"])
a, b = dict(old), dict(new)
a.pop("models"); b.pop("models"); assert a == b
entry = next(x for x in new["models"] if x["id"] == "mohr-coulomb")
assert entry["status"] == "draft" and entry["executable"] is True
review = read(D / "catalogue/reviews/mohr-coulomb-source-v1.json")
assert review["status"] == "pending"
evidence = read(D / "catalogue/evidence/mohr-coulomb-current-backends-v3.json")
with tempfile.TemporaryDirectory(prefix="atlas-mc-plan-verify-") as temp:
    root = Path(temp)
    for src in D.rglob("*"):
        if src.is_file():
            dest = root / src.relative_to(D)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
    for item in evidence["artifacts"] + evidence["source_files"]:
        dest = root / item["path"]
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / item["path"], dest)
    for rel in ["catalogue/reviews/mohr-coulomb-source-v1.json", "catalogue/evidence/mohr-coulomb-current-backends-v3.json"]:
        validate_record(root / rel, root, current=True)
protocol = read(P / "protocol.json")
assert protocol["status"] == "prospective-not-executed"
assert len(protocol["gates"]) == 9
assert sorted(protocol["proposed_root_files"]) == sorted(str(f.relative_to(D)) for f in D.rglob("*") if f.is_file())
print("PASS: pinned plan and proposed records; eleven live models unchanged; no material calls")
