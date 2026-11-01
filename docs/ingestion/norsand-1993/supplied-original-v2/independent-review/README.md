# Independent original-source and contract review v2

Reviewer: actual separate agent `/root/norsand_original_review`, 2026-11-01.
Task: REVIEW-norsand-original-v2. Exclusive output: this directory. The reviewer
did not author the parent's source transcription or execute the Atlas model.
This is a source/contract review, **not E5 model approval**. No executable
definition, backend qualification, experimental replication or live delivery is
accepted by this record.

## Source read

Privately retained source:
`.local/private-sources/norsand-1993/supplied-original-v2/NorSandGeot1993.pdf`,
SHA-256 `fee99108e493f34eb987c759eddf73cfc86e77102c73e42d099c00f1209851b9`.
The reviewer independently inspected every rendered page, original pp91–103,
including all equations, assumptions, notation and figure captions. Readable
original acquisition is no longer blocked. The PDF and page images remain
private; the paper does not supply general redistribution permission.

## Findings against the original

1. Equation7a exponent is `N/(1-N)` on `p/pi`. Equation10a exponent is
   `(N-1)/N` on `(1-N*eta/M)/(1-N)`. Equation11a has the same negative
   exponent `(N-1)/N` on `1+3.5*psi_i*N/M`. Each requires a distinct exact
   `N=0` logarithmic/exponential branch. Reversing an exponent changes the law.
2. Equation5b prints `log p`, whereas Equation9 explicitly uses `ln(pi/p)`.
   The p102 notation defines both Gamma and lambda_c in `e-ln p` space.
   Thus natural-log interpretation is supported internally; retain the printed
   difference, and introduce a stated pressure reference when normalizing to SI.
   Gamma must change when that reference changes.
3. Equations3/9 use current void ratio and the current image pressure. The
   generalized function `g(psi_i)` on p94, the current-image wording on p97 and
   summary on p98 support evaluating Equation11 with current image `psi_i`.
   Solving an additional limiting-image state before Equation12 is not stated.
   Recompute the moving limit from current state; a permanently frozen limit
   does not reproduce the stated hardening/softening concept.
4. Equation12 is `dpi/deps_q=h*(pi_max-pi)`. Dots denote incremental change
   (p102), and the p92 shear rate is arbitrary. This is rate independent; no
   physical seconds or relaxation time is established. The p98 forward-difference
   method with consistency at each step is stated, but detailed step size,
   tolerances, exact lagging and discrete event handling are not.
5. The source assumptions are drained rigid-plastic, axisymmetric conventional
   triaxial, effective stress, normality and stress/strain-increment coaxiality
   (p92). Its p102 invariants are `p=(sigma1+2*sigma3)/3`,
   `q=sigma1-sigma3`, `eps_v=eps1+2*eps3`,
   `eps_q=(2/3)*(eps1-eps3)`. They are work conjugate. A general Mandel 3D
   extension, Lode dependence, finite spin, elastic modulus and cyclic reversal
   closure are not supplied by this original.
6. Standard incompressible-grain/current-volume differential kinematics gives
   `de=-(1+e)*deps_v`. It is a reasonable explicitly labelled reconstruction;
   it is not a printed evolution equation or a paper-specified finite nominal
   strain update. Do not silently substitute one finite-step strain convention.
7. Normally consolidated isotropic initialization gives Equation10 with eta=0;
   for N=.2, pi/p=.4096, consistent with the rounded .41 on p98. An
   overconsolidated state inside the yield surface cannot generally infer its
   independent image/history pressure from an on-yield inversion. R is distinct
   from density/state (pp92–94). Source unloading-zone and elasticity discussion
   does not provide a complete unloading/reversal integration rule.
8. Source examples are useful parameter evidence, not unrestricted ranges or
   exact reference curves. Figure7 lambda_c=.0185, Figure8=.022;
   Figures11/12 lambda_c=.0135. D667 has e0=.590,p0=130kPa,psi0=-.161;
   D684 has e0=.820,p0=200kPa,psi0=+.075. These rounded values allow a rounded
   Gamma reconstruction with a chosen pressure reference, not exact calibration.
   Figure9 h=25,50,100,200 and the fitted h=280 are examples. The source itself
   discloses volumetric overprediction and peak-strain underprediction (p101).
   Post-peak calculated strain concerns the intense shearing zone, not the
   specimen nominal response (pp98–99). No data digitization or experimental
   agreement has been performed in this review.

