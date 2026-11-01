"""Saved-only source/attempt integrity, not constitutive verification."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
manifest = json.loads((BASE / "manifest.json").read_text())
checks = []
for item in manifest["inputs"]:
    path = ROOT / item["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], item["path"]
    checks.append(item["path"])
scan = json.loads((BASE / "local-scan.json").read_text())
private = Path(scan["private_inventory"])
assert hashlib.sha256(private.read_bytes()).hexdigest() == scan["private_inventory_sha256"]
rows = json.loads(private.read_text())
assert len(rows) == scan["pdf_count"]
assert sum(row.get("extraction_ok", False) for row in rows) == scan["extraction_success_count"]
assert [row["path"] for row in rows if row["candidate_match"]] == scan["candidate_paths"]
assert not manifest["source_complete"] and manifest["source_pdf_sha256"] is None
print(json.dumps({"ok": True, "public_input_hashes": len(checks), "private_inventory_hash": True,
                  "local_pdfs_screened": len(rows), "source_complete": False,
                  "constitutive_checks_run": False}, indent=2))
