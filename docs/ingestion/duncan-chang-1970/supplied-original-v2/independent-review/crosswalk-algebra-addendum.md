# Addendum: supplied-source packet and corrected algebra checker

Reviewer `/root/duncan_supplied_review`, 2026-11-01. Scope: independently inspect the coordinator's `supplied-original-v2/README.md`, corrected `check_algebra.py`, and retained initial failure narrative before E1/E2 packet integration. This adds to the source-gate review; it does not approve an executable model or close E1.

## Result

The reviewed packet faithfully distinguishes the original 1970 constant-Poisson incremental closure from later variants. Its equations, parameter table, engineering/Mandel shear mapping, maximum-stress-difference history and explicit source/algorithm gaps agree with the original pages inspected in the first review. It expressly keeps missing printed 1647 and the erratum unresolved and does not substitute the proposed pre-failure domain for complete original-law delivery. No blocking discrepancy was found in this bounded packet/checker review.

The corrected checker independently reran successfully:

```sh
python3 -B docs/ingestion/duncan-chang-1970/supplied-original-v2/check_algebra.py
```

Observed result: pass, 363 exact rational assertions; `constitutive_algorithm_qualified: false`, `compiled_calls: 0`.

The shear correction is required, not a tolerance adjustment. Source Eq.15d-f gives engineering shear `gamma = 2(1+nu) tau/E`. Since `epsilon_M = gamma/sqrt(2)` and `sigma_M = sqrt(2) tau`, the Mandel compliance is `(1+nu)/E = 1/(2G)`. Therefore the common isotropic Mandel stiffness `2G` recovers the incoming Mandel shear stress. The retained original checker used twice that compliance and recovered twice the expected shear stress. The corrected six-component inverse checks recover all normal and shear inputs exactly for three moduli and three Poisson ratios, including 0.48. The scalar hydrostatic identity in the checker is the volumetric compliance under unit stress in each normal direction.

The quotient-rule derivative `a/(a+b*epsilon)^2` and the stress-only tangent agree exactly after `Ei=1/a`, `Dult=1/b`, `Df=Rf*Dult`. The inverse and transformed-line checks are valid on their mathematical branch. The changing-confinement counterexample correctly separates historical `D` from `S`; `D` decreases from 4 to 3 while `S` increases from 1/2 to 3/4.

## Limits and next action

- Some hyperbola sweep points exceed physical failure `D= Df` while remaining below the mathematical asymptote. For example `a=1/4480`, `b=1/16`, `epsilon=1/5`, `Rf=0.91` has `D>Df`. These are algebra identities, not demonstrated postfailure material behavior or exclusively pre-failure numerical coverage.
- The checker does not independently test the confinement power law, Mohr-Coulomb angle/unit conversion, an executable history/event algorithm, changing-confinement quadrature, finite-strain behavior, experimental observations or a backend.
- The printed Eq.15 is a full tensor compliance approximation. Its presence does not remove the packet's explicitly acknowledged noncoaxial averaging/branch ambiguities or establish general-3D scientific accuracy.
- This review did not inspect or bind `receipt.json`, `crosswalk.json` or saved `check-results.json`, which were still being authored when the bounded followup was dispatched. Their existence/content must be checked by the coordinator before packet integration.

The packet/checker may be integrated as bounded E1/E2 progress with these limitations, preserving the failed checker and existing source blockers. The smallest source action remains acquisition of printed 1647 and erratum 1597, followed by correction reconciliation. Exact finite-step/reference decisions and a later independent E5 review are still required before model approval.
