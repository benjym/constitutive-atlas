# End-to-end Terra Cotta refinement v2 — passed bounded accuracy study

All three new paths pass the unchanged independent component limits separately in preparation and hold, on native and Wasm. The new relative tolerance is `2.5e-9`, one quarter of the previous finest tolerance. No physical inputs, reference bytes, source-domain guards, component limits, solver defaults or100000substep budget changed.

| Path | Largest fraction of an unchanged component error limit | Accepted substeps, native and Wasm |
|---|---:|---:|
| Compression | .500568 | 86098 |
| Extension | .500568 | 86098 |
| Isotropic | .586010 | 92404 |

The largest fraction occurs for isotropic preparation total pressure: `.005860093719093129Pa` against `.01Pa`. Each run completes a single30s trajectory with23observations, carrying its own computed preparation state, strain, incoming-rate captured stresses and physical clock into the20s hold. The six new executions retain138points. Exact transition state/strain, output ordering, masked instantaneous hold-entry rates, settings and controlled-stress residual checks pass. Native/Wasm physical-channel parity passes with maximum scaled difference `6.869069736507201e-12` against `1e-7`.

## Historical result remains negative

The [parent study](../terracotta-preparation-hold-v1/RESULTS.md) retains all original nine requests and observations per backend, including its five independent fine component failures. It remains failed; this passing refinement does not rewrite it. `parent-bindings.json` fixes138exact parent evidence/source files. Each added request is identical to its previous fine request except for the explicitly recorded tolerance. Both studies use the same hashed binaries and complete frozen source identity; no rebuild was needed for these new observations. Native completed before Wasm began.

The reference remains the independent author-image Figure1 scalar implementation, not the author mixed-control routine. Each reference refinement carries its own preparation endpoint and stress capture, so the hold comparison includes preparation uncertainty. The parent source replay regenerates exact compiler outputs and requests. `verify_study.py` reconstructs both studies from their pinned files and exactly reproduces the new assessment bytes with isolated Python, without executing compiled artifacts. It also rehashes the unchanged binary bytes and retains the parent's negative outcome.

## Limits and reproduction

This is bounded software/numerical verification of a fixed-axis triaxial research law, not journal-source closure, independent scientific authorship, experimental validation or general3D admission. The known source strictness and halved author mixed-control temperature conflict remain unresolved. The journal PDF request remains inaccessible. These high-workload settings are study inputs, not new engine/browser defaults. No public timed-browser integration, push or deployment occurred.

```sh
python3 -B catalogue/investigations/terracotta-preparation-hold-refinement-v2/verify_study.py
```

The verifier needs the retained parent study and its artifact bytes at the recorded local paths. It performs source replay and raw reassessment only. Re-execution must use a new observation identity/directory; `execute.py` deliberately refuses to overwrite existing observations.
