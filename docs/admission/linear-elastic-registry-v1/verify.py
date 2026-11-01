#!/usr/bin/env python3
"""Verify only the owned exact elastic approval; other registry owners are independent."""
from pathlib import Path
import json
from atlas.agent_review import approval_entry

ROOT = Path(__file__).resolve().parents[3]

def verify():
    expected = approval_entry(ROOT / "catalogue/agent-reviews/linear-elastic-agent-v1.json", root=ROOT)
    handoff = json.loads((ROOT / "docs/admission/linear-elastic-agent-v1/approval-entry.json").read_text())
    assert expected == handoff, "Generated handoff changed"
    registry = json.loads((ROOT / "catalogue/approved-models.json").read_text())
    found = [row for row in registry["models"] if row["model_id"] == "linear-elastic"]
    assert found == [expected], "Exact elastic approval missing, duplicated or altered"
    assert expected["experimental_validation"] == "not_assessed"
    assert expected["deployment_authorized"] is False
    print("PASS: exactly one registered elastic approval equals the actual accepted review and generated handoff.")

if __name__ == "__main__":
    verify()
