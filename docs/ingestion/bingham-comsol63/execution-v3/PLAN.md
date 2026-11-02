# Bingham capped BE-schedule qualification v3 — prospective candidate

This separate candidate is prepared after the retained v1 direct-midpoint observations and after the coordinator reported reversal physical-gate failures during v2 BE collection. The step-cap choice is post-observation. It must not be represented as a pre-observation selection of the model, host, cap or diagnostic hypothesis. V1/v2 bytes, references, failures and gates remain unchanged. No compiled v3 request has been made by the source worker. A separate agent must accept the exact final freeze before the coordinator starts any new v3 call.

The complete v2 protocol in `../execution-v2/PLAN.md` remains the protocol except for the single request-setting change specified here. The same candidate, model identity, source equations, source/runtime bindings, parameters,136case IDs/order, incoming states, loading rates, durations, segment/sample histories, clock3s where originally specified, independent references,13state/6stress comparisons, coarse/fine refinement test, failure contracts, actual-state restart, recovery cases and two exact repeats are preserved. Direct midpoint `atlas_integrate_time` remains excluded from the proposed qualified interface. No continuous equation, runtime, compiler, kernel, public UI or physical gate changes.

## Sole request-setting change

For **every** case, including coarse/fine, all public examples, failures and recoveries, set

    maximum_step = min(previous maximum_step, M)
    M = 100000/(2*10000000*.012*1024)
      = 0.0004069010416666667 seconds.

The numerical value is frozen, not recomputed from an observed response. It equals min(τ/1024,Y/(2G max|d|·1024)) for the original nominal radial inputs, where τ=η/(3G)=2/3s. The source-only [analysis](../step-bound-analysis-v1/README.md) derives an upper bound on a fully omitted active-exit contribution and its exact radial continuation. It motivates this resolution choice only. It does **not** give an overall accuracy guarantee for the compiled host, active smooth steps, partially active endpoints, finite Newton solves, roundoff, noncoaxial loading, mixed controls or broad public parameter values.

No other solver setting changes: fine rtol1e−9, atol1e−12, minimum step1e−12s, maximum accepted halfsteps1,000,000, nonlinear tolerance1e−10,40Newton iterations and maximum depth40. The original coarse diagnostic retains rtol1e−4/atol1e−7 while receiving the same cap. Because the generic host commits two halfsteps, each actual accepted BE step is≤M/2. Cap alone produces16384 dyadic accepted halfsteps over an unsplit2s interval; further refinement, rejected trial work and Newton iterations can increase work. No timeout or budget increase is introduced to assure success.

The late-budget case retains its original complete incoming state, zero-rate hold, start3s, total2s, first1e−6s segment, second1.999999s segment, budget2 and all references. Its old maximum step.1s becomes M. The tiny first segment remains shorter than M and must commit exactly two accepted halfsteps with observed positive Newton iterations and changed state before the later budget failure. The existing partial-history/last-committed-sample contract remains unchanged, including recovery in the same persistent Wasm instance.

## Unchanged checks

Every fine state/history component must satisfy error≤max(3e−7,2e−5|reference|), every stress component error≤max(3Pa,2e−5|reference|). Coarse diagnostic alone retains0.001state/1000Pa floors. Fine maximum state and stress errors must each be strictly less than coarse error/5, even if this new common cap makes that test harder to satisfy. Any failure remains a failure; no reassessment may relax that gate.

The byte-identical v2 assessor checks exact response context, solver settings, identity/catalogue, time/topology, finite13state/6stress, domains, trace, monotonicα, all referenced points, prescribed rates, complete actual-parent restart, two byte-identical stdout repeats, seven invalids with recoveries, and late-budget retained state. Public/noncoaxial references remain the unchanged independent4096/8192-step stress-space oracle and convergence evidence. Native/Wasm parity remains unchanged2e−10scaled, with its original diagnostic exclusions. The collector uses the same persistent Wasm engine for all272calls, including failures and recoveries.

`study.py`, `collect_wasm.mjs`, `parity.py`, `oracle.py`, `synthetic_checks.py`, `expected-catalogue.json` and `reference-convergence.json` are copied byte-for-byte from v2. Their internal historical v2 labels remain intentionally unchanged; `source-bindings.json` and the v3 freeze establish this study's identity. The copied assessor's `prepare` command regenerates uncapped v2-style requests: **do not run `study.py prepare` here**. The separate `PLAN.py` is the v3 preparer and full-record lineage checker. It projects out only specification.solver.maximum_step, args[11], and the value after --max-time-step; the entire remaining per-case record must equal v2 exactly. This includes every reference array and actual-restart lineage.

## Source-only preparation and later coordinator commands

Preparation already performed in this new directory using `PLAN.py prepare`. Repeating preparation is intentionally refused to prevent overwrite. Recheck the136full-record projections and byte-identical helpers with:

```sh
python3 -B docs/ingestion/bingham-comsol63/execution-v3/PLAN.py check
```

The copied synthetic suite has136ideal positive records and25rejected negative mutations. These are manufactured assessor tests only, not observed constitutive results. No native/Wasm pass is claimed. Exact new candidate requests, plan, preparation script/checks, unchanged assessor/collectors/oracles, analysis hashes and unchanged runtime/source bindings are recorded in `freeze-v1.json` after preparation. V2 outputs may still be growing when their snapshot hashes are taken; a partial snapshot is context, not an assertion that the campaign has completed.

Only after independent prospective review of the exact freeze may the coordinator run:

```sh
python3 -B docs/ingestion/bingham-comsol63/execution-v3/study.py native --solver /ABS/atlas_bingham_solver --raw docs/ingestion/bingham-comsol63/execution-v3/native-attempt1.json
node docs/ingestion/bingham-comsol63/execution-v3/collect_wasm.mjs /ABS/bingham.js docs/ingestion/bingham-comsol63/execution-v3/cases.json docs/ingestion/bingham-comsol63/execution-v3/wasm-attempt1.json
python3 -B docs/ingestion/bingham-comsol63/execution-v3/study.py assess --raw docs/ingestion/bingham-comsol63/execution-v3/wasm-attempt1.json
python3 -B docs/ingestion/bingham-comsol63/execution-v3/parity.py docs/ingestion/bingham-comsol63/execution-v3/native-attempt1.json docs/ingestion/bingham-comsol63/execution-v3/wasm-attempt1.json
```

Builds and compiled calls remain coordinator-owned. Keep all partial collection, timeout and failed-assessment evidence. A pass would support this bounded BE policy and declared histories; it would not establish experiments, unrestricted cyclic/general control accuracy, finite rotations or every public parameter combination. Any later public policy must bind the actually qualified settings and range explicitly.
