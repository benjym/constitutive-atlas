# Retrospective delivery audit

The constitutive model and its retained numerical evidence remain sound within
the approved both-active scope. **The complete delivery loop does not yet pass
E0–E8.** The earlier commit/push and local website work were real; they did not
establish full browser lifecycle support or live availability.

## Findings

1. **E6 — material export loses model identity/approval.** `atlas/research.py`
   `export_database()` loads only top-level `all_models()`. The nested timed
   definition is present in the canonical catalogue, but SQLite emits it as a
   candidate, without definition JSON or approval. Source URL survives. Reproduced
   with the ordinary `atlas.cli database` exporter, not inferred from source only.
   Generic timed/research approval/definition export needs a separately owned fix;
   no migration into the strain-path public runtime is justified.
2. **E7 — browser coverage and functionality are incomplete.** The dedicated page
   supports actual creep/relaxation, parameter controls, plots and full JSON export.
   It lacks import/replay, reset and complete six-component state inspection.
   Current actual-browser evidence does not qualify invalid-input/recovery,
   parameter/initial-state changes or latest-request behavior. Add/qualify the
   missing exposed lifecycle before full E7 completion. State measurement-overlay
   applicability explicitly; illustrative coefficients are not experimental data.
3. **E8 — deployment is unverified.** The exact pushed run was still in progress;
   Linux Wasm passed, other required jobs not terminal. Live page returned404.
   All gates, exact deployed upload/asset comparison and an actual live run are
   still required. The umbrella remains open.
4. **E5 — new formal review format was missing.** The real separate-agent review
   and prior explicit-user approval remain valid for their scope. The original independent agent has now authored an accepted
   nine-item exact-hash reconciliation under review-v2. Coordinator validation and
   approval-entry generation pass; no technical decision was invented. The new
   generated entry is retained for E6 integration; prior user approval is preserved.

## Checks and preservation

`check.py` verifies475 historical manifest file hashes, exact nested-model loading
and isolated generation, and reproduces SQLite loss of definition/approval. All
integrity checks pass. The admission checker also passes, including durable
private extracted-text hash retention. Original ingestion29checks pass. No
compiled observations, builds, model changes or historical receipt rewrites are
part of this audit. The original loose-setting numerical failures, source403 and
unrelated strict GIS default failure remain retained.

See [DELIVERY.md](../DELIVERY.md) for stage-by-stage evidence and next owners.
This audit is a check against the new requirements, not a claim that missing
functions were implemented or that pending CI passed.

The audit is complete; the MODEL umbrella remains open on E6–E8. The new formal
review is accepted for bounded material-interface scope, with no constitutive
blocker. This does not waive the documented delivery gaps.
