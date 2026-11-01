# power-creep-itasca900 — ingestion packet

Task ID: ING-power-creep-itasca900  
Owner / date: coordinating parent / 2026-11-01  
Scope: first source ingestion of the **two-component continuum Power Model in
Itasca Software 9.0**, with a proposed continuous, zero-spin host interpretation.
The manual equation inventory is complete for the inspected page. Two printed
inconsistencies and unspecified algorithm details prevent source-complete
executable transcription. No executable model is added.

## Identity and sources

The primary formulation is Itasca's [Power Model, 9.0 documentation](https://docs.itascacg.com/itasca900/common/models/power/doc/modelpower.html),
footer **9.0.182**, updated **12 November 2025**, accessed 1 November 2026.
It combines instantaneous isotropic elasticity with two stress-dependent creep
mechanisms. Its listed lineage is F. H. Norton, *Creep of Steel at High
Temperatures*, McGraw-Hill (1929). That book was **not acquired or inspected**;
this packet identifies the vendor's documented law, not the original 1929 text.
There is no DOI supplied for the manual. Power-Mohr, Power-Ubiquitous,
WIPP, Maxwell and Burgers are distinct laws, not interchangeable names.

Conventions were read in the same-version [Sign Conventions](https://docs.itascacg.com/itasca900/common/docproject/source/manual/program_guide/modelformulation/signconventions.html)
and [Notations](https://docs.itascacg.com/itasca900/common/docproject/source/manual/program_guide/modelformulation/notations.html).
All three sources have exact locators and receipt identity in
[source-receipts.json](source-receipts.json). Their titles and rendered mathematical
text were read, including Eqs. (1)–(7), regime examples and property notes.
These are HTML sources; no PDF was inspected.

Source storage is private:
`/private/tmp/atlas-power-creep-itasca900-sources-2026-11-01/web-source-response.json`.
The SHA-256 in the receipt identifies **the exact JSON serialization of the
web tool's extracted text**, not origin HTML. Direct Python retrieval first
failed DNS in the sandbox, then returned HTTP 403 with network access; no
origin-byte hash is claimed. Two initially guessed documentation URLs failed;
the corrected notation URL above succeeded. These failures are retained in
the receipt. Temporary storage is not a durable source archive. No redistribution
permission is asserted; full source text is not placed in this repository.

## Existing work and gaps

Before claiming this task, the live board, roadmap, research charter, status,
packet template, v0.3 schema and formulation contract were read. Existing
`docs/ingestion/`, `docs/models/` and the catalogue manifest had no named
power-creep ingestion. User Downloads filenames were inspected; no matching
source was identified. The [synthetic Maxwell fixture](../../../tests/fixtures/time/maxwell.json)
is engine verification, not literature ingestion. Concurrent Maxwell and
Burgers tasks remain separately owned. This packet adds no shared definition,
compiler capability, catalogue row, build or admission decision.

## Equations and schema crosswalk

Target: [schema v0.3](../../../schemas/model-v0.3.schema.json) and
[formulation contract](../../FORMULATION_CONTRACT.md).
[formulation-crosswalk.json](formulation-crosswalk.json) records
`schema_version: "0.3"`, the complete proposed `formulation`, source equation
ledger, state/parameter inventory and seven numbered gaps. It is a crosswalk,
**not a complete schema-valid model record**. No top-level `integration` is used.

Let `s = dev(sigma)`, `q = sqrt(3(s:s)/2)`, and `D` be the total symmetric strain
rate. Source signs are tension/extension positive. The source-to-Atlas conversion
negates **every** stress and strain-rate component, including shear. This leaves
`q` unchanged and reverses both sides of the tensor law. Under that conversion,
the proposed compression-positive continuous equations are:

\[
 f(q)=A_1q^{n_1}\mathbf1_{q\ge r_1}
       +A_2q^{n_2}\mathbf1_{q\le r_2},\qquad
 D^c=\frac{3f(q)}{2q}s\quad(q>0),
\]
\[
 \dot\sigma=K\,\operatorname{tr}(D)I
       +2G\operatorname{dev}(D)-\frac{3Gf(q)}q s.
\]

| Source locator | Quantity and mapping | Status / ambiguity |
| --- | --- | --- |
| Eq. (1), invariant definition | One-mechanism intensity `A*q^n`; `J2=(s:s)/2` | Time rate, not strain-path rate |
| Eq. (2) | Deviator increment `2G(dev(D)-Dc)*dt` | Continuous interpretation used above; discrete sampling not specified |
| Eq. (3) | Coaxial isochoric creep `3*f*s/(2*q)` | Undefined at `q=0` as printed |
| Eqs. (4), (6) | `trace(dot_sigma)=3K*trace(D)` | No volumetric creep |
| Eq. (5) and two definitions immediately below | Two inclusive threshold mechanisms | At a common threshold both terms activate |
| Eq. (7) | Printed deviator update uses `D` without `dev` | Conflicts with Eq. (2) for nonzero volumetric strain rate |
| Regime options 1–3 | Default, overlapping, separate mechanisms | Simplified regime descriptions do not resolve equality; reversed thresholds discouraged |
| Properties and final notes | `K,G` or `E,nu`; two `A,n,r` triplets | No numeric parameter defaults, calibration table or admissibility bounds supplied here |
| Sign page: direct stress/strain, strain rate | Tensor signs and symmetry | Convert to Atlas compression positive; no engineering-shear multiplier |
| Notations: dotted quantities | Derivative in physical time | SI seconds are the proposed Atlas time unit |

The independent elastic coordinates are `K,G` in Pa. Alternatively
`K=E/[3(1-2nu)]`, `G=E/[2(1+nu)]`; positive isotropic elasticity requires `E>0`
and `-1<nu<1/2`. These restrictions are physical choices, not printed vendor
bounds. Each `n_i` is dimensionless, `r_i` is a stress in Pa, and `A_i` has units
`Pa^(-n_i)/s` when SI is used. Changing stress or time units changes the numerical
value of `A_i`; it cannot be treated as dimensionless.

For a proposed dissipative, zero-stress-continuous scope use finite `K,G>0`,
`A_i>=0`, `n_i>0`, `0<=r1<=r2`. These are explicit **proposals**; no recommended
salt parameter set or universal material range was acquired. At `q=0`, the
vector creep limit is zero for positive exponents, even when the scalar direction
is undefined; adopting that limit requires review. For `n<=0`, no direction-
independent zero-stress extension is established. Finite mathematical values can
still overflow in binary arithmetic at large stresses/exponents.

One persistent six-component stress tensor is sufficient for future response
under this continuous law with fixed parameters; accumulated creep strain is
not needed in its right-hand side. If strain outputs are wanted, add their
persistent integrals explicitly and define restart semantics. There is no
fabric, density, hardening, temperature, damage or yield/plastic multiplier here.
No void-ratio bookkeeping is inferred. Initialize an explicit finite stress
tensor, time and current strain rate. Anisotropic initial stress immediately
relaxes during a zero-strain hold whenever a mechanism is active; it is not a
prepared equilibrium by virtue of initialization.

Source equations use Cartesian tensors. The proposed Atlas encoding is Mandel
`[xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz]`; tensor norms then equal Cartesian
double contractions. The source calls its deviator effective but gives no pore-pressure relation;
that phrase alone does not settle the total/effective stress split. The proposed
physical-time contract binds the Pa **observable** `stress=sigma` as
Cauchy/effective **only for an uncoupled zero-pore-pressure host**, where both
scopes coincide. This explicit host choice requires review before a model record
is created. No coupled stress conversion is inferred.
`small_strain_3d`, `fixed_spatial`, `objective_rate:none` are the **proposed host
restriction**, not a claim that every vendor large-strain mode has no rotation.
Finite spin/strain needs separate source and capability work.

## Temporal integration and transactions

The proposed profile is `physical_time/ode`, with stage inputs `time` (s) and
`strain_rate` (1/s), plus `start_time` and positive `duration`. Equal strain
increments applied over different durations generally produce different stresses.
No `de`, previous-state symbols or transient residual unknowns belong in this ODE.
The required state is `sigma`; no example values or preparation defaults are chosen.

The continuous interpretation evaluates stress-dependent creep at the current
integration stage. Eqs. (6)–(7) show finite increments but do not settle which
stress is used in Eq. (3), nonlinear iteration, predictor/corrector ordering,
lagging, stability control, transaction behavior or consistent tangent. A chosen
RK/implicit integrator would be a distinct project numerical choice. This packet
does not claim reproduction of vendor updates.

Zero applied strain rate permits deviatoric stress relaxation while mean stress
remains constant. Under imposed stress, creep continues and requires a mechanical
control solver to find compatible strain rate. Stress-free, positive-exponent
creep vanishes under the proposed limit; hydrostatic loading is elastic. No aging,
temperature dependence, parameter switching or internal reset event is supplied.

Switches depend on evolving stress. Generic time callbacks do not locate such
events. Review equality, crossing and restart behavior before selecting an
integrator. A full host must freeze a branch/event policy, stage loading sampling,
error scales and convergence criteria before observing results. Smooth-branch
Jacobian/directional derivatives may support implicit stress control; derivatives
can jump or fail at thresholds and at the origin for sublinear exponents. The
current v0.3 physical-time contract provides no full-update material tangent.

Atlas's proposed transaction contract is: every trial starts from the same
committed stress/time, acceptance commits the complete state, failure rolls back
all work, and repeated trials do not accumulate creep. These are project host
requirements, **unspecified in the inspected vendor source**, not verified vendor
semantics. No compiled transaction checks were run.

## Independent checks

[check_packet.py](check_packet.py) uses Cartesian arithmetic and analytical
solutions without Atlas equation evaluation or a vendor binary. Its only Atlas
import validates the formulation subsection against the current structural
schema. It does not validate this crosswalk as an executable material.
Tolerances were written before the first run and retained unchanged.

At fixed total strain with one active mechanism and no threshold crossing,
`qdot=-3GA*q^n`. The independently differentiated references are
`q=q0*exp(-3GA*t)` for `n=1` and
`q=[q0^(1-n)+(n-1)*3GA*t]^(1/(1-n))` otherwise. Checks cover `n=1,2,3` in their
positive solution interval. They test identities, not time-step accuracy.

The retained Eq. (7) witness sets `D=I`, `G=5`, and uses the fact that `Dc` is
traceless. Its printed deviator has trace increment `30*dt`, violating its
definition. The equality witness uses `q=r1=r2=2`, `A1=3`, `A2=5`, `n1=n2=1`:
literal Eq. (5) gives intensity **16**, not either isolated term **6** or **10**.
These are source findings to resolve, not failed assertions hidden by correction.

Reproduce from repository root:

```sh
python3 docs/ingestion/power-creep-itasca900/check_packet.py --verify-private
python3 docs/ingestion/power-creep-itasca900/check_packet.py
```

[check-results.json](check-results.json) retains **29 passing checks** including
the two source-receipt checks, 27 passing checks without private storage.
Coverage includes threshold overlap/gap witnesses, elastic volume, isochoric
creep, `sigma:Dc=q*f>=0`, Mandel factors, simultaneous sign conversion, passive
rotation covariance, analytical holds, and normalization of variable-power units.
Rotation covariance is not finite-rotation objectivity. No finite-step material
integration, shared-engine parity, compiled build, benchmark fit or experiment
was run. Source download failures remain in the receipt.

## Handoff

Owned files: this README, `source-receipts.json`, `formulation-crosswalk.json`,
`check_packet.py`, `check-results.json`, and `manifest.json`. The only shared
change is this task's live-board row; unrelated changes are preserved.

The smallest next action is **a bounded source/definition decision on PC-01–03**:
deviator projection, inclusive threshold equality, and the positive-exponent
zero-stress extension. Do not silently repair the manual. Then review a dimensionally
fixed equivalent expression `b_i*(q/p_ref)^n_i`, where `b_i=A_i*p_ref^n_i` has
units `1/s`. Fixed-unit declarations cannot directly type a parameter whose
stress exponent varies with `n_i`; normalization avoids that issue if it is
explicitly bound and checked. A generic stress-event handling study (PC-05) is
separate from source ingestion. No model-specific handwritten kernel is proposed.

Source completeness: inspected HTML inventory complete; original HTML bytes,
printed conflicts, vendor discretization and broader host dependencies unresolved.
Executable support: no new material record or integration.
Numerical verification: independent algebra/analytical identities only.
Scientific admission: unassessed; no independent signed review or experiment.
The board may close this bounded ingestion packet without closing those gates.
