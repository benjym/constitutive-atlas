#!/usr/bin/env bash
# Live numerical regressions. Each CMake invocation builds one target serially.
set -euo pipefail
profile=${1:?specify ordinary, schedules or plasticity}
out=${2:?specify an output directory}
mkdir -p "$out"
build_root=${ATLAS_CI_BUILD_ROOT:-.}
mkdir -p "$build_root"
build_root=$(cd "$build_root" && pwd)

build() {
  local source=$1 folder=$2 target=$3
  shift 3
  cmake -S "$source" -B "$folder" -DCMAKE_BUILD_TYPE=Release "$@"
  cmake --build "$folder" --target "$target" --parallel 1
}

case "$profile" in
  ordinary)
    native=$(cd "${3:?specify native build directory}" && pwd)
    wasm=${4:?specify Wasm build directory}
    ATLAS_NATIVE_FIXTURES=explicit-gis20-occ-restart-duncan-sclay1-v6 \
      ctest --test-dir "$native" --output-on-failure -R '^atlas_recorded$'
    python3 -B tools/check_current_numerical_ci.py --build "$native" --output "$out/catalogue"
    node tools/ci_smoke.mjs --native "$native/atlas_solver" --wasm "$wasm/atlas.js"
    node tools/test_current_catalogue.mjs "$native/atlas_solver" "$wasm"
    node tools/collect_scalar_functions_wasm.mjs "$wasm/scalar-functions.js" "$out/scalar-wasm-raw.json"
    python3 -B tools/check_scalar_functions.py "$out/scalar-wasm-raw.json" "$out/scalar-wasm-assessment.json"
    node tools/test_numerics.mjs --native "$native/atlas_solver" --wasm "$wasm/atlas.js"
    node tools/test_recorded.mjs --native "$native/atlas_solver" --wasm "$wasm/atlas.js"
    python3 -B tools/check_ramberg_osgood.py --solver "$native/atlas_solver" --save-responses "$out/ramberg-native.json" --output "$out/ramberg-native-checks.json"
    node tools/check_ramberg_osgood_wasm.mjs "$wasm" "$out/ramberg-wasm.json" "$out/ramberg-native.json"
    python3 -B tools/check_ramberg_osgood.py --responses "$out/ramberg-wasm.json" --output "$out/ramberg-wasm-checks.json"
    ATLAS_SOLVER="$native/atlas_solver" python3 -B -m unittest \
      tests.test_dp_dilatancy_domain tests.test_plasticity_oracles \
      tests.test_hypoplasticity_oracle tests.test_igs_oracle -q
    ATLAS_RECORDED_SOLVER="$native/atlas_solver" python3 -B -m unittest \
      tests.test_recorded_api tests.test_recorded_path tests.test_recorded_restarts -q
    ;;
  schedules)
    build . "$build_root/build-time" atlas_time_solver
    cmake --build "$build_root/build-time" --target atlas_time_tests --parallel 1
    ctest --test-dir "$build_root/build-time" --output-on-failure -R '^atlas_time$'
    ATLAS_TIME_SOLVER="$build_root/build-time/atlas_time_solver" python3 -B -m unittest tests.test_time tests.test_schedule tests.test_parent_reset -q
    python3 -B tools/ci_controlled_time.py
    build cmake/kelvin-voigt "$build_root/build-kelvin-voigt" atlas_kelvin_voigt_solver
    python3 -B tools/test_kelvin_voigt_native.py --solver "$build_root/build-kelvin-voigt/atlas_kelvin_voigt_solver" --output "$out/kelvin-voigt.json"
    build cmake/sls "$build_root/build-sls" atlas_sls_solver -DCMAKE_BUILD_TYPE=Debug
    python3 -B tools/test_sls_native.py --solver "$build_root/build-sls/atlas_sls_solver" --output "$out/sls.json"
    build cmake/burgers "$build_root/build-burgers" atlas_burgers_solver
    python3 -B tools/test_burgers_native.py "$build_root/build-burgers/atlas_burgers_solver" "$out/burgers"
    build cmake/bingham "$build_root/build-bingham" atlas_bingham_solver
    python3 -B tools/ci_schedule_references.py bingham "$build_root/build-bingham/atlas_bingham_solver" "$out/bingham"
    build cmake/perzyna "$build_root/build-perzyna" atlas_perzyna_solver
    python3 -B tools/ci_schedule_references.py perzyna "$build_root/build-perzyna/atlas_perzyna_solver" "$out/perzyna"
    ;;
  plasticity)
    python3 -B -m unittest tests.test_controlled_path tests.test_formulation tests.test_state_contract tests.test_historical_generation.HistoricalGenerationTests.test_current_generation_contains_every_live_definition_and_scope -q
    build cmake/orthotropic "$build_root/build-orthotropic" atlas_orthotropic_solver
    python3 -B tools/test_orthotropic_native.py --solver "$build_root/build-orthotropic/atlas_orthotropic_solver" --output "$out/orthotropic"
    build cmake/j2 "$build_root/build-j2" atlas_j2_solver
    python3 -B tools/test_j2_native.py --solver "$build_root/build-j2/atlas_j2_solver" --output "$out/j2"
    build cmake/hill "$build_root/build-hill" atlas_hill_solver
    python3 -B tools/test_hill_native.py --solver "$build_root/build-hill/atlas_hill_solver" --output "$out/hill"
    build . "$build_root/build-scalars" atlas_scalar_probe
    case "$(uname -s)" in Darwin) extension=dylib ;; *) extension=so ;; esac
    python3 -B tools/test_scalar_functions.py "$build_root/build-scalars/libatlas_scalar_probe.$extension" --output-dir "$out/scalars"
    ;;
  *) echo "Unknown numerical profile: $profile" >&2; exit 2 ;;
esac
