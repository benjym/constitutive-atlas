# Experimental shared history runtime

The [Python reference](HISTORY_REFERENCE.md) now has a separate C++/WebAssembly implementation for synthetic phased-history programs. It is an arithmetic transaction runtime. Material integration, internal subdivisions, mixed control, host reductions and PM4 equations remain separate work. Public model APIs, model identities, source-review flags and the 32-component retained capacity are unchanged.

## Compilation and transport

`python -m atlas.history_compiler OUTPUT_DIRECTORY SOURCE_DIRECTORY` validates each JSON program using the history reference's schema, units, graph, storage and preparation-ancestry rules, then generates a dispatch header. Each program has a canonical SHA256. Every executed numeric AST value is checked for finiteness, including operands of min/max, guards and comparisons. C++ conditional expressions retain lazy `select`; skipped phases do not evaluate writes. Boolean values may control `select` or be checked; Boolean arithmetic is now explicitly rejected by the history validator. This corrects an inference ambiguity in the experimental contract without changing the legacy model DSL.

Numeric history values use binary64. Integer states, inputs, mode values and expression literals must be exactly representable as finite binary64 numbers; for example, 9007199254740993 is rejected before trial rather than rounded during restart. Wire decimal tokens are parsed as binary64 values.

The `atlas_history_solver` target builds [one source](../cpp/history_main.cpp) for both native and Emscripten. It compiles `fixtures/history/*.json`, separately from all model catalogues. Its descriptor lists each complete program, hash, scalarized sizes and explicit `state_order`/`input_order`. **Flat wire layout uses lexicographically sorted field/input names**, with six contiguous Mandel components for each symmetric tensor. Source JSON key order cannot change the layout for a given hash.

Native `--describe` and C export `atlas_history_describe()` return that descriptor. Native trials require all six named arguments:

```
atlas_history_solver --program ID --hash SHA256 --state CSV --inputs CSV --generation INTEGER --epoch INTEGER
```

The equivalent C/Wasm export is `atlas_history_advance(id, hash, state_csv, inputs_csv, generation_decimal, epoch_decimal)`. All six arguments are strings. Counters are canonical unsigned decimal integers bounded by 9007199254740991; scalar wires must have the exact finite component count. Wrong identities/hashes, malformed inputs and invalid parent modes fail before trial (`valid=false`). Native malformed requests exit 2. A correctly formed trial exits 0 even if its constitutive-free transaction fails (`valid=true, ok=false`). Returned C strings belong to the module and remain valid until its next call on that thread; copy/parse them immediately.

Responses carry the program hash, complete flat values, generation, preparation epoch, executed-phase event indexes, attempted/executed phase counts and failed-phase index (`-1` on success). Phase indexes refer to the descriptor's ordered program phases. On any trial failure, every value and both counters equal the incoming parent and events are empty; attempt diagnostics retain provisional work. Successful outputs are candidates for caller publication. Repeated calls have no persistent material state. The wire checks identity and completeness; it does not authenticate a physical history or provide a durable lineage ledger.

## Reproducible checks

Build these targets serially under the current local build policy:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --target atlas_history_solver --parallel 1
python -m unittest tests.test_history tests.test_history_runtime -v
emcmake cmake -S . -B build-wasm -DCMAKE_BUILD_TYPE=Release
cmake --build build-wasm --target atlas_history_solver --parallel 1
python -m tools.history_cases --output /tmp/history-cases.json
node tools/test_history_wasm.mjs --cases /tmp/history-cases.json
```

The 23-case matrix derives expectations from the independent Python evaluator. The ordered fixture also has hand-computed oracles in `tests/test_history.py`. Cases cover simultaneous state/preparation swaps, ordered lag reads, dimensional clock/tensor updates, restart, strict guard signs, unused invalid branches, invalid written modes, overflow hidden in guard/min/norm/comparison, inactive checks, late failure and exhausted counters. Tests require exact rollback and event/counter/phase diagnostics, and compare successful numeric values at relative tolerance 2e-14 with absolute floor 1e-300. Invalid wires are tested separately; compiled descriptors must match current source programs. CI regenerates the Python matrix and exercises the real Wasm C ABI.

These checks advance generic runtime infrastructure toward HIST-G8. They do not close its PM4 source/model gates, all HIST-G3 internal-half/host cases, full HIST-G4 adapter scope or durable HIST-G5 lineage. The [legacy bridge](HISTORY_LEGACY_BRIDGE.md) remains a separate full-integrator transport with its existing reset semantics. No physical model or experimental validation is supplied by the arithmetic fixtures.
