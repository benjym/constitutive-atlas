# Provisional KFS calibration-propagation website view — v1

The existing Methods development page now lets readers explore all four
calibration/evaluation initialization combinations. It shows the original failed
refinement and the separately passing nested caller regime together, with their
scopes, source links and scientific limits. The earlier locked-parameter
pressure3/density3 comparison remains explicitly separate.

## Delivered behavior

- Two selectors choose calibration (TMD13) and evaluation (TMD12/TMD14) assumptions.
  All four six-test scores remain visible; the selected row is highlighted.
  File/file, evaluation-only, calibration-only and combined errors are
  0.129344, 0.136772, 0.124701 and 0.132294. Selection was calibration-only; the
  page shows seed/alpha and all starts exhausting their 96-candidate budgets.
- The original refinement is labelled FAIL, with four nonincrease failures out
  of 32 case/channel checks and a four-row disclosure. The separate nested regime
  is labelled PASS, with 9984 rejection-free caller points and eight disclosed
  checks. It cannot imply acceptance of the old sequence or a new six-test panel.
- The original model publication and four new evidence packets have persistent
  hyperlinks. Source-state disagreement, prior data exposure, exhausted search
  budgets, missing exact source/build identity and pending independent review
  remain visible. No measured or predicted curve arrays are included.

[Public scalar projection](public-summary.json) matches the packaged JSON.
`tools/build_propagation.py` reads only policy/result manifests and scalar evidence
packets. It does not read experiment files, private native outputs or independently
owned paper code. Explicit field construction excludes sibling records, command,
state, acquisition-coordinate and prediction arrays. It checks hashes, archived
model identity, policy/result dependencies, calibration-only selections, complete
factorial panel membership and recomputed aggregate scores. Both sets of
refinement predicates and the nested diagnostics are checked separately.

The existing `build_development.py` incorporates this projection and copies the
new `propagation.mjs`. The new browser module validates complete scenario/check
coverage, gates, limits and safe source URLs, and uses text content for rendering.
Selectors only choose saved reporting; no fit or model execution occurs here.

## Verification

[Verification record](verification.json) and [test log](tests.log) retain:

- 28 Python tests, including two wrappers that execute 14 JavaScript contracts
  (six existing, eight new). The six new Python groups exercise scalar allowlisting,
  a fixture with no experiment/private directories, source hashes/identity,
  duplicate panels, preserved original failure, nested status and promotion
  rejection. An injected unused private sentinel is not exported.
- Historical source archives resolve the previous development manifest to its
  original bytes. Three files were archived before editing: exporter, HTML and
  Python tests. The old evidence packet and its scientific results are unchanged.
- A normal local Pages package reuses the existing verified Wasm artifact. All
  nine default model paths of 101 points pass the existing package smoke check;
  628 public experiments package normally. This executes existing Wasm, not a
  native/Wasm build or a new scientific study. All seven local page assets/links
  resolve under the `/constitutive-atlas/` project prefix.
- Actual browser inspection checks all four selector combinations, selection
  highlighting, alpha changes, four failed/eight nested disclosed rows, visible
  limits/source links and Methods navigation in both directions. A private
  screenshot records the four scores and original failure.

The first package validator was invoked before packaging had completed and
correctly failed on the absent `.nojekyll` completion file. The same live packaging
process completed; the subsequent and final validations pass. The first loopback
server bind was sandbox-denied; normal approved local serving then succeeded.
No process was restarted due to a polling timeout and no protection was bypassed.

## Reproduction

```sh
python3 -B -m unittest discover -s tests -p test_web_propagation.py -v
python3 tools/build_web.py --wasm-dir /path/to/existing/verified-wasm --output /private/tmp/kfs-propagation-site/constitutive-atlas
node tools/test_web_package.mjs --directory /private/tmp/kfs-propagation-site/constitutive-atlas --output /private/tmp/kfs-propagation-package-check.json
python3 -m http.server 8946 --bind 127.0.0.1 --directory /private/tmp/kfs-propagation-site
```

Wait for packaging to finish before validating. The current local preview is
`http://127.0.0.1:8946/constitutive-atlas/development.html`. No push, deployment,
model migration, native study, fit, build, paper edit or scientific admission
occurs. This closes a provisional website delivery task; the research charter's
source, rights and independent-review requirements remain open.
