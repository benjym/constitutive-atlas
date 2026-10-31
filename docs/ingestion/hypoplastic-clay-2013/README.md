# Hypoplastic clay 2013 - source closure and v0.3 preview crosswalk

Task: ING-hypoplastic-clay-2013. Owner: clay2013_source_closure. Date: 2026-10-31. Bounded source/preparation/precision consolidation; no model admission, builds or author-code execution.

## Recommendation

A **named author-manuscript Appendix43-58, zero-spin, regular-compressive-interior laboratory draft** has enough existing equation and finite-path evidence to justify a prospective actual-browser/C-ABI study. It is not ready for scientific admission or a claim of arbitrary-SPD support. Keep the old research definition and historical evidence unchanged; create a separately identified v0.3 definition if the coordinator selects that preview. The source review below closes Appendix equation agreement with the publisher's accessible HTML, but **not complete final-publication equivalence**, physical preparation or experiment matching.

The smallest next implementation is a new v0.3 preview retaining the existing stress/e equations, explicitly named source/kinematic restrictions and bounded rejection policy, followed by a frozen actual-driver all-protocol native/Wasm study. Do not repeat the completed source-rate, isotropic and nonisotropic studies as substitutes for that consumer-level check. Near-SPD boundary resolution and nonisotropic late-failure recovery need distinct bounded cases before making wider numerical claims.

## Identity and source receipts

