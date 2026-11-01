"""Project only independently accepted public scalars; never access raw measurements or an engine."""
from pathlib import Path
import argparse,hashlib,json,math,os
PACKET=Path(__file__).resolve().parent
ROOT=PACKET.parents[2]
DECISION="docs/benchmarks/kfs-tmd2-reporting-agent-v1/decision.json"
REVIEW="docs/benchmarks/kfs-tmd2-reporting-agent-v1/README.md"
MANIFEST="docs/benchmarks/kfs-tmd2-reporting-agent-v1/manifest.json"
SUMMARY="docs/benchmarks/kfs-tmd2-portable-v1/results/summary.json"
REJECTIONS="docs/benchmarks/kfs-tmd2-reference-v1/rejection-assessment.json"
WITNESS="docs/reviews/tmd2-process-status-v1/witness.json"
GUARD="docs/reviews/tmd2-process-status-v1/guard-results.json"
def project(root=ROOT,pins=None):
    pins=pins or json.loads((PACKET/"inputs.json").read_text())
    for name,digest in pins.items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest:raise ValueError("changed frozen input: "+name)
    data={name:json.loads((root/name).read_text())for name in pins if name.endswith(".json")}
    d,m,s=data[DECISION],data[MANIFEST],data[SUMMARY]
    assert d["verdict"]=="accept-qualified-reporting" and not d["blocking_findings_for_stated_scope"]
    assert pins[DECISION]=="ae2591b574efec5ef63db8782e6333d3f880ae8cbcb0b4f7464be39862e0d4dc"
    assert pins[MANIFEST]=="b21fd9e92e41e23482a1e5a65a31dae0f58a8843633aa7ee46a98908965fc8f4"
    for name in [SUMMARY,REJECTIONS,WITNESS,GUARD]:assert m["public_inputs"][name]==pins[name]
    assert m["outputs"]["decision.json"]==pins[DECISION] and m["outputs"]["README.md"]==pins[REVIEW]
    assert d["summary_sha256"]==pins[SUMMARY]
    assert len(d["questions"])==6 and all(q["outcome"]=="accept-with-stated-qualifications"for q in d["questions"])
    assert len(s["paths"])==3 and s["source_pass"]is True and s["refinement_pass"]is True
    rows=[]
    for path in s["paths"]:
        assert path["returncode"]==0 and path["ok"]is True and path["complete"]is True
        assert all(v["pass"]is True and not v["failures"]for v in path["source"].values())
        raw=path["experimental_errors"]
        assert all(math.isfinite(x)and x>=0 for channel in raw.values()for x in channel.values())
        rows.append({"id":path["id"],"caller_intervals":path["points"]-1,"saved_points":path["points"],"target_accumulated_axial_fraction":path["last_control"],"experimental_overlap_accumulated_axial_fraction":path["experimental_overlap"],"errors_SI":raw,"display_errors":{"q_kPa":{k:v/1000 for k,v in raw["q"].items()},"trace_volume_percentage_points":{k:v*100 for k,v in raw["volumetric_strain"].items()}}})
    refinement=[]
    for pair in s["refinement"]:
        for channel,record in pair["channels"].items():
            assert record["pass"]is True and 0<=record["maximum_difference"]<=record["limit"]
            factor,unit=(0.001,"kPa")if channel=="q"else(100,"percentage points")
            refinement.append({"paths":pair["paths"],"channel":channel,"maximum_difference_SI":record["maximum_difference"],"frozen_limit_SI":record["limit"],"display_maximum_difference":record["maximum_difference"]*factor,"display_frozen_limit":record["limit"]*factor,"display_unit":unit,"difference_to_limit_ratio":record["maximum_difference"]/record["limit"]})
    rejections=data[REJECTIONS];w=data[WITNESS];g=data[GUARD]
    assert len(rejections["requests"])==3 and all(x["completed_points"]==0 and x["returncode"]==1 for x in rejections["requests"])
    assert w["altered_returncode"]==23 and w["old_assessor_exit"]==0 and w["source_pass"]and w["refinement_pass"]
    assert g["exit23_rejected"]is True
    return {"kind":"paper-input-public-scalar-projection-v1","model_sha256":d["model_sha256"],"input_sha256":pins,"reporting_review":"accept-qualified-reporting","model_admission":False,"held_out_validation":False,"measurement_redistribution_permission":False,"fresh_engine_qualification":False,"coordinate":"direct accumulated axial strain; volume is the trace of accumulated strain, not established historical finite-deformation output","error_interpretation":"Descriptive calibration-campaign errors over each saved experimental overlap; no ranking, uncertainty, held-out validation or new fit.","error_rows":rows,"refinement_rows":refinement,"historical_original_api_rejections":rejections["requests"],"process_status_witness":w,"corrected_process_guard":g,"mandatory_qualifications":d["remaining_qualifications"]}
