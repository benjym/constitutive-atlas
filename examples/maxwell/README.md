# Run the Maxwell model

This runnable research draft implements continuous Maxwell shear relaxation with elastic volume change. It uses the common Atlas compiler and timed solver. Stress and strain are compression-positive, SI units, in a fixed frame with infinitesimal strain; stress is total stress for a dry material point. The formulation remains a draft pending independent scientific review. The vendor's central-difference timestep algorithm is a separate numerical method.

From the repository root:

```sh
cmake -S cmake/maxwell -B /private/tmp/atlas-maxwell-build -DCMAKE_BUILD_TYPE=Release
cmake --build /private/tmp/atlas-maxwell-build --target atlas_maxwell_solver --parallel 1
python3 -m atlas.cli run examples/maxwell/creep.json \
  --solver /private/tmp/atlas-maxwell-build/atlas_maxwell_solver \
  --output /private/tmp/maxwell-creep.json
```

Choose an example:

| File | Loading | Expected response |
| --- | --- | --- |
| [creep.json](creep.json) | Hold all six stress components for 4s | Constant stress, linear deviatoric strain, zero volume change |
| [relaxation.json](relaxation.json) | Hold all six strain components for 8s | Constant mean stress, exponential deviatoric relaxation |
| [oedometer.json](oedometer.json) | Hold axial stress and prevent lateral strain | Axial creep and radial stress approaching axial stress; begins from elastic equilibrium |
| [load-hold-reverse.json](load-hold-reverse.json) | Strain rate, hold, then reverse | Continuous stress across rate changes and relaxation during the hold |

Each input explicitly supplies all six initial stress components, all material parameters, initial strain/rate, physical time and solver settings. In Mandel order the shear components are sqrt(2) times Cartesian tensor shear. Example parameters are K=20MPa, G=12MPa and eta=24MPa s, giving shear relaxation time eta/G=2s. They are illustrative constants, not a calibration.

Results contain stress in both `state` and `observables`, accumulated `strain`, physical `time`, loading/solver provenance and per-interval diagnostics. Boundary entries with `side: right` capture control transitions; stress-controlled boundary rates can be null. Restart from a regular endpoint with complete state, strain, rate, parameters and time. A stress hold permits creep; a strain hold permits stress relaxation.

Replay a saved result using the same CLI (its `specification` is retained):

```sh
python3 -m atlas.cli run /private/tmp/maxwell-creep.json \
  --solver /private/tmp/atlas-maxwell-build/atlas_maxwell_solver \
  --output /private/tmp/maxwell-creep-replay.json
```

The existing browser laboratory has no timed-control UI; these are timed JSON/CLI and Wasm API examples. Untimed strain-path requests reject this physical-time model. Source/qualification details and retained failures are in the [execution packet](../../docs/ingestion/maxwell-itasca900/integration-v1/README.md).

To reproduce the numerical study after building, use `python3 tests/test_maxwell.py --solver /private/tmp/atlas-maxwell-build/atlas_maxwell_solver --output /private/tmp/maxwell-native-raw.json`. Two calls per frozen case are assessed against independent analytical references. Source-specific tests qualify the displayed examples and the documented tau=0.2,2,20s cases; they do not qualify every combination in the broad declared parameter bounds.

For a separate Wasm build, configure with `emcmake cmake -S cmake/maxwell -B /private/tmp/atlas-maxwell-wasm -DCMAKE_BUILD_TYPE=Release`, then build the same explicit target serially. The result is `maxwell.js` plus `maxwell.wasm`, exposing the existing `atlas_integrate_time` and `atlas_run_schedule` ABI. If Emscripten's installed cache is not writable, copy its cache to a writable temporary directory and set `EM_CACHE` for the build; do not change system permissions.
