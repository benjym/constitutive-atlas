# Implementation sequence and explicit proposed whitelist

Design handoff only. Coordinator must claim tasks and grant the following paths in a dedicated worktree **before** production edits. Existing dirty shared files, historical models, source-v1, capability-v1 and receipts remain untouched. Native/Wasm builds require coordinator serial slot, one explicit target and `--parallel 1`.

## A. Generic profile, transport and analytical capability

Proposed owned existing paths:

- `schemas/model-v0.3.schema.json`
- `atlas/model.py`, `atlas/compiler.py`, `atlas/stress.py`, `atlas/initialization.py`, `atlas/cli.py`
- `docs/FORMULATION_CONTRACT.md`

Proposed new paths:

- `atlas/controlled_time.py`, `atlas/controlled_time_compiler.py`, `atlas/controlled_time_native.py`
- `cpp/include/atlas/controlled_time_runtime.hpp`
- `cmake/controlled-time/CMakeLists.txt`
- `tools/generate_controlled_time.py`
- `tests/test_controlled_time.py`, `tests/fixtures/controlled-time/`
- `tests/test_controlled_time_native.py`, `tools/test_controlled_time_wasm.mjs`
- `docs/CONTROLLED_TIME_API.md`
- `docs/ingestion/vibe-2026/controlled-time-qualification-v1/`

Avoid edits to existing `atlas/path.py`, `atlas/path_compiler.py`, `path_runtime.hpp`, legacy material C++ or ordinary time C ABI by implementing separate additive modules. Reuse DSL expression generation, checked tensor/math helpers and model field metadata; no VIBE-specific handwritten kernel. Route new profile before common material generation. Implement explicit old-route rejection in `atlas/model.py` and initialization/CLI entry points; if code inspection finds another consumer that accepts solely via `physical_time`, report its exact path to coordinator for a separately recorded whitelist extension before editing. `atlas/schedule.py` takes a run spec, not a model; preserve old run schema and wire. New request schema/Python serializer goes in `schemas/run-controlled-time-v1.schema.json` and `atlas/controlled_time.py`.

Stage-A source review before build must inspect units, dimensions, binding roles, complete native checks, end-to-end rollback, initialization/right-rate transitions, newnet isolation and generated metadata. Freeze analytical references/gates/source hashes before compiled output. Coordinator builds `atlas_controlled_time_capability` native then Wasm, serially. Independent reviewer assesses raw outputs versus references and old-profile regression before declaring capability accepted.

## B. Generic browser transport and normal packaging

New generic paths:

- `web/controlled-time-engine.mjs`, `web/controlled-time-worker.mjs`
- `web/controlled-time-contract.mjs`, `web/controlled-time-laboratory.mjs`
- `tests/test_controlled_time_contract.mjs`, `tests/test_controlled_time_routing.mjs`
- `tools/build_controlled_time_laboratory.py`, `tools/test_controlled_time_package.mjs`

Integration paths granted explicitly by coordinator:

- `web/app.js`, `web/timed-laboratory.mjs`, `web/timed-route.mjs`
- `web/formulation-view.mjs`, `web/state-contract.mjs`, `web/stress-scope.mjs` **only where actually required by current code inspection**; absent paths are not invented files to create
- `tools/build_web.py`, `.github/workflows/ci.yml`

Keep build default packaging unchanged until a scientifically accepted exact model/approval exists. A separate synthetic fixture site can exercise generic consumer transport but never enter public model catalogue or masquerade as VIBE. Normal package builder later includes exact approved model and receipt bytes; compiled identity and browser module hashes are checked. Actual browser qualification is an explicit coordinator handoff after frozen packaged reference corpus, not a worker's incidental smoke test. Browser all-controls/restart/hold/profile/error checks and old routes belong to E6–E8, not merely source review.

## C. Exact VIBE scientific candidate and atlas admission

Dependent on reviewed complete source-v2 and capability qualification. Proposed new paths:

- `models/research/vibe/vibe-2026-explicit-appendix-a.json` (final ID coordinator/source-approved)
- `docs/ingestion/vibe-2026/candidate-v1/`, `execution-v1/`, `scientific-review-v1/`, `browser-v1/`, `release-v1/`
- `docs/admission/vibe-2026-approved-v1/`, `catalogue/agent-reviews/vibe-2026-agent-v1.json`

Explicit coordinator integration only:

- `catalogue/manifest.json`, `catalogue/approved-models.json`, `web/model-profile-data.mjs`
- `docs/models/vibe-2026.md`, `docs/ingestion/vibe-2026/DELIVERY.md`, `CHECKLIST.md`, `README.md`
- Own rows/paragraphs in `IMPLEMENTATION_PLAN.md`, `ROADMAP.md`, `docs/STATUS.md`

User authorized full delivery, but completion requires accepted model review, normal catalogue/database/export/profile/mainlab integration, exact native/Wasm/package/browser checks, authorized commit/push, all required exact CI/Pages jobs terminal-success, exact live upload asset proof and actual live profile/control/replay checks. No standalone page. Parent remains lead throughout these handoffs and records all53 criteria honestly. Source/capability completion alone does not close MODEL.

## Resources and cleanup

Track each worktree, build/module, fixture/site extraction and preview process in DELIVERY before creation. Preserve raw runs/failures, exact binaries needed by receipts, unique screenshot/export evidence and private source originals durably with hashes/recovery proof. Remove only owned disposable copies after consumers/reviewer finish; stop confirmed own preview PIDs. Clean completed worktree uses nonforced `git worktree remove`, after retained commit/ignored-evidence proof. This design worker created no temporary process, build, download or worktree; its sole resources are small durable capability-v2 files.
