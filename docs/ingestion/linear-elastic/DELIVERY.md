# Linear elasticity — end-to-end delivery ledger

- Umbrella task: MODEL-linear-elastic; child review SCI-linear-elastic-agent-v1.
- Lead / date: coordinating parent `/root`, 2026-11-01.
- Exact formulation: constant-E/nu isotropic infinitesimal elasticity, reconciled against OpenGeoSys commit `b5d0f115c75ee74a7cdbfad533625a550a416fda`.
- Scope: local compression-positive Mandel stress increments; constant moduli, fixed frame, zero spin. Atlas effective-stress interpretation and exponential void bookkeeping are explicit project choices. No finite rotations, coupled pore pressure, variable source fields, FE qualification or experimental validation.
- Source packet: [README.md](README.md); [receipts](source-receipts.json); [dossier](../../models/linear-elastic.md).
- Candidate: `models/linear-elastic.json`, SHA-256 `33387b2058a3f54ed611949318289db24ab2d5b8edd172d0a2454042c7975041`, historical schema0.1. Migration is separately owned; do not silently substitute an in-memory v0.3 crosswalk for migration of the actual candidate.
- Parent whitelist: this ledger and parent-owned board rows; reviewer owns only `docs/reviews/linear-elastic-agent-v1/`. Shared migration, registry, website and build work require a separate handoff.
- Implementation authors: historical run identities are not established; current coordination `/root`. Independent review run: `/root/linear_elastic_agent_review`.
- Build owner: coordinator, serial explicit targets with `--parallel 1`; no build or compiled execution authorized in this review task.
- Remote authorization: previous user instruction permits the bounded 12-model website refresh. A later reviewed release needs scope reconciliation before publication; this ledger does not authorize remote activity.

Use the [canonical E0–E8 checklist](../../MODEL_DELIVERY_CHECKLIST.md). These are delivery gates, not a count of existing documents.

- [X] **E0 — Claim/scope:** umbrella and independent review claimed on the live board; exact legacy variant and exclusions identified; reuse existing evidence.
- [X] **E1 — Sources:** readable originals, pinned public source links, hash/length receipts, complete source crosswalk and rights/access scope exist. All three originals are now durably retained in ignored repository-private storage; [retention receipts and checker](retention-v1/README.md) verify exact original acquisition identities. No source code was executed.
- [-] **E2 — Contract:** [crosswalk](formulation-crosswalk.json) checks the v0.3 interpretation in memory; actual candidate is still0.1. Separately owned migration and current integration/control contract must be verified before claiming this gate.
- [-] **E3 — Transcription:** exact legacy definition has analytical/source checks and unchanged identity; current v0.3 candidate generation awaits E2. No new production kernel is needed.
- [-] **E4 — Native/Wasm:** historical 29-case analytical evidence and saved backend/transaction evidence are review inputs. Fresh current-candidate/current-package qualification and applicable regressions are not proved by their existence.
- [X] **E5 — Agent approval:** actual separate review accepted the exact legacy scope; canonical record validates for approval, all output-manifest hashes verify, parent static reproduction passes, and [approval entry is generated](../../admission/linear-elastic-agent-v1/README.md). Registry integration/visibility remains E6; no current-build or migration claim.
- [-] **E6 — Atlas:** existing public inclusion is distinct from exact approved-definition integration. Verify approval, source/evidence export and current registry/catalogue identities after E5; preserve all legacy reviews.
- [ ] **E7 — Packaged website:** qualify the actual release package, visible bounded approval/source links, controls/plots, reset/import/export and failure recovery. Existing screenshots or prior packages do not prove the next release.
- [ ] **E8 — Live delivery:** release gates and live artifact/model-run identity remain unverified. The earlier 12-model refresh run failed native jobs and skipped deployment; do not call this model fully delivered on that basis.

## Current handoff

- State: working; E5 accepted; E6 registry insertion verified, export/visibility pending, with the E2 migration dependency recorded; E1 private retention verified.
- Reviewer handoff: accepted; [review and source/numerical checks](../../reviews/linear-elastic-agent-v1/README.md) retained unchanged.
- Next coordinator action: complete normal approval/source/evidence export and visible scope checks; coordinate migration without modifying historical evidence. Scope a release only after required current-definition/package checks.
- Retained failure: reviewer rerun of the historical admission preflight reports `pinned input changed: docs/FORMULATION_CONTRACT.md`. Preserve the failed invocation and assess the document delta separately; do not repin it to make the old check pass.

## Evidence index

| Claim | Exact input / checker | Evidence and limits |
| --- | --- | --- |
| Source mapping, conventions and initialization | `python3 -B docs/ingestion/linear-elastic/check_crosswalk.py --repo .` | [Crosswalk checks](crosswalk-checks.json): eight contract checks and30 rational stiffness columns; in-memory v0.3 validation is not migration. |
| Native analytical cases | unchanged legacy model | [Evidence envelope](../../../catalogue/evidence/linear-elastic-analytical-v1.json), [saved report](../../../catalogue/evidence/reports/linear-elastic-analytical-v1.json):29 cases; historical execution, not fresh current-package qualification. |
| Admission questions | EL-01–05 | [Decision sheet](../../admission/production-readiness-v1/linear-elastic.md): unsigned historical questions, superseded approval mechanism; retain original bytes. |
| Independent agent review | actual separate run | [Accepted actual record](../../../catalogue/agent-reviews/linear-elastic-agent-v1.json) validated by reviewer and coordinator; parent replay is static/saved evidence only. |

## Review, integration and deployment receipts

Accepted canonical record SHA-256: `ff9fef9bc608fbe276d70253f68d648201e4df05a99e4b1f24023072c1652f39`. Generated entry: `docs/admission/linear-elastic-agent-v1/approval-entry.json`. [Registry insertion](../../admission/linear-elastic-registry-v1/README.md) is verified. Website export/visibility, current native/Wasm receipts, packaged catalogue/engine identity, release commit, successful Actions/deployment URL and live browser evidence remain **pending**.

Experimental validation remains unassessed. This baseline is an illustrative material-point law, not an experimentally calibrated soil model.
