# Independent VW96 agent review

SCI-vw96-agent-v1, 2026-11-02. **Accepted for the bounded scope below.** All nine checklist items pass; no unresolved blocking finding remains inside that scope. This is the actual independent source/equation/numerical decision of the separately assigned Codex run `/root/sanisand_source_review`, not an automated test result or a retrospective rewrite of the old pending reviews. The reviewer did not author this model, its original transcription, crosswalk, reference or reports. Legacy author-run IDs were not retained; that fact is stated rather than inventing an identity. Current policy requires no human scientific signature.

Exact reviewed definition: `models/hypoplastic-sand-vw96.json`, SHA-256 `1df95f8128c4f16066004de7615289075bafe96d2174e06e5cd76704f45bbd61`. The root remains schema v0.1 and byte-identical. The explicit v0.3 crosswalk clarifies its interpretation; no migration or approval of a future migrated hash is performed.

## Accepted scope

The eight-physical-parameter VW96 stress/void-ratio law in compression-positive Mandel coordinates, interpreted as effective skeleton Cauchy stress, infinitesimal kinematics, fixed spatial frame and **zero spin**, with strain-path rates and explicit supplied sigma/e. Its numerical verification is bounded to the exact default Karlsruhe illustrative parameter vector and the retained rate/short-history cases, using the historical native CLI evaluator/integrator identities in the pinned reports. This is source/equation acceptance plus bounded numerical verification, not a material prediction guarantee across an input continuum.

Default vector in declaration order: p_ref=100000 Pa (project numerical scale), phi=0.5235987755982988 rad, hs=5800000000 Pa, n=.28, ed0=.53, ec0=.84, ei0=1, alpha=.13, beta=1.05. Algebraic equation fidelity is assessed for the general symbolic factors, but numerical accuracy across the parameter boxes is **not** qualified.

For conventional compressive-soil use retain Decision0004's project restriction to strictly compressive principal effective stress, positive pressure and strict interior ed<e<ei. Exact isotropy is included. Numerical accuracy around the nonzero near-isotropic cutoff/switch, density/pressure boundaries and singular shape denominators is excluded. The source-law identity outside the cutoff is supported, while the finite cutoff is disclosed as a numerical continuation. No whole-trajectory physical-domain certification follows from saved endpoints. Wider/mixed-sign runtime admission is not an applicability claim. Users of broader studies must declare and verify their own stage coverage and numerical acceptance; the runtime guards are not upgraded by this review.

Current release engine, Wasm, browser/atlas hosting, mixed-control solvers, FE use, nonzero-spin/finite-rotation transport, full-update tangents, late-internal-failure recovery and restart interfaces are excluded. The historical native backend evidence is assessed in its own identity only. No registry, model, host or deployment change is made here.

## source_provenance

