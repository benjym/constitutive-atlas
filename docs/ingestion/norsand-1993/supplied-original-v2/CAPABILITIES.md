# Generic mixed-control requirement and finite-step handoff

`CAP-norsand-mixed-control-design-v1`, coordinator `/root`, 2026-11-01; depends on independent review of the [original-source contract](README.md). This document defines the source-derived implementation requirement. It does not authorize or perform shared schema/compiler/runtime edits while migration is separately owned.

## Requirement and minimal witness

Original1993 NorSand is a rigid-plastic associated axial law. It supplies flow, yield and hardening without elastic accommodation of arbitrary prescribed strain. Its useful conventional triaxial protocol fixes effective radial cell stress while axial/shear strain increases. The incremental v0.3 expression contract instead supplies all six Mandel strain increments under `small_strain_3d`; its physical-time ODE profile also supplies a complete strain rate, not an independent cell-stress control. The public laboratory mixed controller calls a strain-driven material update; its existence alone does not establish a well-defined rigid-plastic material map.

At `p0=c=130000Pa,q0=0,M=1.25,N=.2`, yield consistency requires `pi0=.4096*p0=53248Pa`. Source normality requires `deps_v/deps_q=25/16`. An imposed isochoric shear vector has ratio zero. Thus the source's active initial rate cannot simply consume arbitrary `de` without additional solution/branch behavior. Under fixed cell stress, the admissible radial strain is an output of flow instead. This witness establishes an interface/contract gap for the direct transcription; it does not prove that the common residual machinery cannot be extended or composed to solve it.

## Candidate generic capability, to be designed before implementation

1. A declared strain-path coordinate with explicit scalar progress and controlled stress/strain fields, distinct from physical time. Conventional `eps_q` and fixed cell pressure are the minimal example; any claimed support for changing cell/mean pressure needs an explicit prescribed history and interpolation.
2. A state/output binding that represents an axial effective Cauchy law without pretending to supply a general3D source closure. Keep signed `q=sigma1-sigma3`; a nonnegative general deviator norm cannot silently replace it on a reversal branch.
3. A normal material-independent evaluator that can advance coupled differential/algebraic relations and expose required mixed controls, or a reviewed composition of current generic residual/controller mechanisms with equivalent explicit semantics. No model-ID dispatch, handwritten NorSand production kernel, hidden ignored strain components or cell pressure stored as a material constant.
4. Explicit full state and control initialization. The active surface imposes Eq7; the normal-consolidation recipe is Eq10 at zero shear. Do not infer interior unloading response, apply an initial projection or import an elastic predictor absent from the source.
5. A finite volume/void-ratio convention. The local reconstruction `de=-(1+e)deps_v` is natural for incompressible solids and current-volume increments. A finite logarithmic-volume update and a finite engineering-volume update differ; select, label and review one before encoding it. This is a numerical/kinematic convention, not a new source equation.
6. Monotonic positive path progress and qualified zero-progress identity. Negative progress/reversal, invalid/overconsolidated state and unattainable controls must reject or use a separately sourced branch. A zero-duration physical-time hold is irrelevant; no physical relaxation is claimed.
7. Complete parent transaction/restart semantics, including coupled controller state. Failed trials restore all state/control history, and valid calls after rejection must recover. Step subdivision must preserve the selected control path and ordering.
8. Domain and tangent behavior for `N=0`, `N!=0`, `N=1` rejection, power-base boundaries, `p>0`, `q>=0`, `eta<3` on positive constant-cell compression, and finite precision near critical/zero-load states. Limiting stress ratio or denominator failures cannot be resolved by unreviewed floors or clipping.

The source-derived local constant-cell reduction in README.md is a small declarative-capability example and independent-reference starting point. It preserves Eq7, Eq6, Eq11 and Eq12. Neither local derivative agreement nor a specialized constant-cell analysis substitutes for support of the selected complete source formulation and its declared controls.

## Prospective qualification work, not yet an acceptance freeze

Once an actual generic contract is selected, freeze its exact candidate/model/toolchain identities, input corpus and fixed acceptance bounds before compiled observations. Include the exact `N=0` branch and multiple nonzero N values, normally consolidated and active nonzero-shear starts, dense/critical/loose states, useful explicit Gamma/reference preset and declared pressure ranges. Numerical paths must cover contract-supported constant-cell and any other claimed controls, loading progression, zero progress, expected rejections, recovery and checkpoint replay; do not add unsupported unloading to generate a pass.

Use separately constructed high-precision/source-derived references for every persistent field and accumulated strain, with dual-precision/refinement adequacy. Verify consistency, work-conjugate strains, limiting-flow identity, dimensional reference-pressure conversion, derivative behavior, partition/refinement and complete-state rollback. Native then Wasm builds require separate coordinator slot handoff, isolated directories, one explicit target per invocation and `--parallel 1`. Backend agreement does not replace source accuracy. Keep unchanged-model regressions, public preset, full scope disclosures, ordinary package generation and actual browser controls/import/export/failure recovery in E4–E7.

No exact finite-path corpus, tolerances or runtime studies are frozen here because the numerical contract has not been selected. Do not describe this checklist as passed qualification or E2 exit. Source algebra policy/results are a separate completed identity.

## Current handoff

E2 remains open on `NS-HOST-01` (supported generic mixed-control/path-coordinate profile) and `NS-NUM-01` (finite kinematics/discretization and transaction policy). Coordinator must assign a distinct shared-capability implementation/design owner and path whitelist, coordinated with current schema/compiler ownership; then obtain independent prospective review before changes/builds. This is an engineering dependency, not a request for human scientific approval. E3–E8 remain downstream; remote publication is not authorized by source receipt.
