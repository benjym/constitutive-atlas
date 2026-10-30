# Experimental parent-increment resets

This additive legacy-schema capability implements one explicit transaction scope. It is motivated by the pinned [OpenSees implementation](https://github.com/OpenSees/OpenSees/blob/8a0273db3e2f5a14c05924a179c1e439500c852c/SRC/material/nD/UWmaterials/ManzariDafalias.cpp#L858), where reversal memory is selected before entering the constitutive integrator. It is **not a decision that this is the canonical SANISAND-2004 policy**. Original-paper extraction, initialization, variant reconciliation and independent comparison remain open. No public model opts into this capability yet.

## Definition

An optional `increment_reset` object is supported by schema v0.1:

```json
{
  "increment_reset": {
    "scope": "parent_increment",
    "updates": [
      {
        "target": "anchor",
        "guard": "(coordinate - anchor) * trace(de)",
        "value": "coordinate"
      }
    ]
  }
}
```

Each guard is a signed scalar expression in the existing typed DSL. A **finite value strictly below zero** triggers its assignment; zero and positive values do not. Guards may carry units because only their sign is used. There is no implicit tolerance or hysteresis band. A model needing a threshold must declare its dimensional expression and parameter explicitly. Nonfinite guards fail the transaction rather than selecting a branch. Triggered values must be finite and match the target's shape and dimensions. Inactive assignment expressions are not evaluated; shared derived expressions are evaluated eagerly from the parent snapshot and must be finite. Derived values of the prepared state must also be finite for reset-enabled models.

Targets must be distinct persistent state fields. Transient multipliers cannot be reset this way. All guards, values and derived expressions read the same immutable parent snapshot and the complete candidate Mandel strain increment `de`; `_n` aliases that same snapshot. Assignments are simultaneous, so update order supplies no dependency or priority. There is no secondary reset cascade. The reset definition is included in canonical JSON, generated descriptions and catalogue hashes.

## Transaction and differentiation

1. Validate the supplied parent, parameter bounds, state scales and finite increment using the existing incremental API checks. A reset cannot repair an inadmissible parent.
2. Copy the parent. Evaluate the reset specification from that parent and candidate increment. Check finiteness and the ordinary domain of the prepared state. Initial-only checks apply to the supplied initial state, not again to the prepared snapshot.
3. Run continuous integration from the prepared snapshot. Within the constitutive Newton solve, error-estimator probes and recursive cutbacks, the selected reset is frozen. Existing `_n` semantics remain the previous internal substep, initially the prepared state. Resetting a memory field does not automatically freeze its subsequent equation: the model must specify zero rate or an appropriate residual if it should remain constant.
4. On success, return the integrated state, including the reset memory. On any failure, return the **original supplied parent**, including memory from before the reset. Work diagnostics still describe attempted integration; no event log is emitted by this subset.

Each outer mixed-control candidate invokes this pure transaction again from the same committed parent, with that candidate's complete increment. Neither rejected outer iterates nor finite-difference perturbations accumulate history. The reset is not differentiated inside the inner constitutive Newton system: it is a fixed starting state. Outer finite differences include its change when candidate loading changes; a guard crossing can therefore produce a nonsmooth control residual. A consistent material tangent through the reset map is not exposed.

## Caller partitions and event limits

`parent_increment` is an algorithmic boundary, not a located physical event. Guards do not rerun inside an increment even if their expression would later change sign. A caller split introduces a new parent evaluation and may change memory; this is expected and must be stated when comparing references. No partition invariance is promised across such boundaries. A reversal hidden inside a caller's loading path must be represented by explicit caller boundaries; the incremental API only receives one straight strain increment.

Zero increments follow the declared guard. The illustrated loading-dependent guard is zero and preserves memory. An unconditional negative guard can intentionally reset on a zero increment. This distinction is tested through a simultaneous-assignment fixture.

This subset does not support accepted-substep resets, continuous event location, event priorities, physical-time resets, DAEs or event logs. Those require separate contracts if the extracted equations demand them. Schema v0.2 rejects `increment_reset` rather than guessing its timed meaning. Models lacking the optional object retain their equations and numerical update rules.

## Source relationship

The primary implementation revision is `8a0273db3e2f5a14c05924a179c1e439500c852c`; its raw source hash is recorded in the [source audit](../catalogue/source-audits/sanisand-2004-opensees.json). `integrate()` (lines 858–895) computes a trial elastic direction from the candidate strain change and tests its double contraction with committed backstress minus committed reversal backstress. Negative selects committed backstress; otherwise committed reversal memory is restored. The selected memory is passed to the chosen internal integration routine. `commitState()` (lines 369–414) promotes trial memory; `revertToLastCommit()` (lines 414–418) is unimplemented. The 3D wrapper's `setTrialStrain()` (lines 78–85) negates the external strain and calls `integrate()`.

These observations justify separating parent selection from internal continuous integration. They do not establish complete reference equivalence. In particular, the source uses a mutable elastic matrix `mCe`; Atlas expressions in this subset recompute derived values from the supplied parent. The source shear/sign mapping and initialization still need reconciliation. The [original publication](https://doi.org/10.1061/(ASCE)0733-9399(2004)130:6(622)) was not obtained during this implementation; the publisher PDF request returned HTTP 403 and the inspected institutional record supplies metadata. No third-party source is redistributed or executed.

## Analytical acceptance cases

All fixtures are engine tests, excluded from the public catalogue. The base law uses `sigma_dot = p_ref * de`, `coordinate_dot = trace(de)`, and `anchor_dot = 0`, where the dot denotes an increment-scaled rate, not seconds. With `coordinate=1`, `anchor=0`, and axial increment `-0.5`, preparation gives `anchor=1`; the exact endpoint is `coordinate=0.5`. The equivalent implicit fixture uses linear backward-Euler residuals. A six-step loading sequence tests repeated unloading/reloading, multiple reversals and zero increments.

The nonlinear fixture uses `coordinate_dot = coordinate * trace(de)`, giving `coordinate_final = exp(-1)` under axial increment `-1`. It forces rejected trials and recursive cutbacks. Memory must remain the parent-selected value throughout. A second guard, `coordinate - 0.8`, starts positive and becomes negative along this path: one parent call must keep anchor zero; splitting into two calls evaluates the negative guard at the second parent and assigns the intermediate coordinate. This explicitly tests the declared partition dependence.

Other cases cover simultaneous swaps from a common parent, full Mandel tensor assignment, dimensional guards and `_n` aliases, inactive invalid value expressions, nonfinite guards/triggered values, domain failure immediately after reset, and a later domain failure after successful internal work. All failures preserve the complete original state. The outer drained-control fixture has independent isotropic stiffness and a zero-lateral-increment solution, so repeated Newton trials have an analytical final coordinate and anchor.

```sh
cmake --build build --parallel 2
python3 -m unittest discover -s tests -p test_parent_reset.py -v
ctest --test-dir build --output-on-failure
cmake --build build-wasm --parallel 2
node tools/test_time_wasm.mjs
```

The shared analytical case matrix is `tests/fixtures/parent-reset-cases.json`; Python preparation is checked against generated native integration, and native/Wasm runtime checks cover the same independent expected values. Existing five-model references, timed schedules and the Terracotta research cases remain regression gates. This verifies an engine capability, not constitutive scientific admission. SAN-03 remains open for selection and reconciliation of SANISAND's model-specific policy.
