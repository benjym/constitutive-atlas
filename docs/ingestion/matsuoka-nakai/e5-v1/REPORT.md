# Independent E5 review — Nakai–Hinokio 2004 clay / Appendix V / BE

**Decision: accepted for the exact five illustrative Table 2 NC laboratory
inputs and the adjacent-rounding drained-only supplement below.** No unresolved blocker for that scope. This review does not
qualify a general state/preparation editor, broader clay paths, sand,
experimental reproduction, a standard packaged browser, or live release.

Review run `/root/nh2004_e5`, task `REVIEW-nh2004-e5-v1`, 2026-11-11.
This run is separate from the coordinating implementation run `/root`;
it did not author the model, reference study, solver or runtime captures.
It inherits task context, reads the original source personally, and replays
saved data with a new independent mathematical check. No compiled or author
software was run by the reviewer. The exact installed research model is
`nakai-hinokio-2004-clay-appendix-v-be`, SHA-256
`a93d2d47ed0808135f804fb2b0ac0ebb289b3421a43a03c563cbfddffb447ce8`.
Its content matches the frozen working copy.

## source_provenance

Teruo Nakai and Masaya Hinokio, *A Simple Elastoplastic Model for Normally
and Over Consolidated Soils with Unified Material Parameters*, *Soils and
Foundations* 44(2), 53–70 (April 2004), [DOI](https://doi.org/10.3208/sandf.44.2_53).
I verified the 18-page original (1,870,619 bytes, SHA-256
`e2ed4ed2416d5ca65f7760a02ebe4913ea3610579ca6447397db6f03912c6395`)
and visually read all pages from Poppler renders using the PDF skill. The
[original](../source-receipt.json) and [recovery](../current-runtime-receipt.json)
receipts identify the same source bytes. The selected equation set is the full
one-`a` clay extension with Appendix V; not the 1974 Matsuoka–Nakai strength
criterion, the Cam Clay comparison, the 1986 NC predecessor, or the 2004
two-coefficient Toyoura sand calibration. Table 2 supplies the parameters.
Neither a later paper nor author code is used to fill gaps.

## equation_fidelity

| Paper locator | Exact-model mapping and finding |
| --- | --- |
| Table 1, Eqs. 1–5, A1–A6 | From `S=sigma/p_ref`, the positive square root of `adj(S)/I2(S)` has principal entries given by Eq. 2. The two commute, so the symmetrized product used for `tbar` equals `a*S`. The projection gives `tn=3 I3/I2`. The stable deviatoric expression for `Xtwo` is algebraically `I1*I2/(9*I3)-1`. |
| Eqs. 14–21, A7–A11, A17–A25 | `zeta` and the reconstructed surface size use Eqs. 14–16. Table 1 applied to plastic increment proportional to `diag(1,-1/2,-1/2)` gives `Y=(a1-a3)/(sqrt(2)*(a3+a1/2))`, exactly Eqs. 18/A10; the intermediate A8 has an inconsistent plus sign when expanded from the Table 1 projection and is bypassed. `nload` is the ordinary-stress derivative; `mflow` differentiates modified stress with the normal held fixed, per Appendix IV. The `X=0` continuous values are used. |
| Eqs. 22–39, A12–A16 | `Cp=Cc-Ce`. Eq. 29 with total plastic volume gives the density residual; there is no independent plastic volume history to advance. Eqs. 32–34 supply the one-`a` `G(rho)` and AF modulus; Eq. 35 supplies the strain-controlled elastic predictor; Eqs. 37–39 give `K=p/Ce`, the isotropic shear modulus and additive elastic/plastic strain. |
| Eqs. 40–54 and A26–A28 | Negative trial load is elastic. At positive trial loading, negative `hard` selects Eq. 52 (AF only with the full drive). Nonnegative `hard` uses Eq. 51, including AF alone when the positive part of `dtN` is zero. A negative AF drive instead sets AF to zero and uses the full ordinary-stress drive in IC via Appendix V. Eq. 54 agrees with the implemented AF derivative. Solve both multipliers along with stress and density rather than dividing by the hardening modulus at a possible peak. Equality selections are numerical conventions and do not establish a robust peak crossing. |
| Table 2 and project discretization | The eight input values are audited below. Endpoint residuals, fixed-reference small-strain void bookkeeping, and the algebraic auxiliary are project choices. Stress, density, both branch equations, void and auxiliary closures independently agree on all 1,000 current accepted noninitial laboratory points. |

The `beta=1.5` flow has a nonclassical derivative at isotropy; the chosen
zero-branch Newton derivative is an algorithmic selection. No constitutive
update tangent, arbitrary branch crossing or finite softening accuracy
follows from the regular branch fixtures.

## conventions_dimensions

The v0.3 contract explicitly binds a symmetric infinitesimal strain
increment, fixed Cartesian frame and no objective rate. Both stress and
strain are compression-positive, with stress in Pa and strain dimensionless.
Mandel order is xx, yy, zz, sqrt(2)xy, sqrt(2)yz, sqrt(2)xz; the weighted shear
terms implement the paper's double contractions. The paper's saturated-soil
mechanical stress and Table 1/figures are used as effective Cauchy stress.
The stress normalization `p_ref` cancels from the differential ratios and
is restored in the stress residual. No spin, finite strain, pore-fluid
state or physical time is inferred. The Wasm lab scope reports effective
stress; zero-volume and signed-deviator-stress control can reconstruct
pore-pressure change only with fixed radial total stress and incompressible
fluid and grains. This is a host diagnostic; the other protocols expose no
pore-pressure value in the scope-aware API.

## initialization_domain

The approved parameter vector is
`[98000, .0508, .0112, .83, 3.5, 1.5, 500, .2]`, in model order
`p_ref,Cc,Ce,e_ref,Rcs,beta,a_density,nu`; pressure is in Pa, remaining
parameters dimensionless. The exact 16-component replay starts at
`[98000,98000,98000,0,0,0,0,.83,.5773502691896257,.5773502691896257,.5773502691896257,0,0,0,0,0]`.
The isotropic auxiliary represents `a=I/sqrt(3)`; the exact frozen
floating-point value must be passed for this named preset. Stress, density
gap, void ratio and auxiliary persist; AF and IC are temporary increment
unknowns, not physical accumulated strain. The bounds require positive
stress and auxiliary spectra, positive critical coefficient, `Cc>Ce` and
`e>-1`; initial checks include auxiliary square consistency and density
nonnegativity to numerical tolerance. Model metadata bounds are not
calibration or validated applicability ranges.

The Table 2 reference condition
`H=e+rho+(1+e_ref)[Cp*(ln(tN/p_ref)+zeta)+Ce*ln(p/p_ref)]=.83`
holds initially: `p=tN=p_ref`, `rho=0`, `X=0`. The validator can also
accept other pressure/density/void combinations without checking this
intercept, as shown in prior F2. Those combinations are outside approval.
The missing specimen preparation identified at p61 (the paper points to
Nakai and Matsuoka 1986) remains outside the illustrative NC use.

## integration_transactions

The source is a differential, rate independent mechanical law. This update
is endpoint backward Euler on an infinitesimal strain increment with a
committed parent state and trial endpoint. There is no clock, ageing, creep,
parent reversal reset or physical hold duration. Rejected trials preserve
the full input state. Saved exact zero increment, repeated trials, two
inadmissible inputs and deliberately insufficient iteration budget confirm
transaction behavior, including exact rollback and repeatable recovery.
The historical continuous hydrostatic unload/reload is a bounded supporting
diagnostic. Restart here means resupplying the complete committed state;
public serialization/import and cancellation belong to E7. Caller refinement
addresses truncation; nonlinear subdivision is not a truncation controller.
The scope excludes general cyclic/reversal paths and FE host/tangent use.

## independent_numerical_evidence

The prospective working plans freeze an independent Cartesian/principal
compliance reference with RK4, six regular residual fixtures (five branches
and one rotated residual), hydro analytical limits, and error gates. I read
the branch/residual and finite-path reference design and replayed the
six-reference fixture check against the exact model. The retained prior
separate reviewer adds 25 successful checks including regular derivatives,
Mandel covariance and the critical plastic-volume limit. The six original
BE refinement gates independently replay from saved arrays at 32/64/128
caller steps against 256/512/1024 RK4 references, with finest errors about
`1.06e-5–1.07e-3` scaled. This is finite strain-path evidence for those
diagnostics, not six source-matched experiments.

The new [principal-value audit](audit.py) uses Table 1 projection, the
harmonic mean and direct derivatives of the principal invariants, followed by
source compliance and branch checks; it does not use the Atlas interpreter
or the working reference to reconstruct the laboratory equations. Each
recorded step in the ten current runs has one accepted substep. The maximum
endpoint source residual is `2.2471e-10` on the existing `2e-8` fixture
scale; the maximum auxiliary square error is `4.4591e-12`. The isotropic NC
pressure follows the independently derived BE recurrence
`p_j=p_(j-1)/(1-Delta eps_v/Cc)` to `9.78e-10` relative to reference
pressure. The minimum endpoint scaled hardening modulus is `24.1898`; the
observed hydrostatic branch tie does not demonstrate nontrivial transition
coverage. Maximum intercept drift from finite BE is `4.3422e-4` on
the zero-volume path. Drift and the source checks are retained in
[audit-results.json](audit-results.json).

## backend_delivery

The isolated current Debug native runner and Release Wasm C ABI each
returned five 101-point trajectories. I verified the thirteen raw capture
digests, bound runtime files and checked each trajectory's controls, full
state and channels against the historical physical replay gates. The worst
lab replay error is `8.71375e-10` versus the unchanged `1e-8` rule.
I independently replayed the 1,383 current saved Wasm material responses
against original native requests/states: all 22,128 state values pass
(worst scaled `1.57795e-11`) and three failed calls preserve the exact
parent. The current Wasm runner also reported all six residual fixtures
pass. Current comparison is backend/engine reproduction; the independent
source checks above are separate. A distinct drained-only replay used the definition's adjacent binary64
auxiliary value `.5773502691896258` on all three normal components.
Current native and current Wasm exact controls each returned 101 points;
both reproduce the saved physical trajectory to `7.004e-15` and the
source endpoint equations to `1.943e-10`. The checked Wasm wire uses the
scope-aware response and preserves the exact controls, generated by rounding
`target*i` to binary64 and then rounding the division by 100. Its response
contract reports `experimental-laboratory-scope-0.1`. This was an isolated
engine/wire exercise. The standard packaged browser and deployment are
excluded until E6–E8.

## applicability_claims

All five approved examples use the exact initial and parameter vectors above,
100 steps, zero cycles, and integration settings
`2e-10,1e-6,45,14,20000,11`. They are one-dimensional strain (oedometric,
zero radial strain), drained (fixed radial effective stress), zero-volume
triaxial (called undrained by the host), zero-volume signed deviator stress
control, and isotropic compression. The target is 1% axial strain (1% in
each normal direction for isotropic) except for the 5 kPa signed deviator
stress target. The source is the parameter reference; these paths are
project illustrations, not reproduced source protocols or specimens.
The ordinary drained default may use the adjacent auxiliary literal above with the same physical input, settings and monotonic 100-step controls. This allowance is drained-only.
Public controls need to preserve the qualified request and label overrides
as unqualified; an arbitrary parameter/initial-state setting is not a Table 2
specimen. Do not infer sustained softening, large strain, noncoaxial
anisotropy, structured soil, broad cyclic behavior, coupled pressure
evolution, physical time, finite spin, or experimental validation.
In the paper itself, the authors report underpredicted OC extension strength
and dilatancy (p63), possible overprediction of one-direction cyclic strains
(p64), and the omissions of structure, noncoaxiality and time/age effects
(p68). No match to measurements is claimed.

## reproducibility_rights

Replay with NumPy and Python 3 from the repository root:

```sh
python3 -B docs/ingestion/matsuoka-nakai/working-v1/check_reference.py
python3 -B docs/ingestion/matsuoka-nakai/e5-v1/audit.py CURRENT_CAPTURE_DIRECTORY
```

The second command verifies the 52 current evidence hashes, original
compressed and prospective receipts, exact v0.3 model, and all thirteen raw
capture hashes and checks, and reproduces `audit-results.json`. The raw
names, hashes and sizes are in [current-raw-receipt.json](current-raw-receipt.json).
At review they remain under coordinator ownership at
`/private/tmp/atlas-nh2004-current.mVzEBx`; the coordinator should keep a
single ignored local copy before removing any unique originals and document
its location. I verified all five generated/runtime hashes in that directory
and the runner fingerprint stamp. The retained source/closure/binary receipts
identify the toolchains, frozen input and current engine. No new archive is
needed. The private original PDF stays in the ignored source location
listed in the recovery receipt; its redistribution rights were not
established. The raw responses are synthetic software output and contain
no paper measurements or source images.

Retained historical/current failures: the first Wasm link cache lock,
initial checker field mismatch, and one-ULP auxiliary difference in the
first runner invocation remain separate. The historical static working
verifier flags runner drift, the old source verifier flags schema drift,
and the prior review verifier flags current AGENTS policy drift.
The exact prior files are recoverable from existing archive maps; seven prior
review files and 60 current-or-archived review inputs were verified, with
one mutable board context drift and the exact PDF recovered at the new
private location. Nineteen old private renders/skill snapshots were not
replayed. The review's initial audit harness used exact isotropic/radial
stress equality; the maximum radial split observed was `4.37e-11 Pa`
and shear remained zero. The harness now checks radial symmetry using the
existing operational stress/strain tolerances, reports the hydro recurrence
error diagnostically, and leaves the original acceptance gates untouched. The supplementary wire
harness initially assumed a one-rounding ramp and equal request/response
loading envelopes; it was corrected to the existing two-operation producer
and scope-aware response contract without changing captures or tolerances.
No historical or current owner artifact was edited.

The reviewer removed only their own temporary page renders and the
disposable, byte-verified duplicate of the raw capture files. No preview
process, build directory or worktree was created. The raw captures, private
source and current build directory remain with the coordinator.
