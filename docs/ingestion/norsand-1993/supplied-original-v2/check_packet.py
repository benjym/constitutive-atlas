"""Verify exact private source, frozen source context and saved algebra evidence."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest = json.loads((BASE / "manifest.json").read_text())
for entry in manifest["files"]:
    assert digest(BASE / entry["path"]) == entry["sha256"], entry["path"]
for entry in manifest["source_context"]:
    assert digest(BASE / entry["retained_path"]) == entry["sha256"], entry["retained_path"]
receipt = json.loads((BASE / "source-receipt.json").read_text())
source = Path(receipt["private_path"])
assert source.stat().st_size == receipt["bytes"]
assert digest(source) == receipt["sha256"]
assert source.read_bytes().startswith(b"%PDF")
info = subprocess.run(["pdfinfo", str(source)], check=True, capture_output=True, text=True).stdout
assert any(line.split(":", 1)[1].strip() == "13" for line in info.splitlines() if line.startswith("Pages:"))
run = subprocess.run([sys.executable, "-B", str(BASE / "check_algebra.py")],
                     check=True, capture_output=True, text=True)
assert run.stdout == (BASE / "algebra-results.json").read_text(), "algebra replay differs"
result = json.loads(run.stdout)
assert result["ok"] and not result["candidate_or_backend_executed"]
print(json.dumps({"ok": True, "public_file_hashes": len(manifest["files"]),
                  "retained_context_hashes": len(manifest["source_context"]),
                  "private_source_hash": True, "pdf_pages": 13,
                  "algebra_replay_exact": True,
                  "algebra_checks": sum(r["total"] for r in result["runs"]),
                  "candidate_or_backend_executed": False}, indent=2))
