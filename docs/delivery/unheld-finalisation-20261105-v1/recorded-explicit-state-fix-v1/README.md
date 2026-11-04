# Recorded parity explicit fixture state

Source-only one-file proposal. The optional compiled loop copies each request that lacks `initial`, supplying the exact historical example state for its model. It leaves all retained compressed packets, pure checks, explicit requests, response comparisons, 1e-9 tolerance, counters, restart/control arguments, process checks and cleanup unchanged. The output report records the actual explicit request sent. Unknown missing-state models fail closed rather than obtain a guessed state.

There are 46 original compiled-loop pairs: 35 missing initial states and 11 explicit states. `evidence/default-equivalence.json` binds current and intrinsic-archived legacy model definitions. Their ordered flattened fields equal exactly for all five models. The original solver materializes this ordered flattening (`evidence/source/cpp/include/atlas/solver.hpp` initial_state); current main.cpp state_for requires explicit input for v0.3. This restores the harness's fixed fixture intent without restoring runtime defaults or claiming old results validate current equations.

Reproduce: `node docs/delivery/unheld-finalisation-20261105-v1/recorded-explicit-state-fix-v1/check.mjs`. This runs the original optional loop with manufactured native/module boundaries and real pure recorded wire/settings functions. Original input fails the missing-wire assertion; candidate passes all 46 pairs/92 explicit wires; corrupted response rejects; original request packets remain unchanged. Exact reverse substitution recovers every byte of the original source, proving all original assertions remain. No compiled/module artifacts or actual child processes run.

## Remaining current-ordinary harness audit

The saved qualification workflow invokes the following ordinary-engine consumers in both jobs. No other missing-initial defect was found in this bounded source audit:

- test_wasm.mjs explicitly flattens generated state into both native and Wasm calls; its increment/rate/IGS cases also explicitly initialize.
- test_numerics.mjs has the separately reviewed explicit row.parent fix; it is not modified here.
- test_browser_loading.mjs initializes from metadata for ordinary cases and passes the resulting specification.initial to both adapters.
- test_scoped_parity.mjs uses policy cases through runScopedLaboratory; native argument index2 is always forwarded as --initial. Those policy cases already qualified current16, and this patch changes no policy input.
- test_ensemble_wasm.mjs calls makeStudy. web/ensemble.mjs lines97–104 constructs the entire explicit state from experiment stress/void ratio and configured persistent history, then assigns `initial` in every runnable job specification. web/recorded-worker.mjs routes this specification; no implicit initialization is needed. This does not predict experimental or numerical success.
- test_supported_package.mjs ordinary() constructs explicit flattened metadata state. Its supported profile routes retain their existing initialization contracts.
- check_ramberg_osgood_wasm.mjs starts from each c.initial; Ramberg is not one of the five migrated models.
- test_loading/test_experiments and node contract tests are pure/data checks. test_history_wasm and test_time_wasm use separate fixture engines rather than ordinary five definitions; dedicated public role harnesses are outside this five-model initialization change.

Full remote qualification remains necessary. Source audit is not execution evidence and does not waive any failure or package gate. This test-only source change also changes ordinary source-freeze membership: retain the original qualification freeze and bind the new delta; do not claim an unchanged original full source hash set. Parent owns workflow routing, installation, actual retained-engine test, publication and live verification.

No task-owned servers, builds or artifact copies were created. Manufactured temporary control files are removed by the unchanged loop finally block; durable source/evidence snapshots remain in this packet. No other agent's resources were touched.