David Mašín, *Clay hypoplasticity with explicitly defined asymptotic states*, Acta Geotechnica 8,481-496 (2013), [DOI](https://doi.org/10.1007/s11440-012-0199-y). Publisher records online22December2012, issueOctober2013, received25April2012 and accepted19November2012. This is the isotropic-stiffness base, distinct from the 2005 model, the2014 anisotropic-stiffness extension and any IGS/GIS overlay.

The [author manuscript](https://web.natur.cuni.cz/uhigug/masin/download/Masin_AG12-pp.pdf) is available privately at `/private/tmp/atlas-clay-source-private/masin-2013-author.pdf`:2646368bytes,16pages, SHA256 `21834ab9da81ec2cdebdf3a3d7f97b691d47bf481a24432bc0562aca9f503281`, freshly recomputed this pass. PDF pp3,4,8,13,14 were visually inspected from existing renders. The PDF skill was read and its visual-review workflow used. Full text searched for initial/preparation/consolidation/parameter statements. This supplements, rather than replaces, the earlier [source inventory](../../reviews/clay-2013-2014-source-packet.md).

Downloads filename search for clay/hypoplast/Mašín/2013 found other clay/sand material and run files, no named2013 paper. This is a bounded filename inventory; it cannot exclude a generically named PDF. The known private source was then used. No duplicate source request to the user is necessary.

The [publisher HTML](https://link.springer.com/article/10.1007/s11440-012-0199-y), accessed2026-10-31 through the web reader, exposes the entire Appendix43-58 despite the paywalled body. Manual comparison with the actual manuscript renders found the same expressions for:

| Equations | Compared features |
| --- | --- |
|43-46|Minus nonlinear stress term, separate fd/fdA, L and A contractions, fs coefficients and p=-tr(T)/3|
|47-49|alpha=2, 2p/pe power, pe exponential, pr=1kPa and distinct fdA|
|50-54|Invariant quotient, omega sign and a=.3; negative-second-principal-invariant convention|
|55-58|Normalized d, full dA brackets/exponents, negative Lode quotient, xi and normalized deviator|
|Appendix closing paragraph|Exactly five material parameters and state T/e|

This is expression-level visual/manual reconciliation, not byte equivalence, OCR equivalence, an independent human review or a review of the inaccessible body. Publisher PDF access failed through the web reader. A direct Python HTML acquisition additionally failed with DNS resolution; therefore **no raw publisher byte hash is claimed**. `source-receipts.json` distinguishes an actual private-byte receipt from a web-reader observation. No copyrighted PDF, extracted text, images or publisher page is redistributed.

## Equations and source-to-schema map

The complete law is already transcribed in the [source-rate dossier](../../models/clay2013-source-rate.md), [Cartesian note](../../models/clay2013-cartesian-source-note.md) and unchanged `models/research/clay2013/hypoplastic-clay-2013-research.json`. This packet does not create another mathematical implementation. Source Eq43 and density p3Eq7 give the seven coupled rates. The existing eliminated fourth-order operations preserve L:X=X+c tr(X)I and A:X=fs(L:X)+(T/lambda*)tr(X), c=nu/(1-2nu). All factors43-58 remain required; a failure criterion alone would not represent this model.

`crosswalk.json` gives the explicit v0.3 formulation/input/state/initialization fields, a snapshot hash of the unchanged research definition and numerical bounds distinguished from source claims. It is a **crosswalk fragment**, not a complete executable record.

| Source locator | Meaning and proposed adapter | v0.3 representation |
| --- | --- | --- |
|p3Eqs1,3; Appendix43|Rate-independent objective stress law; source Euler stretching and Zaremba-Jaumann rate|strain_path/strain_path_rate; zero-spin restriction small_strain_3d,fixed_spatial,objective_rate:none|
|p3Eq3|T°=Tdot+TW-WT; W skew velocity gradient|W=0 named restriction; changing spin unsupported, no objective finite-step transport inferred|
|Appendix46|p=-tr(T)/3|T=-sigma and D=-E; compression_positive stress and strain; Cauchy effective stress binding to sigma|
|p3Eq7|e_dot=(1+e)tr(D)|e equation=-(1+e)trace(de); genuine persistent scalar invariant|
|Appendix43-58|Symmetric tensor contractions/Frobenius norm|Mandel order xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz; six stress components +e|
|Appendix closing paragraph|Only base T/e persistent state|sigma:cauchy_stress/symmetric_spatial_tensor; e:void_ratio/scalar_invariant; no plastic multiplier, pc, fabric or history reset|
|p3Eq5-7 and p8Sec7|Density interpretation and explicit stress/e|explicit_state,examples_only,required_state:[sigma,e],domain_and_initial_checks|

Source tensor notation does not itself prescribe Mandel ordering. Mapping stress and input together preserves contractions, norms and Cartesian rotations. The effective-skeleton-stress adapter agrees with the existing source inventory; it supplies no pore-pressure/hydraulic constitutive law. The current-frame infinitesimal restriction is narrower than the original objective tensor formulation. Parameter `de` is a dimensionless full strain increment; the ODE derivative is per dimensionless straight-path fraction0..1, not per second. Positive homogeneity supports that reparameterization; no physical viscosity or clock is introduced.

## Parameters, initial state and physical preparation

p8Sec7 identifies phi_c as critical friction angle, lambda* as isotropic NCL slope in ln(1+e) versus ln(p/pr), kappa* as unloading-slope control, N as that NCL intercept at pr=1kPa, and nu as shear-stiffness control. All are dimensionless except the angle convention (table degrees; implementation radians). pr=1000Pa is fixed source normalization. `p_scale` is an Atlas numerical error weight, not a sixth soil parameter. Source does not give the current JSON's rectangular min/max box. For a preview, lambda*>kappa*>0, -1<nu<.5 and0<phi_c<pi/2 are project conservative mathematical restrictions; the actual finite numerical scope can be narrower. Do not present min/max as calibrated or complete source admissibility.

Table1 `eval.` is explicitly fictitious: phi_c=25degrees,lambda*=.1,kappa*=.01,N=1,nu=.2 (the paired r=.242 is for the original model). Current research defaults30degrees,.12,.025,1.1,.2 are different software fixtures; they must retain that label. Other Table1 rows are material-specific fits, not general defaults. Eq39 connects nu to the older model's r through lambda*/kappa*; copying r into nu is incorrect. The source says nu was sometimes fitted independently for experimental comparisons.

Source-supported construction **on the isotropic NCL** follows Eqs5/48: e=expm1[N-lambda*ln(p/1000Pa)], sigma=pI. This is an algebraic declared state construction, not a simulated consolidometer history. An OC density-normalization ratio R=pe/p permits e=expm1[N-lambda*(ln(p/pr)+lnR)], but R is not universally interchangeable with physical OCR under nonisotropic preparation. Require explicit input provenance and reject negative computed e rather than clamp it.

The original provides example prepared states (Fig10 inside ASBS; Fig11 K0 unloading line; Sec8.2 material-specific consolidation/testing), but no universal algorithm prescribing arbitrary initial stress/e. The [initialization review](../../reviews/clay2013-initialization-policy.md) already proves a regular field can point outward from ASBS; do not impose f<=0 as a continuous yield barrier, project onto ASBS or infer physical validity from evaluation success. A named on/inside preparation constraint could be a separate explicit policy. Optional ASBS residual/log-gap diagnostics should not silently alter state or turn diagnostic overflow into material failure.

## Precision and temporal integration

The [algebra review](../../reviews/clay2013-algebra-review.md) supplies the stable Fm quotient and exact-isotropic direction d=-I/sqrt(3); those are existing evidence. Double deviator projection before normalization and exact-isotropy/underflow rejection are project numerical policies, not printed source branches. Existing normalized invariant SPD predicates are equivalent to SPD in real arithmetic but are **not certified binary64 eigenvalue-sign tests near singularity**. Some mathematically SPD states have Fm rounded to1 and reject; no accuracy claim over arbitrarily ill-conditioned states is defensible. Do not add a floor, silently clip Fm/Lode cosine, or call all accepted near-boundary states source-admissible.

A regular-interior preview can explicitly expose conservative rejection and its unresolved boundary precision. If stronger SPD assurance is required, the coordinator should commission a distinct adversarial actual-float positive/indefinite guard study and a reviewed normalized-Cholesky or margin policy before changing the shared definition. It must preserve current evidence and avoid presenting a numerical cutoff as a physical theorem. Small-angle cancellation and finite intermediate overflow/underflow also restrict numerical support.

The law needs coupled stage stress/e, stage-domain/finite checks, adaptive local-error control and transactional trial/commit/rollback. Source does not select the Atlas integrator, tolerances, budgets, substep controller or full-update tangent. No discrete history resets are specified for this base. Zero de gives zero rate/identity advancement in a regular state; zero physical loading does not cause creep. Norm(de) is nondifferentiable at zero for tangent construction. No finite-spin or generally smooth update-tangent claim follows. Nonzero path histories must retain the actual signs, order and full six-component inputs; restarting a reference from each approximate endpoint hides accumulated error.

## Existing evidence and checks performed

Read before new work: source-rate and Cartesian dossiers; research integration; independent algebra/engine/source/initialization/nonisotropic reviews; current formulation/initialization contract and charter. Existing33 isotropic trajectories/115updates,40 noncoaxial rate cases and four nonisotropic physical/rotated cases at three tolerances were **not rerun**. The nonisotropic review's later strict reference replay fixes supersede its retained earlier verifier-blocker section. Its36native and36Wasm calls support modest regular paths at one parameter/pressure setting, not boundary or universal coverage. Current interpreted/native/Wasm agreement is not new independent source verification.

`check_crosswalk.py` is a bounded **new contract-consistency check**, not an independent constitutive algebra oracle: it pins the original definition, builds an in-memory v0.3 copy via the official migrator, declares source-supported e semantics, validates the complete copy, compares the proposed contract and verifies equations/derived/domain/parameters remain unchanged. It smoke-checks an explicit algebraically constructed NCL state at the source's fictitious `eval.` parameters with the generic initializer; omission/negative density reject. Nothing is written to model directories. It records actual outcomes in `checks.json`. No compiled artifact is called.

Run after installation:

```sh
python3 -B docs/ingestion/hypoplastic-clay-2013/check_crosswalk.py --root /Users/bmar5496/code/constitutive-atlas
```

## Handoff and remaining gates

Owned files: README.md,source-receipts.json,crosswalk.json,check_crosswalk.py,checks.json,manifest.json. Staged under `/private/tmp/atlas-clay2013-source-closure-v1/packet/`; coordinator copies only to `docs/ingestion/hypoplastic-clay-2013/`.

1. Source completeness: Appendix agreement now rechecked against publisher HTML; full final body/preparation/calibration equivalence remains open. No new universal domain or specimen initialization rule discovered.
2. Executable support: existing research target only. A new named v0.3 preview needs a new model hash, explicit contract/source limitations and prospective consumer integration verification.
3. Numerical verification: substantial prior bounded evidence; actual consumer mixed-control checks, nonisotropic late-failure/recovery, broader parameter/pressure/partition/boundary precision and tangent limitations remain.
4. Scientific admission: open; no human signature, source-matched calibrated experiment residuals, Wichtmann clay-match study or complete applicability claim is supplied here.

No shared schema/compiler/engine/web changes are requested for the restricted contract itself. Browser explicit-state and parameter provenance controls remain integration-owner decisions; initialization recipes currently do not implement incremental specimen preparation automatically. The live ING task stays WIP until the coordinator reviews its scoped disposition.