def tables(result):
    lines=["# TMD2 qualified reporting: paper tables","","Descriptive calibration-campaign errors; no held-out validation, model ranking or experimental-validation claim. Strain errors below are percentage points (fraction ×100), and stress errors are kPa (Pa ÷1000).","","| Caller intervals | Saved points | q RMSE (kPa) | q MAE (kPa) | q max abs. (kPa) | trace-volume RMSE (pp) | trace-volume MAE (pp) | trace-volume max abs. (pp) |","| --- | --- | --- | --- | --- | --- | --- | --- |"]
    tex=[r"\begin{tabular}{rr rrr rrr}",r"\hline",r"Intervals & Points & \multicolumn{3}{c}{$q$ error (kPa)} & \multicolumn{3}{c}{Trace-volume error (pp)} \\",r" & & RMSE & MAE & Max.\ abs. & RMSE & MAE & Max.\ abs. \\",r"\hline"]
    for row in result["error_rows"]:
        q=row["display_errors"]["q_kPa"];v=row["display_errors"]["trace_volume_percentage_points"]
        vals=[str(row["caller_intervals"]),str(row["saved_points"])]+[f"{group[k]:.6g}"for group in [q,v]for k in ["rmse","mae","maximum_absolute_error"]]
        lines.append("| "+" | ".join(vals)+" |")
        tex.append(" & ".join(vals)+r" \\")
    tex.extend([r"\hline",r"\end{tabular}"])
    lines+=["","## Saved path-pair refinement","","These are saved path-pair differences against frozen assessor limits, not physical integration-error bounds or an observed convergence order.","","| Path pair | Channel | Maximum difference | Frozen limit | Unit | Difference / limit |","| --- | --- | --- | --- | --- | --- |"]
    for row in result["refinement_rows"]:
        lines.append("| "+" | ".join([" → ".join(row["paths"]),row["channel"],f'{row["display_maximum_difference"]:.6g}',f'{row["display_frozen_limit"]:.6g}',row["display_unit"],f'{row["difference_to_limit_ratio"]:.6g}'])+" |")
    lines+=["","## Retained historical failures","","The earlier ordinary laboratory API rejected all three 25% requests with zero points. Those rejections are distinct from the qualified research-range paths tabulated above. A separate saved-receipt exit23 witness passed the historical assessor; the corrected process-status guard rejects it. Neither is discarded or turned into a numerical-accuracy pass.","","## Mandatory scientific qualifications",""]
    lines +=["- "+q for q in result["mandatory_qualifications"]]
    lines+=["","Source/review identities and full-precision values are in reporting.json. All table values are rounded for presentation; raw measurements are excluded.",""]
    caption="""TMD2 operational reconstruction of the published VW96+IGS example. Descriptive calibration-campaign errors use the saved experimental overlap (accumulated axial strain 0 to 0.249529878); stress errors are in kPa and trace-volume strain errors in percentage points. Saved path-pair differences are normalized by their prospectively frozen assessor limits. Values below one establish only those stated saved refinement gates. Exact historical decks, versions and finite-deformation output conversion remain unverified; direct nominal initialization does not replay consolidation. Internal-stage admissibility, blind validation, model ranking, uncertainty and measurement redistribution rights are not established. Earlier ordinary-API rejections and the corrected process-status false-pass witness remain retained. Full qualifiers and exact identities accompany the artifacts in reporting.json. The table and figure derive solely from public accepted scalars, without a new fit or material execution.
"""
    return "\n".join(lines),"\n".join(tex)+"\n",caption
def build(destination):
    if destination.exists():raise FileExistsError(destination)
    result=project()
    destination.mkdir(parents=True)
    (destination/"reporting.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    md,tex,caption=tables(result)
    (destination/"tables.md").write_text(md);(destination/"errors-tabular.tex").write_text(tex);(destination/"CAPTION.txt").write_text(caption)
    os.environ.setdefault("MPLCONFIGDIR","/private/tmp/atlas-tmd2-paper-mpl")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"svg.hashsalt":"atlas-tmd2-reporting-v1"})
    fig,ax=plt.subplots(figsize=(6.6,3.6),layout="constrained")
    for channel,label,color,marker in [("q","Deviatoric stress q","#bc643e","o"),("volumetric_strain","Trace-volume strain","#547a95","s")]:
        rows=[v for v in result["refinement_rows"]if v["channel"]==channel]
        ax.plot(range(len(rows)),[v["difference_to_limit_ratio"]for v in rows],marker=marker,label=label,color=color)
    ax.axhline(1,color="#404040",linestyle="--",linewidth=1,label="Frozen assessor limit")
    ax.set_yscale("log");ax.set_ylim(1e-3,1.7)
    ax.set_xticks([0,1],["400 vs 800","800 vs 1600"]);ax.set_xlabel("Caller intervals in compared saved paths")
    ax.set_ylabel("Maximum path-pair difference / limit");ax.set_title("TMD2 saved refinement gates")
    ax.grid(axis="y",alpha=.2);ax.legend(loc="center right",frameon=False)
    fig.savefig(destination/"refinement.svg",metadata={"Date":None,"Creator":"Constitutive Atlas public scalar projection"})
    fig.savefig(destination/"refinement.png",dpi=200,metadata={"Software":"Constitutive Atlas public scalar projection"})
    plt.close(fig)
    (destination/"render-runtime.json").write_text(json.dumps({"matplotlib":matplotlib.__version__,"backend":"Agg","font":"DejaVu Sans","new_solver_calls":0,"new_fits":0},indent=2)+"\n")
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,required=True);build(parser.parse_args().output)
