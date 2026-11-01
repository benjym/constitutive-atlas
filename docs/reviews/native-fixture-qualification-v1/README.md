# Native fixture qualification v1 — retained failure

The prospective [acceptance policy](ACCEPTANCE.md) is **not met**. No native test source, material/runtime/default, schema, CMake or workflow was changed, and no build occurred. Installation remains held.

The candidate keeps every original physical knot/amplitude/control, all numerical tolerances and all other budgets, while explicitly setting GIS max_depth20 for the test fixture. Native and Wasm both complete the exact original5-knot all-strain and5-knot drained paths. All-strain duplicate observations, exact same-backend checkpoint restart, three direct same-parent material segments and1e-10native/Wasm parity pass.

The additional frozen exact drained-restart requirement fails: maximum native/Wasm final-state differences are respectively2.541098841762901e-21and6.776263578034403e-21, confined to the intergranular-strain components. Stress, void ratio and cyclic memory match exactly. These differences are far below physical comparison bounds, but that does not satisfy the separately frozen exact gate. The all-strain/drained full native/Wasm response comparisons passed before this failure. Rotation and complete C++ AD/FD checks were not reached; they are not claimed.

Two earlier harness failures are retained separately: v1 fed the native checkpoint into Wasm and failed its same-backend exact assertion; v2 corrected ownership, then incorrectly passed a partial run-document settings object to the strict normalization helper for direct integration. v3 uses each backend's own checkpoint and the exact fully normalized recorded material settings. Acceptance criteria/requests remained byte-identical through these harness corrections.

Source inspection identifies a relevant numerical-context difference: recorded.hpp fixes its stress residual scale from the initial state's largest stress magnitude and model scales. The full drained run uses100000Pa; restarting from point2 uses100000.0000027397Pa because the original accepted lateral stresses have small control residuals. Thus the physical checkpoint alone does not reproduce that normalization context. This source fact is consistent with the tiny restart difference; causal sufficiency is not established here. No new driver patch or normalization change is justified solely by this diagnostic.

Keep the original strict native tests and all captured failures. The scoped fixture candidate remains unqualified; do not silently replace exact equality with a tolerance or remove failed cases. Any next study must explicitly decide the required restart contract and original native-test scope before more material execution or shared changes. Existing browser support, scientific admission and default GIS limitations remain separate.

Run `python3 docs/reviews/native-fixture-qualification-v1/verify.py` to check hashes, raw process receipts and retained pass/failure boundaries without material execution.
