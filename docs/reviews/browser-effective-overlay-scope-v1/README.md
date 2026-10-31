# Bounded effective measurement consumer guard

Completed 1 November 2026. This closes the browser half of the consumer gap in the [total-stress design](../total-stress-profile-v1/README.md), complementing the [Python replay guard](../effective-replay-scope-v1/README.md). It does not enable total-stress execution.

Normalized overlays, cached catalogue eligibility and initial-state matching now require effective Cauchy state sigma. Legacy schema 0.1 retains its documented effective interpretation; schema 0.3 requires an explicit effective binding and Mandel/compression-positive convention. Missing, unknown, total and observable bindings fail closed. Full model validation and model–material suitability remain separate requirements.

The match button is disabled when incompatible; the actual handler also returns before changing any controls. Model changes refresh cached catalogue filtering. Source browsing, measurement data and hyperlinks remain available, with a short explanation where normalized comparison is unavailable. All production comparison calls pass the selected model explicitly.

## Verification

- Nine focused Python tests pass, including the Node contracts and existing catalogue/state/markup/experiment asset checks.
- Three new Node groups compare exact prior series across all nine models, three loading/record variants, five protocols, two cycle settings and four plots (1,080 comparisons); reject incompatible bindings for both rows and cached metadata; and execute the actual browser match handler with injected controls to verify zero mutation on rejection and unchanged effective matching.
- Existing `node tools/test_experiments.mjs` import/unit/integrity/ordering/comparison checks pass with an explicit legacy effective model. JavaScript syntax checks pass.
- Original source bytes are retained at the canonical paths in [previous-sources.json](previous-sources.json). Original evidence documents and their hashes are unchanged. This is byte preservation, not a fresh re-verification of every historical campaign.

Reproduce from repository root:

```sh
PYTHONPATH=.:tests python3 -B -m unittest tests.test_web_effective_scope tests.test_browser_numerics tests.test_web_experiments tests.test_web_catalogue -v
node tools/test_experiments.mjs
node --check web/app.js
```

These are synthetic contract/handler checks, not a new full-browser visual inspection, static release package, compiled material run or hosted deployment. No model equations, schema, numerical settings, measurement arrays or scientific statuses change.

## Reflection and stopping point

The atlas remains at nine executable definitions; pending review coverage and calibration tooling do not increase model count. The useful next implementation milestone is one additional runnable draft, with source links and explicit limitations. Tresca already has a transcription and independent reference fixtures: do not transcribe it again.

Its dependency is the existing coherent total-stress implementation plan: generated scope metadata, versioned native/recorded results, pore-pressure availability and browser labels/import/export must agree before activation. Keep the effective-only validator until those gates pass. A future bounded slice should freeze and implement scope metadata plus the native response contract first, against the saved Tresca fixture; retain separate browser/compiled gates before installing a public model. Do not expand calibration or repeat source micro-audits in that slice. Existing source/admission closure assignments remain with their owners.

This cycle stops at the consumer safeguard and focused verification. No new build, fitting campaign, model admission, push or deployment is part of it.
