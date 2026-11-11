"""Read-only E5 evidence and independent diagonal laboratory residual replay."""
from fractions import Fraction
import gzip
import hashlib
import json
from math import exp, isfinite, log, sqrt
from pathlib import Path
from struct import pack
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
PACK = HERE.parent
ROOT = HERE.parents[3]
WORK = PACK / "working-v1"
REVIEW = ROOT / "docs/reviews/nh2004-scientific-v1"
P, CC, CE, N, RCS, BETA, A, NU = PARAMS = [98000, .0508, .0112, .83, 3.5, 1.5, 500, .2]
CP = CC - CE
INIT = [P, P, P, 0, 0, 0, 0, N, .5773502691896257, .5773502691896257,
        .5773502691896257, 0, 0, 0, 0, 0]
NAMES = ("oedometric", "drained", "undrained", "stress-controlled", "isotropic")
MODEL = "nakai-hinokio-2004-clay-appendix-v-be"
MODEL_PATH = ROOT / "models/research/nh2004" / f"{MODEL}.json"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(file):
    return json.loads(file.read_bytes())


def raw(file):
    return gzip.decompress((WORK / (file + ".gz")).read_bytes())


def scaled(a, b):
    assert isfinite(a) and isfinite(b)
    return abs(a-b)/max(1, abs(b))


def source_check(old, new):
    """Use independent principal values; no Atlas and no working reference imports."""
    s = np.asarray(new["state"])
    sn = np.asarray(old["state"])
    eps = np.asarray(new["strain"])
    deps = eps[:3] - np.asarray(old["strain"][:3])
    assert all(s[3:6] == 0) and all(s[11:14] == 0) and all(eps[3:] == 0)
    d = s[:3] / P
    inv = 1/d
    a = np.sqrt(inv/sum(inv))
    tn = 3/sum(inv)
    x = a*d/tn-a
    X = np.linalg.norm(x)
    xc = sqrt(2)/3 * (sqrt(RCS) - 1/sqrt(RCS))
    yc = (1-sqrt(RCS))/(sqrt(2)*(sqrt(RCS)+.5))
    Mp = xc**BETA + xc**(BETA-1)*yc
    zeta = X**BETA / (BETA*Mp)
    p = sum(d)/3
    dn = (tn/3)*inv**2  # d log(t_N) / d s_i from harmonic mean
    m = a/tn
    n = dn.copy()
    if not d[0] == d[1] == d[2]:
        # X² = (sum d)(sum 1/d)/9 - 1 (Appendix IV). Use Table 1
        # projection for X to avoid cancellation in its value near isotropy.
        grad_X2 = (sum(inv)-sum(d)*inv**2)/9
        n += X**(BETA-2)/(2*Mp)*grad_X2
        m += X**(BETA-2)/Mp*(x-X**2*a)/tn
    bulk = p/CE
    shear = 3*bulk*(1-2*NU)/(2*(1+NU))
    ds = (s[:3]-sn[:3])/P
    elastic = (ds-sum(ds)/3)/(2*shear)+sum(ds)/(9*bulk)
    pred = bulk*sum(deps)+2*shear*(deps-sum(deps)/3)
    h = (sum(m)+A*s[6]**2/tn)/CP
    Hic = (1+A*s[6]**2/sum(a))/CP
    fsig = n@ds
    drive = max(tn*(dn@ds), 0)/(tn*exp(zeta))
    af, ic = s[-2:]
    plastic = af*m+ic/3
    # Report same endpoint equation scaling, converting compliance to stress.
    closure = deps-elastic-plastic
    stress_res = bulk*sum(closure)+2*shear*(closure-sum(closure)/3)
    dens_res = s[6]-sn[6]-(1+N)*(sum(plastic)-CP*fsig)
    void_res = s[7]-sn[7]+(1+N)*sum(deps)
    aux_res = s[8:11]**2-a*a
    # Hydrostatic hardening tie may round to either II/III or IV. Both give
    # identical IC volume and zero AF in the exact differential limit.
    if n@pred < 0:
        branch, af_res, ic_res = "elastic", af, ic
    elif h < 0:
        branch, af_res, ic_res = "softening", af*h-fsig, ic
    elif fsig-drive < 0:
        branch, af_res, ic_res = "IC-only", af, ic*Hic-fsig
    else:
        branch, af_res, ic_res = "AF/IC", af*h-fsig+drive, ic*Hic-drive
    intercept = s[7]+s[6]+(1+N)*(CP*(log(tn)+zeta)+CE*log(p))
    return (max(abs(v) for v in (*stress_res, dens_res, void_res, *aux_res, af_res, ic_res)),
            branch, h, abs(intercept-N), max(abs(aux_res)))


