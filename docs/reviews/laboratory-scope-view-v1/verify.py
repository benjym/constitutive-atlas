"""Saved-only evidence gate; no material calls or builds."""
import csv, copy, hashlib, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PACKET=Path(__file__).resolve().parent
def read(name): return json.loads((PACKET/name).read_text())
def compare(a,b,path=""):
    if isinstance(b,bool) or b is None or isinstance(b,str): assert type(a)==type(b) and a==b,path
    elif isinstance(b,(int,float)):
        assert type(a) in (int,float) and math.isfinite(a),path
        assert abs(a-b)<=1e-9*max(1,abs(b)),path
        if path.split(".")[-1] in ("iterations","substeps","rejected","steps","cycles","protocol"): assert a==b,path
    elif isinstance(b,list):
        assert isinstance(a,list) and len(a)==len(b),path
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+"."+str(i))
    else:
        assert isinstance(a,dict) and a.keys()==b.keys(),path
        for k in b:compare(a[k],b[k],path+"."+k)
def clean(r,keys=("elapsed_ms",)):return {k:v for k,v in r.items() if k not in keys}
def assess(packet=None):
    global PACKET
    if packet is not None: PACKET=Path(packet)
    native={}
    for f in (ROOT/"docs/reviews/laboratory-scope-contract-v1/observations").glob("[0-9]*.json"):
        row=json.loads(f.read_text())
        if row["label"].startswith("current-public-"):native[row["label"]]=json.loads(row["stdout"])
    refs=read("public-references.json");rows=read("public-responses.json")
    assert len(refs)==len(rows)==9
    public=read("public-catalogue.json");private=read("private-catalogue.json")
    assert len(public["models"])==9 and len(private["models"])==10
    assert {r["result"]["model"] for r in rows}=={m["id"] for m in public["models"]}
    for old,row in zip(refs,rows):
        compare(old["result"],native[old["label"]])
        expected=copy.deepcopy(old["result"])
        for point in expected["points"]:point["u"]=None
        exclude=("elapsed_ms","catalogue_hash","api_version","stress","pore_pressure","integration_settings")
        compare(clean(row["result"],exclude),clean(expected,exclude))
        assert row["result"]["catalogue_hash"]==public["sha256"]
        assert row["result"]["stress"]["scope"]=="effective"
    inputs=read("browser-inputs.json")
    for i in range(5):
        doc=read(f"browser-total-{i}.json");ref=inputs[f"total-analytical-{i}"]
        compare(doc["specification"],ref["specification"])
        compare(clean(doc["result"]),clean(ref["result"]))
        assert all(p["u"] is None for p in doc["result"]["points"])
    effective=read("browser-effective.json");ref=inputs["scoped-elastic-2"]
    compare(effective["specification"],ref["specification"]);compare(clean(effective["result"]),clean(ref["result"]))
    assert effective["result"]["pore_pressure"]["availability"]=="reconstructed" and effective["result"]["points"][0]["u"]==0
    exact=read("browser-total-exact.json");reference=inputs["exact-reversal"]
    # Explicit synthetic elastic twin only: compare full mechanics, without relabelling a scientific model.
    compare(clean(exact["specification"],("model","stress_scope")),clean(reference["specification"],("model","stress_scope")))
    compare(clean(exact["result"],("model","stress","pore_pressure","elapsed_ms")),clean(reference["result"],("model","stress","pore_pressure","elapsed_ms")))
    assert exact["specification"]["model"]=="scope-synthetic-total-elastic" and exact["result"]["stress"]["scope"]=="total"
    assert exact["result"]["pore_pressure"]=={"quantity":"change","availability":"unavailable","reason":"total_stress_without_pore_pressure_law"}
    assert len(exact["result"]["points"])==17
    table=list(csv.reader((PACKET/"browser-total-exact.csv").read_text().splitlines()))
    assert table[0]==["axial_strain_1","radial_strain_1","volumetric_strain_1","total_mean_stress_Pa","total_signed_deviatoric_stress_Pa","pore_pressure_change_Pa","stress_scope","pore_pressure_availability","iterations","substeps"]
    assert len(table)==18
    for row,point in zip(table[1:],exact["result"]["points"]):
        assert row[5:8]==["","total","unavailable"]
        compare([float(x) for x in row[:5]],[point["strain"][0],point["strain"][1],sum(point["strain"][:3]),point["p"],point["q_signed"]])
        compare([int(x) for x in row[8:]],[point["iterations"],point["substeps"]])
    legacy=read("browser-legacy.json");old=inputs["current-elastic-1"]
    assert legacy["schema_version"]=="0.1" and "stress" not in legacy["result"]
    compare(clean(legacy["specification"],("integration_settings",)),old["specification"])
    compare(clean(legacy["result"]),clean(old["result"]))
    publicdoc=read("browser-public.json")
    assert publicdoc["catalogue_hash"]==public["sha256"] and publicdoc["result"]["ok"]
    assert publicdoc["specification"]["model"]=="hypoplastic-sand-vw96" and len(publicdoc["result"]["points"])==101
    for name in ("configure.json","build.json","exercise-process.json","packaging-process.json"):assert read(name)["returncode"]==0
    cmd=read("build.json")["command"];assert cmd[-4:]==["--target","atlas_laboratory_scope_public_wasm","--parallel","1"]
    assert "Laboratory stress scope/model mismatch." in (PACKET/"browser-rejection-state.txt").read_text()
    browse=(PACKET/"browser-total-source-browsing.txt").read_text()
    assert "Value: 1, ID: browse-source-records" in browse and "Total stress path" in browse
    assert "step=\"any\"" in (ROOT/"web/index.html").read_text()
    return dict(public_native_pairs=9,total_browser_protocols=5,exact_points=17,effective_reconstruction=True,legacy_recovery=True)
if __name__=="__main__":print(json.dumps(assess(),sort_keys=True))
