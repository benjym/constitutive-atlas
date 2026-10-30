# Experimental legacy snapshot bridge

The [typed history reference](HISTORY_REFERENCE.md) now has a [legacy transport bridge](../atlas/history_legacy.py). It wraps existing schema0.1 state and a trusted **complete** integrator in immutable snapshots. No reset expressions are translated into new phase expressions. The existing integrator remains responsible for preparation, domain/initial checks, transient handling, previous-substep `_n`, internal error control and cutbacks.

This preserves an important difference between the two contracts: [legacy parent resets](PARENT_INCREMENT_RESETS.md) allow dimensional signed guards and eagerly evaluate shared derived expressions, whereas the new phase reference has its own explicit bindings and finite-intermediate rules. Replacing the former with a phase translation would not generally preserve failure semantics.

## Snapshot and complete-step callback

```python
from atlas.history_legacy import make_legacy_snapshot, advance_legacy

parent = make_legacy_snapshot(model, named_state, named_parameters, initial_strain)
result = advance_legacy(model, parent, six_component_increment, complete_integrator)
if result['ok']:
    parent = result['snapshot']
```

All parameters and six initial Mandel strain components are mandatory. Snapshot creation validates structure, parameter bounds and finite values; it does not prepare a specimen or prove that a supplied state is admissible. A restored snapshot is not initialization.

The wrapper binds canonical model content, named parameter values, explicit parameter declaration order, and ordered state transport layout through separate hashes. It also stores full strain and its consistency hash. Parameter order needs an explicit record: sorted-key canonical hashes alone do not distinguish reordered parameter dictionaries, while the existing native wire protocol is positional.

The inner history snapshot uses stable `f0`, `f1`, ... slots to avoid name collisions between the two languages. It retains every legacy `State` field for exact transport/replay. A transient or multiplier slot is marked transport `context`; this does not promote it to physical material history or change how the existing integrator resets/uses it. No increase in the 32-component limit is made. The inner preparation epoch remains zero: legacy parent-reset selection is not the new explicit preparation/FirstCall mechanism.

The callback receives independent copies of `(model, named_state, increment, named_parameters)`. It must perform one complete existing material update **from the original supplied state**, including its own reset selection. Passing a pre-reset state would select history twice and is prohibited by this contract. A preparation-only callback is useful for selection tests but is not a complete constitutive integration adapter.

A callback result requires a real Boolean `ok`, every named state field, and finite JSON diagnostics. The bridge does not reevaluate the equations or impose initial-only checks at the endpoint. On success it advances generation once and adds the caller strain increment atomically. Failure, exception, malformed output, exhausted counters or nonfinite accumulated strain returns the exact incoming outer snapshot object and no events. Attempt diagnostics may survive; trial states cannot replace the parent. All outer candidates can reuse the same immutable snapshot.

Complete JSON roundtrips reproduce subsequent bridge results with the same callback/policy. Hashes enforce self-consistency and the selected model/parameter/layout identities; they are not signatures authenticating an imported physical history. A caller remains responsible for selecting the correct lineage and retaining its numerical policy.

## Explicit existing-native callback

[The native callback factory](../atlas/history_native.py) accepts an already-built solver, its generated catalogue and **all six** incremental settings. It never configures/builds a target or silently falls back to an older API.

```python
from atlas.history_native import native_integrator
from atlas.recorded import MATERIAL_DEFAULTS

integrate = native_integrator(
    'build/atlas_time_solver', 'build/time-generated/models.json',
    dict(MATERIAL_DEFAULTS))
result = advance_legacy(model, parent, increment, integrate)
```

The example uses synthetic time-catalogue fixtures, not a new public model. For another compiled catalogue, supply its matching solver/metadata and a model compiled into it. Parameter values are restored from the parent binding.

At binding, the factory verifies the generated catalogue hash, calls the existing `--describe`, compares complete model metadata and explicitly checks compiled parameter order. It hashes the binary around description and every material call. Sorted catalogue hashes alone cannot establish wire-order compatibility. Each integration call uses the existing settings-enabled endpoint, validates status/exit code, checks the complete positional request echo, exact settings version/norm, model and catalogue, and validates returned state/counters. Numeric echoes reject Boolean impostors even though Python considers `False==0` and `True==1`. Returned diagnostics retain binary/model/catalogue/request hashes and resolved settings.

The runtime description is evidence supplied by the selected binary, not an independent proof of compiled machine-code correctness. The caller trusts that binary and its existing integration implementation. This bridge establishes transport/selection isolation and request identity; it does not supply new physical equations or scientific validation.

## Verification and remaining gates

```sh
python -m unittest tests.test_history tests.test_history_legacy tests.test_history_native -v
```

Eleven pure bridge groups test exact original-parent selection, dimensional/eager/lazy legacy behavior, callback isolation, full failure rollback, repeated candidates, restart roundtrips, parameter order/layout identity, counter/strain overflow, all five public state-layout roundtrips and transient transport. Six native-callback groups test binary identity, request echoes, explicit settings and compiled parameter order, plus four **serial** material cases: rate, residual, cutback with frozen memory, and failure after internal work. The actual-native group skips if the existing fixture binary/catalogue is absent; it never builds automatically. CI's existing CTest discovery includes these tests after its builds.

Locally, the old fixture binary lacked `--integration-settings`. It was rejected without committing a candidate. One serial `atlas_time_solver` target rebuild completed, then all 17 bridge/callback groups passed with the existing material equations. No public solver API, model definition or default was changed.

This advances the legacy-adapter part of HIST-G4. Full integration of the phased history envelope into coupled native/Wasm solvers, timed-driver adapters, duplicate-observation/explicit-command handling, host subzones, durable lineage negotiation and source-blocked PM4 updates remain open. Scientific admission and external source-matched histories remain separate gates.
