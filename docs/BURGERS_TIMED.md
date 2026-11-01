# Burgers continuous law: timed draft integration

The source-pinned Itasca9.0.184 continuum Burgers law is available through the common physical-time engine as `burgers-itasca900-dry-zero-spin-ode`. It has a dedicated, opt-in catalogue and remains **draft**. Its scope is dry total stress, infinitesimal strain, fixed spatial coordinates and zero spin. It is distinct from the vendor's centered discrete update, the contact model and Burgers-Mohr plasticity.

Build one native target serially:

```sh
cmake -S . -B build-burgers -DCMAKE_BUILD_TYPE=Release
cmake --build build-burgers --target atlas_burgers_solver --parallel 1
python3 -m atlas.cli run examples/burgers/creep.json \
  --solver build-burgers/atlas_burgers_solver \
  --output /private/tmp/burgers-creep.json
```

The examples also include `relaxation.json`, `mixed.json` and `strain-reversal-hold.json`. They specify every parameter and all twelve initial state components explicitly. Parameters are uncalibrated illustrations. The output retains the specification; passing that result file back to `atlas.cli run` replays it. Restart requires complete stress and Kelvin history, accumulated strain, physical time and the last non-null strain rate.

The state layout is six Mandel stress components in Pa followed by six Mandel Kelvin-strain components. Kelvin strain must be deviatoric within the declared `1e-12` absolute trace tolerance. Mandel order is `[xx, yy, zz, sqrt(2)xy, sqrt(2)yz, sqrt(2)xz]`; strain and stress are compression positive. Parameter order is `[Kmod, Gm, Gk, etam, etak]`, with moduli in Pa and dynamic viscosities in Pa s. Field-level initial values are examples, not an initialization prescription; omitted state is rejected.

A strain hold generally relaxes stress. A stress hold solves for creep strain. With the supplied creep example, stress remains constant during the two-second hold and the analytical final `xx` accumulated strain is approximately `0.0183903`. Setting Kelvin history to `dev(sigma)/(2 Gk)` suppresses only its instantaneous evolution; Maxwell creep remains active.

For a direct constant-rate advance, use native modes `evaluate-time`, `observe-time` and `integrate-time`, supplying `--initial`, `--parameters`, `--strain-rate`, `--start-time` and (for integration) `--duration`. The [timed API](TIME_ODE_API.md) and [schedule contract](TIMED_SCHEDULES.md) describe settings and rollback. The model itself uses v0.3; the existing timed transport serializes responses and schedules as v0.2. The schedule method is backward Euler with step doubling; direct `integrate-time` uses midpoint with step doubling. Neither is the vendor centered update.

The equivalent Wasm target uses the same compiler and solver:

```sh
emcmake cmake -S . -B build-burgers-wasm -DCMAKE_BUILD_TYPE=Debug
cmake --build build-burgers-wasm --target atlas_burgers_solver --parallel 1
```

This produces `burgers.mjs` and `burgers.wasm`, exposing the standard `atlas_evaluate_time`, `atlas_observe_time`, `atlas_integrate_time` and `atlas_run_schedule` APIs. Emscripten requires a writable `EM_CACHE`; use a private writable cache when the installation cache is read-only. No browser laboratory controls for timed histories are provided by the current strain-path UI. This model is excluded from that catalogue and public packaging.

[The integration receipt](ingestion/burgers-itasca900/integration-v1/README.md) retains the prospective references, exact source closure, raw native/Wasm observations, failed first Wasm link and reproducible verification. [The source packet](ingestion/burgers-itasca900/README.md) records source conventions, equation locators, rights and remaining host gaps. Passing software checks does not confer scientific admission, physical calibration, full host equivalence or experimental validation.
