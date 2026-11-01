# Independent OCC endpoint design review

Task `REVIEW-occ-control-selection-v1`, reviewer run `/root/occ_selection_review`, 1 November 2026. This reviewer did not author the proposed contract, historical packet/reference or implementation. Owned output is only this directory. No compiled artifact was built or called. This is a bounded E2 design review, **not E5 approval**, backend qualification, admission or experimental validation.

## Decision

**Accept the hash-bound contract as a complete declared invariant continuation plus strain-interface selection and finite discretization.** It resolves the earlier source-scope and mathematical-selection blockers without deleting source branches. It is not a literal transcription of a complete original 3D author algorithm. The contract clearly states that distinction, the selected electronic artifact, fixed-frame scope, first-order volume discretization, corner exception and discontinuous strain inverse.

The remaining binary64 and engine questions are implementation qualification gates. In particular, a nonzero distortion silently treated as a hold by norm underflow is a correctness failure and must not pass. Rejecting an unrepresentable update atomically is permissible under the declared representability/domain clause; silently returning the old stress is not. No generic primitive change is required by this mathematical review; a demonstrated numerical limitation may justify a separately scoped generic repair.

## Source and scope

Reviewed contract SHA-256: `d9bbb5f0b8c142e13687a3dbccf5e8576f825c2c96fb62a7f8479e58e177c38b`.

Private governing source SHA-256: `638e0ee7dc238ae8922b79983433be7d12ad30450098efe395968f7eeed13cb2`. This is the expressly selected 2005 electronic transcription attributed to Schofield/Wroth's 1968 work. First-edition facsimile fidelity is not established or required by this changed, explicit artifact identity. Prior source receipts and reviews remain intact.

Read prior `delivery-v1/independent-review/README.md` and `delivery-review-v1/contract-review-report.md`. Applied the PDF skill read-only: extracted complete printed pp101,114,216–218; visually inspected complete rendered pp101,114,217 at 1400-pixel scale. PDF page = printed page +11. Private extracts/render scratch reside at `/private/tmp/occ-selection-*` and are not redistributed.

Printed p114 explicitly links the generalization of Eq6.17 to the Mises construction subsequently introduced in Appendix C. Appendix C explicitly uses Granta-gravel packing, so the proposed contract correctly imports its invariant geometry and normality, not its pressure-history law. Combining that geometry with the Chapter6 OCC packing is a defensible source-derived continuation, provided the public name/scope retains that disclosure. This is materially stronger source support than treating Appendix C as wholly unrelated, but it still does not authenticate a complete original author implementation.

Printed p101 admits all normal directions between the axial limiting directions, including isotropic compression. The invariant convex normal cone extends this statement coherently: at the hydrostatic vertex its deviatoric norm is bounded by the summed multiplier. Appendix C10 supplies a limiting direction and would contradict p101 if enforced as a compulsory equality for every interior cone direction. The contract expressly selects the p101 cone and discloses the corner-power distinction. This preserves, rather than suppresses, the source hydrostatic branch.

## Independent mathematical assessment

1. The smooth flow uses `A=M*(1+x-c)` with the hardening coordinate held fixed when taking the plastic normal. Substitution of the endpoint packing relation makes this linear in x, with strictly positive coefficient in the volumetric balance. Thus there is one smooth root. If it lies beyond the hydrostatic intersection, the corner multiplier satisfies `L>=r`; no negative multiplier is concealed.
2. The finite equations are mutually compatible: `v-v_n=-v*E`, log-pressure recovery and endpoint plastic volume imply the stated packing increment. On an elastic step they preserve exactly `v-v_n=-kappa*(x-x_n)`. General finite volume is backward Euler, rather than the exact exponential volume update; this is disclosed and converges to the source volume differential law under refinement.
3. The full signed axial branches follow by reversing the deviatoric strain direction while leaving its norm unchanged. In arbitrary fixed-frame directions, setting the stress deviator parallel to D enforces the tensor flow relation, and its norm gives q. The scalar equations depend only on tensor invariants. Orthogonal rotations of stress and strain therefore commute with this update in real arithmetic; this does not confer finite-spin objectivity.
4. At r=0 the old stress projected on the admissible deviatoric ball is the unique minimum-distance selection. The radial projection follows from Cauchy–Schwarz: at a fixed admissible radius, distance to the old deviator is smallest in its direction; the closest radius is the old radius clipped at the admissible bound. This is a valid disclosed selection of the source relation, not source-derived shear elasticity. The hydrostatic compression corner remains active when elastic recovery would leave the admissible domain.
5. At exact zero increment, an admissible state is a solution with L=0 and unchanged stress/v. The separate exact identity requirement is appropriate. For arbitrarily small nonzero distortion, the selected stress can jump to yield or reverse direction. The proposed `incremental_residual` profile and warnings against assuming a smooth inverse are consequently essential. Treating this as an ordinary `strain_path_rate` would be wrong.
6. Critical undrained flow is an exact endpoint mechanism: v constant, `x=(Gamma-v)/lambda`, `q=M*p`, any positive r with fixed direction. Dry-side packing softening is retained. Stress q itself need not decrease on every dry-side undrained step, so qualification must test source packing/flow and avoid imposing an unsupported universal declining-q condition.

