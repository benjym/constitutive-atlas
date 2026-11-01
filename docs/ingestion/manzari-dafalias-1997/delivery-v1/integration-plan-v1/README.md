# MD1997 E6/E7 integration map v1

Read-only planning artifact, 2026-11-02. Owner `/root/md1997_source`; coordinator `/root` owns implementation, policies, builds, approval and browser observations. No compiled code, generated production package, browser acceptance or scientific approval was produced in this task. Paths below are proposed changes, not completed changes. See `live-inputs.json` for the inspected byte identities and `browser-qualification.md` for prospective observations.

The exact candidate is `docs/ingestion/manzari-dafalias-1997/delivery-v1/manzari-dafalias-1997-constant-m-be-v1.json`, SHA-256 `28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064`. It belongs in the ordinary engine and general atlas laboratory. Its first persistent state is effective Mandel stress; persistent scalar e and symmetric alpha are already supported by generic fields, and the temporary gamma starts at zero through the existing state contract. No dedicated page or MD-specific app branch is needed.

## Current baseline and preservation

At capture, `models/*.json` contains 15 ordinary definitions. `atlas.model.all_models()` loads exactly that top-level glob. The isolated committed 8718467 engine has 12 ordinary definitions and cannot replace this catalogue; see parent `../integration-baseline-assessment-v1.json`. The new common engine must contain every then-current ordinary definition plus this exact candidate (16 if membership is unchanged). Preserve exact existing bytes, including Ramberg–Osgood, Duncan–Chang and OCC; re-inventory immediately before integration if concurrent work adds more.

The current supported-package policy covers 14 models and omits Ramberg–Osgood. The profile policy also retains older prose referring to twelve models. These policies do not certify the current 15-model package, much less the proposed 16-model package. `tools/test_supported_package.mjs::validatePolicy` requires policy IDs to equal all compiled IDs and exact definition hashes. Freeze a distinct current-closure qualification policy and cases before any new compiled observations; do not silently relax the old policy or reinterpret old passes. Preserve the GIS declared ordinary failure and its exact named supported example, OCC cyclic-stress limitation/failed prefix and total-stress legacy rejection. MD ordinary drained and undrained +1%/100 must succeed under its frozen model policy; no full plastic-cycle support claim follows from that.

## Minimal coordinator edits and records

| Path | Required content and consumer |
|---|---|
| `models/manzari-dafalias-1997-constant-m-be-v1.json` | Copy exact reviewed candidate bytes, no metadata edits after review. Root compiler and ordinary UI discover this file automatically. |
| `docs/models/manzari-dafalias-1997-constant-m-be-v1.md` | Public dossier: original DOI/source locators; constant-m Table1 identity; first b_ref branch; BE/unit-normal implementation choices; all parameter/state/sign/scope conventions; illustrative preparation; precise qualification and exclusions; links to retained public review/evidence. No private scans. |
| `catalogue/manifest.json` | Add one exact executable row: id, name, family, status, executable:true, dossier safe `docs/models/*.md`, discovery_url DOI, bounded note. Existing source candidate metadata may remain draft: dynamic approval comes from registry. Preserve family ID `manzari-dafalias-1997` as non-executable bibliographic family and revise its obsolete capability-gap note to distinguish this exact constant-m realization from optional evolving-m branch. No duplicate executable family row. |
| `catalogue/agent-reviews/<new-md-review>.json` | Separate reviewer’s actual accepted checklist, exact final `models/...` path/hash, source/numerical evidence and limitations. Review against candidate location alone is insufficient if intended final path differs: coordinator/reviewer must bind final identity through normal policy. Never synthesize acceptance from prospective review. |
| `catalogue/approved-models.json` | Append actual `atlas.agent_review.approval_entry` result for exact accepted review; preserve existing entries. Shape includes id/model_id/status/approved_on, independent-agent approval_authority, definition path+sha256, scope, review kind/path/hash, limitations/supporting_files, experimental_validation and deployment_authorized. Do not hand-invent authority or deployment. |
| `catalogue/evidence/<new-md-envelope>.json` | Optional but useful numerical envelope; must validate with `atlas.evidence`, bind exact model bytes and retained checker/manifests/outcomes/scope. Auto-discovered by build_evidence. Raw delivery reports are not auto-discovered as numerical envelopes. Alternatively accepted review indexes its actual artifacts without inventing an evidence envelope. |
| New current-closure policy/cases under coordinator-owned delivery path | Full prospective ordinary/profile coverage, exact 15+MD hashes (or larger current membership), retained historical exceptions and new MD scoped requests. Existing root default policy pointers may be updated only after preserving old bytes/identity and qualifying new policy. |
| `catalogue/laboratory-examples.json` plus `protocols/<new-id>.json` | Optional named input only if needed; ordinary defaults already expose the illustrative state. Manifest row: id, model, label, description, definition_sha256, document_sha256, evidence_url HTTPS, document_path matching `protocols/[a-z0-9-]+.json`. Actual retained export must match exact compiled catalogue hash; do not fabricate results. No example is necessary merely to make model discoverable. |

