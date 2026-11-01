# Generic physical solution constraints, v1

Delivered an optional v0.3 incremental-residual `solution_constraints` contract, separately typed and bound to current persistent state and material parameters. See [the contract](../../SOLUTION_CONSTRAINTS.md) and [private compiled qualification](../../../catalogue/investigations/tresca-solution-constraints-v4/README.md).

Initialization, reset preparation, feasible Newton/backtracking, convergence, commit and observation enforce physical admissibility. Raw residual/Jet evaluation continues to use the declared mathematical domain. Full integration rollback is retained. Existing public nine-model generated files remain byte-identical, and the public native numerical regression passes with the shared solver changes.

The native and Wasm candidate each pass all 219 original requests, all 38 derivative columns and all 12 continuous history steps, plus generic malformed/nonfinite/seed/rollback/recovery checks. The focused Python suite reports 95 tests, one existing optional skip, zero failures. The first regression run had one assertion mismatch: a legacy physical-time schema rejects the new field structurally before semantic profile validation. The corrected test accepts either appropriate rejection; runtime/compiler sources and frozen study were unchanged. Pre-compilation generator indexing correction is recorded separately in `preflight-notes.json`.

Before implementation edits, exact pinned bytes were preserved in content-addressed snapshots with additive document-specific maps (`archive-changes.json`). Five untracked packets belonging to other work were left untouched (`deferred-untracked-archive-maps.json`). Two historical verifier implementations now resolve their original source pins through these receipts; historical assessments, model definitions and acceptance gates remain unchanged.

This delivery closes the bounded generic capability and private numerical gate. It does not install Tresca, provide experimental validation, confer scientific admission, or publish the site. Stop here; next task is private laboratory qualification.
