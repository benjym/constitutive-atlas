"""Saved-document integrity only; no material execution or build."""
from pathlib import Path
import hashlib, json, re
root = Path(__file__).resolve().parents[4]
packet = Path(__file__).resolve().parent
receipts = json.loads((packet / "input-receipts.json").read_text())["inputs"]
for item in receipts:
    assert hashlib.sha256((root / item["path"]).read_bytes()).hexdigest() == item["sha256"], item["path"]
crosswalk = json.loads((packet / "crosswalk.json").read_text())
legacy = json.loads((root / crosswalk["retained_model"]["path"]).read_text())
assert legacy["schema_version"] == crosswalk["retained_model"]["schema_version"] == "0.1"
assert crosswalk["qualification_transfer"] is False
assert crosswalk["proposed_formulation"]["equation_form"] == "strain_path_rate"
assert crosswalk["proposed_formulation"]["time_dependence"] == "strain_path"
assert crosswalk["persistent_state"] == legacy["state"]
assert crosswalk["parameter_inventory"] == legacy["parameters"]
links = re.findall(r"\]\(([^)]+)\)", (packet / "README.md").read_text())
local = [link for link in links if not link.startswith("https:")]
for link in local:
    assert (packet / link).resolve().is_file(), link
print(json.dumps({"input_hashes_checked": len(receipts), "local_links_checked": len(local),
                  "retained_schema": "0.1", "migration_performed": False,
                  "builds": 0, "new_numerical_studies": 0}, indent=2))