No schema/compiler/C++/CMake/app changes are indicated by the inspected consumer contract. No support declaration is currently required for MD: `catalogue/laboratory-control-support.json` contains specific unsupported controls, not a scientific qualification list. Do not add an unobserved failure or advertise cyclic support because it is absent. Applicability/experimental overlays do not gain validation from source/model approval. Publications/screening are independent bibliographic records; only amend with actual supported data if the coordinator identifies a missing binding.

## Evidence and database consumers

`tools/build_evidence.py` requires canonical catalogue IDs for numerical and source-review records. `atlas.review_export.collect` omits agent reviews without a matching catalogue ID and validates retained exact review artifacts. Accepted status displays as approved only when definition_current is true and registered_approval_id is non-null (`web/app.js::registeredModelReview`). Historical acceptance never approves changed definition bytes. It publishes only review/definition/registry JSON, never raw private source artifacts. Dossiers become raw `.md` plus `.md.html` escaped-text views. Do not link a nonexistent generated view before packaging.

`tools/build_database.py` requires packaged `models.json` to equal current `all_models()`, and `catalogue.json` to equal the live discovery manifest. Database ordinary executable membership must equal top-level definitions; approved dedicated definitions are additional database entries with their own scope. It records current model/source/approval/review inputs. Preserve its integrity, foreign-key, exact definitions, approvals, reviews and provenance checks. Existing public measurements remain outside this database.

## Build and package handoff

Coordinator must use a new closure based on the current root sources and inventory, not copy the 871 catalogue. Native then Wasm serial targets require explicit build-slot ownership; this plan gives no execution authorization. Freeze toolchain/source/model/runtime hashes and a current-catalogue regression plan before runs. Retain build logs and failed reports.

Package into a NEW explicit output path using `tools/build_web.py --output <new-local-package> --wasm-dir <current-common-build>` and explicit qualified dedicated directories. The builder regenerates current common metadata in a temporary directory and requires byte-identical common `generated/models.json`; an old engine fails as stale. This generator gate does not by itself certify numerical behavior. Do not use `--preview-experiments` for public delivery unless separately intended.

Preserve all seven existing dedicated packagers and their identities:

| Flag / bundle | Existing surface |
|---|---|
| `--power-creep-wasm-dir` (`engine/`) | approved physical-time power-creep; otherwise defaults to common directory containing its dedicated artifacts |
| `--burgers-wasm-dir` (`engine-burgers/`) | main timed Burgers laboratory |
| `--sls-wasm-dir` (`engine-sls/`) | main SLS laboratory/controller router |
| `--j2-wasm-dir` (`material-point-j2/`) | main J2 material-point laboratory |
| `--controlled-path-wasm-dir` (`engine-path/`) | original NorSand active axial controlled-path interface; exact qualified artifact or fresh receipt |
| `--maxwell-wasm-dir` (`engine-maxwell/`) | main Maxwell interface with current-build qualification receipt |
| `--implicit-path-wasm-dir` (`engine-implicit-path/`) | original Lade–Duncan implicit-path interface with exact qualified receipt |

Bundle builders validate exact approval/source/catalogue/runtime receipts; changed shared consumers can require fresh qualification. MD normal-model work does not authorize removing these checks or recertifying them with old binaries. Additional concurrent profiles (e.g. Kelvin/Hill/orthotropic) are not currently called by this inspected build_web; re-read the live builder before packaging so newly integrated work is preserved too.

Coordinator checks after prospective freeze include `node tools/test_supported_package.mjs --directory <package> --policy <new-policy> --output <new-report>`, current scoped/legacy corpus using `tools/laboratory_profile_policy.mjs` with `tools/test_wasm.mjs`, `tools/test_scoped_parity.mjs` and `tools/test_browser_loading.mjs`, package/database validation, named-example validation, all dedicated package checks and actual browser qualification. These commands execute compiled engines and were NOT run by this worker. Inspect each command's current flags before execution. Preserve reports even when failed; strict all-default GIS result remains a separate retained failure.

## Remaining gates

E4 backend observations and separate E5 acceptance precede scientific registry integration. Current closure/native/Wasm/package checks precede E7 browser acceptance; see recipe. This read-only map establishes none of these passes. E8 live verification requires explicit remote publication authorization; local package/browser success is ready-to-publish evidence only. Parent maintains DELIVERY.md and board status.
