# Independent scientific decision: accepted within declared scope

SCI-clay2013-agent-v1, 2 November 2026. Actual reviewer: `/root/clay2013_checklist_review`, a separate dispatched agent run. I did not author the model, transcription, implementation or prior numerical studies. Known coordinator/source-packet author identities are `/root` and `/root/clay2013_source_closure`; original historical transcription run identities are not authenticated. My decision follows actual original-source reading and retained-evidence reassessment, not those authors' recommendations. No unresolved blocking finding remains for the scope below.

Exact reviewed model: `models/hypoplastic-clay-2013.json`, SHA256 `6811580cf9c0678605b9bb7d93a524743bbe5b5cb1f547bd232d090aeda950e4`. Approval concerns the complete author-manuscript Appendix43-58 stress law plus p3 Eq7 void-ratio evolution, at zero spin in the regular compressive interior, with its explicit v0.3 contract and stated numerical policies. All seven stress/e components evolve. This is not approval of a failure surface alone or a substituted narrower governing law.

Backend qualification is limited to exact retained historical interfaces/artifacts/source and cases in clay2013-preview-v2 (settings-aware `atlas_integrate_with_settings`, `atlas_run_with_settings`, fresh native processes and a persistent Wasm module, and the saved local browser export). It does not certify today's entire common engine, package, browser, release or deployment. Current delivery remains a coordinator gate. Source-only replays made no new compiled/material calls and ran no author binaries or builds.

## source_provenance

PASS. I used the PDF skill and visually read original privately retained author-manuscript pages1,3,8,13,14 (complete relevant equation pages, not snippets). Title and author match David Mašin, Clay hypoplasticity with explicitly defined asymptotic states. The source receipt identifies issue2013/online2012, DOI https://doi.org/10.1007/s11440-012-0199-y and author URL https://web.natur.cuni.cz/uhigug/masin/download/Masin_AG12-pp.pdf . Both the frozen temporary PDF and supplemental durable private copy hash to `21834ab9da81ec2cdebdf3a3d7f97b691d47bf481a24432bc0562aca9f503281`. Existing rendered images were visually read; source bytes were independently hashed. This review does not newly authenticate publisher HTML observations or full final-body equivalence. The approval names the manuscript precisely; 2005/2014 and IGS/GIS are separate variants.

## equation_fidelity

PASS. Original Appendix pp13-14 compared directly with every derived/evolution expression:

| Source | Reviewed correspondence |
| --- | --- |
|43|Source `T_circle=fs L:D-(fd/fdA) A:d norm(D)` becomes `sigma_rate=fs L:E+(fd/fdA) Ad norm(E)` under T=-sigma,D=-E; d remains the source direction.|
|44-45|`c=nu/(1-2nu)`, `L:X=X+c tr(X)I`; `Ad=fs L:d-(sigma/lambda_star)tr(d)`. Both contractions and the full nonlinear term are present.|
|46|`fs=(3p/2)(1/lambda_star+1/kappa_star)(1-2nu)/(1+nu)`, p=trace(sigma)/3.|
|47-49|alpha=2; fd=(2p/pe)^2; pe=1000Pa exp((N-ln(1+e))/lambda_star); fdA=4(1-Fm)^(2/omega).|
|50-54|Stable Fm quotient exactly reduces the source invariant ratio, retaining source negative second invariant; omega has the negative log(cos²)/ln2 and +0.3(Fm-sin²) terms.|
|55-58|Full dA bracket and normalization, negative Lode quotient, xi=1.7+3.9sin²(phi_c), and normalized deviator retained.|
|p3 Eq7|Combining its two pe derivatives gives e_dot=(1+e)tr(D); therefore e_rate=-(1+e)trace(E).|

Independent algebra checked here: put S=trace(sigma), r=sigma/S=I/3+a, j2=a:a,j3=tr(a³). Newton identities give det(r)=1/27-j2/6+j3/3. Source I1=-S, I2=S²(-1/3+j2/2), I3=-S³det(r). Thus numerator9I3+I1I2=S³(j2-3j3), denominatorI3+I1I2=S³[8/27-(j2+j3)/3], exactly the model's Fm. Double deviator projection is algebraically idempotent, a declared floating-point policy.

