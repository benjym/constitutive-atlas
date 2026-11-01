"""Materialize this actual independent decision; no model/shared writes."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;M=P.parents[1];ROOT=M.parents[3]
base='docs/ingestion/duncan-chang-1970/';local=str(P.relative_to(ROOT))+'/'
paths=[local+'REPORT.md',local+'check_bindings.py',local+'binding-results.json',
 base+'supplied-original-v2/receipt.json',base+'supplied-original-v2/README.md',base+'supplied-original-v2/check_algebra.py',
 base+'complete-copy-v4/receipt.json',base+'complete-copy-v4/independent-review/README.md',base+'complete-copy-v4/independent-review/receipt.json',
 base+'erratum-v3/README.md',base+'erratum-v3/independent-review/review-receipt.json',
 base+'e2-v2/CONTRACT.md',base+'e2-v2/NUMERICAL_POLICY.md',base+'e2-v2/independent-review/README.md',base+'e2-v2/independent-review/receipt.json',
 base+'material-v1/DOSSIER.md',base+'material-v1/independent-review/README.md',base+'material-v1/independent-review/receipt.json',
 base+'material-v1/independent-review/execution-v1/README.md',base+'material-v1/independent-review/execution-v1/native-failure/README.md',
 base+'material-v1/independent-review/execution-v1/native-failure/analytical-partition-v1/README.md',base+'material-v1/independent-review/execution-v1/native-failure/analytical-partition-v1/receipt.json',
 base+'material-v1/independent-review/execution-v2/README.md',base+'material-v1/independent-review/execution-v2/README_WASM.md',
 base+'material-v1/independent-review/execution-v2/native-receipt.json',base+'material-v1/independent-review/execution-v2/wasm-receipt.json',
 base+'material-v1/execution-v2/material-receipt.json',base+'material-v1/execution-v2/E4_COMPLETE.json',base+'material-v1/execution-v2/freeze.json',base+'material-v1/execution-v2/POLICY.md',
 base+'material-v1/integration-preflight-v1/result.json',
 'docs/reviews/bounded-partition-retry-v1/CONTRACT.md','docs/reviews/bounded-partition-retry-v1/independent-review/FINAL_REVIEW.md','docs/reviews/bounded-partition-retry-v1/independent-review/final-bindings.json']
reasons={
 'source_provenance':'Readable original1970 equations and full page sequence independently inspected; exact private source receipts; later-discussion erratum distinguished.',
 'equation_fidelity':'Every residual, modulus, branch, history and parameter checked against source; endpoint averaging/equalities/failure modulus explicitly identified numerical choices;363 exact algebra assertions pass.',
 'conventions_dimensions':'Explicit v0.3 effective Cauchy, compression-positive Mandel, Pa/radian units, infinitesimal fixed-spatial zero-spin strain-path formulation; correct Mandel shear factor.',
 'initialization_domain':'Explicit sigma6/history preparation, strict finite parameter and positive confinement/strength/modulus guards, exact committed physical constraints; broad metadata ranges not claimed qualified.',
 'integration_transactions':'Qualified implicit finite realization, holds/reversal/restart/full-parent rollback; separately accepted bounded retry retains depth/global-work/residual/physical gates and discloses actual loading defect.',
 'independent_numerical_evidence':'Independent source compliance/eigensystem/characteristic-gradient and quadratic/hyperbola references;70+2 endpoints,24refinement rows, two20column smooth sweeps, retained source-root failures and pre-observation alternate roots; unchanged gates pass.',
 'backend_delivery':'Frozen native/Wasm integrate/evaluate/describe and two drained run presets pass complete72/42/43/2/2/2 matrix; saved assessments and6248call audits independently reproduced; fullstate parity passes4e-8 with narrow margin. Duncan update tangent/FE/browser excluded.',
 'applicability_claims':'Admission limited to exact constant-nu endpoint-average variant, frozen protocol/parameter examples and settings; no experimental, calibration, dilatancy, physical-time, finite-rotation, arbitrary-path or FE suitability claim.',
 'reproducibility_rights':'Exact model/source/request/wire/tool/evidence closures and durable artifacts verified; retained failures; current generator output identical; copyrighted originals remain private; final generic38bindings and E4 receipt verified.'}
scope='Exact Duncan–Chang1970 constant-nu effective-stress isotropic endpoint-principal-average incremental residual, compression-positive Mandel small-strain fixed-spatial zero-spin. Only frozen native/Wasm describe/evaluate/integrate_with_settings and the two source-coefficient drained run_with_settings presets, the exact execution-v2 requests and settings(2e-10,1e-6,45,14,20000,11), with explicitly diagnostic-only modified budgets. Qualified20column residualAD, not a Duncan discrete-update tangent. Exact-copy installation at the stated models path; no scientific metadata change authorized.'
limitations=[
 'Endpoint averaging, equality choices, finite max-D history, positive numerical E_failure and bounded partition retry are disclosed project choices;10psf is arbitrary illustrative coefficient.',
 'Tested source dense/loose examples and explicit boundary/full-tensor cases do not validate the entire metadata parameter region or guarantee arbitrary-path convergence/uniqueness; discontinuous no-unsplit-root steps and representability failures remain possible.',
 'Selected scalar exact-tie rows are not unique classical or proved whole-residual Clarke derivatives; numerically unresolved distinct spectra may reject.',
 'Parity worst3.950669546611607e-8 is close to the frozen4e-8 bound; no bitwise backend equality claim. Non-dyadic loading split has a bounded disclosed exact-real roundoff defect.',
 'No model-specific constitutive-update tangent, FE host, finite-rotation transport, pore-fluid coupling, dilatancy, physical clock, calibration or experimental validation is approved.',
 'Atlas packaging, actual browser qualification and live delivery remain separate E6–E8 gates; no push/deployment authorization is conveyed.',
 'Source commit identifies the repository base; dirty qualified dependencies are separately frozen. Coordinator must install exact candidate bytes and validate final record/model paths before registry integration.'
]
record=dict(schema_version='0.1',kind='agent-model-review',id='duncan-chang-1970-endpoint-average-agent-v1',created_at='2026-11-01',source_commit='cea0dac709132a5c0eea3e637cf34e1d5081e355',model=dict(id='duncan-chang-1970-endpoint-average',path='models/duncan-chang-1970-endpoint-average.json',sha256='452b49ef48668c0c5d8aba20dfca398235fa45431e853ee923be05a17c7c88a0'),status='accepted',reviewer=dict(kind='agent',name='Codex independent source and material reviewer',run_id='/root/duncan_complete_review',independence_basis='Actual separate run from author /root; personally inspected original source pages/equations and performed source algebra/reference, branch-root, derivative, frozen-closure and saved native/Wasm evidence audits; did not author candidate transcription or generic runtime.'),author_run_ids=['/root'],scope=scope,limitations=limitations,blocking_findings=[],artifacts=[dict(path=x,sha256=hashlib.sha256((ROOT/x).read_bytes()).hexdigest()) for x in paths],checklist=[dict(id=k,outcome='pass',reason=v,evidence=[local+'REPORT.md#'+k]) for k,v in reasons.items()])
out=P/'proposed-agent-review.json';assert not out.exists();out.write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n')
print('Wrote actual nine-pass independent review; exact-copy installation/validation remains coordinator responsibility.')
