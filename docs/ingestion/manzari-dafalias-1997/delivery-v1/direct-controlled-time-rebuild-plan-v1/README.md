# Controlled-time VIBE: no CI amendment needed

The unchanged existing CI verifier actually passed source-only on the candidate (Python -I -B, tool chunk 220787, exit 0). See source-check.json: all four selected input manifests, original CI freeze and portable plan pass; 32 points, eight histories, seven invalid contexts, nine reversible path changes. Zero compiled calls. No shared source edits, builds or extra temporary resources were created.

Neither plan-v3.json nor numerical source-manifest-v2.json pins solver.hpp. The two old test/collector exceptions already have independent accepted source-resolution handling. Do not change CI plans, verifier or workflow for solver.hpp. The stale b094c0f08d1f9ca71af5279c7946259e222c491b0bd97c3c70dbda392bbbe46e pin is in the public-engine qualification receipt consumed by tools/build_controlled_time_web.py. Current solver is 05e6cc0c9dd6b6774597e07de0abe2beb7d9128383423d22b34c2e1d0a4d9218. The separate dependency proof reports solver unreachable and all three generated files identical; package-only compatibility review belongs to the coordinator. This packet does not approve that proof or a package exception.

The following is the existing model-only reproduction path, for coordinator use only if reproduction is still needed. It omits the synthetic generic batch, changes no numerical reference or gate, and has NOT been executed. Use fresh build/output paths; retain raw logs and stop on first failure. Native output is .dylib on macOS (.so on Linux); the exact native module path below is macOS. Existing qualification covers point rates, all sampled histories, restart/replay/refinement, trial/depth refusal, raw domain refusal/input/output immutability and exact native/Wasm parity. This is numerical reproduction, not a replacement for public examples/package/browser qualification or an accepted public receipt.

```sh
set -euo pipefail
cd /private/tmp/atlas-md1997-current-main-integration-v1/source
VIBE_NATIVE=/private/tmp/atlas-vibe-current-source-native-v1
VIBE_WASM=/private/tmp/atlas-vibe-current-source-wasm-v1
VIBE_OUT=/private/tmp/atlas-vibe-current-source-qualification-v1
mkdir "$VIBE_OUT"
cmake -S cmake/controlled-time -B "$VIBE_NATIVE" -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON "-DATLAS_CONTROLLED_TIME_MODELS:STRING=$PWD/models/research/vibe/vibe-2026-explicit-appendix-a.json" 2>&1 | tee "$VIBE_OUT/native-configure.log"
cmake --build "$VIBE_NATIVE" --target atlas_controlled_time_capability --parallel 1 2>&1 | tee "$VIBE_OUT/native-build.log"
python3 -B tools/qualify_vibe2026.py --module "$VIBE_NATIVE/libatlas_controlled_time_capability.dylib" --catalogue "$VIBE_NATIVE/generated/controlled_time_catalogue.json" --model models/research/vibe/vibe-2026-explicit-appendix-a.json --plan docs/ingestion/vibe-2026/controlled-time-ci-v1/plan-v3.json --source-manifest docs/ingestion/vibe-2026/numerical-qualification-v1/source-manifest-v2.json --output "$VIBE_OUT/native" 2>&1 | tee "$VIBE_OUT/native-tests.log"
emcmake cmake -S cmake/controlled-time -B "$VIBE_WASM" -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON "-DATLAS_CONTROLLED_TIME_MODELS:STRING=$PWD/models/research/vibe/vibe-2026-explicit-appendix-a.json" 2>&1 | tee "$VIBE_OUT/wasm-configure.log"
cmake --build "$VIBE_WASM" --target atlas_controlled_time_capability --parallel 1 2>&1 | tee "$VIBE_OUT/wasm-build.log"
node tools/qualify_vibe2026.mjs "$VIBE_WASM/atlas_controlled_time_capability.mjs" "$VIBE_WASM/generated/controlled_time_catalogue.json" models/research/vibe/vibe-2026-explicit-appendix-a.json docs/ingestion/vibe-2026/controlled-time-ci-v1/plan-v3.json docs/ingestion/vibe-2026/numerical-qualification-v1/source-manifest-v2.json "$VIBE_OUT/wasm" "$VIBE_OUT/native" 2>&1 | tee "$VIBE_OUT/wasm-tests.log"
```

Do not copy an old accepted public-qualification.json onto new artifacts: bundling requires genuine qualification evidence and the independently reviewed approval-bound root receipt. No such new receipt is authored here. Smallest next action is the package-only independently reviewed unreachable-pin fix; the live CI source gate already passes.
