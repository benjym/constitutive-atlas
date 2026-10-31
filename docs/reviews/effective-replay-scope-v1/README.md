# Effective-only normalized replay guard

FIX-effective-replay-scope-v1, 1 November 2026. The normalized drained experiment
adapter now explicitly requires **state-bound effective Cauchy stress sigma** for
v0.3 input models and validates every supplied model definition. This implements
one consumer-safety requirement from the existing
[total-stress design](../total-stress-profile-v1/README.md); it does not activate
total-stress engine support or substitute effective stress into Tresca.

## Defect and correction

The [pre-fix witness](pre-fix-witness.json) changed only the migrated elastic
model's declared scope to total, then passed the model directly to `prepare_replay`.
The old adapter accepted it and constructed sigma=[103000,100000,100000,0,0,0]
from measured effective p/q. A supplied model bypassed `load()` and its validation.
Standalone total incremental execution was already unsupported; that did not guard
this separate in-memory preprocessing entry point.

The new consumer check rejects total, unknown, missing or observable stress bindings
before effective p/q reconstruction. It remains independent of the engine's current
restriction, so future total-profile support cannot silently enable this conversion.
Supplied definitions also pass normal schema/dimensional/convention validation;
unknown versions, symbols and unsupported fields are rejected. Legacy effective
contracts retain their meaning. No source data, material equation or numerical
threshold changed.

## Verification and preservation

Four focused test groups cover consumer scope rejection, future validator relaxation,
supplied-definition validation and exact before/after replay-bundle equality for all
nine current effective models. With existing conversion and recorded-calibration
contracts, 23 tests pass and one optional native check is skipped. No native/Wasm
call or build ran. The comparison is conversion equality, not material-simulation
accuracy or general model applicability.

```sh
python3 -B -m unittest tests.test_effective_replay_scope tests.test_experiment_replay.ConversionTests tests.test_calibration_recorded -v
python3 -B docs/benchmarks/calibration-elastic-smoke-v1/verify.py
```

The earlier three-candidate elastic evidence still replays its entire search result
exactly without native execution. Its original protocol, receipts, acceptance gates
and delivery manifest remain unchanged. [previous-sources.json](previous-sources.json)
pins exact archived converter and verifier bytes. The current saved-only verifier
can locate an exact canonical source snapshot when a live path has changed; the
historical delivery manifest resolves its old verifier through an additive archive
map. The converter's `digest` function AST is unchanged. Replay uses the same frozen
search/objective mathematics; it never invokes the changed conversion function.
No historical source identity was rebound to new bytes.

The existing Tresca transcription and total-stress design were found on the full
board before a duplicate could be integrated. No duplicate model was added.
Continue the existing scope-aware native/recorded/laboratory/browser design and its
prospective gates before enabling total-stress models. Generic metadata, nullable
pore channels, mechanical labels and effective-experiment guards must remain
consistent. The nine-model public catalogue and scientific statuses are unchanged.