def verify_lab(captures):
    legacy = json.loads(raw("laboratory-responses.json"))
    results = {}
    for idx, (name, ref) in enumerate(zip(NAMES, legacy, strict=True)):
        target = 5000 if idx == 3 else .01
        settings = dict(version="incremental-settings-0.1", norm="scaled_component_max",
                        residual_tolerance=2e-10, rate_tolerance=1e-6, max_iterations=45,
                        max_depth=14, max_substeps=20000, max_backtracks=11)
        exact = dict(protocol=idx, target=target, steps=100, cycles=0, model=MODEL,
                     parameters=PARAMS, initial=INIT, integration_settings=settings)
        rows = {}
        for prefix in ("exact", "wasm"):
            archive_name = f"{prefix}-{name}.json"
            r = json.loads(captures[archive_name])
            bridge = read(PACK / ("current-native-lab.json" if prefix == "exact"
                                   else "current-wasm-lab.json"))["runs"][name]
            assert bridge["response_sha256"] == sha(captures[archive_name])
            assert all(r[k] == ref[k] == v for k, v in exact.items()), name
            assert r["ok"] is True and len(r["points"]) == len(ref["points"]) == 101
            assert r["points"][0]["state"] == INIT
            available = idx in (2, 3)
            if prefix == "wasm":
                assert r["stress"] == dict(source="state", name="sigma", measure="cauchy",
                                           scope="effective", tensor_representation="mandel",
                                           sign="compression_positive")
                assert r["pore_pressure"]["availability"] == ("reconstructed" if available else "unavailable")
                if available:
                    assert r["pore_pressure"]["assumption"] == "fixed_radial_total_stress_incompressible_fluid_and_grains"
            worst = 0.
            count = 0
            residuals, hard, intercepts, auxiliaries, hydro_errors = [], [], [], [], []
            branches = {}
            for i, (point, refpoint) in enumerate(zip(r["points"], ref["points"], strict=True)):
                eps, s = point["strain"], point["state"]
                assert len(eps) == 6 and len(s) == 16
                assert min(s[:3]) > 0 and min(s[8:11]) > 0  # diagonal tensors verified below
                assert all(v == 0 for v in [*s[3:6], *s[11:14], *eps[3:]])
                assert abs(s[1]-s[2]) <= .01 and abs(eps[1]-eps[2]) <= 1e-9
                assert abs(s[7] - (N-(1+N)*sum(eps[:3]))) <= 1e-8
                assert abs(point["control"]-target*i/100) <= 1e-10
                assert abs(point["p"]-sum(s[:3])/3) <= 1e-8
                assert abs(point["q_signed"]-(s[0]-s[1])) <= 1e-8
                if idx == 0:
                    assert eps[1] == eps[2] == 0
                if idx == 1:
                    assert abs(s[1]-P) <= .01
                if available:
                    assert abs(sum(eps[:3])) <= 1e-9
                    assert abs(point["u"]-(P-s[1])) <= 1e-8
                if idx == 3:
                    assert abs(point["q_signed"]-point["control"]) <= .01
                else:
                    assert abs(eps[0]-point["control"]) <= 1e-10
                if idx == 4:
                    assert eps[0] == eps[1] == eps[2]
                    # Hydrostatic NC: d eps_v = Cc dp / p (Eqs. 41–47).
                    hydro_errors.append(abs(s[0]/P-(1-(3*target/100)/CC)**(-i)))
                for k in ("control", "strain", "state", "p", "q", "q_signed", "u"):
                    v, w = point[k], refpoint[k]
                    if k == "u" and prefix == "wasm" and not available:
                        assert v is None
                        continue
                    xs, ys = (v, w) if isinstance(v,list) else ([v],[w])
                    for x, y in zip(xs, ys, strict=True):
                        worst = max(worst, scaled(x, y))
                        count += 1
                if i:
                    assert point["substeps"] == 1
                    residual, branch, h, intercept, aux = source_check(r["points"][i-1], point)
                    residuals.append(residual); hard.append(h)
                    intercepts.append(intercept); auxiliaries.append(aux)
                    branches[branch] = branches.get(branch, 0)+1
            assert max(residuals) <= 2e-8, (name, prefix, max(residuals))
            assert count == bridge["compared"] and worst == bridge["max_scaled_error"]
            assert worst <= 1e-8
            rows[prefix] = dict(points=len(r["points"]), components=count, max_parity=worst,
                                max_source_residual=max(residuals), max_aux_error=max(auxiliaries),
                                min_scaled_hardening_modulus=min(hard), max_intercept_drift=max(intercepts),
                                endpoint_branches=branches, max_scaled_hydro_be_error=max(hydro_errors, default=None))
        results[name] = rows
    return results


