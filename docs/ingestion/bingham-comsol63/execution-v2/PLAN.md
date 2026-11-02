# Bingham BE-schedule numerical qualification v2 — prospective scope

This distinct study is prepared **after** the retained v1 native observations and before any execution of these new requests. It does not claim a pre-observation selection of the Bingham law or of the backward-Euler host. V1’s136raw requests/272exact repeats, frozen gates, raw outputs and failing assessor remain untouched. Independent review diagnosed42radial requests outside the original direct midpoint accuracy budget because its crossing-sensitive error estimate can miss the inactive/active transition. Six v1 BE schedule histories had saved-output physical-budget passes in a bounded diagnostic; those prior observations are disclosed, not relabeled as prospective v2 results.

The candidate and continuous constitutive law do not change. This study qualifies **only the existing generic backward-Euler physical-time schedule host**, `atlas_run_schedule`, with the same full136case identities and source/reference physical error budgets. Direct `atlas_integrate_time` midpoint execution is excluded from the proposed qualified interface. No compiler, model, generic integrator, kernel, shared runtime or numerical gate is modified to turn the original failure into a pass. The later approval and public interface must preserve that host restriction.

## Case lineage and inputs

All108source-derived closed-form coaxial cases retain the original four parameters, full13incoming states, six prescribed strain rates, physical start time3s, durations2s, and exact final13state/6stress references. Each is transported as one schedule segment with all six strain components rate controlled and one output interval. Initial/segment-entry/final outputs all receive independent references. Hydrostatic and zero-hold cases, three fixed-basis covariance cases and all valid recoveries receive the same transport. Request values and full contexts are checked, with CSV spellings compared as exact round-trip numbers rather than language-dependent formatting.

The original public relaxation, creep and constant-rate histories, noncoaxial direction/hold/reversal history and coarse/fine refinement histories retain their original schedule specification and reference bytes. Noncoaxial/public-rate references remain the independent stress-plus-α RK4 oracle with4096/8192grid convergence under1e-9strain and0.02Pa. Their copied oracle, convergence evidence and parity helper are exact-byte identical to v1, with explicit source bindings.

Actual-state restart uses the actual successful public-relaxation endpoint’s full13state, total strain, strain rate and physical time. The next request is re-encoded from those actual values; the independent relaxation formula is evaluated from that actual parent, rather than an ideal reference parent. Restarts retain accumulated α, all tensor components and the clock. Each native request runs twice in separate CLI invocations; every Wasm request runs twice in the same persistent engine, including every failure followed by its original valid recovery. All136cases must be collected; no silent filtering or failure removal is allowed.

## Fixed numerical policy

Use the unchanged BE schedule solver settings: relative tolerance1e-9, absolute state-scale fraction1e-12, minimum step1e-12s, maximum step1e6s, maximum accepted half-substeps1,000,000, nonlinear tolerance1e-10,40Newton iterations and existing maximum depth40. Coarse diagnostic remains1e-4/1e-7. For each fine physical state/history component, error≤max(3e-7,2e-5|reference|); for each stress component, error≤max(3Pa,2e-5|reference|). Coarse diagnostic alone retains0.001state/1000Pa floors. Fine maximum state and stress errors must each be strictly less than coarse error/5. No observed failure permits changing any budget or reference.

Check every initial, right-side event and regular output: exact topology, physical time, model/catalogue identity, settings, parameters, initial context, segment controls, six total strains, finite13state and six stresses, plastic trace≤1e-10, nonnegative/nondecreasing α, entry-state identity and complete response fields. Stress-controlled entry rates must be null; subsequent rates must be finite. Strain-controlled entry rates equal the requested rate exactly. At regular outputs the source computes `(rate*h)/h`; allow only4binary64eps times |rate| roundoff for nonzero prescribed rates, exact zero for holds. This source-derived representation allowance is prospectively disclosed; it changes no physical state/stress accuracy budget. Native/Wasm physical parity remains2e-10scaled with stress floor1000Pa and state floor1, excluding only the original iteration/substep/error diagnostics.

## Failure and transaction contract — source derived

`cpp/main.cpp` lines309–335 parses parameters/state and the schedule wire, delegates to `run_schedule`, and serializes its existing committed points. Parameter and missing-state parse failures return exactly `{ok:false,message}`. For invalid zero/negative duration the run result has the full request envelope and empty points, message `invalid segment duration, identity or sample budget`. Inadmissible negative α or plastic trace has empty points and message `inadmissible initial state or outputs`. The seven invalid requests retain their intended physical invalidity, transported through the schedule API; each is followed by its unchanged valid recovery.

`cpp/include/atlas/schedule.hpp` validates before pushing the initial point, appends a segment-entry event without changing persistent state, and appends a regular point only after an entire output interval succeeds. Failure therefore retains already committed **samples**, not an invented whole-schedule rollback. V1 direct whole-incoming-state rollback is a different host contract and remains outside v2 qualification.

The late-budget case keeps the original incoming state, clock, zero-rate hold,2s total duration,0.1s maximum step and budget2. It introduces a1e-6s output boundary: a first strain-hold segment must commit one sample, consuming exactly two accepted BE half-substeps with positive Newton iterations and a changed material state. The remaining hold segment then begins with zero remaining budget. The expected failed response contains exactly initial, first entry, committed first sample and second entry; the second-entry state/strain/stress must equal the committed sample exactly. Its message is `schedule solve failed in segment budget-exhaustion; last committed sample retained`. No failed candidate sample may appear. Initial and committed-prefix values must independently meet the original accuracy budgets. A final recovery must succeed in the same Wasm instance.

This establishes real prior accepted trial work and consumed budget before a later sample fails. The failed interval’s diagnostics are not serialized by the existing source; the assessor does not invent or claim an observed Newton count for that failed interval. It does not claim that the budget guard evaluates an additional constitutive trial after the budget reaches zero.

## Prospective review and commands

`synthetic_checks.py` manufactures explicitly synthetic records solely to test the assessor:136ideal records pass and25distinct mutations are rejected. It does not run a constitutive model and its pass is not a material qualification. Original compiled evidence and failures remain separate. Collector and assessor source, cases, oracle, model/source/runtime bindings and this plan are frozen in `freeze-v1.json` before new compiled calls. A separate reviewer must accept that exact prospective version before coordinator execution.

Coordinator native collection after acceptance:

```sh
python3 -B docs/ingestion/bingham-comsol63/execution-v2/study.py native --solver /ABS/atlas_bingham_solver --raw docs/ingestion/bingham-comsol63/execution-v2/native-attempt1.json
```

Wasm collection (one persistent engine), separate assessment and parity:

```sh
node docs/ingestion/bingham-comsol63/execution-v2/collect_wasm.mjs /ABS/bingham.js docs/ingestion/bingham-comsol63/execution-v2/cases.json docs/ingestion/bingham-comsol63/execution-v2/wasm-attempt1.json
python3 -B docs/ingestion/bingham-comsol63/execution-v2/study.py assess --raw docs/ingestion/bingham-comsol63/execution-v2/wasm-attempt1.json
python3 -B docs/ingestion/bingham-comsol63/execution-v2/parity.py docs/ingestion/bingham-comsol63/execution-v2/native-attempt1.json docs/ingestion/bingham-comsol63/execution-v2/wasm-attempt1.json
```

Keep every attempt, including partial raw collection and failed assessment, with distinct identities. Build ownership remains coordinator-only, serial explicit target `--parallel 1`. This source worker has run no compiled call or build. Passing this study would establish bounded numerical evidence for the declared BE host, not experimental validation, arbitrary material parameters, finite rotations, calibration or general cyclic histories.
