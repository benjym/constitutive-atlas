"""Read-only independent checks of retained EMC ABI evidence; no Atlas imports."""
from hashlib import sha256
from itertools import chain
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACK = HERE.parent
MODEL = PACK.parent / "selected-return-native-plan-v1/model.json"
POLISH = PACK.parent / "plastic-interior-polish-v1"

def read(path):
    return json.loads(path.read_text())

def pins(directory, manifest):
    lines = (directory / manifest).read_text().splitlines()
    for line in lines:
        digest, name = line.split(maxsplit=1)
        assert sha256((directory / name).read_bytes()).hexdigest() == digest
    return len(lines)

def extrema_of_source_stress(v):
    # Independent closed-form real symmetric 3x3 cubic, off-diagonals in Mandel.
    x, y, z, xy, yz, xz = (-c for c in v)
    xy, yz, xz = (c / math.sqrt(2) for c in (xy, yz, xz))
    p = (x+y+z)/3
    a, b, c = x-p, y-p, z-p
    scale = math.sqrt((a*a+b*b+c*c+2*(xy*xy+yz*yz+xz*xz))/6)
    if not scale:
        return p, p
    a,b,c,xy,yz,xz = (v/scale for v in (a,b,c,xy,yz,xz))
    half_det = (a*b*c+2*xy*yz*xz-a*yz*yz-b*xz*xz-c*xy*xy)/2
    angle = math.acos(max(-1., min(1., half_det)))/3
    return p+2*scale*math.cos(angle), p+2*scale*math.cos(angle+2*math.pi/3)

def hardening(k, parameters):
    _, _, beta, _, peak, _, origin, _, _ = parameters
    alpha = origin / (peak-origin)
    ratio = k / beta + alpha
    return peak * ratio/(1+ratio)  # Solved independently from paper Eq. (12).

def yield_value(v, k, parameters):
    hi, lo = extrema_of_source_stress(v)
    return (hi-lo)/2 + math.sin(hardening(k,parameters))*((hi+lo)/2-parameters[3])

def elastic_trial(parent, de, parameters):
    g, nu = parameters[:2]
    tr = sum(de[:3])
    bulk = 2*g*(1+nu)/(3*(1-2*nu))
    return [x+2*g*(d-tr/3)+bulk*tr if i<3 else x+2*g*d
            for i,(x,d) in enumerate(zip(parent,de))]

def main():
    count = pins(PACK, "RESULTS.sha256")
    qualified = pins(POLISH, "RESULTS.sha256")
    model = read(MODEL)
    reference = read(PACK / "recorded-gate.json")
    wire = read(PACK / "recorded-native.json")
    assert (PACK/"recorded-native.json").read_bytes() == (PACK/"recorded-wasm.json").read_bytes()
    p = reference["parameters"]
    assert wire["model"] == model["id"] == reference["model"]
    assert wire["parameters"] == p and wire["initial"] == reference["initial"]
    assert wire["initial_strain"] == reference["initial_strain"]
    for field in ("controls", "knots"):
        assert wire[f"{field}_wire"] == list(chain.from_iterable(reference[field]))
    points = wire["points"]
    assert wire["ok"] and len(points) == 3 and wire["failed_knot"] == -1
    for point,knot in zip(points,reference["knots"]):
        assert point["coordinate"] == knot[0] and point["strain"] == knot[1:]
        assert len(point["state"]) == 16 and all(map(math.isfinite,point["state"]))
        assert point["state"][7:] == reference["initial"][7:]
    first, loaded, last = [point["state"] for point in points]
    assert first == reference["initial"] and loaded[6] > first[6]
    assert loaded == last == wire["state"]
    assert wire["finite_difference_probes"] == 0 and wire["material_trials"] == 1
    y0 = yield_value(first[:6],first[6],p)
    yt = yield_value(elastic_trial(first[:6],points[1]["strain"],p),first[6],p)
    y1 = yield_value(loaded[:6],loaded[6],p)
    assert y0 < 0 < yt and abs(y1) <= p[7]*p[8]
    for platform in ("native","wasm"):
        log = (PACK/f"{platform}.log").read_text()
        assert log.count("load hold unload reversal replay rollback passed") == 7
        assert f"seven {'Wasm' if platform=='wasm' else platform} ABI lifecycles passed" in log
        out = read(PACK / f"example-{platform}.json")
        assert out["ok"] is False and len(out["points"]) == 3 and "failed at step 3" in out["message"]
        full = (POLISH/f"{platform}-full.log").read_text()
        assert "checks=899 failures=0" in full and "checks=12 failures=0" in full
        assert "original negative controls 7/7" in full
    print(json.dumps({"result_pins":count,"polish_pins":qualified,
        "recorded_points":len(points),"material_trials":wire["material_trials"],
        "independent_yield_pa":{"initial":y0,"full_elastic_trial":yt,"committed":y1},
        "abi_lifecycle_cases_per_platform":7,"axisymmetric_failed_step":3},indent=2))

if __name__ == "__main__":
    main()
