# Single-experiment ensemble explorer

Implemented 2026-11-01 for local exploration. `#ensemble` is an additive main-site
route with a fixed OPARA-TXCD-100 experiment, three existing models and editable
baselines plus one-at-a-time parameter variations. Default: 15 independent runs.
The existing model definitions, compiler and engine bytes were not changed.

The first 95 acquired observations end at 0.992% axial engineering strain. The
source's direct membrane-corrected radial effective stress is imposed alongside
axial strain; q and volume are compared outputs. All 1438 observations can be
shown for context. Measured volume contributes to the radial correction, so this
is conditional replay. Parameters are illustrative, and MCC's initial pc=200 kPa
is an editable unmeasured assumption. There is no calibration, ranking,
model–material admission or independent experimental validation claim.

## Implementation

- `web/ensemble.mjs`: strict experiment/request construction, explicit initial
  history, deterministic independent variations, bounds/domain rejections,
  exact catalogue/request/result-bound export and import with fresh replay.
- `web/ensemble-queue.mjs`, `web/ensemble-worker.mjs`: serial execution, worker
  cancellation, late-response suppression, retained errors/stopped prefixes,
  30-second per-request timeout, exact runtime catalogue identity check.
- `web/ensemble-view.mjs`, `web/ensemble.css`: editable inputs, two comparison
  plots, curve selection, visibility/context controls, outcomes and exact request
  inspection, stale-result handling, study and individual recorded-run exports.
- `tools/build_ensemble_web.py`: deterministic hash-checked source packaging.
- Additive hooks: `web/index.html`, `web/catalogue.mjs`, `tools/build_web.py`.
  Concurrent unrelated changes in those files are preserved.

## Verification

The prospective policy is [POLICY.md](POLICY.md); its tolerances were frozen
before compiled predictions. [wasm-results-v1.json](wasm-results-v1.json) retains
all requests, outputs, outcomes, engine hashes and independent elastic checks.

- 31 Node checks passed: 10 ensemble tests plus catalogue routing/evidence and
  existing package-contract regressions.
- 9 Python checks passed: ensemble source packaging plus existing recorded and
  catalogue packaging regressions.
- Existing matching five-model Wasm engine: all 15 requests completed. All five
  elastic cases passed an independent closed-form solution at all 95 endpoints;
  maximum axial stress error 1.75e-10 Pa and volumetric strain error 3.47e-18.
  DP/MCC completion is software evidence, not independent equation verification.
- Actual headed Chromium: default execution, selected request inspection, model
  visibility, full source context, download/import with fresh replay, stale export
  suppression, excluded model with incomplete inputs, retained rejected variation,
  cancellation, navigation away/back, desktop and 390px mobile layouts passed.
  Mobile document width 390px, controls width 358px, results below controls.
- Browser reproducibility: [browser-checks.cjs](browser-checks.cjs) is a
  Playwright CLI `run-code --filename` function. It delays worker loading only for
  cancellation; numerical responses are real Wasm outputs.

```sh
node --test tests/test_ensemble.mjs tests/test_catalogue_browser.mjs tests/test_web_package.mjs
python3 -B -m unittest tests.test_ensemble_package tests.test_web_recorded tests.test_web_catalogue
python3 -B tools/build_ensemble_web.py --output /private/tmp/atlas-ensemble-preview
# Select a NEW report path: the runner refuses to overwrite retained evidence.
node tools/test_ensemble_wasm.mjs --wasm build-wasm/atlas.js --experiment /private/tmp/atlas-ensemble-preview/ensemble-experiment.json --output /private/tmp/ensemble-wasm-new.json
# Against a running matching local preview and an open CLI browser session:
playwright-cli -s=ensemble run-code --filename docs/reviews/ensemble-opara-v1/browser-checks.cjs
```

The final screenshots and initial mobile failure are retained in `browser/`.
The complete browser download is in `output/playwright/ensemble-final-export.json`;
its hash is in the implementation receipt. The numerical report already preserves
all response bytes semantically, so the duplicate download is not copied here.

## Retained findings and delivery limits

An initial request serialization included settings metadata unsupported by the
recorded-run contract. Requests were rejected before engine execution; serialization
now sends the contract's numerical fields. Initial mobile rendering inherited a
desktop grid-column rule and squeezed controls into an implicit track despite no
document overflow; the mobile CSS now resets both grid coordinates. The original
[mobile screenshot](browser/ensemble-mobile-v1.png) is retained. Browser harness
failures (continuing an aborted route, asserting visibility before the hash-change
handler ran) were corrected with abort-aware cleanup and awaited visibility;
no product acceptance threshold changed.

Whole-site packaging was attempted with:
`python3 -B tools/build_web.py --output /private/tmp/atlas-ensemble-full-package-check`.
It exited 1 with **“Wasm catalogue is stale: rebuild before packaging.”** No build
or deployment was attempted. The matching existing five-model engine/catalogue
was used in an isolated preview, not represented as the current full release.
The preview uses current page/modules and matching engine/model bytes; its
preview-only support declaration is empty because the current shared declaration
refers to a model absent from that old engine. Four unrelated missing ancillary
assets (named examples, applicability, experiment index, evidence) produce 404s;
their unavailable states are not ensemble errors and full-site health is not claimed.
The final screenshots were captured after the transient named-example toast closed.

The preview is served at `http://127.0.0.1:18867/#ensemble` from
`/private/tmp/atlas-ensemble-preview`. To reproduce it, copy `web/index.html`,
`web/style.css`, `web/app.js`, `web/worker.js`, `web/*.mjs` and `web/ensemble.css`
into a private output directory; copy matching `atlas.js`, `atlas.wasm`, generated
`models.json`, matching model JSON files and a catalogue manifest. Generate the
experiment assets with the packager above. For this old preview engine only, use
`{"schema_version":"0.1","models":[]}` as `laboratory-control-support.json`.
Serve that directory on localhost and open `#ensemble`. This preview procedure
is a bounded feature check; the normal website packager retains its stale-engine
gate and requires current matching engines for a release.

No model/source scientific approval, shared native/Wasm build, commit, push or
live delivery is claimed. The next integration step is a current matching engine
package and full-site qualification when the concurrent delivery work is ready.