def verify_ordinary_drained(captures):
    """Bounded supplement: model-literal isotropic auxiliary rounding, drained only."""
    ref = json.loads(raw("laboratory-responses.json"))[1]
    native = json.loads(captures["drained.json"])
    wire = json.loads(captures["ordinary-drained-browser-wire.json"])
    specification, wasm = wire["specification"], wire["result"]
    initial = INIT.copy()
    initial[8:11] = [.5773502691896258]*3
    actual_model = read(MODEL_PATH)
    assert sum((row["initial"] if isinstance(row["initial"],list)
                else [row["initial"]] for row in actual_model["state"]), []) == initial
    for row in (native, specification, wasm):
        assert row["initial"] == initial
        for k in ("model", "protocol", "parameters", "steps", "integration_settings"):
            assert row[k] == ref[k]
    for row in (native, specification):
        assert row["target"] == .01 and row["cycles"] == 0
    bits = lambda value: pack(">d",value).hex()
    control = [float(Fraction(float(Fraction(.01)*i))/100) for i in range(100)] + [.01]
    loading = dict(version="laboratory-controls-0.1", encoding="ieee754-binary64-hex",
                   producer=dict(version="laboratory-waveform-0.1", algorithm="linear-rne-v1",
                                 target_bits=bits(.01), steps=100, cycles=0),
                   controls_bits=list(map(bits,control)))
    assert specification["response_contract"] == "stress-scope-0.1"
    assert specification["stress_scope"] == "effective"
    assert specification["loading"] == loading
    assert wasm["api_version"] == "experimental-laboratory-scope-0.1"
    assert wasm["loading"] == {k: v for k, v in loading.items() if k != "producer"} | {"controls": control}
    assert wasm["stress"]["scope"] == "effective"
    assert wasm["pore_pressure"]["availability"] == "unavailable"
    results = {}
    for name, row in (("native",native), ("wasm_exact_controls",wasm)):
        worst = residual = 0.
        assert row["ok"] and len(row["points"]) == 101
        assert row["points"][0]["state"] == initial
        for i,(point,r) in enumerate(zip(row["points"],ref["points"],strict=True)):
            assert point["control"] == control[i] if row is wasm else abs(point["control"]-control[i]) <= 1e-10
            state = point["state"]
            assert min(state[:3]) > 0 and min(state[8:11]) > 0
            assert abs(state[1]-P) <= .01 and abs(state[2]-P) <= .01
            assert abs(state[7] - (N-(1+N)*sum(point["strain"][:3]))) <= 1e-8
            if i:
                assert point["substeps"] == 1
                err, _, h, _, _ = source_check(row["points"][i-1],point)
                assert h > 0
                residual = max(residual,err)
            for k in ("control", "strain", "state", "p", "q", "q_signed", "u"):
                x,y = point[k],r[k]
                if row is wasm and k == "u":
                    assert x is None
                    continue
                xv,yv = (x,y) if isinstance(x,list) else ([x],[y])
                worst = max(worst,*(scaled(a,b) for a,b in zip(xv,yv,strict=True)))
        assert worst <= 1e-8 and residual <= 2e-8
        results[name] = dict(points=101, max_scaled_parity=worst, max_source_residual=residual)
    return results


def verify_material(first, second):
    worst = 0.
    rejections = []
    assert len(first) == len(second) == 1383
    for i, (a, b) in enumerate(zip(first, second, strict=True)):
        assert a["request"] == b["request"]
        x, y = a["response"], b["response"]
        for k in ("ok", "message", "model", "initial", "strain", "parameters", "integration_settings"):
            assert x[k] == y[k]
        assert len(x["state"]) == len(y["state"]) == 16
        assert list(map(float,a["request"][2].split(","))) == x["initial"]
        assert list(map(float,a["request"][3].split(","))) == x["strain"]
        assert x["parameters"] == PARAMS and x["model"] == MODEL
        worst = max(worst, *(scaled(v,w) for v,w in zip(y["state"],x["state"],strict=True)))
        if not x["ok"]:
            assert x["state"] == y["state"] == x["initial"]
            rejections.append(dict(row=i, message=x["message"]))
    assert worst <= 1e-8
    assert len(rejections) == 3
    for rows in (first, second):
        responses = [row["response"] for row in rows[:7]]
        assert responses[0]["state"] == responses[0]["initial"]
        assert responses[1] == responses[2] == responses[6]
    return dict(pairs=len(first), components=len(first)*16, max_scaled_parity=worst,
                exact_failed_rollbacks=rejections, exact_hold_repeated_trials_recovery=True)