PASS. Primary source: P.-A. von Wolffersdorff (1996), *A hypoplastic relation for granular materials with a predefined limit state surface*, Mechanics of Cohesive-Frictional Materials 1, 251-271, [DOI](https://doi.org/10.1002/%28SICI%291099-1484%28199607%291%3A3%3C251%3A%3AAID-CFM13%3E3.0.CO%3B2-3). The private supplied 21-page journal PDF hashes to `70eb1297cd25e67daf8b35b8f8c22f42c3a7fae2c0a62ae9e0079e3b03e64100`. Printed page=PDF page+250. I read extracted original text for derivation context and visually inspected full equation/title/example pages PDF1,2,12-20 (printed251,252,262-270), including Eqs1-2,40-46 and AppendicesA-C. The separate earlier full21-page audit supplies additional reading coverage and is independently assessed here, not treated as approval by itself. Private renders are hashed in source-reading.json; no image/full extracted text is redistributed.

Fellin's 1999 summary was the transcription source and supplies Karlsruhe defaults; the original confirms the complete eight-parameter law. Its original TableI p264 instead describes Hochstetten (phi33deg, hs1000MPa,n.25,ec0.95,ed0.55,ei0 1.05,alpha.25,beta1.5). Neither this table nor NH97's beta=1 host replaces the current defaults. The root's stale source locator saying original review pending is historical metadata, corrected in the hash-bound dossier/review receipts; it is not a missing original now. A model metadata correction will need new hash binding.

## equation_fidelity

PASS. I compared all18 derived fields, both evolution equations and nine declarations through the crosswalk and exact root. Eq40 p262 gives the tensor law; Eq41 gives a; Eqs42-46 p263 give F and its invariants, characteristic densities, fe,fd,fb. The implemented fb includes the reciprocal bracket, `(ei0/ec0)^beta`, `(1+ei)/ei` and pressure power. No factor is dropped or specialized to beta1. No yield multiplier, elastic-plastic split, fabricated memory or cap is introduced: critical-state surfaces describe asymptotic conditions (p254), not an incremental yield return map.

Under sigma=-T and compression-positive d=-D_source, normalized stress A=T/tr(T)=sigma/tr(sigma) stays unchanged. The linear terms are odd in D; the norm is even. Negating the source stress rate therefore leaves positive linear terms and a negative nonlinear norm term, exactly the root's signs. Eq2 p252 gives e' = -(1+e)tr(d). AppendixA's rank-one inverse and AppendixB's reduction to a tensor proportional to A+dev(A) support the final form; AppendixC C9-C10 p270 matches the negative cubic trace and F expression. The reused 27 algebra checks pass, including sign, Mandel norm, Appendix identities and source-shape witnesses.

Exact isotropy gives F=1. The `j2<=1e-24` cosine-zero branch is not the original nonzero invariant. It replaces direction information for a tiny nonzero deviator; do not call its accuracy exact or assume smooth derivatives through the switch. The absence of an explicit cosine clamp and possible binary64 excursions just beyond [-1,1] remain disclosed numerical limitations. No equation change is justified by this review.

## conventions_dimensions

PASS. Stress and hs,p_ref are Pa; e, normalized stress, density factors and shape quantities are dimensionless; phi is radians, not degrees. fb has stress dimensions, making stress-rate-per-path-fraction stress-valued and e-rate dimensionless. The Mandel order is [xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz]; Frobenius contractions and Euclidean Mandel norms agree. Cubic trace is a matrix invariant rather than a componentwise cube sum in a general frame. Three oblique saved covariance cases test tensor conversion, not finite rotation objectivity.

The primary Eq1 footnote p252 explicitly defines the Jaumann rate `T_circle=T_dot-WT+TW`; it equals the ordinary rate only at W=0. The declared fixed-frame zero-spin restriction is defensible. Reading stress as effective skeleton stress is the project stress binding for granular material; this law supplies no total-stress/pore-pressure coupling. Fixed-frame covariance, source large-strain plots or a path-rate API do not establish a finite-deformation implementation.

## initialization_domain

PASS within declared restrictions. The complete material state is six stresses and scalar void ratio, with no independent plastic strain/fabric/history tensor. Explicit sigma/e is sufficient for this local law; a previous loading process is represented through those state values. Root sigma=100kPaI,e=.7 is an illustration, not a measured preparation. The crosswalk requires both fields explicitly and rejects missing fields without projection; all13 contract checks pass in memory. This does not change the legacy defaults or approve arbitrary automatic initialization.

All eight root guards and parameter boxes are identified as project numerical admission. In particular pressure>1e-8 p_ref, strict ed<e<ei, F>0 and fb>0 are not a complete physical validity theorem. Source p254 includes limiting ed and ei descriptions, while the implementation excludes them. AppendixC characterizes F for u=0 or 0<u<sqrt2; literal guards admit the documented diag(450000,-75000,-75000)Pa continuation outside that range. A separate mixed-sign witness lies inside u<sqrt2, so the shape bound alone is not a principal-compression rule. Neither witness disproves the source equation on the accepted compressive scope or mandates a guessed runtime guard. Decision0004's scope restriction and excluded boundary claims are adequate; no blanket parameter-range approval follows.

Figure10 p265 calculation legends differ from the p264 nominal e=.67 text; Figures13/14 p266-267 captions label .67 at shear start while p264 body gives .633 after isotropic preparation. I confirm those original locators. This is a blocker for claiming exact reproduction of those figures, which is excluded here; it does not prevent verifying the explicitly manufactured sigma/e reference cases.

## integration_transactions

PASS for the stated material law and limited historical CLI contract. Positive homogeneity for positive path scaling permits rate evaluation over a unit path interval; it is not physical-time dependence. At zero d both rates vanish. Reversal changes the linear contribution sign but not norm(d); it needs no event/reset or hidden anchor. The norm is nonsmooth at zero, so no globally smooth tangent is claimed. Explicit sigma/e fully specifies a mathematical restart, but an exposed restart implementation is not certified.

The historical common solver approximates the rate with explicit midpoint, comparing a full step with two half steps, accepting the two-half result and recursively subdividing on error/domain failure. The model-scaled 1e-6 defect criterion is a numerical heuristic, not an a priori error bound. The separate RK4 endpoint comparisons supply the bounded accuracy evidence. Three saved invalid-initial-state CLI calls reject and return their exact input sigma/e. They prove invalid-parent rejection/rollback only. They do not prove rollback after accepted internal substeps, trial/commit isolation in a mutable host, or current API restart behavior. Those stronger guarantees are not promised in this acceptance. The current solver now adds endpoint-defect sampling; historical reports are not silently assigned to that revision. No new compiled calls occurred.

## independent_numerical_evidence

PASS for the retained finite test scope. I read the Cartesian oracle and its tests. It independently constructs ordinary 3x3 tension-positive source rates, reverses signs and uses classical RK4, without the DSL/generated tensor machinery or production midpoint integration. This is method independence; this actual separate source review supplies reviewer independence. Backend parity alone would not pass this item.

`check_saved.py` is a new independent saved-only review checker: it recomputes direct compression-positive Eq40 rates at all retained saved arguments, verifies covariance, recalculates saved-grid and native endpoint comparison ratios, checks exact Eq2 density continuity and exact rejected-parent states. It never calls RK4 generation, an engine integrator or compiled code. In v2 and the later clean native-resume report, all219 rate/covariance entries agree; all seven short prescribed-strain histories and three invalid-parent cases pass. The 216-grid rate cases cover three pressures (20kPa,100kPa,1MPa), two interior densities, four stress shapes and nine directions including hold, isotropic loading/unloading, axial compression/extension and three shears. Histories start at100kPaI,e=.7 with increments up to .002 and include one reversal.

Failed v1 remains failed (225/226): its second reversal segment's128/256 reference ratio is2.9623579758>1. V2 retains the same rate, path and reference thresholds and refines that segment through1024 steps; final reference ratio is.6677505811. Other references converge at256. Rate tolerances remain1e-4Pa/1e-11 state+1e-9relative; native paths1Pa/1e-8+2e-5relative; reference-grid .001Pa/1e-11+1e-10relative. The largest native path ratio is.3160116536. These budgets are reasonable bounded software checks, with a distinctly tighter reference gate; they are not calibrated engineering error limits. Reversal's convergence behavior is empirical, not a rigorous global RK4 error certificate. v2's expanded refinement resolves a retained failed reference, without tolerance relaxation or deletion.

No dense/loose-boundary, switch-transition, tensile, all-parameter, derivative/full-update tangent, broad path or experimental accuracy is established. The saved report records endpoints/grid levels, not every material stage, so full-stage physical-domain coverage is not asserted. These are limitations of the named finite verification, not unresolved in-scope findings.

## backend_delivery

PASS only for the **historical pinned native CLI evaluate/integrate interfaces** and finite checks just assessed. The v2 record binds exact model hash, source identities, solver hash and full saved comparison report. The31October native-resume manifest records a clean Release build (AppleClang21), matching model hash and229/229 focused checks with a retained report. I checked both saved reports; this adds software delivery evidence for their identities, independently from source-law correctness. Initial v2 binary identity alone is not a clean-build attestation; the later receipt is identified separately.

This item does not qualify any current-release binary, Wasm, packaged browser, catalogue integration, alternate settings/mixed controls, or changed engine/hash. These unsupported interfaces are explicitly excluded; no backend agreement is used as independent mathematics. No new build, compiled execution or author code execution was needed or performed.

## applicability_claims

PASS with the explicit boundaries above. Decision0004 correctly separates runtime acceptance, declared comparison scope and scientific support. I accept its conventional compressive project restriction without misattributing it to a universal source guard. Symbolic source agreement, empirical finite numerical verification and experimental predictive performance remain separate. The source itself warns at p266/Fig15 that reloading stiffness can be too small for certain cyclic loading with more than one reversal. A numerically correct single-reversal history does not remove that physical limitation. No general cyclic, Wichtmann, original-figure, FE or experimental validation claim is accepted.

Karlsruhe illustrative defaults, original Hochstetten TableI, NH97 beta1 and later fitted vectors remain distinct identities. No fitting, parameter substitution or new benchmark is performed. Lack of new experiments is not a blanket approval blocker under the current policy because predictive validation is outside this review's claim.

## reproducibility_rights

PASS. review.json binds the exact model, policy-format nine decisions, reviewer/run identity and hashed evidence. inputs.json binds reviewed source/code/report documents; source-reading.json binds the private original/render receipts and inspection locators. manifest.json binds the new packet. The checker validates exact current model, all review artifact hashes, source receipts, retained failed-v1/passed-v2 dispositions and recomputed saved comparisons. Private PDF is optional to replay saved checks but required to repeat actual source reading. No private copyrighted source, raster, full extraction or experimental archive is distributed. Original author code is neither imported nor executed.

Run from repository root:

```
python3 -B docs/reviews/vw96-agent-v1/verify.py
python3 -B -m atlas.agent_review docs/reviews/vw96-agent-v1/review.json --for-approval
```

`verify.py --private-source` additionally checks the local original PDF and retained private render hashes. It runs no builds or compiled material calls. A passing checker validates this accepted record and saved evidence; it is not a new qualification of a changed engine. The coordinator may integrate a new approval record for exactly this bounded scope after checking these bytes. No old pending source review is rewritten. Root migration, current-release/browser qualification, broader studies and external release remain separately owned work.
