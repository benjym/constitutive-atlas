# SANISAND source/scope decision

DEC-sanisand-source-scope-v1, 1 November 2026. **Retain the selected fixed-memory
variant as research evidence; park numerical expansion and public installation.**
This is a technical scope decision, not independent scientific admission. It
completes the queued decision task without completing ROADMAP M2/SAN-01–07.

## Original-paper crosscheck

The private supplied [Dafalias & Manzari (2004) paper](https://doi.org/10.1061/%28ASCE%290733-9399%282004%29130%3A6%28622%29)
was visually rechecked at printed pp626,628,631. PDF and retained render hashes
match the original receipt; see [source-reading.json](source-reading.json).
No copyrighted source bytes are added. This pass addresses the flow coefficients,
Table1 constant and memory dependency, not every equation or original simulation.

At p628, Eqs15–16 give `cos(3theta)=sqrt(6)*tr(n^3)` and
`g=2c/((1+c)-(1-c)*cos(3theta))`. Eqs18–19 give

```
Rdev = B*n - C*(n^2-I/3)
B = 1 + (3/2)*(1-c)/c*g*cos(3theta)
C = 3*sqrt(3/2)*(1-c)/c*g.
```

Here `n^2` is a matrix square. Because `tr(n)=0` and `tr(n^2)=1`, the
candidate's `dev(B*n-C*tensor_square(n))` is the same on-cone expression.
The independent Cartesian reference uses the displayed expression directly.
The inspected Table1, p626, has `c=0.712`. Thus neither a reversed C sign nor a
different c is supported by this targeted crosscheck.

For symmetric extension, `n=(-2,1,1)/sqrt(6)`, `cos(3theta)=-1`, and `g=c`.
The antisymmetric transverse flow derivative is

```
f = B - 2*C*n_yy = (9*c-7)/2 = -37/125 = -0.296.
```

It changes sign at `c=7/9`. This is an algebraic threshold for this derivative,
not a new source parameter restriction or a general constitutive stability bound.
On the exactly symmetric extension branch, however, `Rdev=n`: the c-dependent
terms cancel in the value. Thus agreement with a scalar triaxial reduction does
not establish behavior under transverse perturbations. The existing
[full linearization](../sanisand-transverse-extension-v1/DERIVATION.md) supplies
the stress/backstress saddle argument; the negative f alone is not the proof.

The source p631 Eq24 states the hardening denominator and refers loading-process
memory updates to Dafalias1986. It does not supply the missing full conjugacy and
finite-step event contract. This recheck does not resolve that separate gate.

## What the evidence supports

| Claim | Disposition |
| --- | --- |
| Selected 3D flow B/C/g/c transcription | Targeted original-paper match; no sign correction indicated |
| Strong transverse sensitivity of selected fixed-memory law | Supported by analytic linearization, derivative checks and separately identified diagnostic output audit |
| Every native error caused by transverse sensitivity | Unproven; three compression/general-shear fine accuracy failures also remain |
| Compiler implementation wrong | Not established: 39-state rotation/AD covariance and 135 independent selected derivative components pass, within their scopes |
| 81-path native qualification | Failed: 77/81 trajectory checks pass; four fine errors and refinement failures retained |
| Original continuous v1 audit | Failed: three original configurations hit minimum step |
| Rescaled v2 diagnostic | Three runs complete and original output gates pass; full frozen assessor still fails its additional reference-coordinate binding |
| Canonical cyclic SANISAND2004 or experimental validation | Not established |

The [native study](../sanisand-v03-monotonic-v1/README.md),
[continuous/discrete results](../sanisand-transverse-extension-v1/RESULTS.md) and
[rescaled diagnostic](../../references/sanisand-homogeneous-variation-v2/README.md)
remain distinct. Index-matched base differences do not cure the frozen v2 binding
failure. Infinitesimal gains do not predict infinite finite-amplitude stresses.
No sensitivity result proves a specific Newton root-selection mechanism.

## Decision and remaining gates

The explicitly named fixed-memory/zero-spin/small-strain research artifact is
defensible as a transparent implementation hypothesis and diagnostic corpus.
It is **not qualified for public general 3D use**. A compression-only or
symmetry-constrained replacement would evade the intended M2 proof. Keep the
full failed matrix; do not tune c, change signs, impose symmetry, raise precision
or remove failed paths to manufacture qualification. A future source-supported
variant would need a new identity and prospective acceptance study.

The [D01–D08 closure ledger](../../ingestion/sanisand-2004/production-closure-v1/README.md)
remains unsigned. In particular: current-density elasticity and printed Eq20's
missing K interpretation; prepared full history; off-cone/zero-distance branch
choices; finite-step uniqueness and numerical scope; and exact1986 loading-process
mapping remain distinct source/review questions. Available fixed-memory studies
cannot stand in for reversal, nested loading, mixed-volume entry or preparation.
Wasm, public catalogue/browser integration and independent scientific review
remain downstream of a qualified definition. Experimental comparison also needs
matched preparation, calibration/evaluation discipline and data reuse rights.

## Bounded follow-through

Park this numerical branch. Reopen source acquisition only with a readable exact
1986 copy or concrete new lead. A named independent review or genuinely new
source evidence can motivate a separately scoped correction/qualification;
this record assigns nobody and grants no signature. Do not repeat blocked routes
or launch a new refinement ladder. Other atlas ingestion/source closure can
continue under separately claimed tasks while these gates remain explicit.

[decision.json](decision.json) is the machine-readable disposition;
[inputs.json](inputs.json) pins the actual evidence. Run from the repository root:

```sh
python3 docs/reviews/sanisand-source-scope-v1/verify.py
```

Verification checks saved hashes, failure dispositions and exact rational
coefficient/cancellation identities. It neither integrates a model nor executes
compiled code. No engine/schema/model definition, public site, paper or historical
packet is changed by this decision. No push/deployment is performed.
