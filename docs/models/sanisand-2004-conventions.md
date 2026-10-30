# SANISAND: pinned OpenSees conventions and selected source functions

This is an implementation-variant audit supporting SAN-01/02/06. It does not
establish the original 2004 equations or admit an executable Atlas model.
The [source inventory](../../catalogue/source-audits/sanisand-2004-opensees.json)
pins OpenSees revision `8a0273db3e2f5a14c05924a179c1e439500c852c`.
All locators below refer to
[`ManzariDafalias.cpp`](https://github.com/OpenSees/OpenSees/blob/8a0273db3e2f5a14c05924a179c1e439500c852c/SRC/material/nD/UWmaterials/ManzariDafalias.cpp),
except the explicitly named 3D wrapper. The full original paper remains uninspected.

## Boundary conventions

The source labels stress-like storage “contravariant” and engineering-strain
storage “covariant”; these labels describe its six-component convention, not a
general curvilinear-coordinate transform. Both order components as
`[xx, yy, zz, xy, yz, xz]`. Internal stress, backstress ratio and fabric store
physical tensor shear. Internal strains store twice physical tensor shear.
`DoubleDot2_2_Contr` therefore weights shear by two, `DoubleDot2_2_Cov` by one
half, and `DoubleDot2_2_Mixed` by one (lines 4811–4932).

Let `S = diag(1,1,1,sqrt(2),sqrt(2),sqrt(2))`, and let `u` be Pa per numeric
source pressure unit. The
[`ManzariDafalias3D` wrapper](https://github.com/OpenSees/OpenSees/blob/8a0273db3e2f5a14c05924a179c1e439500c852c/SRC/material/nD/UWmaterials/ManzariDafalias3D.cpp)
negates incoming strain (lines 78–85) and outgoing stress (119–123).
For external OpenSees values and Atlas compression-positive Mandel values:

| Quantity | OpenSees external → Atlas |
| --- | --- |
| Stress | `sigma_M = -u S sigma_external` |
| Strain | `epsilon_M = -S^-1 epsilon_engineering_external` |
| Tangent | `C_M = u S C_external S` |
| Internal dimensionless stress-like history | `a_M = S a_internal` |

The signs cancel in work and the tangent chain rule:
`sigma_M · epsilon_M = u sigma_external · epsilon_engineering_external`.
An isotropic source tangent has engineering shear diagonal `G`; Atlas has `2G`.
There is no sign reversal for internal backstress or fabric. These material-specific
conversions live in `atlas/opensees.py`; tests check all three shear planes,
Cartesian work, full nonsymmetric tangent action and invalid inputs.

`SingleDot(a,b)` returns `(AB+BA)/2` in symmetric tensor storage. It is not an
unsymmetric Cartesian product for arbitrary `A,B`. Its use for `n*n` and
`n*(n*n)` is valid because these factors commute.

## State functions actually selected

Here all tensors are Cartesian symmetric tensors, `:` is the full Frobenius
contraction, `I` is identity, and `a_in` is the supplied reversal backstress.
These formulas describe the pinned code, including its corrections.

Define `p_raw = tr(sigma)/3 + p_residual`, `s = sigma - tr(sigma) I/3`,
`p_residual = 0.01 P_atm`, and `p_min = 0.0001 P_atm` (initialization, lines
780 onwards). The yield function is
`f = ||s - p_raw alpha|| - sqrt(2/3) m p_raw` (`GetF`, 4467–4475).
`GetNormalToYield` (4629–4655) returns zero when `abs(p_raw)<1e-10`; otherwise
it divides `s-p_raw alpha` by its norm, substituting denominator one when the
norm is below `1e-10`. In that latter limit `n` can be small and nonunit.

`GetStateDependent` (4686–4754) uses `p = max(p_raw,1e-10)` for its pressure
functions, but calls the normal function with the unfloored pressure. It computes:

- `psi = e - e0 + lambda_c (p/P_atm)^ksi`.
- `cos3 = clip(sqrt(6) tr(n^3), -1, 1)` and
  `g = 2c / ((1+c)-(1-c)cos3)`.
- `aB = g Mc exp(-nb psi) - m`; `aD = g Mc exp(nd psi) - m`.
- `b = sqrt(2/3) aB n - alpha`; `d = sqrt(2/3) aD n - alpha`.
- `b0 = G0 h0 (1-ch e)/sqrt(p/P_atm)`.
- `h = b0 / ((alpha-alpha_in):n)`, replacing `h` by `1e10` when the absolute
  denominator is below `1e-10`. Away from that guard the denominator is signed.
- `A = A0 (1+max(fabric:n,0))`; `D = A (d:n) factor(p)`.
- `B = 1 + 1.5 (1-c) g cos3/c`; `C = 3 sqrt(1.5) (1-c) g/c`.
- `R = B n - C (n^2-I/3) + D I/3`.

`factor(p)` is one when `p >= 0.05 P_atm`; below that cutoff it is
`1/(1+exp(7.6349-7.2713 p))`. **The exponent uses raw numeric pressure**,
without normalization by `P_atm`. A physically identical low-pressure state
expressed in Pa versus kPa can therefore produce different dimensionless `D`.
Do not silently translate this into a unit-invariant original-paper law or
assume pressure-unit changes alone reproduce this implementation variant.
For the paired verification state with mean pressure `0.2 kPa` and
`P_atm=100 kPa`, the selected source returns `D=0.2237947600` with kPa numeric
inputs and `D=0.2989886053` with physically equivalent Pa inputs.

The four-argument `GetElasticModuli` (4542–4554) uses
`p_el=max(tr(sigma)/3,p_min)`, without residual pressure, and
`G = G0 P_atm (2.97-e_init)^2/(1+e_init) sqrt(p_el/P_atm)`.
It omits the square-root factor in elastic stage (`mElastFlag=0`).
`K=(2/3)(1+nu)/(1-2nu) G`. Its current void-ratio argument is unused;
elasticity depends on the initial void ratio. The total-strain void-ratio
update elsewhere in the source is `e=e_init-(1+e_init)tr(epsilon_total)`;
it must be reconciled separately with any proposed continuous evolution law.

At a singular zero normal, the formula for `R` still contains the `I/3` term
inside the tensor-square correction. Identities that assume unit deviatoric `n`,
such as `tr(R)=D`, must not be imposed on that branch without a separate policy.

The source also contains integration-specific behavior outside this probe.
In `ForwardEuler` (1214 onwards), a block-local declaration of `Vector r`
shadows the outer stress-ratio vector. The apparent intent and actual compiled
path must be reconciled before treating that branch as a constitutive reference.
The base `revertToLastCommit` is unimplemented. Neither point is covered by
selected-function agreement.

## Reproduction and interpretation

Supply unmodified files matching the inventory: `ManzariDafalias.cpp`,
`ManzariDafalias.h`, `ManzariDafalias3D.cpp`, and `COPYRIGHT`.

```sh
python3 tools/verify_sanisand_source.py \
  --reference-directory /path/to/private/reference \
  --output /tmp/sanisand-source-functions.json
python3 -m unittest discover -s tests -p 'test_opensees.py'
python3 -m unittest discover -s tests -p 'test_sanisand_source.py'
```

The tool first checks every immutable reference-file hash. It extracts 18 exact
methods, records their normalized-newline hashes and line ranges, and compiles
them in a private temporary directory. That translation unit retains the source
header and complete supplied copyright notice. It substitutes an Atlas-written
vector storage adapter and minimal class context; constants, identity, pressure
offsets and parameter values are supplied explicitly. Full OpenSees class
construction, linking, integration, memory transactions and tangent generation
are outside this execution scope. Nothing from the supplied source is vendored,
published with the website or inserted into the Atlas solver.

The independent oracle uses Cartesian 3×3 products and contractions rather than
Atlas DSL operations. Cases include compression, extension, all shear components,
rotations, random deviatoric history, elastic stage, current versus initial void
ratio, singular normal and hardening limits, signed hardening, pressure cutoff
neighbors, and paired Pa/kPa states. Tolerances are fixed in the tool before
execution. Every component and failure is retained; a unit-dependent low-pressure
response is recorded as an observed source issue, not a successful physical
invariance test. The documentation example supplies verification parameters,
not a Wichtmann calibration.

Selected-function agreement checks extraction and our interpretation of this
implementation. It does not validate its scientific equations, show complete
stress-path agreement, establish independent review, or close SAN-01/06.
The original-paper dossier, exact variant choice, initialization, full reference
integration and canonical declarative transcription remain required.
