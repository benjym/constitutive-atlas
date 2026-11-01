# GIS named example for the twelve-model catalogue

This additive proposed asset resolves the [retained P01 failure](../mc-private-package-v3/README.md) without weakening import identity. The new document uses the actual `GIS/named_example` response saved in the qualified twelve-model Wasm archive. Its specification is unchanged; the complete response matches the historical observation except catalogue identity and elapsed time, as already allowed by the numerical compatibility policy. All nine points and all state, loading and diagnostic fields match.

The proposed registry changes only `document_path` and `document_sha256`. The historical eleven-model document remains untouched. There is no model, parser, parameter, default or numerical-policy change; no new build or material call. `checks.json` binds the archive, member and new asset. `validate.mjs` uses production example validation and confirms the old document remains rejected against the new catalogue.

The expanded candidate overlay is exactly the five files in `../mc-browser-plan-v3/proposed/` plus the two files in this packet's `proposed/`. Both packet manifests must verify before a fresh package attempt; the original plan gates P01–B06 and qualified engine hashes remain unchanged. This resolves the input-asset issue only; package/browser results and root installation are still separate.
