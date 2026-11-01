"""Read-only closure preflight; no Atlas/author imports or compiled calls."""
from pathlib import Path
import hashlib
import json


def verify():
    here = Path(__file__).resolve().parent
    root = here.parents[3]
    load = lambda path: json.loads((root / path).read_text())
    inputs = json.loads((here / "inputs.json").read_text())
    paths = [row["path"] for row in inputs["files"]]
    assert len(paths) == len(set(paths))
    for row in inputs["files"]:
        path = Path(row["path"])
        assert not path.is_absolute() and ".." not in path.parts
        assert hashlib.sha256((root / path).read_bytes()).hexdigest() == row["sha256"], path
    closure = json.loads((here / "closure.json").read_text())
    assert closure["scientific_reviewer"] is None
    assert closure["scientific_signoff"] is False
    assert closure["source_acquisition"]["new_source_acquired"] is False
    assert closure["existing_evidence"]["repeat_completed_study"] is False
    parent = "catalogue/investigations/terracotta-preparation-hold-v1/"
    refined = "catalogue/investigations/terracotta-preparation-hold-refinement-v2/"
    old, new = load(parent + "assessment.json"), load(refined + "assessment.json")
    assert old["status"] == "failed"
    assert new["status"] == "passed" and new["parent_outcome"] == "failed"
    assert set(new["backends"]) == {"native", "wasm"}
    for backend in new["backends"].values():
        assert backend["status"] == "passed" and backend["failures"] == []
        assert {row["case"] for row in backend["metrics"]} == {"compression", "extension", "isotropic"}
    assert new["parity"]["new_pairs"] == 3 and new["parity"]["status"] == "passed"
    policy = load(parent + "policy.json")
    refinement = load(refined + "policy.json")
    contract = closure["prospective_changed_artifact_contract"]
    assert contract["fine_bounds"] == policy["fine_bounds"]
    assert contract["maximum_substeps"] == policy["maximum_substeps"] == refinement["budget"]
    assert contract["relative_tolerance"] == refinement["added_relative_tolerance"]
    assert contract["absolute_scale_fraction"] == policy["absolute_scale_fraction"]
    assert contract["held_control_residual_Pa"] == policy["controls_held_residual_Pa"]
    assert contract["parity_scaled_max"] == policy["parity_scaled_max"]
    assert refinement["acceptance_bound_changes"] == refinement["physical_input_changes"] == []
    assert contract["inject_reference_endpoint"] is False
    assert contract["loosen_gates_after_observation"] is False
    assert load("models/research/terracotta-2024-fig1.json")["schema_version"] == "0.2"
    crosswalk = load("docs/ingestion/terracotta-2024/journal-followup-v1/schema-crosswalk-v03.json")
    assert crosswalk["schema_version"] == "0.3"
    assert crosswalk["formulation"]["stress"] == {
        "source": "observable", "name": "stress", "measure": "cauchy", "scope": "total"
    }
    return {"status": "passed", "pinned_files": len(paths), "original_accuracy_outcome": "failed",
            "refined_accuracy_outcome": "passed", "new_compiled_execution": False,
            "new_reference_generation": False, "source_complete": False,
            "scientific_signoff": False}


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