At exact isotropy a=Fm=0; original Eq56 reduces to `-(2/3)sin(phi_c)^xi/(1-sin(phi_c)^xi) I`, nonzero negative for the selected angles. Normalization gives d=-I/sqrt(3). Placeholder cos3theta=0 cannot change this because Fm^(1/4)=0. This is a justified continuation of the combined law, not a literal value of undefined Eq57. Nonisotropic underflow to j2=0 rejects. The raw64ulp Lode margin, finite-intermediate bounds and rejection policies are explicit project numerical choices; no silent clipping/floor/projection is approved.

## conventions_dimensions

PASS. Source p3 Eq3 names the Zaremba-Jaumann rate with spin; W=0 makes it the ordinary stress derivative. The JSON explicitly restricts to small_strain_3d, fixed_spatial, objective_rate:none, strain_path_rate, compression-positive effective Cauchy stress and compression-positive infinitesimal increments. This does not assert finite-spin objectivity. Mandel order xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz preserves source Frobenius contraction/norm when both input and stress use it. Stress/rates/fs/Ad are Pa per dimensionless path coordinate; angles are radians, remaining five-material-parameter quantities dimensionless. Fixed pr=1000Pa is the source1kPa; p_scale is error weighting, not a material parameter. Input de supplies a straight increment over fraction0..1, not physical seconds; positive homogeneity in positive path rescaling justifies this rate-independent parameterization. Effective stress supplies no pore-fluid law.

## initialization_domain

PASS. Six stress components and scalar e are the complete persistent state inventory stated after Eq58. JSON requires explicit sigma/e, with examples_only and domain_and_initial_checks; no inferred OCR or specimen history. Five material defaults30degrees,.12,.025,1.1,.2 are software fixtures, different from Table1 fictitious eval25degrees,.1,.01,1,.2, which I visually checked on p8. Source parameter interpretations are respected. Rectangular bounds and lambda*>kappa*, e>=0, positive pressure/factors, nonzero dA and finite-arithmetic restrictions are conservative project limits, not calibrated/full-source domains.

In exact arithmetic positive trace,pair-sum,determinant imply SPD for real symmetric stress: two negative eigenvalues with positive trace force negative pair-sum, contradicting the guard. Binary64 invariant checks are not a certified near-singular sign test; no universal-SPD accuracy/retention is approved. Fm<1 alone is not SPD. Actual accepted example paths independently pass Cartesian principal-minor checks. The source's ASBS is diagnostic, not a yield return/barrier; prior outward-rate witness and preparation limits are retained. Arbitrary evaluability is not physical preparation or validity.

## integration_transactions

PASS for the historical bounded interface. I inspected frozen solver.hpp: coupled stress/e explicit midpoint with step doubling and endpoint-defect sampling, stage/end domain/finite checks, scaled-component-max local error, recursive half increments, explicit budgets. Source does not prescribe these numerical choices. `integrate` initializes result.state to incoming state and assigns trial only on success; attempted-work counters may survive failure. Controlled trials restart from the same committed state, preserving last committed point. Seven persistent fields contain all base-law memory; restart supplies them explicitly, no hidden reset or plastic state. Loading order/reversals matter; zero strain gives no creep/identity. Norm(input) is nonsmooth at zero, so a general update tangent is excluded.

Retained Wasm budget/domain failures show partial-progress counters2/256 and bitwise incoming-state return; zero probe succeeds unchanged. V2 checks invalid-integrate rollback, omitted-state rejection, failed100kPa last committed point, and successful same-instance10kPa recovery. This supports observed interfaces/cases, not arbitrary nonisotropic failure paths or every future runtime revision. No FE/update-tangent approval is inferred.

## independent_numerical_evidence

PASS. I read the independently coded Cartesian oracle (81 fourth-order entries, direct cofactor determinant and actual matrix products), high-precision invariant review, isotropic closed-form derivation, source-rate and nonisotropic reviews. Their source arithmetic differs from the reduced model, though common scientific transcription risks remain; my original-equation/algebra check addresses those separately. Historical rate40cases, isotropic arbitrary-density/reversal/partition tests, high-precision near-isotropy diagnostics and nonisotropic noncoaxial/shear-reversal plus fixed rotations supply distinct evidence. A constant basis rotation is not finite physical spin.

