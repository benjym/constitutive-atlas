# LIVE-sls-comsol63-v1 — verified live delivery, release v3

Owner /root/sls_browser_delivery;2026-11-01. Scope only this directory. No source, frozen local evidence, build, commit or remote mutation. Actual read-only browser checks followed PLAN-v3.md after coordinator provided successful exact-revision combined CI and Pages proof.

Verified URL: https://benjym.github.io/constitutive-atlas/sls.html. Exact release f18db8e75d27cf182f2c03dfcd6534b7f51d5a86; CI41289504263; Pages deployment7470820389. Parent proof docs/reviews/sls-release-v1/deployment-proof-v3.json records allfour native/Wasm jobs plus deploy success. Its SHA256 and the exact upload receipt binding are in artifact-bindings-v3.json. Tested upload extracted at /private/tmp/sls-pages-extracted-f18; private tar SHA2567c2981630798a628e49748a8cf1c115f27072a56d37308863b2bf54900163a5a. Live observation is supported by exact artifact equality, not the URL alone.

Actual Chrome156.0.8078.74 completed the frozen default relaxation (8s,4intervals), exposed7table rows/19columns and2plots, exported the entire request/result/provenance, then completed finite-rate loading (1s,4intervals), exported the complete state and reset successfully. browser-default.json and browser-rate.json retain all12state and6observable stress values. check_live_v3.py passed216 independent-reference comparisons using unchanged frozen execution-v1 references and bounds (strain3e-8, branch/observable stress1Pa). assessment-v3.json records the pass.

browser-assets.log records actual browser fetches: all9 SLS package assets plus package manifest returned200 and match the exact CI upload SHA256 bytes. Live model SHA256eccfeb372810afd81a5e9cddf5d8ac33e2cb5df6921fc88e14e9175c73e50906; page0d3a61a24216b9cae7ad3d7e7338d43cd00c4c44651c7068797168a61dccdb70; CI/live Wasm1f39471279e8eb01b45f036ef73062c42ab9e3c039bb1ff48e04c7945e7b8e6c. The CI Wasm differs from the prior local build and is correctly compared to the tested CI artifact, not silently repinned to a local binary. Each returned result carries the expected catalogue identity11dd07e8b896a71bdc72ce4ff93aba664916af583c703fd6b8671a0727a6ff6e.

Primary COMSOL source, readable independent review, approval, checklist and exact model links returned200. The retained source digest appears in the footer and equals the frozen primary receipt. browser-console.log contains0errors/0warnings; browser-network.log records200 asset requests. browser-layout.log records document/viewport width equality at1280 and390 with2plots. Desktop and narrow viewport screenshots were visually inspected; layouts remain contained and results visible. Original live default full-page screenshot is also retained. No live browser failure occurred in this v3 observation.

Prior release attempts remain explicitly distinct: original9a27359/run41287314779 had cancelled/incomplete combined CI; d5f7b320/run41287657999 failed a recorded-path fixture regression and deploy was skipped. No live observation was made under either failed attempt. Original/v2 plans/checkers, old artifact bindings and preparation receipts remain unchanged. Parent release-revision-v3.json records the scope-aware fixture correction and unchanged SLS application/scientific paths. No numerical acceptance gate or tolerance changed after observations.

Reproduce the saved observation assessment from repository root:

```
python3 docs/reviews/sls-live-v1/check_live_v3.py /private/tmp/sls-pages-extracted-f18 --deployment-proof docs/reviews/sls-release-v1/deployment-proof-v3.json
```

Retained browser scripts execute through the Playwright skill CLI: open the live SLS URL; browser-default.js, browser-assets.js, browser-rate.js and browser-layout.js run-code files then console/requests capture. Scratch screenshots were created in private output/playwright and copied here. Full main-catalogue/entry verification is independently owned by the coordinator. This is bounded functional live delivery and synthetic numerical verification; no experimental material validation, broad parameter envelope or finite strain/spin claim is added. Next action: coordinator integrate this handoff into delivery ledger/board and final release receipts.
