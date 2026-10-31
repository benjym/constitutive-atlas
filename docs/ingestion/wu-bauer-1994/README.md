# Wu-Bauer 1994: Appendix I and ingestion contract

Task: `SRC-wu-bauer-1994`. Owner: `ingest_wu_bauer`. Date: 2026-10-31.

This is an additive, bounded source packet for the four-coefficient law in Wei Wu and Erich Bauer, *A simple hypoplastic constitutive model for sand*, IJNAMG 18, 833-862 (1994), [DOI](https://doi.org/10.1002/nag.1610181203). It closes the assigned Appendix I inspection and records additional conflicts. It does **not** resolve those conflicts, select corrected equations, create a public formulation, or certify the full paper.

## Sources and existing work

The user-supplied private PDF matches the existing receipt exactly: SHA-256 `c8dfbc3cac0adc8bf3d273ec9e8a08ae9bff2273c696b354f1a4059c2f5bb050`, 1,606,948 bytes, 30 pages. See [source receipt](source-receipt.json) and [reviewed inputs](reviewed-inputs.json). Printed p.833 is PDF1. Appendix I starts on printed p.859/PDF27, gives all component formulas on p.860/PDF28, and defines its trace and norm on p.861/PDF29. Those three pages were rendered and visually inspected; raw PDF, text extraction and page images remain private.

The [prior dossier](../../models/wu-bauer-1994-original.md), [typed instantaneous fragment](../../../catalogue/source-audits/wu-bauer-1994-original.json), and its existing algebra tests remain unchanged. This packet does not rerun or replace their Cartesian/axisymmetric/rotation studies. Newly inspected Appendix I material is reconciled in [the component audit](appendix-reconciliation.md); [schema-contract.json](schema-contract.json) adds a bounded representation and temporal contract, rather than an executable model definition.

## Findings

- All six printed nonlinear `N` expressions agree with Eq.(21), after retaining the matrix equation's outer `-N` and each `N` expression's own minus sign.
- Two of the 21 displayed upper-triangle `L` expressions disagree with Eq.(21): `L15` and `L55`.
- The stated symmetry of the displayed 6x6 matrix is incompatible with its raw tensor shear input/output vectors. Raw normal/shear columns have different contraction weights. A weighted self-adjoint relation holds for the Eq.(21)-derived matrix; an ordinary symmetric matrix requires a declared orthonormal representation.
- The prior sign conflict, Eq.(28) calibration conflict and Eq.(33) real-domain failure remain. Exact witnesses extend the prior calibration diagnosis without adopting a converter. No authoritative correction was found in the limited publisher lookup; this is not proof that none exists.

## Equations and schema crosswalk

Let `T=tr(stress)`, `s=dev(stress)`, and `D` be the paper's stretching tensor. The inspected Eq.(21) law is

```
H = c1*T*D + c2*(stress:D)*stress/T
    + (c3*(stress @ stress) + c4*(s @ s))*norm(D)/T.
```

| Source locator | Quantity | Representation / units | Status |
| --- | --- | --- | --- |
| Eq.(21), p.840/PDF8 | Four constant coefficients `c1..c4` | Four scalar parameters, dimensionless | Printed coefficients remain distinct from a calibration converter |
| Eqs.(2)-(3), p.835/PDF3 | Cauchy stress and objective rate | Six symmetric stress states, Pa; Jaumann output, Pa/s | Source stress/stretch signs unresolved |
| Eq.(1), p.834/PDF2 | `D=sym(velocity gradient)` and skew spin `W` | Symmetric loading, 1/s; optional skew loading, 1/s | Ordinary stress rate requires explicit spin correction or declared zero spin |
| Eq.(22), p.840/PDF8 | Deviator | `dev(stress)`, Pa | Matrix square means Cartesian product |
| Appendix I, p.860-861/PDF28-29 | Trace `p` and stretching norm | `p=T`, **not mean pressure**; Frobenius norm | Raw shear order `12,13,23`; weights `1,1,1,2,2,2` |
| Eq.(21) and Appendix I | Linear/nonlinear operators | `trace`, `dot`, `norm`, `tensor_square`, scalar/symmetric arithmetic | Existing typed fragment covers body algebra; do not import conflicting Appendix matrix |
| Eqs.(25)-(32), p.842/PDF10 | Calibration relationships | Separate derived/calibration record | Inconsistent; blocked for canonical conversion |
| Eq.(33), p.843/PDF11 | Failure ratio to friction angle | Dimensionless arcsine argument | Printed argument outside real domain for `Rf>1` |
| Table II, p.843/PDF11 | Karlsruhe **medium** sand loose/dense sets | Constant four-coefficient records, `Dr=.10/.95` | Neither Wichtmann fine-sand calibration nor evolving density closure |
| Section 3.3.1, Eq.(34), p.846/PDF14 | Forward Euler stress update and radial control solve | Integrator/control metadata | Reproduction step size and precise control tolerances not established here |

The current source fragment uses Atlas Mandel order `(11,22,33,sqrt(2)12,sqrt(2)23,sqrt(2)13)`. Appendix raw order is `(11,22,33,12,13,23)`: both shear permutation and scaling must be explicit. Multiplying all raw shears by `sqrt(2)` without swapping the last two positions is wrong. Other coefficient sets and figures elsewhere in the paper are outside this bounded packet; full simulation/calibration inventory remains open.

## Temporal integration and transactions

This is a rate-independent nonlinear stress ODE, not a return map. Physical time can parameterize it, but positive reparameterization of the complete loading path introduces no material timescale (Eq.(4), p.835/PDF3). Reversal must use the actual signed `D`; its norm is even, so negative rescaling is not an odd extension of the full law.

At each stage evaluate the rate from that stage's stress and loading. For ordinary Cauchy stress, Eq.(3) implies `stress_dot = H - stress@W + W@stress`. Zero spin is an explicit restricted scope, unsuitable for claiming the paper's simple-shear reproduction. At nonzero trace, `D=0,W=0` gives an exact stationary stress state; `D=0,W!=0` is rigid rotation, not an ordinary-component hold. There is no creep/relaxation or independent density/history state in Eq.(21). No plastic multiplier, yield activation, history reset or saturation projection should be invented.

Trial/commit/rollback, adaptive tolerances, substep acceptance, diagnostics and event scheduling are unspecified in the inspected source. Atlas must define them as algorithm choices: clone the complete trial stress/control/clock state; commit only after accepted complete integration; reject undefined/nonfinite stages and restore all trial changes. Recompute mixed-control rates from the trial stress, rather than freezing the radial rate over arbitrary adaptive stages. Source Euler reproduction and an adaptive project integration must have separate algorithm identities and refinement evidence.

The loading tangent at `D!=0` is `dH = L[dD] + B*(D:dD)/norm(D)`, where `B=(c3*stress^2+c4*s^2)/T`. In Mandel coordinates this is an ordinary rank-one addition. In raw tensor coordinates use the contraction metric. It is generally nonunique at `D=0`. Appendix `L` alone is neither the complete loading Jacobian nor an integrated algorithmic tangent. Mixed controls need a nonlinear solve; this packet proves no existence, uniqueness or global convergence.

Finite inputs and nonzero `T` define only an algebraic domain. A physical stress cone, pressure floor, tension cutoff, stress-free start and robust near-zero-trace support are not supplied or selected. Initial stress, coefficient set, material/preparation identity, path and spin scope are mandatory declared study inputs. Density interpolation is not inferred.

## Independent checks

Run from any directory with Python's standard library:

```
python3 -B docs/ingestion/wu-bauer-1994/check_appendix.py
```

The script has no Atlas import. Exact `Fraction` Cartesian products and six tensor-unit loading bases check 200 deterministic stress cases: 7,200 linear-rate components, 1,200 nonlinear coefficients, 7,200 metric-symmetry entries and 200 norm identities. The generic witness retains precisely two upper-entry conflicts, with 19 of 21 entries agreeing. It also retains one raw normal/shear asymmetry witness, the four nonzero Eq.(25) residuals of literal Eqs.(26)-(29), and four invalid printed friction-angle arguments. [Results](check-results.json) are exact rational strings. “Pass” means the diagnostic reproduces these specified failures; it does not mean the printed appendix or converter passed.

No compiler, native/Wasm artifact, author code, finite integrator, shared interpreter or experimental dataset was executed. The checks establish component algebra within the declared source variables, not source signs or scientific validity.

## Handoff and smallest next action

The [manifest](manifest.json) lists exact owned files. The coordinator alone integrates and updates the live board. Source inspection within this task is complete; complete formulation/source-path reproduction remains incomplete. No executable support, numerical finite-path admission, scientific admission or public catalogue count changes.

Next: independent visual review of the two Appendix entries and sign/calibration observations, then explicitly select a **research variant** (e.g. Eq.(21) body law with separately declared operational signs and Table II constants) before generating reference trajectories. Resolve or retain a separately named conflict policy rather than silently correcting the appendix. A source-specific constant-confinement triaxial reference with a declared radial-rate branch and step refinement is the smallest subsequent numerical study. Canonical signs, authoritative corrections, physical domain/preparation, full simulation inventory, finite-spin coupling and scientific review remain gates.

Proposed shared capability: versioned per-equation ambiguity/variant provenance, declared objective-rate and shear-coordinate contracts, and nonsmooth loading tangent policy. No new model-specific kernel is proposed.
