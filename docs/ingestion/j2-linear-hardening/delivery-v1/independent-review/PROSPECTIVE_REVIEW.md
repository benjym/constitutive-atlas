# Prospective J2 delivery interface review

REV-j2-delivery-interface-v1, independent reviewer `/root/j2_scientific_review`, 2026-11-01. Source-only review of the prospective delivery plan; final acceptance is pending exact frozen source, compiled saved results, package/interface and actual UI evidence. No build/backend execution or shared edits are authorized to this reviewer.

The exact mathematical definition and named material-point parameter/solver scope are unchanged. Reusing the original physical budgets and independent execution-v2 cases is appropriate; backend parity is supplementary to those references. The dedicated common-engine route must preserve model/engine/catalogue identity, common Mandel components, total Cauchy-stress scope and explicit eight-slot state. A separate interface acceptance may close the prior browser exclusion for documented cases; the historical v2 scientific checklist must remain unchanged.

Before observing new backend results, `check_preset.py` independently derives the three-row public preset with exact rational arithmetic. It imports neither Atlas expressions nor the parent's reference oracle. The first row is plastic, with alpha=gamma=1/775. The reversed second row is elastic, retaining alpha but resetting gamma to zero. The zero third row holds that complete endpoint. This path demonstrates unloading/reversal and reset, while the longer frozen histories supply additional reverse/nonproportional behavior.

Conditions to assess against code and saved evidence:

- Six strain-increment entries, six stress entries and alpha/gamma must use explicit labels/units/order. Gamma is temporary and not accumulated history. Row index is a path index, with no physical clock inferred.
- State advances only on successful rows. Runtime failure must expose the accepted prefix and last committed full state accurately; malformed whole-path import/parse rejection is a separate case. Recovery must use the same module and a valid committed state.
- Editing, import and reset must invalidate stale output. Export/import binds exact model and catalogue identities plus complete parameters, initial state, solver settings and all path rows. Corrupt, missing or stale identities cannot silently fall back to defaults. Restarts must not confuse transient gamma with persistent initialization.
- Package checks must exercise the copied engine, enforce embedded exact model metadata, reject stale combinations, and verify existing root assets/catalogue are unchanged. Reference/replay/parity gates need complete state and every strict-branch tangent row, rather than plotted stress only.
- UI arbitrary parameters/path rows remain exploratory. Neither editable inputs nor validation of parameter bounds qualifies the entire parameter envelope or arbitrary-path convergence. The named preset, finite BE steps, no internal subdivision, dry total stress, zero spin and absence of experimental calibration need visible disclosure.
- Actual browser evidence must establish the real exposed path, meaningful rendered values/plots, input changes, import/export/reset, failure/recovery and source/approval links. Passing Node/module checks alone do not establish browser usability or live deployment.

No source-only blocker is found in the prospective plan. This is not final interface acceptance. Public integration, packaged browser behavior, CI and live asset/run verification remain distinct later gates.
