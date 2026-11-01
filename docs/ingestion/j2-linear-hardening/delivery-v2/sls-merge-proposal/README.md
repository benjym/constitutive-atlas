# Preserve committed SLS/Burgers routing with J2

Source-only proposal against HEAD **302f2adc06d39b634e1865899e24ff088cc32f72**, extending the exact prior accepted Burgers/J2 merge. No root/shared files, engines, model/contract/module bytes, builds or Git state were changed. Old mixed proposals/receipts remain intact.

Copy `app.js` to parent stage `web/app.js` and `test_j2_main_routing.mjs` to stage `tests/test_j2_main_routing.mjs`. The application adds the exact HEAD imports `setupSlsLaboratory` and `createLaboratoryControllerRouter`, initializes the committed router with Burgers and SLS, and changes timed profile identity conditions to `timedView.supports(id)`. The existing parent coordinator deactivates the timed proxy only when active, before J2 activates and hides ordinary controls. Catalogue availability/status, development notes, routing and Explore use the same support predicate. All other prior mixed-app logic and async guards are retained.

Reproduce in the isolated mirror:

```sh
node --check /private/tmp/atlas-j2-main-v2/merge-sls/web/app.js
node /private/tmp/atlas-j2-main-v2/merge-sls/tests/test_j2_main_routing.mjs
```

The durable test accepts optional application/router paths for proposal replay:

```sh
node docs/ingestion/j2-linear-hardening/delivery-v2/sls-merge-proposal/test_j2_main_routing.mjs docs/ingestion/j2-linear-hardening/delivery-v2/sls-merge-proposal/app.js /private/tmp/atlas-j2-main-v2/merge-sls/web/laboratory-controller-router.mjs
```

`pure-results.json` records **157 checks / 27 transitions**, zero engine/network/compiled calls. The original exact-source 63-check coordinator/import harness is preserved with a `supports` method added to the inert timed stub. Additional checks import the actual committed router, evaluate the actual app coordinator, and exercise all 12 directed edges among ordinary/J2/Burgers/SLS plus all four same-interface selections. They assert active-profile exclusivity, ordinary/workspace/import visibility and absence of deactivation after target activation. They retain ordinary delayed-import/new-revision guards and reject accidental timed singleton identity references. Router source is copied unchanged only into the authorized temp mirror; no physical backend is loaded.

A pre-freeze source-construction replacement initially produced `entry.timedView?.supports(id)` in catalogue expressions. A source inspection caught it before any engine/package/browser observation; the final source uses `timedView?.supports(entry.id)`, and the durable test explicitly rejects `entry.timedView`. This correction changes no numerical/reference gate.

`app-vs-head.patch` is the full new application delta against HEAD302f2adc; `app-vs-previous-mixed.patch` isolates the small SLS/router adaptation against the accepted mixed proposal. `manifest.json` binds those inputs, the exact committed router, proposal source, test and outputs.

Parent still owns stage freeze, package checks, actual browser mixed transitions/delayed work, independent review, CI, commit/push and live validation. Pure mocks cannot establish real widget/worker scheduling or package/engine identity. In particular, browser qualification should execute J2→Burgers→SLS→J2→ordinary and the reverse transitions under delayed initialization/import/run; no prior browser evidence is silently carried forward as proof of this merged app.