No source-law gap remains within this declared fixed-frame strain-controlled continuation. Stress/mixed-control qualification can remain a separate exposed-control gate. No unsupported promise of unique equilibrium or finite-rotation transport is needed to accept this specific formulation.

## Reproduction

Run from the repository root:

```sh
python3 -B docs/ingestion/original-cam-clay/control-selection-v1/independent-review/check_constraints.py
```

`check_constraints.py` imports neither the candidate nor production interpreter. Its oracle locates the hydrostatic intersection by bisection of packing/yield, then locates the smooth solution by bisection of the uneliminated volumetric flow balance, or uses exact source elastic recovery. The proposed elimination is evaluated separately and compared to that oracle. Decimal precision90 and absolute tolerance `1e-65` were fixed before the run; bisection uses300 iterations. Pressure is normalized by `p_ref=1` in this algebra study.

All400 combinations passed: four incoming log pressures, four overconsolidation/yield gaps, five positive/negative/zero volumetric increments and five distortion magnitudes including zero and `1e-40`. The study directly verifies volume balance, flow, packing, yield admissibility, complementarity and corner cone inequality, plus critical mechanism and a specific dry-side declining-q case. Direction reconstruction and projection uniqueness are independently proved above; this scalar study does not claim to have run backend tensor derivatives or controls.

One initial reviewer assertion failed and is retained in the JSON/report: it assumed q must decline on an undrained dry-side step at initial gap2. Packing softened but q did not decline. The unsupported assertion was replaced by an explicitly different test at gap1.1; the oracle, equations,400-case grid and tolerance were unchanged. This is a corrected reviewer expectation, not a changed acceptance policy for a compiled result. No compiled results were observed.

## Numerical qualification conditions

The retained tiny-distortion witness is decisive. Let `p_n=50000 Pa`, `pc_n=100000 Pa`, `q_n=0`, choose v by OCC packing, and prescribe one Mandel shear component `1e-200`, zero other components. E=0 and r is mathematically positive. The real endpoint tends to the positive capacity `M*p_n*ln(pc_n/p_n)=41588.830833596716 Pa` as r decreases. Binary64 `sqrt(tiny*tiny)` returns zero. An identity branch based on this norm returns q=0: a finite stress error despite the tiny input. Exact componentwise nonzero classification alone is insufficient if the subsequent direction calculation still divides by an underflowed norm. A scale-safe norm/direction or explicit atomic numerical failure is required. The contract does not permit silently restricting source branches to avoid this witness.

The prospective backend qualification must also exercise cancellation near the corner and critical state, pure hydrostatic input with inexact deviator extraction, very small holds/restarts, norm overflow, pressure/log/packing representability, invalid initialization and transaction rollback. These are bounded implementation risks already named by the contract, not newly invented constitutive requirements. The present acceptance does not claim that the existing residual engine, adaptive error estimator, controllers or browser has passed them.

The smallest next action is to run the separately owned prototype against these finite constraints and the parent’s frozen source-path study, then transcribe/qualify the candidate only after its numerical outcomes are supported. Preserve this review's input hash if the contract changes; a changed contract is a new review input.
