# Independent interface v7/v8 source review

Reviewer: `/root/kelvin_scientific_review`. Scope: saved JavaScript proposals and pure extracted-function/SVG mocks only. No browser, compiled engine, build, shared source edit or scientific approval amendment.

## V7 finding — do not integrate

The five supplied tests pass independently (see `interface-v7-tests.log`), and padding removes the misleading full-height display of roundoff in nominally constant held stress. However, applying the new tolerance to the shared x/y helper introduces a time-axis regression: the representably distinct times `[1e9,1e9+1e-6]` acquire domain `[950000000,1050000000.000001]`, compared with the original `[999999999.9999999,1000000000.0000011]`. A real short interval becomes invisible. Large origin plus one second, covered by the original tests, does not exercise this case. The coordinator accepted the finding and retained v7 without insertion.

## V8 decision — source proposal accepted

The exact v8 proposal SHA-256 is `8a8f15fc889e5f86c20d885414f61476c4c54121c276db848f714c02f5fdc721`; its prior app is `a989a23c5cdc19c4d02a9b28c5f051ee77795e6983d246e0627068acd0f48ab7`. The optional `nearConstant=false` guard preserves original x-axis behavior, including all representably distinct intervals. Only the y-domain call opts into `64*Number.EPSILON*max(1,abs(lo),abs(hi))` padding. Exact constants retain the existing padding, ordinary y spans retain seven-percent span padding, and plotted data are unchanged.

All four supplied pure tests pass independently (`interface-v8-tests.log`). They exercise positive and negative large-origin short intervals, exact constants, roundoff-scale and physically resolved y spans, tolerance boundaries, and the actual extracted chart function with SVG mocks. The chart mock proves x separation remains greater than 200 pixels while the held-stress roundoff spread becomes less than 1e-8 pixels, with unchanged input arrays. Independent saved ranges/hashes are in `axis-proposals-check-v1.json`.

No unresolved blocker remains for this narrow source insertion. This is acceptance of the exact source proposal, not an actual browser or final package pass. The coordinator must retain the prior app/package, integrate narrowly, and qualify final package/browser plots. Existing backend model, controls, accepted scientific record and complete exported state/stress remain unchanged.
