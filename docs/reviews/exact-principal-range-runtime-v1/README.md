# Generic exact principal-range runtime qualification

The generic `principal_range_le(A,Y)` capability is implemented through normal DSL typing, interpretation, model code generation, checked C++ and history code generation. It follows the [separately frozen proof and independent exact oracle](../certified-spectral-range-v1/README.md); no material-ID branch, yield tolerance or initial-state repair is introduced. See the [user contract](../../PRINCIPAL_RANGE.md).

The DSL requires matching symmetric-tensor/scalar physical dimensions and returns value-only Boolean control. Lazy branch behavior and sticky executed-failure marking match the existing expression pipeline. Model and history event/reset dependency tracking rejects this value-only query as a switching-time guard, including through numeric aliases. The Python implementation uses exact Fractions plus the existing radical sign routine; C++ reuses existing exact dyadic/radical primitives, validating primals and all 38 seeds before exact scaling or trace subtraction. Boolean checked outputs remain untouched on failure.

## Prospective evidence

[policy.json](policy.json) was written before implementation; [prospective-freeze.json](prospective-freeze.json) binds the source closure, generated fixtures, driver, input corpus and assessor before either compiled run. [requests.json](requests.json) retains all 230 exact-design cases, 61 original material case parents and 12 history parents. The independent expected decisions are unchanged. Python interpretation agrees on all 303 before compiled observation.

One explicit target `atlas_exact_range` was built natively with `--parallel 1`, then built under Emscripten with `--parallel 1`; both executions use regular-file stdin. The complete driver, compiler outputs, process logs, response streams and binary hashes are retained. Binaries remain local. [assessment.json](assessment.json) verifies, per backend:

- 303 double and 303 real Jet decisions match the frozen oracle exactly.
- 303 normally generated initial checks return the expected membership, preserving supplied full state and the output sentinel; this includes rejection of history parent7.
- 819 NaN/positive-infinity/negative-infinity cases span all seven operand primals and all 38 seeds. Checked output sentinels survive rejection; generated masked expressions set sticky failure; a subsequent valid call recovers.
- Negative widths fail, an unselected invalid branch stays unexecuted, and a pre-existing failed evaluation flag remains failed.
- A normally generated history programme rolls back its full state, generation, epoch and events after an executed invalid operand, then succeeds on recovery without altering the supplied parent.

The focused regression suite passes 57 tests. This includes independently replayed exact designs, DSL type failures and reset alias tracking, a byte-for-byte nine-model public header/catalogue comparison using the archived pre-change compiler/DSL, saved native/Wasm response corruption checks, earlier Tresca evidence, spectral/normalized-determinant behavior and archive coverage. The first preflight fixture generation lacked a required source role; [the failure note](preflight-failure-note.json) records that fixture-only correction. No numerical gate, oracle or runtime source was changed after compiled observation.

## Reopen and limits

From the repository root run:

```sh
python3 -B docs/reviews/exact-principal-range-runtime-v1/assess.py
python3 -B -m unittest tests.test_principal_range_dsl
```

`run_study.py` records the serial build recipe and verifies frozen source hashes before compiled stages. Its original stage is `/private/tmp/atlas-exact-range-runtime-v1`; `prepare_fixtures.py` generates normal fixtures into a fresh directory. Do not overwrite retained evidence to rerun a changed study: create a new study identity.

`previous-sources.json`, `archive-changes.json` and additive document-bound sidecars preserve the pre-change source and map bytes. Original historical numerical evidence, budgets and source hashes were not edited. The live nine-model catalogue remains unchanged.

This qualifies the generic predicate over the stated frozen corpus, not the complete Tresca model. No model is installed, admitted or deployed. In particular, width construction such as `2*k` can overflow before this predicate, and absolute stress recombination can lose an unrepresentable deviator; neither limitation is hidden by narrowing the physical parameter domain. The next bounded task is a new private pressure-split Tresca study using this predicate and the existing independent transformed residual references, with prospective gates for full values, all 38 derivative columns, branch coverage, strict initialization, full-history restart rejection and rollback/recovery. Original failed Tresca evidence remains a failure.
