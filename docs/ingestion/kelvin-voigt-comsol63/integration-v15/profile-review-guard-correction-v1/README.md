# Profile review guard correction v1

The first full package-v6 builder failed before compiled checks because the exact accepted VW96 review `catalogue/agent-reviews/vw96-agent-v1.json` pins historical `AGENTS.md` af554aa5c12e4f3706efdf20399a283e7a09bda8be748b1f394b4d0c78c3709e. The parent agent-review map existed but did not register this original review document or that source binding. The prior preservation scan required an already valid checked_receipt context and therefore skipped the unregistered VW96 context. The canonical historical AGENTS bytes were already present.

The correction registers the exact unchanged VW96 review hash 644975afbdd3e0dff5b41f6ab9aae069fad345812b263df3db6c573b04d4a20a and its historical AGENTS binding. It preserves the prior agent-review map bytes and redirects the exact original integration-v13 receipt that pins that old map. The current AGENTS pin in integration-v14 proposal is also preserved. Exact installed paths are in `receipt.json`: three canonical snapshots and three sidecars, with three bindings. The new integration-v13 and integration-v14 sidecars bind all existing sibling JSON documents.

No review, approval, model, policy content, runtime source, acceptance gate, or original package failure was changed. The original failed builder log remains in package-v6/build.log. All 20 catalogue agent-model reviews now validate, and all 14 archive tests pass.

```sh
python3 docs/ingestion/kelvin-voigt-comsol63/integration-v15/profile-review-guard-correction-v1/verify.py
python3 -m unittest tests.test_evidence_archives
```

The exact one-shot installation script is retained as `preserve.py`; replay uses `verify.py`. New sibling receipts later added under integration-v13 or integration-v14 must be explicitly registered in those contexts if they use archived inputs.
