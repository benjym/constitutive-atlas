# Burgers main-laboratory delivery review v1

Task **REVIEW-burgers-browser-v1**, actual separate reviewer `/root/burgers_scientific_review`; implementation/build/browser operator `/root`. This is an interface-delivery review of the unchanged model `burgers-itasca900-dry-zero-spin-ode`, SHA-256 `1452a27d5d3b50989ca66df5beb7f08e22434596800133983339466d3571933c`. It does not replace or mutate the accepted [core E5 review](../../../catalogue/agent-reviews/burgers-agent-v2.json).

**Verdict: accepted for the exact scoped local main-laboratory interface and package.** No unresolved blocker remains for the two hold protocols and recorded lifecycle coverage. This accepts the reviewed E6/E7 interface delivery; **E8 deployment/live verification remains pending**. It is not an approval of the dirty shared checkout, arbitrary exploratory inputs or a new scientific model decision.

The final package is `/private/tmp/atlas-burgers-delivery-v1/release-site`, from scoped source `/private/tmp/atlas-burgers-release-v1` based on `fbf0ed5871611213c2a21a0ebbcf728276c9c7b3`. Exact archived shared hooks are under `delivery-v1/release-source/`; new Burgers files match the reviewed root copies. Its twelve-model ordinary engine is distinct from the earlier dirty-checkout thirteen-model development package. The local identity's `release_revision` identifies the base commit; exact modified release bytes are pinned separately. It must not be described as proof those modifications were already committed/deployed at that base revision.

## Reviewed design and scientific scope

The main `index.html` laboratory gains a dedicated Burgers selector and project-relative `#laboratory?model=...` route. The ordinary strain-path model catalogue/engine remains separate from the timed engine. The dedicated assets live under `engine-burgers/`; retired standalone SLS/J2/power-creep pages are not reinstated. Catalogue discovery and the explore button route to the main timed panel rather than a standalone page. The final actual browser evidence supports this placement.

Two experiments are exposed: holding all six strain components for relaxation, or all six stress components for creep. They use the already reviewed physical-time common engine and backward-Euler step-doubling schedule contract. The interface does not implement constitutive equations in JavaScript. It displays axial total stress in kPa, accumulated axial strain and Kelvin strain in percent, all against seconds; complete final stress/history/strain/rate and provenance are inspectable. All five constants, twelve initial state components, initial strain/rate and clock are explicit. The unchanged nonlinear solve settings match the original examples. Mixed/ramped controls are engine evidence, not exposed browser choices.

The panel discloses dry uncoupled total stress, infinitesimal strain, fixed frame/zero spin, illustrative uncalibrated preparation and exploratory edits without a general accuracy guarantee. It explains why measurement comparison is unavailable. Browser availability and exact-definition approval do not establish specimen prediction, experimental validation, finite-rotation/FE/MPM qualification or the vendor centered algorithm.

## Contract and identity assessment

The 7-string/8-number `atlas_run_schedule` ABI request explicitly carries parameters, complete history, strain, initial rate, control wire, segment identity, clock and fixed solver settings. Imported JSON is scanned for duplicate names, overflowing numbers and inexact large integer inputs before use. Engine/model/approval/review provenance and the exact canonical request must match; imported response curves are discarded and the engine is rerun. Unknown/missing control fields now reject.

The timed API intentionally emits initial left and right samples at the same time. Both retain state/strain; the stress-controlled right event's six unresolved rates are null. Subsequent rates must be finite. The hardened contract checks history length, uniform sample times, event side/segment, stress observable binding, Kelvin trace, exact solver/units/version/parameters and initial/end state/time bindings. These semantics prevent an initial-event convention from being silently mistaken for an extra interval or a physical instantaneous stress-control rate.

The worker fetches/hashes module, Wasm, catalogue, exact model, approval and review bytes, then checks the actual engine descriptor against the packaged catalogue before running. The builder validates the accepted exact model review and integrated approval, regenerates the expected catalogue and rejects a stale engine descriptor. Hashes are integrity bindings to the package, not a cryptographic authentication of the publisher. Browser failure/recovery must additionally be demonstrated for the actual fetched assets; it is not inferred merely from static checks.

Each edit/run/import/model switch invalidates prior results, disables stale export, terminates the old worker and increments a generation token. Responses must match the current generation. Imported-file async work also carries that token, and each run has a timeout. Static inspection supports the intended latest-request behavior; actual lifecycle observations are required below.

## Independent checks and retained observations

[check_contract.mjs](check_contract.mjs) imports only the pure contract and saved JSON; it never loads Wasm. Its expanded **70 assertions** pass for valid holds/events/import mapping and invalid scalar/history/provenance/request/JSON/result mutations. [Initial diagnostics](contract-results-v1.json) recorded two hardening gaps: accepted unknown controls and off-grid interior times. The coordinator tightened those gates; [current results](contract-results.json) confirm both now reject, together with mutated side/segment, solver settings, units, version and parameters. These were interface-contract findings rather than evidence of an incorrectly calculated source trajectory.

