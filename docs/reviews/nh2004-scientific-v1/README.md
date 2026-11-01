# Independent technical scientific assessment: NH2004 clay / Appendix V / BE

Task **SCI-nh2004-independent-review-v1**, 2026-11-01. Reviewer: fresh-context automated AI agent, separate from the implementation author. Owned scope: this directory only. No compiled or vendor artifacts were executed, no source/evidence files changed, no admission status promoted. This is an **automated independent technical assessment**, not the charter's canonical external scientific signature and not experimental validation.

**Verdict: conditionally supported as a bounded research transcription.** The inspected differential equations, signs, stress transformation and selected Appendix V branch agree with the readable primary source, subject to the explicitly documented A8 decision and project finite discretization. Twenty-five new independent algebra checks pass. Two material gaps prevent a broad scientific-readiness judgment: the executable permits reference-inconsistent density/void initializations, and the retained finite-path study does not traverse softening. Prepared-specimen reproduction and external scientific signature remain unresolved. No critical equation-transcription defect was demonstrated in the tested domain.

The exact installed definition reviewed is `models/research/nh2004/nakai-hinokio-2004-clay-appendix-v-be.json`, SHA-256 `a93d2d47ed0808135f804fb2b0ac0ebb289b3421a43a03c563cbfddffb447ce8`. Its bytes equal the working model. Exact reviewed input hashes, including the primary source, implementation/reference scripts, retained plans/reports and policies, are in [input-manifest.json](input-manifest.json). Hash inventory is distinguished there from files substantively read. The mutable live board hash records reviewed context; its later coordination edits are reported as context drift rather than evidence corruption.

## Primary source and reading boundary

