# Clay2005 original-stress homogeneous ratio: passing complete-rate study

Both native and WebAssembly pass all **120 ordered calls and unchanged acceptance gates**. The candidate changes only `detH` from `determinant(H)` to `normalized_determinant(sigma)`, plus descriptive provenance. All other source algebra, conservative guards, parameters, initialization metadata and literal research model ID remain unchanged. The new generic operation evaluates the exact-input homogeneous determinant ratio before normalized-component rounding can alter the geometry.

Each backend passes 81 source-accuracy rows, ten finite-only support rows and 29 recognized rejection rows, including all 29 immediate same-instance recovery pairs. All eleven appended actual-input boundary accuracy cases pass. Their largest source-budget fraction is 0.001396 native / 0.001713 Wasm (a fraction at or below one passes). The two previously failing cases improve as follows; original failed results remain retained in the separate [normalized-H study](../clay2005-determinant-rates-v1/RESULTS.md).

| Case | Previous native / Wasm budget fraction | New native / Wasm budget fraction |
| --- | --- | --- |
| Oblique tiny positive | 1203.853 / 1203.850 | 0.001396 / 0.001713 |
| Shear near positive interior | 5551.944 / 5551.944 | 0.00002672 / 0.00002969 |

Native/Wasm parity passes for every request; the maximum parity-budget fraction is 0.014293. Finite-only agreement remains a support/parity result, not independent source accuracy. The independent source vectors, all 120 request objects, budgets, labels, order and policies are byte-equivalent at the parsed-object level to the previous protocol. No gate was relaxed, difficult input removed, source domain narrowed or parameter fitted.

The [comparison](comparison.json) and [verification](verification.json) retain per-case numerical evidence. The [prospective freeze](prospective-freeze.json) precedes all compiled observations and binds the protocol plus 125 cache-free source/reference/harness files and expected generated declarations. Native and Wasm generated outputs match the expected bytes. Builds completed serially, ordinary Release, one explicit `atlas_isolated` target with `--parallel 1` and `EMCC_CORES=1`; exact commands, toolchain versions, verbatim flags/link/cache files and opaque raw journals are retained. Three prospective structural tests passed before builds and again during final verification.

`replay.py` reconstructs the frozen source closure in a fresh temporary tree and reruns the original retained auditors against the opaque observations. It does not rebuild or execute material artifacts; recorded temporary artifact bytes are reopened for hash verification only. The replay preserves the exact passing verification report and does not monkeypatch source roots or old receipt hashes. Historical studies and their failures remain unchanged.

This completes the bounded instantaneous seven-rate study and its generic arithmetic dependency. It does **not** establish finite-path integration, material AD/tangents, specimen preparation, experimental validation, all-domain accuracy, performance or scientific admission. Final publisher equivalence is still unverified. The candidate remains separate research evidence; no production model or website was changed. Next is a prospectively specified finite-path/default-example study before any laboratory draft integration.

Reproduction from the repository root:

```sh
python3 -B catalogue/investigations/clay2005-homogeneous-rates-v1/verify_study.py
python3 -B catalogue/investigations/clay2005-homogeneous-rates-v1/replay.py
python3 -B catalogue/investigations/clay2005-homogeneous-rates-v1/audit_evidence.py
```
