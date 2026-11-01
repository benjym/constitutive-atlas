# Bingham main-atlas interface qualification preparation

Worker scope WEB-bingham-comsol63-v1. The main laboratory controller uses the generic `atlas_run_schedule` engine. No model-specific numerical kernel, build or engine execution was performed by this worker. Main app, router and normal website builder integration remain coordinator-owned.

The four implementation files were handed off with exact candidate SHA `6c5ee29c5c8cfbe18eaac09808a86ed7b656c8716511409bb23ecd0d3ad89850`. The original bytes are preserved in `superseded-implementation-v1/`; `IMPLEMENTATION-REVISION-v2.json` records exact before/after hashes. Version2 adds a fail-closed, accepted-review-bound engine receipt. The UI file itself is unchanged.

`POLICY.json` retains the initial prospective interface policy. `POLICY-v2.json` adds exact engine artifact qualification, retains the original numerical budgets, and pins the current implementation plus stored independent references. It was prepared without observing the package engine. Native numerical work already belongs to the parent’s separate E4 study.

## Required exact engine receipt

The coordinator must produce the real `docs/ingestion/bingham-comsol63/execution-v1/build-receipt.json` before E5 review. No accepted receipt is manufactured here. Required shape:

```json
{
  "kind": "bingham-qualified-engine-build-v1",
  "model": {
    "id": "bingham-comsol63-mises-perfect-zero-spin-ode",
    "sha256": "6c5ee29c5c8cfbe18eaac09808a86ed7b656c8716511409bb23ecd0d3ad89850"
  },
  "artifacts": {
    "module": {"path": "original qualified module path", "sha256": "actual SHA256"},
    "wasm": {"path": "original qualified Wasm path", "sha256": "actual SHA256"},
    "metadata": {"path": "original qualified generated/models.json path", "sha256": "actual SHA256"}
  }
}
```

All three artifact keys and each `path`/`sha256` pair are mandatory. Paths retain original acquisition/build provenance; actual supplied bytes must match the digests. The receipt itself must be an exact SHA-bound artifact in the accepted independent scientific review. The builder also regenerates model metadata and requires byte equality. Worker and package checker verify the receipt is review-bound and its three digests equal the actual module, Wasm and metadata identities. Same-name artifact substitution fails closed.

This binds a fixed qualified public artifact. It makes no claim that independent operating systems or later builds reproduce identical binary bytes. The coordinator’s proposed fixed-artifact archive/provision workflow and any separate fresh-build numerical qualification are additional integration work.

## Checks and commands

`node --test tests/test_bingham_laboratory_contract.mjs` passes7tests without instantiating an engine. `static-tests-attempt1.log` and `static-tests-attempt2.log` retain the earlier6-test passes; `static-tests-attempt3.log` adds exact receipt rejection tests. Tests cover all three wire-control modes/full13state, invalid inputs and plastic trace/history constraints, strict JSON and exact provenance, complete output replay/tamper, independent approval, and controller latest-request/cancel/invalid/reset behavior using a deliberately small DOM/Worker double. The test fixture uses frozen independent values only as transport data, not as a claim that a compiled engine produced them.

All implementation/package/test `.mjs` files pass `node --check`; the Python builder passes AST parsing. No engine was instantiated by the worker.

Coordinator executable check, after producing and sealing the real review-bound bundle:

```sh
node tools/test_bingham_package.mjs /absolute/path/to/normal-atlas-package
```

That command intentionally instantiates the packaged Wasm. It compares all13state and6stress components at all6output/event points in each of three modes (342 comparisons) to `public-relaxation`, `public-creep` and `public-rate` in frozen `execution-v1/cases.json`. Relaxation/creep use source-derived closed-form references; the public rate case uses the independent stress-space RK4 reference. Budgets remain `max(3e-7,2e-5|reference|)` for strain/history and `max(3Pa,2e-5|reference|)` for stress. It also checks every package identity/manifest digest, exact complete replay, finite result tampering, provenance tampering and invalid-request recovery in the same engine instance.

Actual browser rendering, real Web Worker/network lifecycle, downloads, file import, accessible controls, plots, route coexistence and complete end-to-end delivery remain separate E7/E8 qualification. No experimental comparison, calibration, broad accuracy or finite-rotation claim is made.
