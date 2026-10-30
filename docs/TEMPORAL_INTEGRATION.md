# Physical time and temporal integration — design draft

Status: **design contract with an implemented experimental ODE subset**. See [the accepted ODE API and current limits](TIME_ODE_API.md). Recorded 30 October 2026 for roadmap TC-02/TC-03 and REP-03/NUM-03/NUM-04. This document defines requirements and implementation gates; it preserves v0.1 semantics and does not promote Terracotta to executable status. The separately versioned v0.2 ODE schema is implemented; the [component schedule/observable subset](TIMED_SCHEDULES.md) is also implemented. The broader invariant/constraint contract below remains proposed. Equation extraction (TC-01) and independent review remain open.

## 1. Decision and motivation

Separate three choices: **the constitutive formulation**, **the loading history**, and **the numerical integration method**. A physical-time model must be identified by its equations and dimensions, not by choosing an implicit solver. A rate-independent model can use an implicit method; a time-dependent model can use an explicit or implicit method where suitable.

Today `integration: "rate"` means the equations return state increments for a supplied strain increment `de`. The midpoint implementation integrates over a normalized path interval. Its equations have state units, not state/second units. `integration: "residual"` supplies incremental residuals. Neither v0.1 mode has a physical clock; physical-time execution now uses a separate v0.2 contract. Reinterpreting either existing mode as a derivative in seconds would change the five current formulations.

