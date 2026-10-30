# Timed mixed controls and algebraic outputs — experimental v0.2

This implements a small-strain, fixed-frame ODE laboratory driver in the common C++ engine. See [the ODE model contract](TIME_ODE_API.md), [model schema](../schemas/model-v0.2.schema.json), [run schema](../schemas/run-v0.2.schema.json) and [implementation](../cpp/include/atlas/schedule.hpp). The browser does not yet expose timed schedules, and Terracotta remains a non-executable candidate.

## Model outputs

A physical-time model may declare `observables`, each with `name`, `shape` (`scalar` or `sym`), `unit`, positive parameter-only `scale`, and `expr`. Expressions use current persistent state, parameters, derived values, `time` and `strain_rate`. Outputs are evaluated algebraically; they are neither integrated state nor inputs to evolution equations or other observables. This avoids differentiating a viscous stress and introducing strain acceleration just to display or control stress.

The driver requires an observable named `stress`, with symmetric Mandel shape and Pa units. It need not be a persistent state. Other observables are returned in declaration order, with symmetric tensors flattened into six components. Model metadata supplies names, offsets and shapes. Scales use the same dimensional checks as state scales.

## Ordered loading histories

A run declares `schema_version: "0.2"`, `units: "SI"`, `model`, `start_time`, ordered `segments`, and `solver`. Optional `parameters` and `initial` use declaration order; optional `initial_strain` and `initial_strain_rate` are six-component tensors, defaulting to zero. Defaults for persistent state and parameters come from the model. The initial rate defines the incoming algebraic stress before the first control transition, so it matters when stress depends on rate.

Each segment has a unique `id`, positive `duration` in seconds, `samples`, and exactly six component controls in order `xx, yy, zz, sqrt(2)xy, sqrt(2)yz, sqrt(2)xz`. Compression follows the existing positive geomechanics convention. Each component independently selects `quantity: "strain"` or `"stress"`, and one control:

| Kind | Meaning | Value units |
| --- | --- | --- |
| `hold` | Capture the incoming component value and keep it constant | No `value` field |
| `rate` | Linear path from the incoming value at the specified constant rate | 1/s or Pa/s |
| `target` | Linear path from the incoming value to an absolute endpoint | 1 or Pa |

A stress hold solves for the unknown strain increment; it does not prescribe zero strain rate. Strain-controlled components prescribe the strain increment. No component may simultaneously prescribe both. A target is reached over the entire segment duration, regardless of output sample count. These are component controls, not a general invariant/poromechanics constraint language. Volumetric, undrained or axisymmetric restrictions need explicit compatible controls and a model whose capabilities support them.

For example, this synthetic Maxwell fixture computes creep under six stress holds:

```json
{
  "schema_version": "0.2",
  "units": "SI",
  "model": "test-maxwell",
  "start_time": 0,
  "segments": [{
    "id": "creep", "duration": 4, "samples": 4,
    "controls": [
      {"quantity": "stress", "kind": "hold"},
      {"quantity": "stress", "kind": "hold"},
      {"quantity": "stress", "kind": "hold"},
      {"quantity": "stress", "kind": "hold"},
      {"quantity": "stress", "kind": "hold"},
      {"quantity": "stress", "kind": "hold"}
    ]
  }],
  "solver": {"method": "backward-euler-step-doubling"}
}
```

Save it as a local JSON file and run `python3 -m atlas.cli run FILE.json --solver build/atlas_time_solver --output /tmp/creep-result.json`. The fixture is separate from the public model catalogue; it is not a literature model. A CLI result can be replayed because it retains the original `specification`.

## Boundaries, failure and restart

At entry, each segment captures incoming strain and observed stress. The driver first solves rate-dependent algebraic stress controls with persistent state fixed. It records the incoming left value and a right transition value at the same physical time. A strain-rate jump may change stress instantly, while persistent state and accumulated strain stay continuous. Incompatible entry controls fail without committing a transition. Stress-controlled rates at transition samples are `null`: a state-only stress observable need not determine an instantaneous rate from a snapshot. Finite-step endpoint rates are solved and reported thereafter.

Every trial starts from its incoming committed state, strain and time. A failed output interval discards all trial progress and retains earlier committed points, including a valid entry transition if one was committed. Domain failure never clips state. A successful schedule ends exactly at its representable final time. Restart requires the last state, accumulated strain, endpoint rate, parameters and physical time; a transition point with null rates is not a complete restart record.