Teruo Nakai and Masaya Hinokio, *A Simple Elastoplastic Model for Normally and Over Consolidated Soils with Unified Material Parameters*, Soils and Foundations 44(2), 53-70 (2004), [DOI](https://doi.org/10.3208/sandf.44.2_53). Primary readable evidence: private original PDF `/private/tmp/atlas-nakai-hinokio-2004-source/original.pdf`, SHA-256 `e2ed4ed2416d5ca65f7760a02ebe4913ea3610579ca6447397db6f03912c6395`. All eighteen rendered pages were visually inspected in this review; equations were read from images, not watermark extraction or snippets. The supplied PDF skill was read and used for the visual inspection. No PDF/images are redistributed here.

The principal audit is pp54-61 Table1/Eqs1-54 and pp69-70 Appendices I-V. The remaining pages establish publication identity, experimental conditions, variant separation and limitations. This review did not acquire the cited 1986 preparation paper, reproduce a paper figure, digitize measurements, contact authors or inspect any author implementation. The paper's sand experiments and two-a calibration are context, not evidence validating this clay executable.

## Severity-ranked actionable findings

### F1 - High evidence gap: finite softening/peak and meaningful branch-crossing accuracy are unqualified

The working README says the model runs including softening. A saved regular **softening residual fixture** exists and is useful evidence of instantaneous equation transcription. It is not a finite softening path. Independently classifying endpoints of all six saved 32/64/128-grid material paths finds no softening endpoints: hydro unloading is elastic; all four deviatoric/non-diagonal paths are AF; hydro compression numerically splits AF+IC/IC-only on the hydro equality boundary. Counts and diagnostics are retained in [check-results.json](check-results.json). These classifications use accepted caller endpoints, not unknown internal substep histories, so they do not establish the absence of an internal crossing; they establish the absence of a demonstrated sustained softening path in the saved accuracy corpus.

All four deviatoric material paths start at rho=.03 and remain above .0292; their final stress ratios are modest. The sole continuous unload/reload path is hydrostatic. A rotated residual fixture covers **elastic** flow. General-tensor and shear paths do provide independent non-diagonal plastic accuracy evidence; nevertheless they do not establish a rotated softening transition or arbitrary strain-path cycle. The five 1% laboratory runs verify operations/control and void bookkeeping, not independent trajectory accuracy; they have no RK4 or experimental comparator.

**Smallest action:** qualify the README's softening statement as residual-level evidence until a separate prospective finite-path study crosses hP=0, follows sustained hP<0, and reverses through branch boundaries. Freeze independent trajectory convergence, nonnegative AF multiplier/admissibility, density evolution and rollback rules before compiled observation. Add a genuine nonhydro AF/IC/Appendix-V crossing path. Do not change existing gates or overwrite this study. This gap blocks a general softening/path-fidelity claim, not the existing short-path pass.

### F2 - Moderate scientific-consistency defect: Table2 reference density/void relation is not enforced

For the chosen fixed reference, let P=p/p_ref, T=tN/p_ref, zeta=ln(tN1/tN), lambda=(1+e_ref)Cc and kappa=(1+e_ref)Ce. The differential law implies the invariant

`H = e + rho + (1+e_ref)[Cp (ln(T)+zeta) + Ce ln(P)]`, with `Cp=Cc-Ce`.

For Table2's NC reference at98kPa, **H=N=.83**. This follows by differentiating: `de=-(1+e_ref)tr(dstrain)`, `drho=(1+e_ref)[tr(dep)-Cp n:ds]`, `d(ln(T)+zeta)=n:ds`, and elastic volumetric strain `tr(dee)=Ce dln(p)`. Eqs26-29 supply the same surface/density meaning. The default state satisfies H=.83, as does the study's OC synthetic state `(p=98kPa,rho=.03,e=.8)`.

The declared initialization checks enforce rho's sign and SMP consistency but not H. The current Python initializer demonstrably accepts both `(98kPa,.03,.83)`, H=.86, and `(196kPa,0,.83)`, H=.89443773449. These correspond to the runner's independent `--rho` or `--pressure` options without a compatible void-ratio change. Probes exactly replay via [probe_initialization.py](probe_initialization.py). Since e does not feed stiffness/hardening, this inconsistency can remain invisible in stress curves while misreporting physical specimen density.

**Qualification:** arbitrary H can be interpreted as a different reference-intercept/gauge for a synthetic mechanical problem. It is not intrinsically an algebraic contradiction in the differential system. It cannot simultaneously be the published N=.83 Table2 material/preparation. The present independent choices need an explicit interpretation.

**Smallest action:** add a separately reviewed preparation recipe that computes compatible e or rho from the declared reference, or explicitly expose/reference an alternative intercept and label such states synthetic. Preserve a deliberate raw-state mode if needed. For H=N, the recipe is `e=N-rho-(1+e_ref)[Cp(ln(T)+zeta)+Ce ln(P)]`; it is algebraic consistency, not a substitute for the missing1986 preparation history. Do not silently project user states or infer an OCR from pressure alone.

### F3 - Moderate numerical limitation: finite BE density/reference drift is not an exact surface reconstruction

The rho residual applies differential compatibility at endpoint values. Finite `n_endpoint:delta_sigma` is not exactly `delta ln(tN1)`. The e residual is constant-reference infinitesimal bookkeeping. Consequently the exact continuous H invariant drifts under finite BE steps even while algebraic residuals pass. The saved100step laboratory runs show maximum absolute H drift from about3.96e-6 to4.34e-4; the largest is the zero-volume protocol. This is expected truncation behavior, not evidence that source Eq29 was transcribed with the wrong sign. It is additional quantified limitation, not a post hoc failure of the frozen qualification.

Rho remains essentially zero in the NC laboratory runs; tiny negative values (minimum about-4.65e-13 in isotropic compression) are numerical roundoff/residual tolerance, not demonstrated physical NC/OC departure. All saved laboratory auxiliaries are SPD; minimum eigenvalue is at least.40069 and their square-equation error is at most4.46e-12 in the independent saved-data audit.

**Smallest action:** include H drift and grid refinement when a preparation/experimental comparison uses reconstructed surface size, OCR or void ratio. Set a purpose-specific prospective accuracy target; no exact finite invariant claim is justified. A log-compatible integrator would be a separately identified numerical variant, not a silent change to these bytes.

### F4 - Moderate admission gap: source preparation and predictive evidence remain absent

P61 explicitly delegates Fujinomori specimen preparation to Nakai/Matsuoka1986. The paper's clay comparisons include constant mean and constant radial stress, OCR1/2/4/8, cyclic loading and strains well beyond these short material paths. At p63 the authors acknowledge underprediction of OC extension strength/dilatancy; p64 acknowledges overprediction of one-direction cyclic strains. These limitations must survive any eventual user-facing applicability description. P68 marks anisotropy/noncoaxiality, structured soil, time/age effects unconsidered and cyclic behavior only partially considered.

**Smallest action:** obtain/read the specific1986 preparation source and define one bounded source-matched clay experiment, including stress path, consolidation/OCR, compatible initial density and source-coordinate conversions. Freeze comparison channels, uncertainty/digitization policy and acceptance criteria before evaluation. Publication curves establish the authors' evidence for their formulation; they do not validate this project discretization or synthetic states. No broad literature search or parameter fitting is needed to take this next step.

### F5 - Low verification-maintenance issue: laboratory checker does not implement its whole auxiliary gate

The frozen delivery plan asks for SPD stress/auxiliary. `check_laboratory.py` checks stress SPD, finite state, control and void closure but does not check auxiliary SPD or its square residual. The new independent read-only diagnostic confirms the saved auxiliaries meet both conditions (F3), so no saved failure is alleged. Add these checks to a new reusable verifier, preserving the historical capture/checker bytes. The original static working verifier replays saved reports and residuals; it does not independently recalculate every physical trajectory gate. Backend parity alone remains shared-equation agreement.

## Equation, convention and branch judgments

| Item | Judgment | Reason / boundary |
| --- | --- | --- |
| Publication/variant | Supported | Full one-a clay extension Eqs40-52 plus explicitly selected AppendixV; not the1974 criterion, associated-only predecessor or two-a Toyoura sand. |
| Compression-positive effective stress/strain | Supported | Table1, saturated-clay context and p66 effective stress; positive tensor shear convention converted through Mandel sqrt(2), no engineering-shear factor2 error found. No pore-pressure evolution is supplied. |
| SMP tensor | Supported | `a^2=adj(S)/I2=inv(S)/trace(inv(S))`; unique SPD square root equals Eq2. Positive repeated spectra and hydro are valid. The polynomial symmetrized product gives `t=aS` on the consistent auxiliary manifold. |
| Stress positivity | Supported mathematically | For a real symmetric3x3 matrix, positive I1,I2,I3 together exclude negative eigenvalues. The auxiliary analogous conditions select its positive root. Near-zero/tension continuation is not authorized. |
| X and derivative | Supported in regular domain | Direct projection and invariant form agree. Deviatoric evaluation avoids hydro cancellation. Ordinary n differentiates the stress transformation; modified-space m holds a fixed as AppendixIV specifies. They must not be conflated. |
| Mstar/Rcs/Ycs | Supported with declared source decision | Table1 projection for `(1,-1/2,-1/2)` recovers Eq18/A10 and trace(m)=0 at Rcs=3.5. The printed A8 plus-sign denominator cannot yield that result; rejecting that intermediate while retaining Table1/repeated constants is justified. This is a documented resolution, not a verified erratum. |
| Elastic law | Supported | K=p/Ce and G=3K(1-2nu)/(2(1+nu)) reproduce Eqs37-38 with fixed e_ref. Cc/Ce are normalized slopes, not lambda/kappa directly. |
| AF, IC, AppendixV | Supported locally | Positive dtN enters IC through `<dtN>/tN1`; hardening AF uses `(n:ds-ICdrive)/h`; regionIV sets AF=0 and IC=`(n:ds)/icmod`, matching A26-A28. Softening excludes IC per Eq52. No misplaced delta_ij/3 or sign found. |
| Loading and peak | Conditional | Using n:D_el:de follows Eq35. Simultaneous multipliers avoid division by hP at peak. Global uniqueness/admissibility, all equality boundaries and finite crossings are not established. The predeclared positive-axisymmetric grid found no negative softening multiplier witness; this is a bounded negative search, not proof. |
| Density evolution | Supported differentially, conditional initialization/finite update | Eq29 uses total plastic volume on every selected branch. Elastic unloading raises rho via the moving passing surface; freezing rho on unloading would be wrong. Associated-only drho=-Lambda G/tN cannot be applied to all full-extension branches. F2/F3 remain. |
| Void ratio | Conditional | Linear fixed-reference small-strain bookkeeping is explicit and internally compatible differentially. It is not finite-volume conservation/current-e elasticity. Absolute reference and preparation need F2/F4. |
| Hydro derivative/tangent | Supported limitation | For beta1.5 the nonhydro flow correction scales as magnitude(dev stress)^.5, so the continuous value exists but a classical derivative generally diverges at hydro. The zero-branch AD derivative is an algorithmic choice. No general consistent material tangent is verified. |
| Time, frame, events | Supported bounded host | Rate independent, no creep on a regular mechanical hold. Fixed Cartesian infinitesimal zero-spin scope, no objective finite-spin transport, no source reversal reset. Rotational covariance is not finite-rotation objectivity. |
| Thermodynamics/stability | Unresolved globally | Normality in t space is not normality in sigma space. No global dissipation, uniqueness, acoustic/stability or mesh-objectivity proof follows from residual agreement. The paper's numerical second-order-work comment for its negative-AF branch is not such a proof for all parameters/AppendixV. |

## What the retained numerical evidence supports

Both read-only retained verifiers pass: original source/packet hashes and nine algebra groups; working full v0.3 model/installed bytes, freeze receipts, six residual fixtures, and1383saved native/Wasm pairs. The review did not run native/Wasm or recreate the builds. Saved source and binary receipts, build/setup failures and compressed raw-response identities remain retained.

The independent NumPy reference is structurally useful: spectral principal construction plus augmented compliance solves and RK4, without Atlas imports. It shares the implementation author's source interpretation and branch assumptions; it is independent computational mathematics, not an external scientific signature. Its256/512/1024reference refinement and six32/64/128BE path studies support the declared short synthetic paths. The finest endpoint errors are approximately1.06e-5 to1.07e-3 scaled; residual checks alone would not establish this accuracy. The existing refinement gate only demands finest error below coarsest (or a small-error exception), not strict monotonicity at every intermediate grid or a measured first-order rate. No stronger order claim is made here.

The new checks use no working reference or Atlas imports for algebra and saved physical diagnostics. They independently establish SMP identities, Mandel contraction, regular ordinary-stress gradient, critical-state trace and the Table1 projection (25passes); derive H; inspect reference-consistency drift and caller-endpoint branches; and search a predeclared softening-denominator grid. No tested negative-multiplier witness was found. Initialization probes separately use the existing Python API solely to show F2 acceptance. All new rules were recorded in [CHECK_PLAN.md](CHECK_PLAN.md) before running the new checks. There were no new failed numerical checks, no tolerance changes and no compiled observations. Historical failures were preserved and not reclassified.

## Reproduction and decisions

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/reviews/nh2004-scientific-v1/check_review.py
PYTHONDONTWRITEBYTECODE=1 python3 docs/reviews/nh2004-scientific-v1/probe_initialization.py
PYTHONDONTWRITEBYTECODE=1 python3 docs/ingestion/matsuoka-nakai/working-v1/verify.py
PYTHONDONTWRITEBYTECODE=1 python3 docs/ingestion/matsuoka-nakai/verify_packet.py --source
PYTHONDONTWRITEBYTECODE=1 python3 docs/reviews/nh2004-scientific-v1/verify_review.py
```

The first command only rewrites this review's deterministic diagnostic output. The remaining commands are read-only. NumPy is required; the private PDF is required only for `--source` and full private input-hash verification. No compiled artifact is called.

| Claim | Verdict |
| --- | --- |
| Bounded differential clay/AppendixV transcription | **Supported**, subject to explicit A8 resolution and declared scope. |
| Exact source finite return map | **Rejected**: this is a named project endpoint BE discretization. |
| Qualified short synthetic paths and saved backend agreement | **Supported** to the frozen corpus/bounds, with F1/F3 limits. |
| Arbitrary runner states represent Table2 Fujinomori specimens | **Rejected** without compatible reference/preparation, F2. |
| General softening/cyclic/path accuracy | **Unresolved**, F1. |
| Experimental validation or reproduction of paper curves | **Unresolved**, F4. |
| General tangent, finite-spin/finite-strain, anisotropy, structure, aging/creep | **Rejected as current capabilities/claims**. |
| External scientific sign-off / reviewed promotion | **Unresolved**; this automated assessment does not supply it. |

The smallest immediate implementation-facing action is a separately reviewed initialization/reference recipe with explicit synthetic-state disclosure (F2). The smallest scientific action is the bounded1986 preparation/source study (F4). A new prospective softening/branch-crossing numerical study (F1) can be scoped independently. No edits outside this directory, staging, commits, builds, push or deployment were performed.
