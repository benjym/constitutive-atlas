# Experimental history and transaction contract

This is a design proposal, not an implemented API or executable model schema. The [PM4Sand3D contract example](../proposals/pm4sand3d-history-contract.json) is intentionally **not loadable** by the current model parser. It supplies storage classes, snapshot rules, phase dependencies and blockers, not missing constitutive equations. PM4Sand3D remains a non-executable candidate; independent review remains pending.

The proposal is based on repository revision `6cf1e58e8781353200e0fa15e32e4f5801590713`, its [PM4Sand3D history inventory](../catalogue/source-audits/pm4sand3d-1.0-history-inventory.json), [parent-increment resets](PARENT_INCREMENT_RESETS.md), and existing solver/DSL behavior. The inventory pins the [June 2026 vendor manual](https://itasca-software.s3.amazonaws.com/udm-library/Kippen_et_al_PM4Sand3D_v1_CGM-26-01.pdf), SHA256 `6073a97a374d4b947e20a492b5009bbd01e3e5b0b773841b0f3b037c194f7453`. Printed n maps to PDF n+5. Edition/DLL pairing and source access remain unresolved. No 2D PM4Sand3.3 semantics are imported.

## The problem the contract must solve

The existing legacy schema gives every persistent field an equation and optional simultaneous parent-increment reset. PM4Sand3D also has histories copied at reversals, initialization-dependent parameters, D/Kp lagged from the previous caller step, host zone averaging, and independent subzone stabilization. Flattening these into a larger state array would hide the algorithm's meaning and put unrelated retained values into the AD solve.

The inventory's conservative 58/62/75/79-slot scenarios are **not** a minimum independent count and do not authorize a capacity change. `atlas/model.py` currently limits scalarized state to32; `atlas/compiler.py::generate` emits capacity assertions; `cpp/include/atlas/tensor.hpp` fixes32 state derivative slots plus6 control directions. Keep these limits and the five existing catalogue definitions unchanged in this packet. Storage layout, independent unknown count and AD resource budget are distinct future decisions.

## Explicit storage classes

| Container | Lifetime | Required contents and rules |
|---|---|---|
| State/history | Committed, restartable | Mechanical state and path-dependent constitutive history. Shape/unit and update law are independent declarations; retention does not imply a differential equation. |
| Parameters/preparation | Committed, restartable | Raw inputs, supplied/default mask, resolved parameters, initial stress corrections, initialization normalizers, source/version and preparation epoch. Immutable within an ordinary caller advance. |
| Lag/cache | Committed when algorithm-required | D/Kp and stage-tagged next-step moduli or other proven caches. Retain their dependency stage and epoch; do not silently reevaluate from a later state. |
| User modes | Committed, restartable | Validated finite enums/flags, e.g. PostShake. Pending commands are input requests, not already committed modes. |
| Host subzone state | Committed per subzone | Independent stabilization histories if that capability is implemented. Their unknown layout blocks full-host admission. |
| Host workspace | Trial-local | Weighted sums, completion markers and scratch. Never shared between outer candidates or serialized as a complete-step restart. |
| Derived stage values | Trial-local | Pure typed evaluations from explicitly named snapshots. Caching them does not change their dependency scope. |
| Diagnostics | Attempt-local | Work counts and provisional event trace. They may count rejected work; they cannot influence material evolution. |

Stress, alpha, reversal anchors, fabric and scalar fabric histories map to state/history, subject to inventory aliases. Initial CSR normalization and default Ado provenance map to preparation. D/Kp map to retained lag, even if a sufficiently complete earlier-stage record could reconstruct them. p/r/n are cache candidates until averaging/correction identities are established. Current density representation, z_alpha, unnamed strain accumulators and per-subzone hourglass fields stay explicitly unresolved. No guessed equations or placeholder zero rates make them executable.

## Complete snapshots and public transactions

A complete committed snapshot contains all state/history, required lag, preparation, modes, applicable host state and strain/clock context. Its identity includes model/source hash, contract version, preparation epoch, committed generation and host scope. Serialization must preserve every required component and its stage metadata. A restore is not initialization.

The proposed generic operation is conceptually:

```text
trial = evaluate(parent_snapshot, caller_input, pending_command, settings)
result = {ok, candidate_snapshot_or_original_parent, diagnostics, provisional_events}
commit(selected_trial)  // caller selects at most once; no mutation during evaluate
```

These are design names, not callable functions. Current `Advance` APIs remain unchanged. Implementation may continue returning values without an explicit commit method, provided publication has the same single-commit semantics.

The phases are exact at the transaction level:

1. Validate supported version/capabilities, parent shape/units/domain, positive finite scales, preparation lineage, loading, settings and command. An initialization request cannot repair an arbitrary inadmissible parent silently; a dedicated preparation endpoint must validate the host input under its own declared rules.
2. Fork a private trial snapshot and workspace. All parameter records may be shared only as immutable data.
3. Apply any supported explicit initialization/reset/mode command provisionally. The resulting **base** snapshot is `prepared` if preparation succeeds, otherwise the unchanged parent when no preparation is requested. Every subsequent old-history read uses that base, not accidentally the pre-reset history. The incoming parent remains the rollback target.
4. Evaluate the model's declared phase DAG. No public state, clock, epoch, flag, host value or durable event record changes during evaluation.
5. Validate completeness, finite values, domains, cache stages, reduction completion, budgets and caller-control residuals. A partially filled zone does not produce a material result.
6. The outer control solver selects one valid candidate. Rejected Newton iterates, finite differences, line searches and restart seeds never become parents for later candidates.
7. Publish selected state, lag, preparation epoch, modes, host state and strain/clock atomically once. Only accepted event records are published.
8. On any failure, return the **exact incoming snapshot and identity**, even if provisional preparation or accepted internal substeps already occurred. Attempt diagnostics may survive. Discard every provisional event and workspace value.

Here “exact” means unchanged retained values and lineage, not a test that compares only stress within tolerance. An implementation can test bytewise copies within one backend; restart across JSON/native/Wasm must also define an exact-value roundtrip encoding and verify all named fields. NaN is rejected rather than used as a missing-field sentinel.

## Ordered snapshots without mutable old/new ambiguity

Each phase declares its input snapshots and unique write targets. All guards and right-hand sides within that phase read the same immutable input snapshots; their assignments become visible simultaneously in a named output snapshot. A dependency on an earlier update requires an edge to that phase output. Future-phase reads, cycles, undeclared reads and competing same-phase writes are rejected. Separate phases may overwrite a field only through an explicit ordered dependency.

For a synthetic anchor example, let `old` be the base reversal history and `current` the corrected endpoint. The desired generic test can assign:

```text
anchor_previous_next = old.anchor_initial
anchor_initial_next  = current.coordinate
```

Both reads remain independent of write order. Another phase may explicitly read `anchor_initial_next`; it cannot read an unqualified mutable `new.anchor_initial`. A simultaneous swap fixture must also preserve both old values. This example tests the engine, not PM4Sand3D's unresolved step19/20 algorithm. The PM4 JSON shows analogous copies **disabled**, with source blockers attached. Likewise z_in must specify whether its snapshot is before or after the same-step fabric update; “new fabric” is insufficient.

For a future phased contract, evaluate a guard before its selected assignment RHS and selected derived dependencies. Nonfinite guards fail; inactive invalid RHS is not evaluated. When using the legacy sign rule, only a finite guard strictly below zero fires, without inferred tolerance. This future lazy phase evaluation must not change legacy eager shared-derived evaluation. Preserve that legacy behavior explicitly in its adapter.

Expressions remain typed scalar/symmetric-tensor DSL expressions where supported. Snapshot-qualified references are a proposed symbol-table binding, not new textual operators already accepted by `atlas/dsl.py`. Do not inject arbitrary C++/Python expressions or resolve an unknown field dynamically. Existing `_n` retains its existing previous-internal-substep meaning under the legacy adapter; it is not silently rebound to the original caller parent or a whole-zone snapshot.

## PM4Sand3D phase skeleton and blocked edges

[Tables3.1–3.2, pp76–77](https://itasca-software.s3.amazonaws.com/udm-library/Kippen_et_al_PM4Sand3D_v1_CGM-26-01.pdf#page=81) document this skeleton:

| Phase | Inputs and outputs | Admission condition |
|---|---|---|
| Preparation | Host current stress and input/default provenance → initialized history and caches | Resolve signs, floors, equality/domain branches and later reset/default behavior. |
| Per-subzone trial | Base state plus shared committed D/Kp/G/K and subzone strain → provisional stress/backstress/direction | Complete plastic law, corrections, subzone parent and stabilization scope required. |
| Complete-zone reduction | All subzone outputs and weights → averaged increments, p, stress, alpha, n and rotations | Exact weights, completion and normalization treatment required. |
| Corrected zone | Averaged values → consistency/bounding correction, images and reversal predicate | Corrections and event input stages required. |
| Next D/Kp | Past averaged response/history → coefficients for **next caller step** | Full old/new dependency map required; do not replace with immediate state reevaluation. |
| Fabric/history | Plastic volumetric increment and staged D → fabric, cumulative/peak/product/pressure and reversal fabric | Resolve D=0, product typing/aliases, peak rule and snapshot ordering. |
| Surfaces/moduli | Updated fabric and state → g, density/state index, surfaces and base G/K | Exact volume law and initialization normalization required. |
| Reversal anchors | Corrected endpoint plus base histories → new anchors and accumulators | Step19/20 duplication, extrema/app/true relation and unnamed accumulators unresolved. |
| Rotation/PostShake | Candidate mechanical/history/cache values → final staged snapshot | Initially zero spin only; PostShake domains and mode semantics must be admitted. |

The manual's intermediate “commit” operations describe local stage values. They do not authorize durable publication before zone completion or outer-control acceptance. The JSON lists source blockers for every phase; the skeleton has **no executable model dispatch**.

Full FLAC3D scope also requires host-owned subzone stress, its mixed-discretization stress handling, zone-level common histories and independent parallel hourglass resistance. A proposed homogeneous single-subzone reduction must state which operations reduce to identities and whether stabilization is excluded. It must not advertise full-host equivalence. Large-strain rotation of all historical tensors remains unsupported.

## Caller boundaries, subdivisions and observations

The caller increment is the declared discrete algorithm boundary. For PM4Sand3D the manual describes explicit integration without constitutive substeps and D/Kp lagging one caller step ([Sec3.2 pp71–72](https://itasca-software.s3.amazonaws.com/udm-library/Kippen_et_al_PM4Sand3D_v1_CGM-26-01.pdf#page=76)). The initial source-matched capability should therefore reject a failed full material trial, allowing the caller to submit an explicitly refined path with recorded new boundaries. It must not hide half steps while claiming the same lag/event algorithm. A future subdivision policy needs its own source/reference evidence and capability label.

Legacy parent-increment resets already select a simultaneous reset once from parent and the complete candidate increment; that selection stays frozen through inner Newton iterations, midpoint/error-estimator trials and recursive cutbacks. Continuous state and `_n` still evolve per internal substep. Preserve this policy exactly. A caller split evaluates a fresh parent reset and can change the response; do not promise partition invariance. A timed ODE retains its stage time/rate semantics and atomically commits clock; a caller-history envelope must not add `de` or previous-state hidden arguments to its ODE RHS.

An observation is distinct from a material update or command. The recorded driver currently preserves history for exactly repeated targets and skips integration. Keep that behavior. New reset/mode commands require an explicit command boundary; they cannot disappear because targets repeat, nor may observations manufacture a zero material increment. Legacy explicit zero increments may still fire a declared negative reset guard. Physical-time holds remain positive-duration updates even when strain is unchanged.

Every outer candidate uses the same immutable committed parent and pending command. Provisional FirstCall preparation can be recomputed for each candidate deterministically; its epoch advances only on the selected commit. It cannot be consumed by the first failed Newton probe. Caches keyed only by current stress or field values are unsafe: trial memoization, if added, must include model/source, contract, parent/preparation identity, full candidate loading, command, settings and stage. Initial implementation should keep such memoization transaction-local.

## Initialization, resets and user modes

`assign_material` and `FirstCall_zero` are explicit preparation transactions. [Table3.3 pp78–79](https://itasca-software.s3.amazonaws.com/udm-library/Kippen_et_al_PM4Sand3D_v1_CGM-26-01.pdf#page=83) initializes from current host stress, may correct that stress, resolves initial values and histories, and sets D=0/Kp=100G. A later FirstCall reset erases specified history from the **current** stress; it does not restore the original specimen. Record pre/post stress, supplied/default values and the successful preparation epoch. Exact reset recomputation of effective defaults remains blocked.

PostShake is a user-selected mode, initially off; it is not inferred from elapsed time, pore pressure or a loading reversal. The proposed command boundary makes the mode available for the next declared caller update and applies stiffness reduction at the source's end-stage ordering. This interface choice needs explicit source-reference tests before admission. Apply Fsed to conventional newly computed G/K, not cumulatively to already reduced moduli. Do not assume turning the mode off repairs history. Ordinary restart restores the saved mode/caches without FirstCall, renormalization or implicit fabric erasure.

## Migration and acceptance gates

1. **HIST-G1: isolation.** Keep this proposal outside model directories. Existing loaders reject its version/shape; no candidate becomes executable. Confirm catalogue model definitions/hashes remain unchanged.
2. **HIST-G2: typed validation.** Implement a separate experimental envelope schema with declared capabilities. Synthetic layouts fit current limits. Reject unknown scopes, untyped shapes/units, missing lag fields, invalid enums, future reads, cyclic phases, conflicting assignments and unbounded host layouts.
3. **HIST-G3: independent transaction oracles.** Use simple arithmetic fixtures with analytically known histories: simultaneous swaps, ordered old/new copies, positive/zero/negative guards, inactive invalid RHS, nonfinite guard, failure after preparation and later provisional work, failed second internal half, and incomplete host reduction. Verify every retained field, epoch/mode and applicable time/strain stays at the original parent on failure. Diagnostic work may increase.
4. **HIST-G4: legacy adapters.** Run existing parent-reset fixtures unchanged, including eager-derived failure, `_n`, frozen resets across cutbacks, zero increment and intentional caller-partition dependence. Preserve five-model references, recorded finite-difference/restart isolation, duplicate observations and exact accepted prefix, and physical-time/timed-schedule stage clocks/holds/failure rollback. No new semantics reach existing model versions.
5. **HIST-G5: restart and lineage.** Serialized complete snapshots reproduce subsequent endpoints. Reject wrong model/source/contract/epoch, omitted lag/stage or required preparation fields. Reset commands publish once, failed probes do not consume them, and restoring a snapshot does not invoke initialization. Reordering output observations cannot change material evolution.
6. **HIST-G6: PM4 source gate.** Resolve the JSON's source blockers, or exclude the affected capability explicitly. Obtain independent source review of initialization, reversal/extrema, fabric-pressure history, density, lag stages and the exact selected implementation/version. No amount of generic engine testing closes scientific gaps.
7. **HIST-G7: bounded model evidence.** Define zero-spin homogeneous scope and compare source-matched reference trajectories for initialization/reset, tiny reversal loops, fabric/peak-pressure history, caller-step refinement and lag partition effects. Specify errors, tolerance, settings, source locators and retained data. Test stabilization separately if implemented. Do not assert caller-partition invariance as a generic expected result.
8. **HIST-G8: runtime evidence.** Only after the Python reference and source gates, run controlled serial native/Wasm checks with the same fixtures and explicit contract versions, respecting the current build caution. Publish honest supported/unsupported capabilities; numerical/independent-review status changes require their separate evidence.

Implement the Python validation/interpreter reference before code generation. Then design typed buffers and the coupled AD unknown layout from resolved fields, rather than copying every persistent field into Jet. Preserve the legacy `State`/API path through identity adapters; any new public result envelope is versioned and negotiates required capabilities before evaluating inputs. This packet adds no kernel, public API, schema parser change, state-capacity increase or build requirement.

## Python reference progress

The separate [typed Python history reference](HISTORY_REFERENCE.md) now implements a bounded scalar/symmetric-tensor envelope, explicit immutable phase bindings, guarded simultaneous writes, preparation ancestry, finite-intermediate checks and atomic rollback. Its arithmetic regression fixtures advance HIST-G2/G3; native/legacy adapters, host reductions, source-blocked PM4 equations and scientific/runtime admission remain separate gates. The PM4 design example above is still not an executable program.