The [pinned Terracotta author README](https://github.com/MaxWiebicke/Terracotta-pq/blob/a4039d0124d8ff61e766f5201f44ddc163c4cff5/README.md) describes strain-rate loading in 1/s, stress-rate loading in kPa/s, multi-path histories, and timed relaxation/creep controls. It uses `scipy.solve_ivp`. These are requirements evidence, not evidence that the reference code and the [2024 journal formulation](https://doi.org/10.1016/j.jmps.2024.105789) are identical. See [the source brief](models/terracotta-2024.md).

### Baseline v0.1 gap audit (before the temporal extension)

| Location | Present behaviour | Required change |
| --- | --- | --- |
| `schemas/model.schema.json`, `atlas/model.py` | Version 0.1; declarations in `1`/`Pa`; first state is Mandel stress | Versioned time/equation contract and source-justified state/observable roles |
| `atlas/compiler.py`, `atlas/model.py::interpret` | Evaluators receive state, previous state and `de` | Typed temporal inputs with identical interpretation/code-generation semantics |
| `cpp/include/atlas/solver.hpp::midpoint` | Stage state changes, but there is no stage clock | Evaluate time, state and controls together |
| `advance_recursive`, `integrate` | Halve `de`; rollback state only | Partition time and controls; transactional state/clock result |
| `domain` | Calls the full equation evaluator with zero strain | Separate admissibility from evolution evaluation; initialization must not require a fictitious positive `dt` or divide by zero |
| `controlled_step`, `run_protocol` | One ramp/sine path; trial updates start from committed state | Ordered timed segments; trials share committed state/time; explicit hold constraints |
| `cpp/main.cpp`, `atlas/cli.py`, `web/worker.js` | Existing ABI/run fields contain no physical time | Versioned time-aware entry points and serialization, preserving old callers |

## 2. Mathematical and schema requirements

| Concern | Required meaning | Admission rule |
| --- | --- | --- |
| Time dependence | `rate_independent` or `physical_time` | Declared separately from equation form and integrator; do not infer it from the word `rate` |
| Equation form | Incremental residual, strain-path rate, physical-time ODE, or differential/algebraic system | Support only forms implemented by both interpreters and the shared engine; reject the others |
| Physical-time ODE | `dz/dt = f(z, D, t, parameters)`, with `D = dε/dt` | Each rate has its state's dimensions divided by seconds; `D` has units 1/s |
| Incremental residual | An explicitly discretized equation involving previous/current state and the time increment where applicable | Record its discretization; changing a run's solver cannot silently replace it |
| Algebraic quantities | Constraints or derived observables, rather than independent rates by default | Extract Terracotta's stress/energy relationships first; do not invent differential equations to fit today's stress-first layout |
| Physical units | SI dimensions with explicit conversion at import/export | Add time and derived dimensions; never treat kPa/s as Pa/s |
| Initial state | Admissible differential state plus consistent algebraic state | Validate at the initial physical time; a failed initialization produces no evolved state |
| Model scope | Original triaxial invariants or supported tensor kinematics | Time support does not supply the missing tensorial formulation |

Proposed names below are illustrative **v0.2 design syntax**, not accepted model fields:

```json
{
  "schema_version": "0.2-draft",
  "formulation": {
    "time_dependence": "physical_time",
    "equation_form": "ode"
  },
  "rate_equations": {
    "s": "2 * G * dev(strain_rate) - s / tau"
  }
}
```

This fragment illustrates a synthetic Maxwell deviatoric relaxation law, **not Terracotta**. For `s` in Pa, `G` in Pa and `tau` in seconds, the right-hand side is Pa/s. A full test definition needs its state/parameter declarations, domain and initialization. A residual formulation and any algebraic constraints need their own explicit contracts; they are not aliases for this field.

### Dimensions and expression inputs

- Keep rational SI dimension vectors. Support a bounded, validated representation for derived dimensions rather than adding an ad hoc list for every new coefficient. The spelling and serialization of that representation require a schema decision in TIME-01.
- At minimum, express seconds, 1/s, Pa/s and Pa·s, with dimensionally compatible state scales and tolerances. Determine Terracotta's remaining coefficient and internal-variable dimensions from TC-01. **Mesoscopic temperature must not be assumed to be thermodynamic temperature in kelvin.**
- Reserve `time`, `time_n`, `dt` and `strain_rate` as engine inputs when their equation form permits them. They cannot be redeclared as parameters, state or derived names. Physical-time rates see stage time and stage strain rate; incremental residuals see the committed start and trial endpoint times and the substep duration.
- In a physical-time ODE, previous committed state and total increment must not become hidden arguments to `f`: splitting a step must still represent the same ODE. Use explicit state for genuine memory. Keep `de` and previous-state symbols available only to equation forms that define their meaning.
- Validate dimensions separately for rate equations, residuals, constraints and observables. Do not normalize a dimensional error away using a numerical scale.

### Compatibility and versioning

Preserve all v0.1 definitions and their strain-path semantics. Accept physical-time fields only under a new, explicitly supported schema/expression version. The implemented ODE subset uses `schema_version: "0.2"`, `formulation` as shown above and `equations` for its typed rates; the illustrative `rate_equations` spelling is not accepted. Unknown versions and unsupported equation forms must fail clearly in Python, native and Wasm before integration. The parser rejects `0.2-draft`; do not loosen it merely to accept a proposal.

Migration must be explicit. For example, an existing homogeneous strain-path law may be rewritten using `strain_rate` and verified under a physical clock, but multiplying an arbitrary expression by `dt` is not a general migration. Preserve original source/model identities and record the representation migration. Separate model revision, schema version, expression version and engine version in run provenance.

## 3. Time belongs to the run and each material update

The initial clock is elapsed physical time, in seconds, with an explicit `start_time` (normally zero). Autonomous laws must give equivalent trajectories under a shift of that origin. Laws with explicit age dependence need a sourced initial age/state; do not reset age to zero when restarting a simulation.

The update contract is conceptually:

```text
advance(committed_state, step_context, control_path, parameters, solver_settings)
step_context = {start_time, duration}
result = {ok, committed_state, committed_time, diagnostics}
```

Both numbers must be finite; duration must be strictly positive and the endpoint representably later than the start. Initialization and diagnostic equation evaluation are separate operations, not zero-duration advances. Do not use a zero strain increment to mean zero elapsed time. Do not insert a fictitious one-second duration when an input omits time for a physical-time law.

On success, state and clock advance together. On failure, return the incoming state **and incoming time**. Numerical trial state, mixed-control trials and rejected stages never commit either. Retry integrator caches/history consistently; do not reuse a cache from a different trial trajectory. Diagnostic counts may include rejected work, but they cannot affect constitutive evolution. The integration clock belongs to the update context rather than a hidden extra constitutive state component; genuine material age or memory belongs to explicitly declared physical state.

### Substeps and stage evaluation

- Splitting `[t0, t1]` gives consecutive intervals with durations summing to the original duration. Every half step receives its actual start time. Partition physical time and evaluate the prescribed history on that interval; do not merely halve strain while retaining the original duration or rate.
- A stage-based ODE integrator evaluates state, time and controls at the **same stage**. For midpoint step doubling, the full and two-half solutions must span the same physical interval, with quarter/three-quarter evaluations on the half steps. Endpoint time must not be supplied at every stage.
- For a backward-Euler residual, the endpoint state/rate and `dt` refer to that trial interval. Any discretization error estimator must compare consistent intervals and states.
- Output sampling is separate from internal integration steps. An output request must not change the imposed history or redefine the physical loading rate. Dense output or interval splitting must have a documented policy.
- A restart includes committed time and complete persistent state. Any multistep solver history is either serialized with a version or explicitly reinitialized by a documented restart procedure.

## 4. Timed loading histories and boundary controls

Use ordered, finite-duration segments with named controls and units. Existing integer protocols can remain as v0.1 shorthand; do not overload `steps`, `target` or `cycles` to mean seconds. A cycle needs a period/frequency if a physical-time model is used. Internal substeps and output sample counts are numerical settings, not loading rates.

For the first timed driver, restrict execution to the reviewed axisymmetric controls. Full component-wise mixed control, arbitrary poromechanics and tensorial generalization remain separate capability gates.

| Segment/control | Prescribed condition | What can evolve |
| --- | --- | --- |
| Strain ramp | Endpoint strain and duration, or strain rate and duration | Stress and internal state |
| Stress ramp | Endpoint stress and duration, or stress rate and duration | Strain and internal state under a solved mixed boundary condition |
| Relaxation | Hold the declared strain components at their values at entry | Stress and internal state during positive elapsed time |
| Creep | Hold the declared stress components at their values at entry | Strain and internal state during positive elapsed time |
| Mixed hold | Declare held components and complementary boundary conditions | All unconstrained quantities consistent with those conditions |

An axial strain hold with free lateral deformation is different from holding all strain components. Holding signed `q` under zero volume change is different from holding all stresses. Specify the held components and drainage/volume constraints explicitly. Reference-code labels such as `creep` must be mapped to their actual equations and controls before claiming a matching protocol.

Require one unambiguous history parameterization per controlled quantity: endpoint plus duration, or rate plus duration. Do not accept conflicting rate, endpoint and duration inputs. Ramp endpoints are continuous at segment boundaries by default; a rate change is allowed. An instantaneous strain/stress jump is not a finite-rate ramp and is unsupported in the initial timed driver. Reject overconstrained or underdetermined controls.

Illustrative run fragment, also **not an accepted v0.1 run**:

```json
{
  "schema_version": "0.2-draft",
  "clock": {"unit": "s", "start_time": 0},
  "control_basis": "axisymmetric_small_strain",
  "segments": [
    {
      "id": "load",
      "duration": 10,
      "controls": {
        "axial_strain": {"kind": "rate", "value": 0.0001, "unit": "1/s"},
        "radial_effective_stress": {"kind": "hold"}
      }
    },
    {
      "id": "axial-hold",
      "duration": 100,
      "controls": {
        "axial_strain": {"kind": "hold"},
        "radial_effective_stress": {"kind": "hold"}
      }
    }
  ]
}
```

`hold` captures that control's value from the committed state at segment entry. The second segment is a mixed axial hold, not a claim of a fully constrained relaxation test. Resulting initial control values and absolute segment boundaries must be materialized in run provenance. A rate change starts a new segment; it does not reset internal state.

Integration must land exactly on each segment boundary (within a recorded floating-point boundary tolerance) without stepping across a control discontinuity. Specify one-sided stage evaluation at boundaries and avoid duplicate/zero-duration intervals. In the initial driver, start each segment using the new segment's controls and report the same continuous persistent state in both boundary records (incoming left and new-control right). Preserve one-sided observable values where needed: a rate-dependent viscous stress may jump at a prescribed rate change even when internal state remains continuous. See TC-A04 in [the source audit](models/terracotta-2024-source-audit.md). Constitutive reversal events remain a separate SANISAND requirement; a schedule boundary cannot stand in for internal event detection.

Recorded experiments must retain acquisition order and timestamps. Never sort cyclic or creep data by strain. Missing timestamps can still support strain-domain comparisons but cannot establish a physical loading rate or validate time-dependent behaviour without a separate sourced protocol.

## 5. Solver settings, errors and reproducibility

Keep numerical method selection in the run specification; the model declares required equation form/capabilities. Report an unsupported-method error rather than silently substituting a different scheme. A model's physics must not depend on the selected output sample count.

The current midpoint step-doubling implementation can be adapted for nonstiff physical-time ODEs after stage/clock semantics pass verification. It is not evidence of suitability for all Terracotta parameter regimes. Assess stiffness using the extracted law and reference cases. An implicit ODE method with error control may be necessary; a DAE solver must not be promised until the constraint structure and initialization are established. Newton convergence alone does not control temporal truncation error. Report nonlinear residual norm and estimated temporal error separately; the current single diagnostic `error` field cannot communicate both unambiguously.

Require explicit settings for relative tolerance, per-state absolute tolerances or documented state-scaled equivalents, minimum/maximum time step, initial-step policy, accepted/rejected-step budgets and nonlinear iteration limits. Tolerances must be positive, finite and dimensionally meaningful. Numerical failure must be reported without clipping a physical internal state into its domain. Include time-step refinement in acceptance, not only solver-to-solver agreement.

Return committed physical time in each output sample, segment identity, declared control values and rates, differential/algebraic state, observed quantities and diagnostics. Record model/source revision, catalogue hash, schema/expression/engine versions, units, initial time/state, full ordered schedule, solver method/settings and failure location. Separate computation wall-clock time (`elapsed_ms`) from physical elapsed time. Native and Wasm must export the same versioned contract; the UI must not invent missing fields.

## 6. Verification cases required before Terracotta execution

Keep synthetic constitutive laws in test fixtures, outside the public model catalogue. They test the engine; they are not new literature models or independent verification of Terracotta.

| Case | Independent expectation / failure exposed |
| --- | --- |
| Maxwell deviatoric relaxation | With fixed strain and constant `tau`, `s(t) = s0 exp(-(t-t0)/tau)` while pressure remains constant; catches skipped zero-strain holds |
| Maxwell deviatoric creep | Under constant deviatoric stress, `dev(D) = s/(2 G tau)`; catches a stress hold being treated as a strain hold |
| Nonautonomous synthetic scalar law | `dx/dt = time / tau²` has a known quadratic increment; catches wrong stage time and restarted clocks |
| Prescribed changing strain rate | Elastic response equals the analytical integral of the imposed rate; catches wrong rate sampling and units |
| Partition and refinement | A full interval and consecutive partitions converge to the same trajectory; tighter tolerances reduce error against analytical solutions |
| Forced rejection/failure | A rejected attempt commits neither clock nor state; a failed second half returns the original full-step state/time |
| Schedule boundary/rate change | Continuous state, correct new control rate, no integration across the discontinuity |
| Time/units/input failures | Reject missing or nonpositive duration, nonfinite time, non-increasing representable endpoint, inconsistent rate dimensions and unsupported controls |
| Rate-independent regression | The existing five models retain results; an explicit timed adaptation is invariant to duration where the source law is rate independent |
| Native/Wasm parity and replay | Same committed sample times/states and declared tolerances; replay/restart retains persistent history |

After these pass, reproduce the author Terracotta cases pinned in TC-05, with source-matched parameters, initialization, rates and durations. Numerical agreement with shared-source code still requires independent equation review. Experimental validation needs compatible clay data and timing/preparation metadata.

## 7. Implementation order and unresolved decisions

The design draft and the [experimental physical-time ODE subset](TIME_ODE_API.md) are delivered; **TC-02 and TC-03 are not closed**. TIME-01/02/04/05 have partial implementation evidence; ordered mixed component controls and observables now have [analytical native/Wasm evidence](TIMED_SCHEDULES.md). Source reconciliation, original invariant capabilities, stiffness assessment and browser integration remain open. Execute these bounded work packages after the relevant TC-01 extraction:

1. **TIME-01 — representation:** settle unit serialization, typed engine inputs, equation/state/observable roles, capability/version declarations and migration fixtures. Resolve whether the original Terracotta representation is an ODE after eliminating algebraic stress relationships, or needs a DAE contract. Verify the stress-first state restriction can represent it honestly.
2. **TIME-02 — transactional update:** pass time context through the Python evaluator, generated C++, domain/initial checks and material-update API. Add generic time-aware integration and analytical fixtures. Keep v0.1 entry points working unchanged.
3. **TIME-03 — timed driver:** implement a validated ordered schedule, supported mixed-control combinations, holds, stage control evaluation and exact segment termination. Every control trial starts from the same committed state **and clock**.
4. **TIME-04 — numerical evidence:** configurable tolerances/step budgets, error control, stiffness assessment, refinement and failure evidence. Select additional implicit integration only against demonstrated requirements.
5. **TIME-05 — portable interfaces:** versioned native/C ABI/Wasm serialization, time-aware parity/replay fixtures and recorded diagnostics. No time-dependent model is published with a native-only execution path.
6. **TIME-06 — Terracotta and browser:** transcribe the extracted original formulation, reproduce the author cases, then expose supported rates/durations/holds in the laboratory with accurate scope labels. This implements TC-04–06; it does not close the SANISAND six-model gate.

Open scientific decisions are Terracotta's precise units and consistent initial states; the relation between its algebraic observables and rate variables; the controls actually used in each reference test; any stiffness/domain restrictions; and the original triaxial variant's place in the 3D release target. They must be resolved from sources and evidence, not inferred from this proposed API.
