# Merge committed Burgers with the qualified J2 main interface

INT-j2-main-laboratory-v2 source-only handoff, 2026-11-01. Base commit is **5ae90008d44575ef4b92b2b9e6e34fe1ca1f47b3**. The exact prior J2 stage is `/private/tmp/atlas-j2-main-v2/release-final/web/app.js`. This proposal changes only an isolated app copy; no production files, model/contract/module/engine bytes, shared build or Git state were modified. No compiled calls occurred.

## Integrate and reproduce

Copy `app.js` to the parent's new stage `web/app.js`, and `test_j2_main_routing.mjs` to `tests/test_j2_main_routing.mjs`. Do not overwrite the root checkout or another owner's files through this proposal. `app-vs-head.patch` is the exact delta against committed base `web/app.js`. Temp mirrors are `/private/tmp/atlas-j2-main-v2/merge-burgers/web/app.js` and its `tests/test_j2_main_routing.mjs`.

```sh
node --check /private/tmp/atlas-j2-main-v2/merge-burgers/web/app.js
node /private/tmp/atlas-j2-main-v2/merge-burgers/tests/test_j2_main_routing.mjs
```

For the durable proposal copy:

```sh
node docs/ingestion/j2-linear-hardening/delivery-v2/burgers-merge-proposal/test_j2_main_routing.mjs docs/ingestion/j2-linear-hardening/delivery-v2/burgers-merge-proposal/app.js
```

`pure-results.json` records 63 checks and 11 profile transitions, with zero network/compiled calls. The durable test extracts and evaluates the actual app dispatch and ordinary import functions against inert profile/DOM stubs; it does not duplicate the dispatch implementation. It covers all six directed edges among ordinary/J2/Burgers, repeated J2 selection, correct activation/deactivation order, visibility and lazy ordinary import completion after either special profile or a newer ordinary revision. Static assertions retain setup, route, catalogue Explore, equations, source identity and async guards. `test_merge.mjs` is an earlier 59-check construction witness retained for history; the named routing test is the current CI proposal.

## Resulting behavior

Both committed Burgers `setupTimedLaboratory` and accepted J2 `setupJ2Laboratory` are imported and initialized. `selectLaboratory(id)` is the common dispatch for main selector, special hash routes and catalogue Explore. It deactivates another **active** special profile first. Specifically, the committed timed module's `select(false)` restores ordinary visibility, so Burgers is deactivated before the J2 helper establishes J2 visibility and summary. The dispatcher never calls an inactive timed module merely because a J2 selection occurs. Selecting Burgers deactivates J2 first and delegates to committed timed selection, preserving its header and source updates. Ordinary selection deactivates whichever profile is active and restores ordinary visibility once. The equations button asks each profile before opening ordinary equations.

Catalogue availability/status/Explore supports both special profiles and existing published timed routes. J2's exact-ID `model()` lookup has no VW96 fallback; background source-description refresh therefore cannot label J2 as an ordinary model. Ordinary population, simulation, charts, measurement controls and example application return while either profile owns the workspace.

Existing ordinary worker sequence cancellation remains; explicit active-interface and callback-ID checks additionally reject queued ordinary results/errors/timeouts under a special profile or a later job. Ordinary import completion requires its original sequence and no special owner. Entering a special profile invalidates pending experiment-selection revisions. Delayed measurement selection/import completion and cleanup cannot overwrite another profile's current interface. Cached source catalogues may load in the background, while their ordinary UI updates are deferred until ordinary controls resume.

## Scope and risks

This is integration source evidence, not a passing browser/backend qualification. The J2 shadow module, pure contract, law approval, engines and numerical gates are unchanged. The committed Burgers module is reused unchanged, including its existing own-worker behavior and disclosures. No new physical/scientific scope is inferred.

Parent must freeze this new app/test with the reconstructed stage and rerun mixed real-browser transitions, including delayed init/run/import and ordinary recovery. The inert tests cannot establish actual shadow DOM rendering, worker scheduling, package URLs, Wasm identities, generated metadata or public deployment. Package checker source markers and input archives must bind the new app/test; previous accepted stage receipts remain historical and must not be repinned silently. Required CI must run the routing test alongside the existing J2 contract test. Parent owns independent review, actual package/browser execution, scoped commit/push and live release verification.
