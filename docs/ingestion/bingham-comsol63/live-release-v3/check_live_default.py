"""Assess an actual live UI export against the qualified local default; no execution."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent / "browser-v4/relaxation-actual.json"
LIVE = HERE / "browser/relaxation-actual.json"
HEAD = "43ea5c45f0e6112661fe996b685a3adcdac12ce6"
assert hashlib.sha256(LOCAL.read_bytes()).hexdigest() == "745e2742deb9d6a5fed15549d2b4fee43c5ab86590d1297290ff66bd6b5c2570"
old, new = (json.loads(p.read_text()) for p in (LOCAL, LIVE))
checks = {"same_top_level_keys": old.keys() == new.keys()}
for name in ("kind", "controls", "request", "result"):
    checks[name + "_exact"] = old[name] == new[name]
checks["current_release_revision"] = new["provenance"]["release_revision"] == HEAD
checks["provenance_keys_exact"] = old["provenance"].keys() == new["provenance"].keys()
checks["all_other_provenance_exact"] = {
    k: v for k, v in old["provenance"].items() if k != "release_revision"
} == {k: v for k, v in new["provenance"].items() if k != "release_revision"}
out = {"passed": all(checks.values()), "source_revision": HEAD,
       "actual_export_sha256": hashlib.sha256(LIVE.read_bytes()).hexdigest(),
       "checks": checks, "assessment_only_no_material_execution": True}
(HERE / "LIVE-DEFAULT-CHECK.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out))
raise SystemExit(0 if out["passed"] else 1)
