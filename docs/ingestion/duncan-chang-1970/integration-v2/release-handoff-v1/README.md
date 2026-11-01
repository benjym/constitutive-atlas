# Duncan release handoff v1

The accepted local E6/E7 package is retained in a reproducible private tarball. `artifact-receipt.json` binds exactly 953 public files; every archived file was rechecked against the accepted package manifest. This is a tested publication artifact, not a release commit or live deployment.

E8 remains open. The checkout includes concurrent model/compiler/schema/workflow changes and unrelated deletions. HEAD is only the source base and does not identify the tested dirty-tree inputs. A scoped source release commit must be assembled with the integration owners. Do not stage the whole checkout. The fresh source recheck records two later changes to unrelated Lade UI files; the frozen receipt remains unchanged and the separate reviewer accepted the preserved original identities in [SOURCE_DRIFT_ADDENDUM_V1.md](../independent-review/SOURCE_DRIFT_ADDENDUM_V1.md). Bounded E6/E7 acceptance is unchanged; future builds require a fresh source closure. Package bytes still match completely.

Next: consolidate exact reviewed shared dependencies in an isolated release checkout and inspect the scoped diff. Obtain explicit push/deployment authorization required by AGENTS.md, then monitor the actual remote workflow and verify deployed assets plus a live Duncan example. No staging, commit, push, remote CI or deployment has occurred. The model umbrella stays open.

Retained limitations: declared GIS strict-default failure, older qualified dedicated engines, and no experimental validation, finite-rotation host or Duncan update-tangent claim. See ../independent-review/FINAL_REVIEW_V1.md for the bounded decision.
