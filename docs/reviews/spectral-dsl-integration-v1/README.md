# Spectral DSL integration v1 — staged, not installed

This candidate implements the generic capability needed by the selected Mohr–Coulomb formulation. Production source is unchanged. The implementation board remains WIP; this packet does not admit a model or change the hosted laboratory.

The eight files in `candidate/` add principal values, complementary pair sums and isolated-extreme projectors; a Python numerical mirror; checked C++ model/history emission; and a static `Type.value_only` qualifier. Arithmetic and numeric function results propagate that qualifier. Comparisons consume it as primal branch control; selected numerical branches still propagate their own qualifiers. Existing numerical sinks reject qualified results. Boolean arithmetic is rejected to prevent predicate-to-number leakage. Legacy increment-reset guards and experimental history signed event guards reject any value-only query dependency, including a dependency consumed by an internal comparison. Ordinary spectral operations retain the frozen primitive's isolation and range diagnostics.

The C++ numerical helper is byte-for-byte identical to the verified primitive study. Its historical internal namespace/version/comment are retained intentionally. New checked wrappers mark a sticky evaluation failure. This is source implementation and review evidence; generated execution, derivatives through the generators, solver rollback and event behavior still need a separately frozen compiled-context study.

## Source-only observations

- Coordinator source checks: 1,016 assertions, including 480 pre-existing independent primal reference cases (384 successful, 96 expected failures), exact diagonal results and unchanged nine-model generated catalogue bytes. Worst primal error/allowed-bound fraction: 0.2400830675 under the unchanged primitive policy.
- Consumer checks: 20 cases spanning model equations/domain/initial checks, indirect reset guard dependencies, history numeric/Boolean expressions and signed event guards, and initialization terms/state/rates.
- Existing source regression suites: 46 tests, 45 passed and one compiled-artifact test intentionally skipped. No native/Wasm compilation or compiled execution occurred.
- Independent staged code review found a history event-guard bypass. The original complete-program witness is retained in `code-review/`; the staged fix rejects it and accepts ordinary differentiable spectral control. No other blocking source defect was found; compiled contexts remain unverified.

The coordinator's first reset-consumer test used an incomplete v0.2 fixture and failed at schema validation. That failed log is retained. The corrected test uses a complete existing v0.1 model with the required parent-increment reset scope. No model source, numerical reference or acceptance bound was changed to obtain a pass.

`coordinator-checks/` retains the exact staging scripts and logs. Those scripts name their original private staging/repository locations; they are observation records, not a portable replay capsule. `manifest.json` pins this packet's exact bytes and the base commit. Do not claim full replay from these eight overlay files alone: imports, schemas, fixtures and independent reference inputs also belong in the prospective compiled study closure.

## Next required work

Preserve and verify document-bound references to `atlas/history.py` before its new shared edit; the original four-source closure is committed at a3de6f5. Then integrate the reviewed overlay and permanent tests. Freeze the complete generated-context corpus, independent expectations, source closure and policy before any compiled observation. Exercise double and all 38 Jet seed columns, selected/unselected invalid operations, sticky predicates/eager masking, initial/observable/reset contexts, history transactions and solver rollback. Run native then Wasm serially with one explicit target and `--parallel 1`. Retain all failures. Mohr–Coulomb integration and scientific admission remain separate tasks.
