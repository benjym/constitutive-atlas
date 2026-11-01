# J2 integrated main-laboratory interface proposal

WEB-j2-main-laboratory-v2, 2026-11-01. This is a reversible source-only proposal, prepared while the main application routing choice was pending. No production/shared file, standalone page, engine, scientific definition, approval or historical v1 evidence was changed. No build or compiled artifact was executed. Concurrent Burgers files were read as an interface pattern only; this module has no dependency on them and does not claim they are committed.

## Files and checks

`j2-laboratory.mjs` is the proposed new `web/j2-laboratory.mjs`; an exact copy is staged at `/private/tmp/atlas-j2-main-v2/web/j2-laboratory.mjs`. `test_j2_main_proposal.mjs` is proposed for `tests/test_j2_main_proposal.mjs`, and its exact staging copy is under the temporary `tests/` directory. The staging `web/j2-contract.mjs` is an unchanged copy of the already qualified production contract; its source identity is recorded in `manifest.json`. Only copies under the authorized proposal/temp paths were written.

Reproduce source-only checks:

```sh
node --check /private/tmp/atlas-j2-main-v2/web/j2-laboratory.mjs
node docs/ingestion/j2-linear-hardening/delivery-v2/interface-proposal/test_j2_main_proposal.mjs /private/tmp/atlas-j2-main-v2
node tests/test_j2_contract.mjs
```

The retained outputs record 56 pure DOM/API/source assertions and the existing 51 qualified pure-contract assertions. Tests mock DOM and pending fetch; no actual fetch, engine call or Wasm compile occurs. They check sibling mounting, shadow-scoped IDs/styles, main selector addition, lazy loading, deactivation without altering ordinary/concurrent visibility, hidden equations, delayed initialization failure after deselection, retry on reselection, stale-import cleanup after reselection and absence of retired standalone paths. These are not browser, backend, package or scientific qualification.

## Module contract

`setupJ2Laboratory({cancelOrdinary})` mounts `#j2-material-laboratory` immediately after the ordinary `#laboratory > .lab-layout`. All form/result/style IDs live in an open shadow root. It appends one option to the main `#model` selector and returns `{modelId, active, select(id), showEquations()}`. `active` is a getter. `select(id)` returns true only for the exact J2 ID; `select(false)` or any other ID hides the J2 panel and invalidates its generation. It never unhides the ordinary layout, touches another module or writes the root summary/status/chart/export controls. On explicit activation it calls `cancelOrdinary` and sets the main selector value. Parent owns the shared summary and interface visibility.

The engine loads lazily on first selection, once per successful module instance. Per-run request inputs are cloned by the exact existing contract. Each awaited row checks the generation and active flag. Deactivation invalidates results and stops the next row; an in-flight engine initialization never auto-runs on inactive selection. Completion handlers require both current generation and active selection. Failed engine initialization can be retried by leaving and reselecting J2. A successful hidden initialization is reusable when J2 is selected again.

All six editable increment components, five parameters, complete eight-slot explicit state, component plots, every accepted state table, full request/result export, identity-bound import/replay, named reset, failure prefix and recovery behavior are retained. The loader hashes fetched engine bytes then imports the verified JS from a Blob, compiles the verified Wasm bytes and supplies the supported Emscripten `instantiateWasm` hook; it does not URL-refetch executable bytes. Blob URL revocation is in `finally`. The original exact contract and accepted a28068cb… law are unchanged. This interface claims neither experimental calibration nor broader constitutive qualification.

## Parent integration hooks

Parent integrates the module into committed main-app sources, independently of other owners' dirty files:

1. Copy the proposed module and test into the intended production paths; package `j2-laboratory.mjs` and the unchanged `j2-contract.mjs` with the root application. Import/setup it after ordinary form setup. Setup appends the J2 selector option; do not insert this model into the root twelve-model generated engine catalogue.
2. Centralize special-interface selection. First deactivate every other module, then activate the requested one, and finally have the parent set ordinary `.lab-layout`, `.workspace-links` and ordinary `#import-run` visibility based on the selected interface. An existing module that unhides ordinary on deactivation must not override the final parent visibility decision. J2 deactivation itself deliberately changes only its own panel.
3. Dispatch main selector changes, `#laboratory?model=<id>` routes and catalogue Explore through the same selector function. Recognize J2 as executable through this dedicated material-point route. Avoid ordinary `populate()`, `model()` fallback, experiment refresh or `simulate()` while a special interface is active; these could otherwise overwrite the header or submit an ordinary model. Use `showEquations()` before ordinary equation handling. Set the root J2 summary/source links in parent scope to the exact bounded law and assets below.
4. Ordinary selection must deactivate J2, restore ordinary controls once in parent scope, populate its own definition and run its own engine. Root import/export stays ordinary; J2 provides its complete import/export controls inside its shadow root. Parameter/state/path edits inside J2 do not bubble into ordinary listeners because those are attached to the ordinary form.
5. Guard every parent async ordinary result/header/summary/export update against the selected model and active interface. Browser qualification must deliberately delay J2 initialization and row processing while selecting J2→ordinary and back, verifying that ordinary headers/status/plots/export remain current and J2 can rerun.

## Builder assets and pending qualification

Do not invoke the retired standalone-page bundler. Parent's integrated builder should preserve the exact dedicated engine bytes and generated single-model catalogue, validate the current registry/approval/accepted review and generate these assets:

| Asset path | Required content |
| --- | --- |
| `material-point-j2/j2.js`, `j2.wasm` | Exact qualified dedicated generic engine artifacts |
| `material-point-j2/models.json` | Exact generated one-model catalogue |
| `material-point-j2/j2-linear-isotropic-hardening-be.json` | Exact a28068cb… approved definition |
| `material-point-j2/identity.json` | Existing complete identity keys; digests bind the exact files, model and catalogue |
| `material-point-j2/approval.json` | Exact current J2 approval |
| `material-point-j2/review.json` | Exact accepted independent law-review checklist |
| `material-point-j2/review.html` | Combined readable accepted law review (`#law-review`) and separately reviewed integrated-interface evidence (`#interface-review`), accurately marked pending until accepted |
| `material-point-j2/package-manifest.json` | Exact bytes of all new assets and integrated module/contract |

The identity keys remain `model,model_sha256,catalogue_hash,catalogue_sha256,module_sha256,wasm_sha256,approval_sha256,review_sha256`; renaming asset directories does not change those semantics. Module asset URLs resolve against `import.meta.url` for project-path hosting. No private original source is packaged. Rendered review links must target the new directory or source repository, never retired standalone pages.

Parent must freeze a new interface study before package observations, adapt the package checker to the new paths/main module, reuse the existing independently frozen preset/main/default/history references and original physical gates, and execute copied-module/package checks. Required real-browser checks include all six edits, complete state display, import/export/reset/corrupt import, accepted failure prefix and recovery, ordinary↔J2 transitions, delayed-load latest-request behavior, source/approval/review links and exact fetched/executed identities. Arrange a separate independent interface reviewer before claiming delivery. Push/CI/Pages/live verification are parent-owned and outside this source-only handoff.

A pre-handoff source inspection found stale import cleanup could clear a newer file selection after deactivation/reselection. The corrected proposal guards the post-file-text path and cleanup by active/current generation, and clears the successful file before run invalidates its token. A pure delayed-import test verifies the old import cannot clear the newer value or change its current status. The earlier proposal module and manifest are retained under `construction-v1/`; no compiled observation or acceptance gate was changed. Parent requested the combined `material-point-j2/review.html` asset; footer links now distinguish its law/interface anchors.
