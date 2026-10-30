# Experimental update-linearization JSON API

The native C ABI and CLI expose the accepted-update tangent described in [UPDATE_LINEARIZATION.md](UPDATE_LINEARIZATION.md). This is an opt-in experimental interface, version `experimental-update-linearization-0.1`, independent of model schema versions. Native evidence is retained. Subsequent [browser numerical verification](BROWSER_NUMERICS.md) covers this endpoint in WebAssembly for the five public formulations; the website exposes configured protocol runs, not a tangent viewer.

## Calling convention

```cpp
extern "C" const char* atlas_linearize(
    const char* id, const char* parameters,
    const char* initial, const char* strain);
```

Supply comma-separated finite numbers in descriptor order. Empty parameter and initial-state strings select model defaults. Strain must contain six Mandel components. The returned UTF-8 JSON C string uses the existing shared API buffer: copy it before another API call; concurrent calls are not supported.

With a rebuilt solver:

```sh
solver --mode linearize --model linear-elastic --strain 0.00001,0,0,0,0,0
```

Only `--mode`, `--model`, `--parameters`, `--initial` and `--strain` are accepted in this mode. Physical-time models require their separate update API and are rejected here.

## Response contract

- `ok` describes the material update. `state` is its accepted result or the complete parent after update failure.
- `tangent_ok` describes derivative availability. `state_tangent` is an array of state rows by six strain columns when available, otherwise JSON `null`. A singular derivative can coexist with `ok=true`; callers must inspect both flags. CLI exit status follows material `ok`, so that case exits successfully.
- `message` describes the material update; `tangent_message` explains the derivative result.
- `state_fields` gives each field's name, zero-based row offset and component count. `tangent_columns` is `xx, yy, zz, sqrt2_xy, sqrt2_yz, sqrt2_xz`. Row units are the corresponding descriptor state units per unit strain; stress rows are the material stiffness. No symmetry is imposed.
- `model`, `catalogue_hash`, resolved `parameters`, `initial` and `strain` identify the evaluated request. Use the matching descriptor for units and full model metadata.
- `partition_policy="accepted_fixed"` and `branch_policy="selected_fixed"` declare the derivative convention. `reset_guard_at_zero` marks exact-zero parent reset guards only, not every possible nonsmooth boundary.
- `diagnostics` retains iterations, accepted substeps, rejections and increment fractions. Its `error` is the integrator's diagnostic, serialized as `null` when nonfinite; it is not a tangent-error estimate or a global accuracy bound.

Unknown models, invalid CSV or parameter decoding errors return `ok=false`, `tangent_ok=false`, `state_tangent=null` and a message, without inventing a material state. CLI option parsing can fail earlier with the existing minimal `ok=false,message` response. Consumers must not assume full metadata is present on errors. The existing `integrate` response is unchanged.

The API holds parameters and parent state fixed, differentiates selected preparation and all accepted substeps, and inherits the C++ API's branch and singularity limitations. Time, mixed-control solution and parameter derivatives remain outside this contract. A returned matrix at a switch is not a guarantee of a unique derivative.

## Native evidence and gradual reproduction

The [retained record](../catalogue/investigations/linearization-api-v1/manifest.json) and compressed responses cover 21 serial CLI cases through the C ABI. Eleven matrices exactly match the previously verified C++ results. Other cases cover successful updates with singular derivatives, failed-update rollback, physical-time rejection, malformed requests, unsupported options and compatibility with the existing integrate endpoint. Four new offline test groups plus twenty related groups pass. This adds interface verification, not independent constitutive validation.

Preparation and offline verification do not execute native code. Compile and capture are separate explicit steps:

```sh
python3 tools/verify_linearization_api.py prepare /private/tmp/atlas-linearization-api-reproduce
c++ -std=c++20 -O0 -Icpp/include -I/private/tmp/atlas-linearization-api-reproduce/generated cpp/main.cpp -o /private/tmp/atlas-linearization-api-reproduce/solver
python3 tools/verify_linearization_api.py capture --solver /private/tmp/atlas-linearization-api-reproduce/solver --output /private/tmp/atlas-linearization-api-reproduce/responses.json
python3 tools/verify_linearization_api.py verify /private/tmp/atlas-linearization-api-reproduce/responses.json --output /private/tmp/atlas-linearization-api-reproduce/verification.json
python3 -m unittest tests.test_linearization_api tests.test_update_tangent tests.test_atlas.LanguageTests tests.test_parent_reset.ParentResetLanguageTests -q
```

Two small standalone C++20 `-O0` builds and separate captures completed normally. The final capture bounds each invocation to 45 seconds. No full native suite, external reference build, CI run or Wasm build was performed for this change. `ATLAS_EXPORT` supplies the existing Emscripten keepalive annotation for a future rebuild; source annotation alone does not establish export/runtime parity. Browser integration and native/Wasm matrix comparisons remain open under NUM-01/02.

The subsequent [incremental settings API](INCREMENTAL_SETTINGS.md) adds `atlas_linearize_with_settings` and the opt-in `--integration-settings` option. It records numerical choices and uses the same settings for update and tangent replay; calls without that option retain the response contract above.
