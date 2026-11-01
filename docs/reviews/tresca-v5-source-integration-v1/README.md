# Tresca v5 source-bound draft integration decision

Task REV-tresca-v5-source-integration-v1, coordinating parent, 1 November 2026. The bounded outcome is a concrete proposal for a separately scoped local draft integration. This packet installs no public model, builds no binary and signs no scientific review.

- [Public definition proposal](public-model.json): only id, name and description differ from the qualified private v5 definition.
- [Pending review](pending-review.json): exact proposed-definition hash, canonical [dossier](../../models/tresca-associated-perfect-bk2022v1-be.md), unresolved questions and no reviewer signature. It remains outside the registered catalogue until integration.
- [Technical source crosswalk](source-crosswalk.json): source/algorithm identity, conventions, preparation, residual equivalence, numerical limits and stress scope, based on existing pinned reading.
- [Machine-readable decision](decision.json) and [next bounded integration task](INTEGRATION_PLAN.md).
- [Baseline public inventory](baseline-public-models.json), [source receipts](source-pins.json) and [checks](checks.json).

The nine-model baseline and eighteen pending registered reviews are historical observations at preparation, not permanent constraints on future catalogue growth. The verifier checks this immutable baseline through source receipts and does not require future absence of an installed Tresca record. There is no new material execution in this packet. `verify.py` validates exact-definition binding, pending status, unchanged numerical implementation and normal-generated numerical code identity. Existing v5 saved-result checks remain the numerical evidence; this technical crosswalk is not independent scientific judgment.

Reproduce from repository root: `python3 -B docs/reviews/tresca-v5-source-integration-v1/verify.py`, then `python3 -B -m unittest tests.test_tresca_source_integration_review tests.test_tresca_certified_corners -q`. Tests and source receipts refer to this delivery; they do not claim current hosted deployment.
