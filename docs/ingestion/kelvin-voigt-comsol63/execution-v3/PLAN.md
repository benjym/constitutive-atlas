# Kelvin–Voigt accuracy study v3 — prospective after retained v2 failure

NUM-kelvin-voigt-accuracy-v3; same COMSOL6.3 ordinary Kelvin–Voigt exact model SHA080fa946ea5d7743b133b62bbd39098b6b50ecf09d835f1a9966fa9283b6f8da and the same 43 independent reference cases. This revision is prepared **after observing and retaining v1/v2 failures**, before any v3 compiled observation. It does not retroactively describe the old controls as prospectively qualified. v1's CLI-spelling defect and v2's corrected observation results remain immutable historical evidence.

The v2 saved diagnosis measures default creep maximum strain error3.6550244596764495e-8 against the frozen3e-8 gate, tau20 creep2.7137911473573695e-7 against3e-8, and diagnostic coarse creep3.796891301368569e-6 against3e-6. These are genuine retained numerical accuracy failures; agreement between backends would not excuse them. This revision tightens time controls rather than changing references or acceptance limits.

Only the following solver controls change prospectively:

- Fine/public/direct controls: rtol3e-11, absolute scale fraction3e-14, maximum_substeps1000000.
- Coarse refinement diagnostic: rtol1e-5, absolute scale fraction1e-8, maximum_substeps1000000.
- Intentional negative budget-exhaustion cases keep their budget2 exactly. Minimum1e-12s, maximum1e6s, Newton1e-10/40iterations, method, loading, samples and every physical input remain unchanged.

The million-step allowance is a new explicit execution policy frozen before v3 observations, not a waiver of the two negative budget gates. budget-basis.json records original per-case accepted step counts, an indicative square-root work multiplier sqrt(1e-8/3e-11)=18.257… for the first-order step-doubling local estimator, and the selected allowance. That projection is planning evidence, not a guaranteed error/work bound. A v3 budget or wall-time failure remains a failure. Parent separately freezes Release toolchain flags and exact unchanged160-source closure before any compiled call; optimization targets runtime performance without changing source/model identity or acceptance gates.

All independent Cartesian3x3 Lame spring/dashpot and integrating-factor references remain byte-identical. The 43 cases still cover all-six constant rates, tau=.2/2/20, hydrostatic zero viscosity, shear, strain hold, all-six creep preset, stress ramp, finite rate jumps/load-hold-reverse, actual numerical endpoint restart, centered stress partial derivatives, passive basis covariance, replay, parent rollback, schedule valid-prefix retention, and eight invalid/recovery pairs. No finite-rotation objectivity, calibration or experimental validation is inferred.

Hard gates are unchanged: all-six persistent and accumulated strain3e-8; stress1Pa; direct/algebraic stress1e-7Pa; time relative1e-12; diagnostic coarse strain3e-6; centered directional partial normalized error1e-9; passive basis covariance1e-7Pa. Fine refinement strain error must be lower than coarse. Same-backend two-call replay remains exact. Stress-controlled transition rates may be null; finite-step endpoint rates are not compared to instantaneous analytical derivatives. Side/segment matching still distinguishes left and right finite-rate-jump stress.

New native and Wasm collectors run all43cases using the new controls, with no reused v2 trajectories. Wasm runs every call in one persistent instance so each invalid request is immediately followed by valid recovery. Native uses fresh subprocesses. Raw outputs are retained under execution-v3, never replacing old outputs. Each backend has86primarycalls plus direct-endpoint observations. Use create-only output paths; the unchanged Wasm collector writes incremental output and parent must ensure its destination is absent before execution.

Preparation commands perform no compiled calls:

```
python3 -B docs/ingestion/kelvin-voigt-comsol63/execution-v3/prepare_accuracy.py
python3 -B docs/ingestion/kelvin-voigt-comsol63/execution-v3/check_preparation.py
```

Parent-only commands after independent review, exact build/source/toolchain freeze and serial build handoff:

```
python3 -B docs/ingestion/kelvin-voigt-comsol63/execution-v3/study.py native --solver /absolute/qualified/atlas_kelvin_voigt_solver
node docs/ingestion/kelvin-voigt-comsol63/execution-v3/collect_wasm.mjs /absolute/qualified/kv.mjs docs/ingestion/kelvin-voigt-comsol63/execution-v3/cases.json docs/ingestion/kelvin-voigt-comsol63/execution-v3/wasm-raw.json
python3 -B docs/ingestion/kelvin-voigt-comsol63/execution-v3/study.py assess --backend wasm
python3 -B docs/ingestion/kelvin-voigt-comsol63/execution-v3/study.py parity
```

Use prepare_accuracy.py rather than the historical copied study.py prepare function; the latter retains original v1 metadata while the copied collector/assessor is otherwise deliberately unchanged. No gate can be weakened after v3 observations. Distinct diagnostics/revisions retain failures and exact identities.
