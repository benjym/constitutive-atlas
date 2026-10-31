# Integrated trace operator results v1

The frozen operator study passed on native AppleClang and Emscripten/Wasm: **753 checks per backend, zero failures**. All97 independent exact-input Fraction fixtures, including rejected destinations, and all38 Jet cancellation derivative columns match bit for bit across backends. Both environments reported alternate rounding-mode support. Acceptance was frozen in commit669a4e8 before either build; original prospective documents and all14 input hashes remain unchanged.

The production `atlas::trace` route now uses the reviewed bounded compensated sum with an exact fixed-storage fallback. Its checked form validates all six components and all38 derivative columns, preserves the destination on rejection and supports finite final sums despite intermediate overflow. Exact zero is canonical positive zero. No model identity selects this arithmetic.

## Evidence and reproduction

- [Independent complete-row assessment](assessment.json) and [assessor](assess.py).
- Native and Wasm directories retain configure/build/observation stdout and stderr, command exits, source identities and compiled artifact hashes in receipts. Binaries remain outside the repository. Wasm cache generation messages are retained in build stderr; the observation streams had no stderr.
- [Original execution script](execution-script.py) records the exact coordinator invocation, environment overrides and local paths used. It is historical provenance, not an overwrite-safe replay command; do not rerun it over retained evidence.
- Re-audit without compiling or executing artifacts: `python3 -B catalogue/investigations/tensor-trace-operator-v1/assess.py`.
- Regression: `python3 -B -m unittest discover -s tests -p test_trace_operator_evidence.py -v`. Two groups pass; adversaries include missing/duplicate fixture rows, wrong result bits/status, a corrupted derivative, incomplete count and reported failure.
- Historical identity regression: `python3 -B -m unittest discover -s tests -p test_tensor_source_archive.py -v`. Both groups pass with the changed live header; missing/corrupt archives and altered receipt documents still reject.
- [File manifest](manifest.json) binds the retained study files. Artifact receipts describe binaries observed during this run; the source-only re-audit does not claim to authenticate or rerun absent binaries.

## Remaining roadmap gates

This study verifies the generic C++ scalar/Jet operator. A plain C++ lazy branch is not generated-DSL verification. Before a new constitutive rate study, audit and test generated trace/deviator contexts, especially invalid traces used in predicates: a NaN comparison can otherwise hide a rejected operator result. Ensure failure reaches the evaluation context while unselected branches stay lazy. Python reference semantics also require explicit cancellation checks.

Then freeze a new sand-rate study under the repaired engine identity and re-evaluate the complete original corpus with unchanged numerical budgets. Preserve the original failed `barodesy2015-rates-v1` study and its portable source closure. Clay instantaneous rates, finite integration, material derivative studies, experimental comparisons and scientific admission remain separate open gates.
