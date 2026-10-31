# Bounded complete-candidate calibration search

`atlas.calibration_search.calibrate` adds a deterministic serial search driver for
CAL-03 around the existing [whole-test objective](STUDY_OBJECTIVE.md). It evaluates
complete predictions for one frozen calibration package. This is reusable software,
not a new fit, scientific study freeze or replacement for historical pilot scores.

A search specification explicitly provides an ID, method
`bounded-coordinate-poll-v1`, a complete parameter vector, ordered fitted parameter
names with bounds and `linear`/`log` transforms, `max_evaluations` in 1..10000, and
normalized `initial_step`/`minimum_step` with 0 < minimum <= initial <= 1.
Parameters absent from the fitted list remain fixed. Search bounds are computational
bounds; the caller must separately validate complete parameter coverage, units,
model constraints, provenance and scientific suitability. This helper neither
infers model parameters nor edits a model definition.

The driver first scores the seed using its original values, then polls minus/plus
neighbours for each fitted parameter in the declared order in a normalized [0,1]
transformed box. Each sweep uses a frozen center; the strictly best successful
candidate becomes the next center. Ties retain the first candidate. If there is no
improvement, halve the step, stopping after an unsuccessful minimum-step poll.
Coordinates are bounded, representationally duplicate fitted vectors are skipped,
and **every actual evaluation, including rejection, consumes budget**. Budget
exhaustion takes precedence when both stopping limits are reached. There is one
explicit seed, no randomness, concurrency or hidden restart. The algorithm is a
local pattern search, with no guarantee of a global optimum or parameter identifiability.

```python
from atlas.calibration_search import calibrate, PredictionFailure

result = calibrate(
    search_spec, predict, objective, allocation, reservations, observations,
    allocation_sha256=allocation_hash, reservation_sha256=reservation_hash,
    on_candidate=save_receipt,
)
```

`predict(parameters)` receives a detached complete vector and returns the same
whole-test prediction bundles accepted by `score_objective`. It never returns a
precomputed scalar objective. The shared scorer enforces exact calibration IDs,
units, completion, finite values and acquired ordering. No evaluation/reserved
tests may enter scoring. Before the first callback, metadata and observations are
validated using the same metric contract (observation self-comparison is only a
shape/unit/travel check, never a model result).

For expected nonconvergence or an unsupported model domain, the adapter should
raise `PredictionFailure` or return a failed prediction bundle. The complete
candidate is rejected, with a diagnostic and null objective/score; successful
prefixes are never scored and no finite penalty is invented. Other evaluator
exceptions produce a recorded error and stop the search immediately. Sink
exceptions propagate before any next prediction, making a persistence failure
visible. Keyboard interrupts and process termination are not caught or resumed.

Every attempted evaluation has a zero-based sequence, full parameter vector,
status, diagnostic and, on success, the complete per-test/channel score. The result
contains all receipts, a detached best receipt (or null), configuration, objective
policy, allocation/reservation identities and a canonical JSON SHA-256 of the
observation values actually used. That value hash is explicitly not the original
measurement-file byte hash. All input objects and callback/sink payloads are copied.
`success` means a feasible scored candidate exists; `stop_reason` still distinguishes
budget exhaustion from minimum-step stopping. No convergence or scientific claim
is inferred from the word success.

A production study runner must persist each receipt through `on_candidate`, freeze
model/executable and source-data identities, initialization/control/solver settings,
parameter provenance, search limits and evaluation policy **before** a real fit.
This API has no filesystem, subprocess, experiment-loader, clock or PRNG access;
it cannot authenticate those external identities or ensure a callback's runtime
limits. The adapter must reset preparation/state for every candidate and whole test,
and produce deterministic predictions from the frozen inputs; duplicate suppression
assumes that contract. It supplies no durable journal/resume protocol. Historical study policies,
model bytes and results remain unchanged. Prospective scientific choices remain open under CAL-01/02/03/05. The
[fixed-preparation drained recorded runner](CALIBRATION_RECORDED.md) now supplies
one native connection with persistent request/response/assessment receipts; its
source/provenance and preparation limitations remain explicit.

```sh
python3 -B -m unittest tests.test_calibration_search tests.test_study_objective tests.test_curve_metrics tests.test_study_allocation -v
```

Synthetic verification covers known quadratic scores, linear/log polls, fixed
parameters, exact budgets and deterministic sequence, all-failed stopping,
failed/truncated/extra/nonfinite candidates, fatal adapter errors, receipt isolation
and sink failure, observation identity, and pre-evaluation metadata rejection.
No real measurements, model/backend calls, fitting campaign or build is needed.
