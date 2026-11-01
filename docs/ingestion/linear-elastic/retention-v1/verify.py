#!/usr/bin/env python3
"""Verify static private originals; never execute upstream source."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
PACKET = Path(__file__).resolve().parent

def verify():
    receipt = json.loads((PACKET / "receipts.json").read_text())
    original = ROOT / receipt["original_receipts_path"]
    assert hashlib.sha256(original.read_bytes()).hexdigest() == receipt["original_receipts_sha256"], "Original receipt changed"
    expected = json.loads(original.read_text())
    assert len(receipt["files"]) == len(expected) == 3
    assert {x["url"] for x in receipt["files"]} == {x["url"] for x in expected}
    by_url = {x["url"]: x for x in expected}
    for item in receipt["files"]:
        previous = by_url[item["url"]]
        assert (item["sha256"], item["bytes"]) == (previous["sha256"], previous["bytes"])
        path = (ROOT / item["local_path"]).resolve()
        assert path.is_relative_to((ROOT / ".local/private-sources/linear-elastic").resolve())
        data = path.read_bytes()
        assert len(data) == item["bytes"], item["local_path"]
        assert hashlib.sha256(data).hexdigest() == item["sha256"], item["local_path"]
    print("PASS: all three retained OGS originals match the unchanged acquisition receipts.")

if __name__ == "__main__":
    verify()