[check_saved.py](check_saved.py) independently reassesses the saved final fresh 44-call/88-point-per-backend study and physical parity without executing binaries; verifies separate stress/Kelvin refinement and the corrupted-Kelvin rejection; compares actual downloaded final default/creep histories with original independent references; checks the earlier exact changed-input browser example by the previously reviewed closed forms; and checks every frozen build-source/archive and packaged identity. [Final results](saved-results.json) pass against the clean scoped release-build-v2, all **96** source-file archive hashes and all **16** coordinator-pinned package assets. The earlier 98-file dirty-checkout build and interim source/site mismatch in `saved-check-stderr.txt` remain distinct retained checkpoints, not the accepted release source.

The fresh final scientific assessments pass the unchanged gates and all 6,168 physical parity comparisons. Separate refinement improves endpoint stress `4.23654 -> 0.452406 Pa` and Kelvin history `1.01460e-6 -> 1.09904e-7`; a worsened fine Kelvin component now explicitly fails the new gate. Original assessor/record bytes are preserved.

| Actual browser download | Maximum stress error | Maximum Kelvin error | Maximum accumulated-strain error |
| --- | --- | --- | --- |
| Final relaxation | 3.26545 Pa | 1.16375e-7 | 0 |
| Final creep | 0 Pa | 5.40541e-7 | 5.40541e-7 |
| Earlier changed-input example | 2.93384 Pa | 1.55224e-7 | 0 |

All meet the existing 20 Pa/2e-6 source-reference budgets. The third row is explicitly the earlier package's individual exploratory example; it is not a broad clean-release parameter-envelope qualification. Final default and imported/reexecuted downloads are exactly equal as complete JSON, and all three final exports bind the exact final package identity.

I visually inspected the retained main-laboratory desktop and mobile screenshots, including the final scoped-release desktop: time axes, total-stress label, Kelvin/strain channels, model-specific preparation controls and unavailable-measurement explanation are legible. The coordinator's final actual browser record, [release-browser.txt](../../ingestion/burgers-itasca900/delivery-v1/release-browser.txt), passes default/creep runs, actual download/import-and-reexecute, reset and invalid-input recovery, ordinary linear-elastic switching, catalogue-to-main-panel navigation, all four internal source/review/approval/dossier links and a 390px viewport without horizontal overflow. It reports no page errors during the recorded lifecycle. Its `/release-site/` URL exercises project-relative resource loading. This is coordinator-operated browser evidence independently reviewed here, not a claim that this reviewer ran the browser/compiled engine.

The earlier second browser result additionally passes rejected-import recovery, custom coefficients/history/time, rapid latest request and deliberately corrupted Wasm hash rejection/recovery. Static inspection of the same final timed worker/lifecycle implementation and pure-contract replay support that bounded behavior; those extended scenarios were not all rerun in the final clean twelve-model wrapper. The third run timed out because its fixture awaited the word `complete` whereas the ordinary laboratory's real status is `✓ Response up to date`; the preserved corrected run waits for that actual status and passes. No product change or weaker numerical gate was needed. This explains rather than discards the failed probe.

The original package test initially reported 600 channel comparisons, including six nullable initial creep-rate slots; numeric subtraction alone did not distinguish null from zero. The final test now explicitly compares **594 finite physical scalars and six null masks**, and exact engine reexecution passes. This closes the regression-test precision finding without altering equations or tolerances.

## Final findings and handoff

No critical/high/medium blocker remains for the accepted local scope. The reported unknown-control/interior-time and nullable-mask concerns are corrected and checked. The new public dossier fixes current browser/source wording while retaining historical model/guide/review bytes. The clean scoped source removes unrelated dirty J2/OCC/shared-support/solver work from this release; this review pins its actual copies rather than assuming the root shared `app.js` is the release file. Workflow hooks build native before Wasm, one explicit target and `--parallel 1`, run the frozen study and invoke the package gate. This checks the workflow definition, not a yet-unobserved remote run.

Nonblocking boundaries: the two presets and recorded interactions do not qualify all positive coefficients/large times/history values accepted for exploration; a run can fail its budget/timeout. Instantaneous returned-rate accuracy, arbitrary histories, browser restart continuation and exhaustive accessibility/network-failure testing are not established. The final log asserts no page errors, not a comprehensive network capture from initial navigation. Earlier extended browser scenarios and their package identities are distinguished from final wrapper observations. Experimental validation remains unassessed.

[Reviewed inputs](reviewed-inputs.json) identify exact final implementation/evidence bytes and [package inputs](package-inputs.json) additionally pin relevant runtime dependencies and the ordinary reused engine. [Decision](decision.json) records this bounded technical verdict. [Manifest](manifest.json) pins the new review artifacts; the verifier checks hashes and pure contracts without compiled execution. The scripts read compiled files only to hash them. All new files are exclusively under `docs/reviews/burgers-browser-v1/`; this reviewer made no production, registry, law-review or board changes and no build/compiled/vendor call.

```sh
python3 -B docs/reviews/burgers-browser-v1/verify.py
node docs/reviews/burgers-browser-v1/check_contract.mjs
python3 -B docs/reviews/burgers-browser-v1/check_saved.py \
  /private/tmp/atlas-burgers-delivery-v1/release-site \
  --source /private/tmp/atlas-burgers-release-v1
```

Smallest next action: coordinator integrates this local delivery review, then performs separately authorized commit/CI/upload/deployment and compares the tested entry/engine/model/catalogue/approval/review bytes with live artifacts and an actual live Burgers run. A final commit identifier and live receipt must replace any inference from the local base-revision label. Do not mark E8/live delivery complete from this acceptance alone.