## Numerical contract

The current schedule method is backward Euler with step doubling, returning the two-half-step result. A joint Newton solve uses automatic derivatives for state balance and the unknown stress-controlled strain increments. It uses pivoting and a decreasing-residual line search. This is an ODE coupled to loading constraints, not a general constitutive DAE solver or the author's variable-order BDF implementation.

The local temporal estimate is the full/two-half difference (first-order Richardson factor one), divided componentwise by:

```text
absolute_scale_fraction * scale
  + relative_tolerance * max(abs(incoming_value), abs(candidate_value))
```

Declared scales apply to state; accumulated strain uses unit scale. Both state and strain must pass. Local acceptance does not bound global trajectory error; perform refinement against the required observable. The normalized nonlinear residual uses state balance divided by `state_scale * min(step_seconds, 1)` (an explicit one-second normalization), and stress mismatch divided by observable scale. Its default tolerance is `1e-10`, distinct from temporal error control. Each point records `nonlinear_residual_norm` separately from `temporal_error_norm`; regular points report the final accepted half-step residual, while transitions report the algebraic entry mismatch.

Defaults: relative tolerance `1e-6`, absolute scale fraction `1e-9`, minimum accepted half-step `1e-12` s, maximum full trial interval `1e6` s, 20,000 accepted substeps across the schedule, depth 40, and 40 Newton iterations per solve. Tight first-order refinement can exceed the default budget: the analytical Kelvin–Voigt ramp/creep test explicitly records 100,000 allowed substeps at `rtol=1e-8`, `atol=1e-11`. This is test evidence, not a recommended setting for Terracotta. At most 100 segments, 5,000 regular samples per segment, and 10,000 regular samples overall are accepted, plus boundary records. Output intervals partition integration and can affect numerical error; they do not redefine the loading history.

Results record catalogue hash, model, parameters, initial values, start time, SI units, complete ordered controls, all resolved solver settings, committed samples and per-interval work/error diagnostics. Adaptive counts and near-roundoff error estimates may differ across platforms; scientific output parity is checked with explicit numerical tolerances.

## Interfaces and evidence

Native mode `observe-time` uses the same inputs as `evaluate-time`, returning algebraic values. The additive C/Wasm ABI is:

```text
atlas_observe_time(id, parameters_csv, current_csv, strain_rate_csv, time)
atlas_run_schedule(id, parameters_csv, initial_csv,
                   initial_strain_csv, initial_strain_rate_csv,
                   segments_csv, segment_ids_csv,
                   start_time, rtol, atol, min_step, max_step, max_substeps,
                   nonlinear_tolerance, max_iterations)
```

Each wire segment is 20 numbers: duration, samples, then six triples `(quantity, kind, value)`. Quantity tags are strain=0/stress=1; kind tags are hold=0/rate=1/target=2; hold's value must be zero. IDs are comma-separated ASCII letters/digits/underscores/hyphens. Native `--mode schedule` uses `--segments` and `--segment-ids`; Python validation/encoding is in [schedule.py](../atlas/schedule.py). C/Wasm returns JSON strings with the existing shared output-buffer lifetime. Existing untimed APIs continue to reject physical-time models.

[Python/native analytical tests](../tests/test_schedule.py) verify Maxwell relaxation/refinement and stress-controlled creep, Kelvin–Voigt stress ramp/creep and rate-jump stress, mixed component controls, absolute targets, sampling/restart, replay, domain failure and budget rollback. For Kelvin–Voigt, `stress = elastic_stress + 2 viscosity dev(D)` and elastic stress evolves as `K tr(D) I + 2 G dev(D)`. Under the tested deviatoric ramp of amplitude-rate `A`, the elastic deviatoric component is `A[t - tau(1-exp(-t/tau))]`, with `tau=viscosity/G`; during a following stress hold it approaches the held stress exponentially. These closed forms are independent expectations. [Wasm tests](../tools/test_schedule_wasm.mjs) check five analytical success/failure histories and native output agreement, plus algebraic observation.

Remaining gates include source-complete Terracotta transcription, signed invariant/kinematic capability declarations, source-matched reference cases and stiffness assessment, independent review, consistent tangent exposure and browser controls. Synthetic checks do not close TC-01–06 or the twenty-model research release.
