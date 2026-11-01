# Prospective constrained-law capability requirements

MODEL-original-cam-clay / E2; 1 November 2026. Design requirements only;
not a new schema profile, production model, acceptance waiver or build handoff.

Source identity and receipt: [checkpoint](README.md). Existing complete available
inventory: [historical packet](../README.md). Target remains model schema v0.3
and [the formulation contract](../../../FORMULATION_CONTRACT.md).

## Concrete relation and caller ambiguity

Use p>0, pc>0, signed axisymmetric q and
`f=abs(q)+M*p*ln(p/pc)<=0`. On an interior segment, packing is fixed,
`dv=-kappa*dp/p` and `d epsilon_s=0` (Chapter6.2/6.5).
At fixed p, constant q and any sufficiently small changing q which stays strictly
inside yield both admit zero strain and unchanged packing. All six Mandel strain
components can therefore be zero while the stress reaction differs. The six-input
strain increment alone does not specify the stress-controlled probe. Choosing to
retain q at zero strain is an additional host/selection convention, not an
inference from zero recoverable shear. Setting G=0 gives the opposite compliance;
finite G creates an augmented material.

At `q=0,p=pc`, the two smooth axisymmetric normal limits have `(f_p,f_q)=(M,+1)`
and `(M,-1)`. Their conic hull contains purely volumetric plastic flow. Selecting
one sign or differentiating abs at zero omits admissible source directions.
For a cone-interior direction, isotropic plastic compression has positive stress
work although net distortion is zero. The smooth Eq6.9/6.10 absolute-net-shear
dissipation equality therefore cannot be imposed unchanged on that direction.
Reconcile this corner extension and AppendixC10 limiting statement explicitly.
Stress-controlled corner distortion is not uniquely selected without additional
control/selection information. Critical-state stress control likewise admits a
mechanism. These are interface/solution-set issues, not proof that no loading
protocol has a well-defined solution.

## Contract decisions before production implementation

1. Declare a constrained constitutive relation and caller stress/strain controls
   in consistent work-conjugate coordinates, including which reaction variables
   are unknown. Decide the axisymmetric versus 3D formulation identity through
   source review before selecting storage or adding a profile.
2. Define admissible outcomes: unique solution, mechanism/nonunique solution,
   incompatible control and numerical failure. A numerical root finder returning
   one state cannot establish physical uniqueness. Define zero-input semantics
   separately from externally imposed constant-stress or changing-stress probes.
3. Preserve exact packing, bulk recovery, signed branches, source corner cone,
   critical hardening limit and dry-side softening. Define entry/unloading/reversal
   events and finite-step discretization without fabricating source algorithms.
4. Assess a constraint/active-set solve without requiring an invertible
   elastic shear stiffness. The current `cpp/include/atlas/solver.hpp`
   `implicit_step` forces plastic multipliers to zero in its predictor;
   `solve_linear` rejects near-zero pivots. A shear-rigid interior predictor can
   be underdetermined. Existing `increment_unknown` variables avoid that automatic
   predictor while retaining temporary-state semantics. First freeze a bounded
   current-residual experiment using the two signed axisymmetric branches and
   complementarity, with explicit initial/zero-input selection and corner policy.
   This is an experiment toward full delivery, not a replacement restricted model.
   Only a demonstrated semantic/algorithm gap justifies a generic runtime change;
   that change needs a separate task and regression policy. No handwritten
   model-specific production kernel is authorized.
5. Define immutable trial parents, atomic commit, exact full-state failure
   rollback, deterministic replay and preservation of externally prescribed
   control history across restart. Increment-local multipliers are not history.
6. Declare infinitesimal fixed-spatial, zero-spin, compression-positive effective
   stress and dimensionless strain-path evolution. Physical-time ODE or a scalar
   post-vertex reference is not a substitute for the complete constrained model.
7. The browser must expose the selected controls and distinguish mechanisms,
   unsupported requests and solver failures. Preserve complete stress/packing
   history, units, source identity and import/export provenance.

## Prospective verification allocation

Before any compiled observation, a separate implementation task must freeze
exact cases, reference identities, scaling and numerical tolerances for:

- Interior controlled stress probes with exactly zero distortion; two compatible
  distinct reactions for the same strain history demonstrate missing selection.
- Isotropic loading/unloading and source corner-cone inclusion; no arbitrary
  shear direction from the q=0 normal.
- Positive/negative smooth branches, entry/reversal, critical mechanism and
  dry-side/control-compatibility classifications.
- The existing positive-offset undrained analytical/refinement reference, with
  all state/packing components; this is reused without changing its old policy.
- Explicit full initialization consistency, domain and invalid control rejection,
  rollback/recovery/restart and useful source-backed illustrative protocols.
- Native/Wasm full-state/reference parity, all affected prior-model regressions,
  actual browser control/export/import/reset and identity checks.

This allocation is not yet a frozen numerical acceptance policy. It deliberately
does not assign tolerances to an unselected finite algorithm or count source-only
witnesses as compiled qualification. Separate independent approval follows the
completed candidate and retained numerical evidence, under checklist v1.
