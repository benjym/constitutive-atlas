# SANISAND: ordered production closure

ADMIT-sanisand-closure-v1, 1 November 2026. **Unsigned implementation and review
proposal; no model promotion.** The coordinating parent owns integration. An AI
analysis is not independent scientific admission. No reviewer is assigned here.

The next useful task is a **new v0.3, monotonic, fixed-memory research candidate
and independent finite-path reference**, after decisions D01–D06 below are
reviewed. This can establish a bounded implementation without pretending to
resolve the original model's missing reversal contract. A general cyclic
SANISAND-2004 production release remains blocked on D07. If a bounded monotonic
release is not useful, retain this as a research milestone and wait for D07.

This consolidates existing work rather than repeating source acquisition or
building another solver. The exact inputs are pinned in [inputs.json](inputs.json).
[decisions.json](decisions.json) records unsigned choices and dependencies;
[reference-plan.json](reference-plan.json) gives prospective case families and
acceptance sequencing. No candidate observations have selected these proposals.

## Source identity and what is already delivered

Dafalias and Manzari (2004), *Simple Plasticity Sand Model Accounting for Fabric
Change Effects*, Journal of Engineering Mechanics 130(6), 622–634,
[DOI](https://doi.org/10.1061/%28ASCE%290733-9399%282004%29130%3A6%28622%29),
is **received and inspected**. The user-supplied 13-page PDF in Downloads has
SHA-256 `b6e0f6ccfd018729a9bbd8492745af649c7682a8a1e929348ae25a728917e023`;
the [receipt](../../../../catalogue/source-audits/original-papers-2026-10-31.json)
records acquisition on 31 October 2026. Printed page = PDF page + 621. This pass
uses the retained transcription/audits; it does not claim new PDF inspection.
The PDF is private and is not redistributed.

The missing source is specifically Dafalias (1986), *Bounding Surface Plasticity.
I: Mathematical Foundation and Hypoplasticity*, 112(9), 966–987,
[DOI](https://doi.org/10.1061/%28ASCE%290733-9399%281986%29112%3A9%28966%29).
Its loading-process rules are referenced after 2004 Eq. (24), p. 631. The
[bounded access checkpoint](../../../reviews/sanisand-1986-access-v2/README.md)
found a login page, not a PDF. There is no 1986 full-text hash or equation review.
Resume acquisition only with a readable exact copy or a concrete new lead.

Completed evidence, which this task does not redo:

- [Original extraction](../../../models/sanisand-2004-original.md): source
  equations and Table 1; typed on-cone algebra with current-density elasticity.
- [Hardening products](../../../models/sanisand-2004-hardening-limit.md): a
  regular one-sided zero-distance limit, not a universal singularity remedy.
- [Elastic entry](../../../models/sanisand-2004-elastic-entry.md): exact
  continuous elastic path and first-yield bracket within its stated domain.
- [Fixed-memory residuals](../../../models/sanisand-2004-fixed-memory-be.md):
  26-component common-solver research implementation, monotonic native evidence
  and full-state late-failure rollback.
- [Parent-reset variant](../../../models/sanisand-2004-parent-reset-be.md):
  native cyclic and reset rollback evidence with a declared algorithmic guard;
  [mixed controls](../../../models/sanisand-2004-mixed-controls.md) add native
  radial-stress and prescribed-q tests. Neither is canonical reversal evidence.
- [Capacity analysis](../../../SANISAND_CAPABILITIES.md): 32-component bound,
  all state/control derivative columns and tensor square are available.

Some older dossiers still say the original paper was unavailable. Those are
historical statements at their inspection date, not the current access status.
The two existing research model records remain legacy v0.1 and are not migrated
or rewritten by this task.

## Decisions to sign before implementation

| ID | Recommended bounded choice | Why approval is still needed |
| --- | --- | --- |
| D01 | Target the 2004 continuous effective-stress law plus explicitly named project discretization, in fixed-frame small-strain 3D. Keep OpenSees as a distinct implementation variant. | Original law, numerical variant and complete source implementation have different identities. |
| D02 | Retain current `e` in Eq. (3); derive loading from the uneliminated stress/plastic relation; disclose the missing `K` in printed Eq. (20). | Independent equation review must accept the dimensional correction, or select a differently named interpretation. |
| D03 | Require explicit prepared `sigma,e,alpha,fabric,alpha_in`; no automatic stress/history generation. Use isotropic zero-history states only as declared verification hypotheses. | Table 1 constants and reported specimen densities do not establish arbitrary 3D history or preparation. |
| D04 | Retain finite-product backward-Euler residuals with `gamma=Delta_lambda*h`; verify the regular `d -> 0+`, `Hbar>0` branch. Reject unsupported simultaneous-zero/nonpositive-limit branches. | Existing continuous limit and sampled residual success do not prove general finite-step uniqueness or admissibility. |
| D05 | Freeze off-cone direction/centre handling, domain checks, complementarity, volume closure and finite-step solver policy as project choices. | Off-cone normalization and exponential void-ratio closure are not a numbered complete algorithm in the article. |
| D06 | First implement fixed memory and an explicit initial monotonic-use restriction; compare exact elastic entry and independent plastic references. | Successful reversed calls cannot be interpreted as valid original-model reversals. |
| D07 | Keep canonical reversal **unresolved** pending the exact 1986 mapping; alternatively approve a separately named parent-reset variant with its partition dependence disclosed. | The cone-normal denominator and parent trial-direction guard can have different signs. No tolerance or extra testing establishes their equivalence. |
| D08 | Freeze numerical budgets, precision, derivative branch policy and review scope before candidate execution. | A solver residual, refinement ratio or native/Wasm agreement alone is not an independent trajectory reference. |

For D01, OpenSees commit `8a0273db3e2f5a14c05924a179c1e439500c852c` is
already pinned in the [source audit](../../../../catalogue/source-audits/sanisand-2004-opensees.json).
It uses initial-density stiffness, residual pressure, floors, a finite hardening
guard, unit-dependent low-pressure dilatancy, special preparation/stage changes
and integration-specific fallbacks. None is imported into the proposed original-law
candidate. Its public return code and stored tangent are insufficient convergence
or transaction evidence; the [integration](../../../models/sanisand-2004-integration.md)
and [initialization](../../../models/sanisand-2004-initialization.md) audits remain
the comparison contract. Do not execute supplied author binaries.

## Initialization, singular branches and yield entry

The prepared persistent state has 25 scalar components: effective Cauchy stress
`sigma[6]` in Pa, current void ratio `e`, dimensionless deviatoric `alpha[6]`,
`fabric[6]` and loading-process anchor `alpha_in[6]`. `gamma` is one temporary
dimensionless plastic multiplier. An anisotropically prepared sample needs all
histories supplied or a reviewed preparation trajectory; setting them to zero
would erase preparation. An initial stress of `p I` and a supplied `e` describe a
prepared hypothetical state, not a simulated consolidation or calibrated sample.

For a bounded verification domain propose `p>0`, `0<e<2.97`, `1-ch*e>0`, finite
parameters, positive elastic moduli, deviatoric histories and initial yield
admissibility. The trace/yield tolerances must be frozen in D08. These are audit
bounds, not a complete physical calibration domain. Never repair an invalid
parent with a silent pressure floor or projection.

At an isotropic cone-centre parent the normal is undefined. Elasticity is
well-defined and histories should remain fixed until first yield. At yield,
`alpha_in=alpha` creates zero hardening distance. The regular continuous limit
has elastic instantaneous stress rate and finite outward backstress rate; setting
`Delta_lambda=0` before forming its product with `h` loses that rate. At `d=0`
require the reviewed positive-`Hbar` branch, not a universal assignment. Negative
distance, `Hbar<=0` at zero distance, and a zero loading denominator need explicit
rejection or a separately approved event/continuation rule.

The existing exact elastic locator assumes fixed histories and an entire valid
elastic predictor. It rejects if that predictor leaves its audit domain, even if
yield might have occurred earlier. It is an independent reference, not currently
a production event integrator. For the first residual candidate retain the
existing implicit update, measure yield-entry error against this oracle, and
require refinement. Only if exact first-yield splitting is a signed requirement
should a separate generic event contract be designed. Such a contract must define
domain-boundary versus yield priority, partial-interval restart, event state and
rollback. There is no demonstrated requirement for a new operator or capacity
extension now.

## v0.3 implementation crosswalk

A new record must declare `schema_version: "0.3"` and the complete formulation:
`strain_path` / `incremental_residual`, `small_strain_3d`, `fixed_spatial`,
`objective_rate: none`, Mandel representation, compression-positive stress and
strain, the exact `de` descriptor and empty `advance` from the current
[contract](../../../FORMULATION_CONTRACT.md). Bind effective Cauchy stress to
state `sigma`; declare explicit-state initialization with
`default_policy: examples_only` and required persistent fields in layout order.
There is no physical time, duration, creep claim, finite rotation or pore-pressure
input. An undrained test means a stated total-volume control here, not a coupled
pore-pressure analysis.

Assign `persistent` roles to the five history fields and `plastic_multiplier` to
`gamma`, with zero temporary initialization. Stress has `cauchy_stress` and
`symmetric_spatial_tensor` semantics; void ratio is a scalar invariant. Review the
physical tensor transformation of `alpha`, `fabric` and `alpha_in` explicitly
before declaring it; their component arrays are not arbitrary scalar histories.
Use descriptive quantities tied to the source, not guessed generic meanings.
No legacy top-level `integration`, `transient` or `multiplier` flags. The existing
v0.3 residual profile permits `increment_reset`; this removes a structural schema
obstacle but does not approve the parent-reset policy. Migration of existing
records belongs to its separate owner; stage a new candidate under a new identity.

## Ordered acceptance and smallest next task

1. Obtain a named reviewer and signed D01–D06/D08 scope. Leave D07 blocked unless
   its separate variant/source decision is actually made. No maintainer is
   assigned without agreement.
2. **REF-sanisand-monotonic-v1:** construct an independent Cartesian/multiprecision
   elastic-plus-plastic trajectory oracle for the signed fixed-memory scope.
   Freeze exact decimal inputs, preparation assumptions, event conventions,
   full-state sample grid and two-precision adequacy before any candidate run.
   Review the reference equations and assessor with deliberate corruptions.
3. **INT-sanisand-v03-monotonic-v1:** stage a new declarative v0.3 record, using
   existing finite-product residuals/common solver. Pin model, schema, compiler,
   solver and generation identities. Do not handwrite a SANISAND kernel.
4. **NUM-sanisand-monotonic-backends-v1:** coordinator builds serially, one explicit
   target and `--parallel 1`; run unchanged frozen accuracy, refinement,
   rejection/rollback and smooth-branch derivative gates in native/Wasm.
   Record all failures; never widen budgets after observing a failure.
5. **INT-sanisand-laboratory-v1:** only after passing the bounded backend study,
   test source links, explicit initialization, restart/import/export, loading
   restrictions and failed-request recovery in the real packaged browser API.
   A cyclic UI must not be offered for a monotonic-only claim.
6. Independent equation/numerical sign-off then pins a bounded release. Experimental
   validation requires separate source-matched preparation and data rights;
   figures or the Toyoura constants alone do not supply those. A general cyclic
   release waits for D07 and its nonproportional/nested-reversal matrix.

The exact numeric backend budgets are intentionally **not frozen by this planning
packet**: they depend on the reviewed reference and intended-use range. The
matrix is freezeable, not a claim to have frozen an acceptance policy. D08 must
resolve the explicitly enumerated budget fields before executing the candidate.
This prevents inventing a tolerance merely to declare an existing curve a pass.

## Local preflight and retained limits

Run `python3 -B docs/ingestion/sanisand-2004/production-closure-v1/preflight.py`.
It checks exact input pins, unsigned decisions, nonempty prospective coverage,
the v0.3 profile and state capacity, then derives 18 constant-volume first-yield
references using Decimal arithmetic at 80 and 120 digits. It imports no Atlas
model evaluator or compiled artifact. The analytical axial yield magnitude is
`p*m/(3*G)` for zero-history isotropic parents; extension uses its negative.
It also verifies that these selected entry states have positive `b0` and `Hbar`.
The three densities and pressures form a verification grid, not published test
reproductions. This small preflight is independent algebra, not a new full
plastic reference, scientific reviewer, production test pass or admission.

`preflight.json` retains the local result. No acquisition, author code execution,
build, compiled material run, shared file modification, commit, push or deployment
occurred in this task. Source completeness remains partial at the loading-process
contract; executable status remains the two existing research variants;
finite-path independent reference, full backend/browser acceptance and scientific
admission remain open.