## Current profile fit

The v0.3 contract allows strain-path residual/rate inputs consisting exactly
of a complete symmetric strain increment; physical-time ODE instead requires
time and a complete symmetric strain rate. Axisymmetric restriction exists
only on that ODE profile. The original active flow law constrains
`deps_v/deps_q=(M-eta)/(1-N)`. In a conventional constant-cell test this ratio
is an output coupled to the stress state, rather than an independently fixed
six-component input. Merely declaring a cell pressure symbol does not give the
schema/evaluator/host a mixed-control meaning. Adding finite elasticity or later
3D/cyclic equations to accept arbitrary strains changes the assigned identity.

This is a bounded current-contract/control gap, not a mathematical impossibility
claim. A generic strain-path, axisymmetric mixed-control profile and protocol
adapter could expose the original equations without adding elasticity. A future
task must specify the dependent radial strain, prescribed strain coordinate and
stress control, supported initial active state, hold/unloading policy, transactions
and source-supported applicability, then qualify the generic route.

For example, with constant effective cell stress and independent positive
eps_q, write `r=pi/p`, `y=(p/pi)^(N/(1-N))`, and `rL=pi_max/p` from current
psi_i. Direct differentiation of Equation7 and consistency gives
`eta'=h*M*y*(3-eta)/(3-eta+M*y)*(rL/r-1)` (with y=1 for N=0),
where prime means d/deps_q. This derivation follows because
`deta/dln(r)=M*y` and `p'/p=eta'/(3-eta)`. It illustrates a possible
monotonic constant-cell protocol; it does not deliver the full engine/profile.

## Independent checks

From repository root:

```sh
python3 -B docs/ingestion/norsand-1993/supplied-original-v2/independent-review/check_source_algebra.py
```

The script imports no Atlas implementation. Its declared tolerances precede
execution. Sixteen yield/inversion checks, sixteen central-difference
yield-normal checks, twelve limiting-flow checks, normally consolidated image
pressure and triaxial work conjugacy pass. Exact results and source/script hashes
are in [algebra-results.json](algebra-results.json). This verifies algebraic
relationships over selected points; it does not qualify numerical trajectories,
zero/hold uniqueness, reversal, full domain, native/Wasm or browser behavior.

## Parent packet review and decision

**Accepted for source transcription and bounded contract-gap reporting only.**
No unresolved blocking source-fidelity finding remains in the reviewed bundle.
The acquired and fully read original supports completing E1. E2 remains open on
NS-HOST-01 and NS-NUM-01; there is no candidate for E3–E8 or E5 approval.

The reviewer read the parent's README, receipt, crosswalk, prospective algebra
policy, algebra script/results, CAPABILITIES, packet checker/results and manifest.
CAPABILITIES correctly identifies the need to design a generic declarative
control contract and finite-step convention before qualification; its alternatives
include composing existing residual/controller machinery rather than asserting
that a new solver is mandatory. The requested future engineering handoff is
appropriate and does not require another human scientific approval.

The parent algebra script reproduced 425 checks at each of 70 and 110 Decimal
digits. The parent packet checker independently reproduced all eight public
file hashes, two retained schema/contract hashes, the exact private PDF hash and
13-page count, and exact replay of all 850 algebra checks. See
[parent-algebra-reproduction.json](parent-algebra-reproduction.json) and
[parent-packet-reproduction.json](parent-packet-reproduction.json). The reviewer
also ran the separately authored finite-difference checks described above.

Exact reviewed inputs and reviewer-owned outputs are bound in
[review-bindings.json](review-bindings.json). This decision accepts only those
bytes and this scope. The follow-on work is a separately owned generic
mixed-control/finite-kinematic contract task, followed by actual candidate,
reference, backend and browser qualification. Source algebra is not substitute
evidence for those gates.
