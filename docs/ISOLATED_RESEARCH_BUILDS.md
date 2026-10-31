# Isolated common-engine research builds

Use [cmake/research](../cmake/research/CMakeLists.txt) to compile one reviewed
declarative model through the ordinary Atlas compiler and C++ engine. It accepts
an exact model file, so packet manifests, analytical references and neighbouring
drafts cannot accidentally become model inputs. No material equations or
model-specific dispatch are added by this target. The public model list and
top-level build are unchanged.

The coordinator owns compiled builds and execution. Freeze the model, independent
references, corpus and acceptance policy before source-model observations. Record
the generic target and transport sources, compiler/schema/engine dependencies,
toolchain, commands, logs and exact generated/executable hashes with the study.
An isolated build is not equation review, numerical acceptance or public admission.

## Native

Choose a fresh build directory per source/study revision. Supply an absolute
model path and select `rate` for instantaneous rates or `integrate` for the
ordinary material-update API:

```sh
cmake -S cmake/research -B /private/tmp/atlas-study-native \
  -DATLAS_MODEL_FILE=/absolute/path/to/reviewed-model.json \
  -DATLAS_RESEARCH_TRANSPORT=rate
cmake --build /private/tmp/atlas-study-native --target atlas_isolated --parallel 1
```

The generated descriptor and C++ are in `generated/models.json` and
`generated/models.hpp`. The native executable is `atlas_isolated`.

`rate` reuses `tests/research_rate_driver.cpp`, exposing `--describe`, a
four-argument rate call and `--stream`. Stream requests are four tab-separated
fields: model ID, parameters CSV, state CSV and six-component increment CSV.
It evaluates the compiled rate expression without integrating it. This transport
is intended for source-rate studies; residual/incremental laws need a different
study interface.

`integrate` reuses `tests/research_integrate_driver.cpp`, which wraps the ordinary
material API. Its stream accepts `--describe` or five tab-separated fields:
model ID, parameters CSV, full parent CSV, strain-increment CSV and settings CSV.
The caller owns ordered loading and actual returned-parent chaining. Physical-time
or event/preparation studies must use their applicable API and contract; this
strain-increment stream does not create those capabilities.

## WebAssembly

Activate the existing Emscripten SDK, then configure a different fresh directory:

```sh
emcmake cmake -S cmake/research -B /private/tmp/atlas-study-wasm \
  -DATLAS_MODEL_FILE=/absolute/path/to/reviewed-model.json \
  -DATLAS_RESEARCH_TRANSPORT=rate
cmake --build /private/tmp/atlas-study-wasm --target atlas_isolated --parallel 1
```

Outputs are `atlas-isolated.js` and `atlas-isolated.wasm`. The rate transport
exports `atlas_describe` and `atlas_research_rate`; the integration transport
uses the ordinary `cpp/main.cpp` exports, including `atlas_integrate_with_settings`.
Use a study-specific opaque collector and retain every C-ABI name/type/argument
and raw response. Native/Wasm agreement alone does not independently verify a law.

Keep native and Wasm builds serial, one explicit target and one job, because of
the observed Cortex interruptions. Do not execute source-author programs or
bypass endpoint protection. This target invokes only project-owned compiler and
transport code over declarative input.
