# Modified Cam Clay — end-to-end delivery ledger

- Umbrella: MODEL-modified-cam-clay; coordinator `/root`, 2026-11-01.
- Exact formulation: legacy associated MCC with endpoint pressure/current-volume elasticity, M² ellipse/associated flow, normalized temporary multiplier and exponential total-volume/log-pc updates. These Atlas numerical choices and printed source conflicts are explicit.
- Definition: `models/modified-cam-clay.json`, SHA-256 `e075117e07a71a17a35ce47dac66172a0cc402860f5c6cf106f7883db5721a14`, schema0.1. Existing-record migration is separately owned.
- Scope: compression-positive Mandel effective stress, infinitesimal 3D fixed frame/zero spin; explicit caller stress, void ratio and preconsolidation pressure. Named default-parameter material-point cases only; no FE/finite rotation/physical time/general uniqueness or experimental claim.
- Sources/crosswalk: [packet](README.md), [crosswalk](formulation-crosswalk.json), [durable private retention](retention-v1/README.md).
- Authors: historical transcription run IDs unknown; current reconciliation `/root`. Actual independent reviewer `/root/mcc_agent_review`.
- Whitelist: coordinator owns this ledger, new admission packet, canonical review, exact generated registry entry and own board rows. Reviewer's output is separate. No shared schema migration/build/deployment in this task.
- Builds: coordinator-only serial explicit targets with `--parallel 1`; this integration performs no builds or compiled calls. No remote publication authority inferred.

Follow the [E0–E8 checklist](../../MODEL_DELIVERY_CHECKLIST.md).

- [X] **E0 — Claim/scope:** exact baseline, owners, existing evidence, exclusions and dependent integration work recorded.
- [X] **E1 — Sources:** original readable Silbermann–Nagel PDF privately retained and hash checked; full source crosswalk and source equation conflicts disclosed. Mutable hashless Itasca reading remains explicitly distinct.
- [-] **E2 — Contract:** in-memory v0.3 crosswalk and legacy discrete contract checked; actual candidate migration and current integration/control contract remain open.
- [-] **E3 — Transcription:** exact legacy model independently checked; migrated candidate validation/generation awaits E2.
- [-] **E4 — Native/Wasm:** 57 saved native cases and eleven matching frozen native/Wasm pairs checked. No MCC-specific Wasm failure/recovery or general serialization-restart qualification; current-candidate/current-package tests and regressions remain open.
- [X] **E5 — Agent approval:** separate actual review accepts all nine items for exact bytes and declared scope, no blockers. Coordinator reproduces saved-only independent checks and all 30 manifest bindings; [canonical acceptance and integration](../../admission/mcc-agent-v1/README.md).
- [-] **E6 — Atlas:** generated exact registry entry inserted; ordinary evidence exporter includes the accepted review, exact registered approval and unchanged definition. Current migrated database/package identity remains open.
- [ ] **E7 — Packaged website:** fresh matching release engine/catalogue, full controls/lifecycle/failure recovery and actual browser checks remain to be qualified. Export alone is insufficient.
- [ ] **E8 — Live delivery:** scoped authorized release, all required CI/deployment gates, exact live asset comparison and live model run remain unverified.

## Current handoff

Working; scientific acceptance and bounded registry/catalogue projection complete. Next: coordinate separately owned actual migration, then freeze a current-candidate numerical/interface qualification plan and release scope. Preserve all historical inputs and failures; do not reuse this acceptance for changed bytes without renewed review.

## Evidence and limitations

[Independent review](../../reviews/mcc-agent-v1/README.md), [parent replay](../../admission/mcc-agent-v1/parent-results.json), [integration checks](../../admission/mcc-agent-v1/integration-results.json) and [actual catalogue projection](../../admission/mcc-agent-v1/catalogue-projection.json) bind the current handoff.

The failed unpartitioned v1 and direct historical preflight failure remain intact. Exact archived preflight reconstruction does not certify changed root contracts. Actual-partition agreement is not adaptive error control or global uniqueness. Selected M² and volume-law interpretations are disclosed Atlas choices rather than an asserted author erratum. Experimental validation is unassessed.

Deployment commit, Actions/deployment URLs, matching current native/Wasm package receipts and actual live browser evidence are pending. The umbrella remains open.
