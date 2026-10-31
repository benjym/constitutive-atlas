# Clay2005 accurate determinant: complete-rate result

The candidate **fails independent source accuracy**, despite passing native/Wasm parity. This is a retained negative research result, not a public model or scientific admission.

## Frozen change and evidence

Only the derived expression `detH` changes from `1/27-j2/6+j3/3` to `determinant(H)`; descriptive provenance also identifies the research candidate. All other equations, explicit schema0.3 formulation, conservative support guards, initialization, parameters and literal model ID remain unchanged. `prepare.py` enforces that difference. The source is [Mašín2005](https://doi.org/10.1002/nag.416), using the reviewed accepted manuscript and corrected PLUS Eq38; final-publisher equivalence remains unresolved.

The [prospective freeze](prospective-freeze.json) pins120source files, current compiler/headers/transports, complete expected generated output and120literal requests before any compiled candidate observation. The first109case objects, source vectors, budgets, finite-only labels,29immediate rejection/recovery relations and parity policy are copied exactly from the historical study. Eleven appended source-accuracy cases use the independently converged240digit Cartesian rates at the **actual stored binary64 input**. Their new pre-observation stress budget is `1e-10*max(1,abs(reference_component))`; void budget is `1e-15+2e-13*abs(reference_void)`. These are evaluation targets, not conditioning/input-uncertainty allowances. Historical finite-only calls are not relabeled.

The coordinator independently reran both source-only studies and reproduced their complete retained JSON results exactly. [Reference replay receipt](reference-replay.json) and frozen source packets retain that identity. No reference comes from the Atlas material evaluator.

## Observations

Serial ordinary Release builds used one explicit target and one worker each, native first and Wasm second. No contraction override or fast-math flag was added. Exact commands, generated snapshots, compiler versions, actual CMake cache/flags/link commands and artifact hashes are retained. One direct-file Python collector launch failed during import before any material call; the corrected module invocation succeeded, as recorded in [execution notes](execution-notes.json).

Each backend retained121raw rows: descriptor plus120material calls, comprising81accuracy,10finite-only and29rejection rows. All29immediate recovery checks and both positive/negative subnormal echo/material-rejection checks pass.

| Gate | Native | Wasm |
|---|---|---|
| Original109calls, source/support/recovery gates | Pass | Pass |
| Appended boundary accuracy |9/11pass |9/11pass |
| Oblique-tiny-positive: maximum source error/budget |1203.852729 |1203.849619 |
| Shear-near-positive-interior: maximum source error/budget |5551.944484 |5551.944485 |

Each backend has nine failed stress-component source gates across those two cases. Native/Wasm parity passes **all120calls**, with maximum parity error/budget `0.014292059599288873`. Agreement does not establish source accuracy. The other nine added cases pass without changing any budget.

[Comparison](comparison.json) retains the failed overall outcome, all component failures and decoded responses. [Verification](verification.json) re-audits the raw bundles and confirms generated identity, live artifact hashes, frozen-source snapshots, original cases/policies and counts. Four source/assembly unit tests pass. The historical archived raw replay still reproduces the original failed rates study and passing contraction-only diagnostic exactly, without executing compiled artifacts.

## Interpretation and next gate

The [independent normalization diagnostic](../../../docs/ingestion/hypoplastic-clay-2005/determinant-input-rounding-v1/README.md) identifies geometry loss before the accurate determinant receives H. Computing each normalized component in binary64 changes the tensor, with determinant-factor relative errors around1.16e-7and5.55e-7for the same two sensitive inputs. Exact trace alone does not fix component rounding. This explains a concrete remaining error source; it is not a proof that every other coupled factor is accurate.

Next implement and independently verify a generic dimensionless homogeneous determinant ratio from the **original stored tensor**, without rounding six normalized tensor components or separately overflowing/underflowing a determinant/trace cube. Specify trace-zero/final-overflow handling, mixed scales, exact-input/radical arithmetic, dimensional typing and all38AD columns before introducing a new frozen whole-law candidate. Preserve this failure and all earlier gates. No stress floor, domain narrowing, clipping, parameter fit or model-specific handwritten kernel is authorized by these observations.

No finite integration, spin, preparation, tangent, experimental validation, all-SPD theorem, scientific admission, public executable addition, push or deployment occurred.

## Reproduction

From the repository root:

```sh
python3 -B catalogue/investigations/clay2005-determinant-rates-v1/test_study.py
python3 -B catalogue/investigations/clay2005-determinant-rates-v1/prepare.py --check
python3 -B catalogue/investigations/clay2005-determinant-rates-v1/verify_study.py
python3 -B -m atlas.source_replay tagged-rates-v3 --registry catalogue/source-replays/tagged-rates-v3/registry.json --timeout 60
```

For a fresh checkout use `python3 -B catalogue/investigations/clay2005-determinant-rates-v1/replay.py`. It verifies the evidence manifest, reconstructs the exact frozen source closure in a temporary directory and reproduces `verification.json` without material execution or rebuilding. The prospective source enumeration accidentally included one pre-existing ignored `compiled-plan-v3/__pycache__/corpus.cpython-314.pyc` file as well as the actual source. Its original hash and snapshot are preserved as opaque evidence rather than editing a post-observation freeze. It is not imported or executed by the replay. The isolated closure supplies those exact bytes; a clean root checkout need not contain that cache. Future freeze enumeration must exclude cache directories before observation.

The current-study verifier and frozen-source replay reopen the hash-bound temporary native/Wasm artifacts; they must still exist. Historical replay uses its coherent archived Python source closure and opaque evidence and does not rebuild or reopen artifacts. Builds/collectors require fresh output paths and must not overwrite retained receipts.
