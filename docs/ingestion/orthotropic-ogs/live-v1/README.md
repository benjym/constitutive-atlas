# Published main-atlas orthotropic browser qualification

Task LIVE-orthotropic-ogs-v1, owner `/root/sls_browser_delivery`. Evidence is confined to this directory and `output/playwright/orthotropic-live-v1/`; earlier local browser packets remain unchanged. No builds, native execution, production edits or commits were performed.

Target exact revision `462a450c69b0fd481fc99b67e8c42f03f82e0e97`, Actions run `41341461226`, tested artifact `13098336823`. Parent authorized actual browser execution after all six CI/Pages jobs succeeded and the unchanged 155-asset live/upload gate passed. The deployment-only retry reused that artifact. See `release-handoff.json` and the parent release-v1 receipts; earlier CDN failures remain there. Browser observation started 2026-11-01 19:59 UTC, Chrome 156.0.8078.74, unique session `orthotropic-live-462-a`.

`PLAN-v2.md` and the 22-file prospective freeze were recorded before target opening. Original 17-file freeze remains unchanged. Frozen source-derived Fraction compliance references use stress tolerance 1e-6 Pa and strain tolerance 1e-15. The model remains exact SHA256 `60a734a0c40fb0f03642752d22c046d4a05ea66bbf53a3c8e7be06fe71287c14`.

Actual default and custom exports preserve all nine parameters, six initial stresses, six strain-increment components, complete six-stress state and complete request/response records. Checks cover 66 stress references and 48 strain references, exact default/reset/replay/merged-switch documents, and exact custom/fresh documents. Repeated same-file import succeeds twice with consumed input cleared; finite later result tampering and duplicate JSON keys reject with stale export disabled, followed by recovery. Invalid compliance rejects; input edits and a newer two-row run supersede a long worker request. Ordinary/SLS/orthotropic switching works; current merged Lade and Maxwell entries/panels remain selectable. This does not qualify those models numerically.

The shareable main route, shared selector, actual catalogue card→Explore and shared equations work. The catalogue title diagnostic waits for the asynchronous visible title; the first script sampled an empty title early while its actual Explore check passed. All six plot channels are available, two plots render, and the complete 5×7 state table is inspectable. At 1280 and 390 pixels the document fits the viewport; the narrow state table scrolls locally. All six saved screenshots were visually inspected. Exact fetched runtime/model/review/approval/component/main-entry/catalogue assets match the tested upload; public dossier Markdown and HTML match it and disclose current status and portable links.

Retained availability failures: initial six-footer-link check had GitHub header HTTP429; unchanged attempt 2 passed all six. Dossier attempts 1 and 2 had GitHub429, and the paced attempt 3 passed ten of eleven URLs, retaining the ledger429 and response headers. The affected ledger URL returned HTTP200 at 20:09:49 UTC in attempt 4 after a cooldown. The eleven distinct unchanged dossier URLs each returned HTTP200 across named attempts 3 and 4; this is an aggregate availability record, not one successful batch. See `link-availability-provenance.json`, `retry-v3-freeze.json` and `affected-retry-freeze.json`. Canonical assessor logs are copies of the named successful/aggregate receipts; originals remain retained. Original strict assessor rejection is retained under `failures/assessment-attempt1.log`. No numerical or tolerance gate changed.

The unchanged frozen `assess_v2.py` passes; see `assessment.json`. Both prospective freezes remain unchanged. No blockers remain in this scoped browser qualification. Final page network has 310 terminal HTTP200 entries and five entries without terminal status after intentional cancellation. Separate unchanged-URL availability probes pass for all five; this does not assert the original canceled requests completed. Zero console errors/warnings. See `network-summary.json` and complete raw logs. This evidence qualifies the bounded implemented model interface, not experimental validation or a broad material envelope.

Reproduce saved-data assessment (no compiled execution):

```sh
python3 docs/ingestion/orthotropic-ogs/live-v1/assess_v2.py /private/tmp/atlas-orthotropic-final-upload-v1
```

Browser scripts use the cached Playwright CLI with the unique session noted above. Raw logs embed the exact code executed; scripts and complete JSON exports are retained. Screenshot files are in `output/playwright/orthotropic-live-v1/`.
