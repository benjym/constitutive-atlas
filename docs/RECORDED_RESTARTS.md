# Experimental bounded recorded-control restarts

This opt-in policy lets the common recorded-path solver escape a locally constant material response when its reduced mixed-control Jacobian is singular. The [prior diagnosis](RECORDED_RESOLUTION_DIAGNOSIS.md) established that the three coarse Drucker–Prager unloading failures start inside its apex branch, despite attainable endpoint controls. All three now complete with restarts enabled. Their original failed reports remain unchanged.

## Request and interfaces

Add a top-level object to an existing recorded-run request:

```json
"restart_settings": {
  "max_restarts": 1,
  "restart_step": 0.0001,
  "restart_levels": 8
}
```

The object is optional and closed. An empty object selects the values above. Omitting it keeps restarts disabled and preserves the legacy response shape. Explicit `max_restarts: 0` also disables searches while returning the resolved policy and zero restart counters. The [complete example](../protocols/recorded-dp-restart-run.json) fixes initial state and parameters to the illustrative Drucker–Prager study values. Use `atlas.cli replay` or import it in **Recorded paths** in the website.

| Setting | Meaning | Allowed range |
|---|---|---|
| `max_restarts` | Maximum search invocations at each attempted caller knot | integer 0–16 |
| `restart_step` | First search radius, maximum absolute Mandel strain-increment perturbation | finite, greater than 0, at most 0.01 |
| `restart_levels` | Number of dyadic radii per search | integer 1–16 |

The C/Wasm function `atlas_replay_recorded_with_restarts` takes the same eight string arguments as `atlas_replay_recorded`, plus a ninth CSV string in the order `max_restarts,restart_step,restart_levels`. All three values are required on this numeric wire. The old function is unchanged. Native CLI users pass the same CSV to `--recorded-restarts`; the flag is rejected outside recorded mode. Python and browser JSON clients resolve the optional object and verify that the returned policy matches it. Browser exports retain it, and the resolved settings panel displays it.

## Search and transaction policy

The normal root solve, accepted-update tangent and feasible finite-difference fallback run first. Restarts apply only when a **finite** reduced Jacobian fails its rank solve. They do not handle a failed first material update, nonsingular line-search failure, or a nonfinite Jacobian. IGS97 depth exhaustion remains a separate material-budget issue.

The driver already constructs a particular strain increment and normalized nullspace directions for prescribed strain constraints. For each search radius `restart_step * 2^level`:

1. Try the positive and negative sum of the free directions, normalized by its maximum absolute physical Mandel component. Then try positive and negative individual directions, each already normalized in that way. A single free direction is tried once per sign.
2. Construct every candidate from the current feasible free coordinates and the original particular increment. Skip nonfinite or bit-identical increments.
3. Evaluate the complete material update from the same committed parent as every other root trial. Failed material candidates are discarded. Count each executed call against `max_material_trials` and account for its attempted internal substeps.
4. Accept a converged candidate immediately, including on the final permitted material trial or root iteration. Otherwise select the lowest-error candidate at the first radius with a sufficient improvement, preserving the first candidate on an exact tie. Its next root iteration recomputes the tangent.

A nonconverged seed must reduce the fixed scaled maximum control residual by more than a relative `1e-8` to avoid selecting floating-point noise on a flat branch. A converged candidate is not subject to that extra reduction rule. Search invocations also consume ordinary outer iterations, so existing iteration/trial limits remain effective. Each radius has at most `2*(number_of_free_directions+1)` candidates; the finite search is additionally limited by its restart count, level count and the global material-trial budget.

No candidate is committed until all endpoint controls converge. Failure retains the exact accepted observation prefix, full state and strain. The search adds no caller knots, material projection or constitutive equations. It is deterministic in the fixed coordinate frame, but its finite direction set is not rotationally invariant and does not cover every possible escape direction or sign combination.

## Diagnostics and evidence

Explicit-policy responses add resolved `restart_settings` and `restart_diagnostics`:

- `searches`: number of search invocations across the path;
- `material_trials`: executed exploratory calls, included in the existing total `material_trials`;
- `accepted`: selected improving seeds or converged candidates. This counts selections even if a later root iteration or knot fails; it does **not** count committed observations.

`finite_difference_probes` remains separate from restart trials. Existing last-root diagnostics describe the current root or selected seed, rather than every discarded search candidate.

The [evidence manifest](../catalogue/investigations/recorded-restarts-v1/manifest.json) retains 29 native requests/responses: all 16 previous API cases unchanged, three additional disabled coarse Drucker–Prager cases, their three explicitly disabled variants, five enabled successful histories and two enabled bounded failures. The three original coarse factors 1, 2 and 4 complete with 2, 4 and 4 selected restarts, respectively. Their committed stresses and void-ratio increments agree with independent scalar return/volume calculations. Radial symmetry and a scaled/permuted control-row case are checked within numerical tolerances.

A synthetic material has a flat stress response below a strain threshold and a quadratic persistent memory update. Its checks cover deterministic replay, history isolation, a too-small unsuccessful search, exact trial caps, immediate final-trial/final-iteration convergence, oblique prescribed-strain feasibility, row scaling/permutation and late-failure prefix retention. The existing recorded-path and native API suites also run. Native/Wasm parity includes all retained requests plus the standalone example (46 pairs). This milestone checks the browser module under Node/Wasm; no new interactive browser session is retained.

These checks establish bounded solver behavior, not general nonlinear convergence or scientific model validation. Stress controls remain endpoint constraints. Constitutive discretization accuracy and source-matched/experimental validation remain separate roadmap gates. Builds were serial, and each capture runner executes requests in order. The work was not deployed.

```sh
ATLAS_RECORDED_SOLVER=/path/to/atlas_solver python3 -m unittest tests.test_recorded_restarts -v
node tools/test_recorded.mjs --wasm /path/to/atlas.js --native /path/to/atlas_solver
```
