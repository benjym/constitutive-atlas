# Clay2014 controlled-resolution hydrostatic follow-up

This prospective protocol isolates the numerical mechanism found in the
[retained failed tolerance-refinement study](clay2014-midpoint-negative-diagnostic.md).
It does not amend that study, settle source discrepancies, or admit the model.
The protocol and independent references are frozen before any new compiled
observations. The factor1 baseline was already observed in the failed study;
factors2/4/8 are new observations when collected.

## Inputs and controlled resolution

Use only the published isotropic-ratio, zero-spin, no-IGS hydrostatic path of the
printed-Am/proposed-Eq49 research formulation. Keep the original17 parameters,
seven-state initial parent, fixed original stress scale, three physical segments
and seven original caller pieces per segment. Subdivide every actual binary64
caller piece by factors1,2,4,8. Because these factors are powers of two, every
subdivision is exactly representable. Fraction receipts prove exact loading sums
and identical physical endpoints; no decimal re-rounding repairs a path.

At unchanged rate tolerance1e-4, require each call to return exactly two half-step
fractions and zero rejected recursive steps. This gives14/28/56/112 effective
midpoint steps per original segment. There are21/42/84/168 calls,315 per backend.
Run each resolution from the original initial state, chaining every subsequent
request from the actual preceding result. Restarting from analytical targets is
prohibited. If the required mesh is not observed, retain a failed protocol
observation and report it; do not claim controlled-mesh convergence.

## Independent analytical reference

`tools/clay2014_controlled_reference.py` imports only standard-library utilities.
It does not import Atlas, a model interpreter, a rate oracle or an integrator.
It reads only the pinned historical inputs and confirms the model byte hash.
For specific volume w=1+e, positive compressive volume v and equivalent pressure
pe, the scalar source reduction gives w'=−wv, pe'=pe v/λ. With
y=(pe/p)^α, y'=−α(1/κ−1/λ)(y−sign(v))v/2. The generator solves these linear scalar
equations in closed form across signed loading pieces and samples the original
initial-value solution at every caller point. It computes the source exponent
independently from the source parameters using Decimal sine, logarithms and
square roots. No native result enters a target.

The90/140-digit results and their binary64 target rounding determine a separate
empirical uncertainty receipt. Precision differences are not certified error
bounds. Checks compare the new target with prior independent full-tensor RK4,
differentiate the closed form against a separately written scalar source RHS,
and verify exact volume and endpoint identity. These checks establish only this
restricted hydrostatic reference, not anisotropic behavior or physical validity.

## Frozen gates

The exact policy is in
[protocol-reference.json](../../catalogue/investigations/clay2014-controlled-resolution-v1/protocol-reference.json).
Every caller point must have stress Frobenius error≤1e-4 times the fixed original
stress norm and absolute void error≤5e-8. Each of the three physical endpoint
stress and void errors must contract by≤.35 at each successive resolution, with
an allowance of twice the sum of the fixed floor and the larger adjacent
reference uncertainty. Stress floor is5e-12 times the original stress norm;
void floor is5e-13. Keep error signs and each channel separate. References must
meet their declared precision limits before collection. Native/Wasm state and
actual-parent parity, when collected, uses the separate frozen scaled5e-11 bound.

Retain all requests, raw responses, descriptors, stderr/exit receipts, fractions,
full states and failed outcomes. Bind observations to this protocol hash and the
exact generator/model/solver artifact hashes. Run native and Wasm sequentially;
reuse exact previously receipted local artifacts only after verifying their
hashes. Any rebuild remains one target, one job. A future collector/assessor must
also be frozen before its compiled execution; this reference packet does not
assert that collection has happened.

## Current status and reproduction

Protocol/reference preparation is delivered; compiled collection and assessment
are pending. All scientific/public/experimental admission claims remain false.
Preserve the original failed experiment regardless of this follow-up's outcome.

From the repository, generate a fresh independent reference with
`python3 -B -m tools.clay2014_controlled_reference --output /private/tmp/new-controlled-reference.json`.
Run the seven pure-Python regression groups with
`python3 -B -m unittest discover -s tests -p test_clay2014_controlled_reference.py -v`.
Portable replay requires no native build or compiled execution.
