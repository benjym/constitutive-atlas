# Current catalogue recorded-scope fixture repair

`TEST-recorded-scope-catalogue-v1`, 1 November 2026. Test fixtures now read each canonical model's declared stress scope rather than requesting effective stress universally. Every canonical fixture also has an explicit opposite-scope rejection. The catalogue-size assertion scales with the enumerated models while retaining all seventeen original malformed-contract cases and two explicit synthetic scope fixtures.

No production validator, scope semantics, model definition or numerical acceptance criterion changed. The original failure is retained in the preceding [parser repair baseline](../browser-strict-json-v1/atlas-strict-json-baseline-complete.txt). Exact prior test bytes and affected receipt maps were archived before this edit; `archive.json` records the redirects.

Current evidence: eleven canonical models, thirteen positive fixtures, twenty-eight negative fixtures (including eleven opposite-scope cases), forty-one Python/browser codec comparisons with unchanged input and blocked legacy-engine fallback. All twelve focused unittest checks pass. Ordered numeric wires remain identical to the legacy mechanics representation after explicit scope validation. These fixtures test metadata and codecs; they do not establish that specimen parameters/initial states suit every model or qualify a material integration.

```sh
python3 -B -m unittest tests.test_recorded_scope tests.test_strict_json tests.test_recorded_document tests.test_laboratory_document tests.test_strict_observation_json
python3 -B docs/reviews/recorded-scope-catalogue-v1/verify.py
```

Next: freeze the current twelve-model MC collector and independent assessor against the repaired import boundary before any numerical qualification. No builds, backend execution, model installation, scientific admission or deployment in this task.
