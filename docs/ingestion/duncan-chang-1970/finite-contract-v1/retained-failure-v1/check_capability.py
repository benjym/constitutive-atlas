"""Source-relevant capability diagnostic; no candidate, compiled run or oracle claim."""
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from atlas.dsl import ValidationError
from atlas.model import validate
from atlas.symmetric_spectral import spectral


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def run():
    cases = {
        "hydrostatic": ([100000., 100000., 100000., 0., 0., 0.], [100000., 100000.]),
        "triaxial_compression": ([150000., 100000., 100000., 0., 0., 0.], [150000., 100000.]),
        "triaxial_extension": ([150000., 150000., 100000., 0., 0., 0.], [150000., 100000.]),
        "distinct_control": ([150000., 125000., 100000., 0., 0., 0.], [150000., 100000.]),
    }
    rows = []
    for name, (stress, extrema) in cases.items():
        row = {"name": name, "stress_mandel_Pa": stress, "operations": {}}
        for operation in ("max_value", "min_value", "max", "min", "upper_sum", "lower_sum"):
            try:
                row["operations"][operation] = {"value_Pa": spectral(stress, operation)}
            except ValueError as exc:
                row["operations"][operation] = {"expected_rejection": str(exc)}
        assert row["operations"]["max_value"]["value_Pa"] == extrema[0]
        assert row["operations"]["min_value"]["value_Pa"] == extrema[1]
        failed = [op for op in ("max", "min") if "expected_rejection" in row["operations"][op]]
        assert failed == {"hydrostatic": ["max", "min"], "triaxial_compression": ["min"],
                          "triaxial_extension": ["max"], "distinct_control": []}[name]
        rows.append(row)

    # In-memory minimal mutation only tests numerical sink validation; no file is emitted.
    baseline_path = "models/tresca-associated-perfect-bk2022v1-be.json"
    baseline = json.loads((ROOT / baseline_path).read_text())
    validate(baseline)
    probe = copy.deepcopy(baseline)
    probe["derived"] = []
    probe["equations"] = {"sigma": "sigma-principal_max_value(sigma)*I", "ep": "ep-ep_n"}
    try:
        validate(probe)
    except ValidationError as exc:
        rejection = str(exc)
        assert "value-only" in rejection, rejection
    else:
        raise AssertionError("value-only numerical sink unexpectedly accepted")

    # Exact diagonal, one-sided spectral slopes: no eigensolver/difference noise.
    from fractions import Fraction as F
    p, t = F(100000), F(1, 8)
    slope_plus = (max(p+t, p, p)-p)/t
    slope_minus = (max(p-t, p, p)-p)/t
    assert (slope_plus, slope_minus) == (1, 0)
    assert slope_minus != -slope_plus
    return {
        "identity": "duncan-chang-repeated-extremum-capability-v1",
        "scope": "Python expression/validator diagnostic only; not model qualification",
        "passed": True,
        "cases": rows,
        "value_only_numeric_sink_rejection": rejection,
        "exact_hydrostatic_one_sided_slopes": {"H_diag_1_0_0": str(slope_plus), "minus_H": str(slope_minus)},
        "input_sha256": {p: digest(p) for p in (
            "atlas/symmetric_spectral.py", "atlas/dsl.py", "atlas/model.py", baseline_path,
            "docs/ingestion/duncan-chang-1970/finite-contract-v1/check_capability.py")},
        "conclusion": "Existing direct differentiable numerical extrema cannot cover source triaxial/hydrostatic states; generic nonsmooth design required, no impossibility theorem for alternative formulations.",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2) + "\n", end="")
