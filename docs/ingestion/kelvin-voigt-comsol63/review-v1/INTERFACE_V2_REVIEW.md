# Independent interface v2 follow-up

Reviewer `/root/kelvin_scientific_review`; task REVIEW-kelvin-voigt-comsol63-v1; date2026-11-02. This adds interface failure-path evidence to INITIAL_REVIEW.md; scientific admission remains pending compiled results.

Compared the exact preserved v1 laboratory bytes in interface-v2/prior/ with current `web/kelvin-voigt-laboratory.mjs`. The only production change moves the existing generation-guarded failure handler before Worker construction and catches synchronous constructor/postMessage exceptions. Both paths use invalidate: terminate any acquired worker, clear timer and prior result, advance generation, disable export, restore Run and show failure. A subsequent valid run recovers. No material expression, state/control/solver setting, numerical gate, asset guard or model hash changed.

Independently verified every current and prior file hash in interface-v2/freeze.json. Read the added lifecycle tests and actual isolated release app hook. The new synthetic DOM/Worker test exercises constructor and postMessage failure without thrown UI exceptions, cleanup, and later valid recovery. Other lifecycle tests exercise full-six rendering, plot selection, reset, latest-generation rejection, outgoing profile cancellation, invalid-input/error/timeout recovery, verified import/replay, tamper rejection and stale file-read cancellation. These are transport/lifecycle tests, not numerical or actual-browser evidence.

Independent commands/results:

- Default dirty-root invocation:11/12pass; the release-hook check fails because root app.js intentionally preserves unowned work and has no new Kelvin hook yet. Retained `interface-v2-dirty-root-test.log`; no gate was changed.
- `KELVIN_RELEASE_APP=/private/tmp/atlas-kelvin-voigt-delivery-v1/release-source/web/app.js node --test --test-reporter=spec tests/test_kelvin_voigt_contract.mjs tests/test_kelvin_voigt_routing.mjs`:12/12pass, retained `interface-v2-release-test.log`.
- Current/prior freeze byte hashes:all match.

No blocking finding in the v2 startup fix. Actual browser/package/backend qualification remains coordinator-owned and unobserved by this follow-up. Model approval is not issued here.
