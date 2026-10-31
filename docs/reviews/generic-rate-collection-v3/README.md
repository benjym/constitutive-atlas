# Generic tagged instantaneous-rate collection v3

The separate v3 Python collector/assessor, Python comparison wrapper, Node collector and C++ driver introduce protocol/observation/assessment/comparison version `0.3`. Historical v1/v2 tools and the original C++ driver remain byte-identical to HEAD. These tools contain no material equations or model-ID-specific branches.

The [contract](CONTRACT.md) separates source accuracy, finite output support and recognized rejection. It enables the existing [clay2005 prospective matrix](../../ingestion/hypoplastic-clay-2005/compiled-plan-v3/README.md) without converting ten support-only cases into invented reference rates. Its 41 independent source vectors and original budgets are unchanged. The generic tools do not yet constitute a compiled clay2005 study.

`tests.log` records **47 passing synthetic checks** across historical, v2 and v3 suites (24 v3 checks). Tests use project-owned ESM stubs and inert bytes, with fabricated raw native receipts; they never instantiate compiled Wasm or execute native materials. They cover strict tags/expectation fields, finite-only parity without source references, opposite finite extremes, exact response/echo and positional layout, duplicate keys, source/build/raw mutation, incomplete/trapped calls, recovery pairing and full response recovery, and contradictory failure markers. `initial-tests.log` and `closure-tests.log` retain earlier passing development runs before all review findings were closed.

The [independent source-only review](../tagged-rate-transport-review-v3/README.md) retains the initial lexical, missing recovery relation and contradictory error-marker failures. Its final report has44/44 expected observations. The fixes require ASCII decimal CSV, an explicit immediately preceding rejection for every recovery row, closed successful raw shapes and no failure markers on completed observations. Review fixtures are structural adversarial tests, not evidence that a binary ran.

The new `tests/research_rate_driver_v3.cpp` uses an ASCII decimal scanner and finite/full-consumption `strtod` conversion. It accepts finite representable subnormal conversions even when libc reports ERANGE. This driver has **source review only** in this packet; actual native/Wasm compilation, minimum-subnormal echoes/material rejection and all109 literal clay2005 calls remain required in the separately frozen study. The original driver is preserved for historical receipts.

`source-pins.json` binds exact new sources, evidence and historical source identities. Snapshots under `sources/` retain these v3 source bytes. Reproduce the synthetic checks from the repository root:

```sh
python3 -B -m unittest tests.test_research_rate_collection tests.test_research_rate_collection_v2 tests.test_research_rate_collection_v3 -v
```

No finite-path integration, material tangent, experimental validation, scientific admission, new public runnable model or deployment follows from this tooling result.
