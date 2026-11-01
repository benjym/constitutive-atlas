# Historical test contexts, release repair v1

The original macOS CI run 41282257917 retained 20 failing methods among 1,364 tests. Their assertions mixed frozen nine-model/compiler-era expectations with the current twelve-model catalogue. This repair changes only test contexts, not models, compiler/runtime code, solver settings or numerical tolerances.

`tests/fixtures/historical-test-contexts.json` binds the nine original preview definitions, original compiler receipts, original integration catalogues and unchanged expected artifacts. The three 32-row catalogue inputs are exact Git blobs from the commits that introduced their corresponding tests. The first pressure-split compiler is the exact source in the candidate-validation commit. Other compiler identities come directly from their immutable study receipts. Old pre/post comparisons still compare both complete generated files. Current typing, registration, transaction, numerical and corruption gates remain current and unchanged.

All 20 original methods remain. AST verification checks that every other method in the 18 affected modules is unchanged. Current generation separately verifies every live definition, the exact twelve-model release identity, eleven effective scopes and one total scope. Synthetic total transport still includes every current model plus its fixture. The historical pre-total validator still rejects total admission; current admission tests continue to pass.

Validation: 20 originally failing methods pass; all 91 tests in their complete modules pass; 26 integrity/archive/CI checks pass. No new skips, native/Wasm builds, expected-output regeneration or admission claims. Original test bytes and transitively referenced archive maps are preserved: 38 snapshots, 98 receipt edges and 22 additive sidecars. Original native and GIS restart failures remain retained in their separately identified packets.

During development the new release-identity test used an incomplete Tresca ID, then assumed the older descriptor initializer suffix. These two new-test setup failures were corrected to the existing exact ID and current descriptor layout; no production code or acceptance bound changed. The original 20-method repair passed on its first run.

Run `python3 -B docs/reviews/historical-test-context-v1/verify.py` and `python3 -B -m unittest tests.test_historical_generation -v`. Full hosted native/Wasm checks and Pages deployment are separate release gates and remain pending at this packet's completion.