Actual source-only replay re-evaluated saved native/Wasm records against the independent Decimal isotropic solution:33trajectories/115calls each. Strict nonisotropic assessor freshly recomputed its exact pinned Cartesian reference, all8/16/32 grids, metadata, covariance/refinement and input/dependency receipts;12trajectories/36calls per backend pass. Tight maximum stress error is0.001412215038726572Pa. Prior additional64-grid review supports fourth-order smooth-reference refinement; its1e-5Pa allowance is a working uncertainty, not a rigorous bound. Global regression bounds are distinct from requested local tolerances, and finite adaptive covariance need not improve monotonically at every pair.

Exact research parameters/derived/equations/domain and state layout are unchanged in current model; v2 separately binds exact current bytes. Original failures and pre-fix verifier findings remain history, with strict replay closure explicitly recorded. No new numerical campaign was performed. Broad parameter, ill-conditioned stress and experiment claims remain unsupported.

## backend_delivery

PASS for historical qualification only. The source-only frozen v2 verify_study.py and assessor replay pass exact receipts, source/model/generated byte identities, original build reuse, ordered raw descriptor/calls, settings and positional layouts, independent physical controls/observables/volume checks, failures/recovery and native/Wasm parity.20calls and598successful points per backend remain unchanged. Maximum void error4.1637138181727096e-10 against1e-6 and scaled backend difference2.8978507326692877e-16 against1e-10 are retained. Original v1 expected-success100kPa default remains failed; v2 explicitly preserves its step1 failure and has a distinct passing10kPa example.

Saved local browser specification/101physical points exactly match frozen Wasm; export/snapshot/console and result manifest hashes are bound. This is reassessment of historical browser output, not a fresh browser or entire current-delivery test. No current engine/package compatibility, released website, ongoing availability or deployment is certified. Missing original temporary binaries would require coordinator rebuild/requalification for new execution, not invalidate hashed historical observations. Approval is explicitly bound to historical artifact receipts and supported interface scope.

## applicability_claims

PASS with mandatory exclusions: no complete publisher-body equivalence; calibrated specimen preparation or experimental validation; arbitrary-parameter or universal-SPD/near-boundary accuracy; finite spin; FE use or update tangent; IGS/GIS/2014 anisotropic extension; current entire runtime/package/browser delivery or deployment. Approval establishes a source-faithful complete base law under stated restriction with bounded numerical evidence. It does not transform fictional software examples into material calibrations. The negative100kPa initial mixed-control tangent result and numerical failure remain separate from finite-endpoint impossibility or physical inadmissibility claims. The distinct10kPa passing example changes no governing term or old gate.

## reproducibility_rights

PASS. replay.py verifies23freeze hashes, original/durable private PDF hash,46archive-aware historical receipts, exact current/preview identity and research-rate equivalence, then only source-level saved-observation assessors. replay-inputs.json additionally binds every directly used replay module and principal evidence. replay-results.json records actual run output. Public report includes derived explanations/source locators, not source PDF/text/renders or experimental data. Private source retention is supplemental identity, not a new edition claim. Repository source-archive maps preserve old implementation receipts without claiming current compatibility.

Run from any directory: `python3 -B /absolute/repository/docs/ingestion/hypoplastic-clay-2013/approval-v1/independent-review/replay.py --root /absolute/repository`. Exact Cartesian replay is intentionally local provenance mode: different libm/platform last bits may fail and require explicit regeneration/review; no silent tolerances are added. Source reading still requires authorized private PDF access; hash replay does not replace scientific equation reading.

Reviewer-script development initially assumed native saved summary pressure keys were numeric (they are strings), and that all entries named failure_probes failed (one is successful zero). Those assertions failed before final replay, with no model/evidence mutation. Final replay explicitly converts only saved summary key[0] to float and separately checks the zero-success identity. All numerical/error/physical gates remain unchanged. These clerical replay assumptions were not source/core defects; no waiver was used.

The schema-valid draft agent-review.json is my actual accepted decision, ready for coordinator installation only. No registry, shared implementation, historical report, paper or board was edited by this run.
