# Generic implicit predictor / physical-constraint transition v1

CAP-implicit-predictor-constraints-v1, specialist `/root/md1997_source`, 2026-11-02. Isolated source `/private/tmp/atlas-predictor-constraints-v1/source/`; original frozen MD source-v2 and root runtime are unchanged. The only modified existing source is isolated `cpp/include/atlas/solver.hpp`; additions are standalone `cmake/predictor-constraint/CMakeLists.txt` and `tests/fixtures/predictor-constraint/projection.json`. No builds or compiled calls were made; no scientific approval is claimed.

## Change and invariant

The elastic predictor replaces each multiplier equation with gamma=0. A converged elastic trial outside the final physical yield constraint must be allowed to enter the full corrector. The old solver required final `solution_admissible` before that phase transition, preventing plastic correction for the newly constrained MD law even where independently constructed admissible BE roots exist. Original MD failure evidence remains unchanged.

The patch moves only the phase transition ahead of the final physical admissibility test when residual tolerance is met. `evaluate_model` has already checked domain and residual finiteness. Corrector success still requires `solution_admissible`; no success is returned merely because predictor converges. Line search, representable-neighbor correction, iteration limits, subdivision, failed parent rollback and final integrate-level physical check remain unchanged. The fixture with a cap below its full root verifies that domain-valid but physically excluded roots are NOT accepted. No model-specific condition or relaxed source constraint is added.

Exact old solver is retained in `original/solver.hpp`, SHA-256 b094c0f08d1f9ca71af5279c7946259e222c491b0bd97c3c70dbda392bbbe46e. `solver.patch` is the minimal diff; `source-receipt.json` binds isolated final files. Policy and requests were prepared before solver editing and any compiled observation. Preobservation fixture schema/unit metadata errors and the Mandel label correction are retained in `validation-attempts.json`; original request bytes are retained. Numeric requests and analytic expected endpoints did not change with the label correction.

## Fixture and checks

A deliberately synthetic scalar-pressure perfect-plastic projection uses complete sigma6/ep/gamma8 state, a multiplier residual and independent physical yield/cap constraints. It is not an admitted soil law and never enters the public catalogue. The source-only closed form is p=min(p_n+K*v,Y), gamma=max((p_n+K*v-Y)/K,0), ep=ep_n+gamma subject to positive domain and physical cap. It covers elastic inside-yield, first plastic predictor outside yield, unload/reload, hold/transient reset, invalid initial state, no domain root, physically excluded full root, iteration exhaustion and valid recovery. The first plastic trial is p21; corrector root p10/gamma.11 is admissible. With cap8, that same root must fail. Final gamma nonnegativity is enforced by complementarity and checked numerically; schema intentionally restricts physical solution constraints to persistent state.

`check_source.py` checks the independent analytical projection and evaluates declarative residuals at those endpoints through Python only; it explicitly proves predictor domain-valid/physical-invalid and full cap-excluded root. Saved `source-checks.json` passes all11case checks. Individual fixture schema/semantic validation and normal compiler generation pass; `source-check-generated/` retains generated C++ text/metadata only, not binaries. Python scripts parse and Wasm worker passes `node --check`.

`run_fixture.py` is the coordinator's executable collector AND checker: it runs all11literal cases plus the4 explicit reject/recovery pairs (19actualcalls/backend), saves each exact actual request/command/raw stdout/stderr/response in report.json, compares all8state components against frozen analytical expectations and exact failure rollback. Unload/reload/hold use the previous ACTUAL returned state for restart, not fabricated reference state. The native CLI executes one fresh process per request; Wasm uses one persistent engine, so reject/recovery shares an engine instance. Native parent-memory transaction correctness still needs existing transaction/C++ regressions; process isolation alone cannot certify hidden mutable memory. Every backend failure is retained; no gate is waived. `check_parity.py` compares saved backend reports/all8state components at the frozen1e-10absolute budget. The source checker alone is NOT a checker for compiled responses.

Coordinator commands after independent prospective review and explicit serial build slot (NOT executed by worker):

```sh
cmake -S /private/tmp/atlas-predictor-constraints-v1/source/cmake/predictor-constraint -B <new-native-build> -DCMAKE_BUILD_TYPE=Release
cmake --build <new-native-build> --target atlas_predictor_constraint_solver --parallel 1
python3 -B docs/investigations/implicit-predictor-constraints-v1/run_fixture.py --solver <new-native-build>/atlas_predictor_constraint_solver --output <new-native-report-dir>
# After native results are understood, equivalent Emscripten standalone target:
emcmake cmake -S /private/tmp/atlas-predictor-constraints-v1/source/cmake/predictor-constraint -B <new-wasm-build> -DCMAKE_BUILD_TYPE=Release
cmake --build <new-wasm-build> --target atlas_predictor_constraint_solver --parallel 1
python3 -B docs/investigations/implicit-predictor-constraints-v1/run_fixture.py --wasm <new-wasm-build>/predictor-constraint.js --output <new-wasm-report-dir>
python3 -B docs/investigations/implicit-predictor-constraints-v1/check_parity.py <native-report-dir>/report.json <wasm-report-dir>/report.json --output <new-parity-report.json>
```

Use fresh report directories; collectors refuse overwriting existing output. Preserve module, Wasm, generated catalogue and complete source/toolchain/build log hashes separately; engine module SHA alone is not a full runtime closure. Parent owns serial native/Wasm execution, unchanged MD qualification, all current16ordinary and dedicated-profile regressions, separate actual capability review and any later root installation. This source-only deliverable does not establish improved MD trajectories, absence of generic regressions, final E5 approval or live delivery.