def verify_refinement():
    study = json.loads(raw("qualification.json"))
    assert study["status"] == "pass" and study["native_calls"] == 1383 and not study["failures"]
    assert len(study["hydro_cycle"]) == 32 and all(x["ok"] for x in study["hydro_cycle"])
    assert len(study["paths"]) == 6
    results = {}
    def errors(a,b):
        return max(abs(x-y)/P for x,y in zip(a[:6],b[:6],strict=True)), max(abs(x-y) for x,y in zip(a[6:8],b[6:8],strict=True))
    for case in study["paths"]:
        rs = case["references"]
        reference_refinement = errors(rs["1024"],rs["512"])
        assert reference_refinement[0] <= 2e-6 and reference_refinement[1] <= 2e-7
        grids = case["native_grids"]
        assert [x["steps"] for x in grids] == [32,64,128]
        errs = []
        for g in grids:
            assert g["failure"] is None and len(g["trajectory"]) == g["steps"]+1
            errs.append(errors(g["trajectory"][-1],rs["1024"]))
            assert max(errs[-1]) == g["scaled_endpoint_error"]
        assert errs[-1][0] <= 3e-3 and errs[-1][1] <= 3e-4
        assert max(errs[-1]) < max(errs[0]) or max(errs[-1]) <= 1e-7
        if case["name"].startswith("hydro"):
            C = CC if case["name"] == "hydro_nc" else CE
            ev = sum(case["total_strain"][:3])
            end = grids[-1]["trajectory"][-1]
            assert abs(end[0]/P-exp(ev/C)) <= 3e-3
            assert abs(end[7]-(case["initial"][7]-(1+N)*ev)) <= 1e-10
        results[case["name"]] = dict(reference_refinement=reference_refinement, errors=errs)
    return results


def main():
    runtime = read(PACK / "current-runtime-receipt.json")
    for k,v in runtime["evidence_digests"].items():
        assert sha((ROOT/k).read_bytes()) == v, k
    assert sha(MODEL_PATH.read_bytes()) == runtime["model_sha256"]
    # Read-only v0.3 dimensional, structural and semantic checks of exact bytes.
    sys.path.insert(0, str(ROOT))
    from atlas.model import load
    assert load(MODEL_PATH)["id"] == MODEL
    for name, row in read(WORK/"compressed-receipts.json").items():
        data = raw(name)
        assert sha(data) == row["uncompressed_sha256"] and len(data) == row["uncompressed_bytes"]
    for fn in ("prospective-freeze.json", "delivery-freeze.json"):
        for name, h in read(WORK/fn)["files"].items():
            data = (WORK/name).read_bytes() if (WORK/name).exists() else raw(name)
            assert sha(data) == h
    raw_dir = Path(sys.argv[1])
    receipt = read(HERE/"current-raw-receipt.json")
    captures = {name: (raw_dir/name).read_bytes() for name in receipt}
    assert len(captures) == len(receipt) == 13
    for key, item in receipt.items():
        assert sha(captures[key]) == item["sha256"] and len(captures[key]) == item["bytes"]
    lab = verify_lab(captures)
    rows = lambda b: [json.loads(line) for line in b.splitlines()]
    native = rows(raw("native-responses.jsonl"))
    historical_wasm = verify_material(native,rows(raw("wasm-responses.jsonl")))
    current_wasm = verify_material(native,rows(captures["wasm-replay/wasm-responses.jsonl"]))
    old_review = read(REVIEW/"check-results.json")
    assert old_review["algebra_pass"] and len(old_review["algebra"]) == 25
    print(json.dumps(dict(status="pass", current_lab=lab, ordinary_drained=verify_ordinary_drained(captures),
                          current_material=current_wasm,
                          historical_material=historical_wasm, refinement=verify_refinement(),
                          bound_current_evidence=len(runtime["evidence_digests"]),
                          recovered_current_captures=len(captures)),indent=2))


if __name__ == "__main__":
    main()
