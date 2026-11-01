# External input protocol

All paths below are absolute. Parent produces actual receipts only after genuine build-only work; this packet produces no actual receipt. Every referenced JSON is independently pinned by raw SHA256. Pass `--decimal-freeze FILE --decimal-freeze-sha256 INDEPENDENT_EXPECTED_SHA` to positive operations. Place the execution freeze and its four direct receipt files outside source, build and output-parent trees.

Execution freeze closed keys: `identity` = `md1997-decimal-ci-execution-freeze-v1`; `purpose` = `actual`; `source_directory`; `source_freeze`, `build_binding`, `build_receipt`, `toolchain` each `{path,sha256}`; `inputs` mapping absolute path to `{sha256,realpath}`. Inputs may hold additional pre-reviewed collector/build-policy/receipt pins. Their complete source/tool closure remains parent review's responsibility.

Source freeze closed keys: `identity`, `directory`, `files` mapping every relative source file to its SHA256; exactly601 files, no extras/missing paths, symlinks or bytecode. Independent review pins its exact bytes and verifies the accepted source overlay. The helper validates complete inventory and hashes; the identity string is documentary, not an alternate admission route.

Build binding is the accepted oracle schema: identity `md1997-decimal-native-build-binding-v1`, purpose actual, source_freeze_sha256 (hash of this full new source-freeze JSON), fixture_sha256, generated_catalogue_sha256, executable_sha256, executable_path (BUILD/atlas_numerical_tests), working_directory (BUILD), model_sha256. Actual source-freeze and executable hashes are deliberately not fabricated in this implementation packet. Fixed reference/evaluator/policy/base-source identities are compiled into the separately reviewed C++ exporter; only actual build-binding SHA is supplied through ATLAS_MD1997_DECIMAL_BUILD_BINDING_SHA256.

Reviewed build receipt closed keys: identity `md1997-decimal-reviewed-build-binding-v1`; passed literaltrue; source_freeze_sha256; build_binding_sha256; `artifacts` mapping absolute artifact path to SHA256; `evidence` nonempty mapping absolute saved build/generated/tool/source/process/review evidence path to SHA256. Artifacts must include all generated/cache/CTest/strict executables and every registered executable/Python/script/scalar library from dispatcher context. Every supplied evidence/artifact path must remain byte-exact. This is an adapter for externally reviewed genuine build evidence, never proof inferred from its passed field. Parent's independent actual-build binding review is a mandatory prerequisite.

Toolchain file must contain nonempty `files` mapping each absolute tool path to an object containing `sha256` and `realpath` (additional documentary metadata permitted). Every mapped path's resolved bytes and realpath are checked at every boundary. Selected Python and CTest must resolve to mapped bytes. Tool symlinks are permitted only by their frozen realpaths; source/receipt/artifact symlinks are rejected. Parent must supply complete reviewed tool/input closure, not a two-tool synthetic test map.

Commands (all placeholders require independently frozen real inputs):

```
python3 -B tools/check_native_fixture_dispatch.py check --catalogue BUILD/generated/models.json --source-root SOURCE --build BUILD --output NEGATIVES.json
python3 -B tools/check_native_fixture_dispatch.py decimal --catalogue BUILD/generated/models.json --source-root SOURCE --build BUILD --output DIRECT.json --decimal-freeze FREEZE.json --decimal-freeze-sha256 SHA
python3 -B tools/check_native_fixture_dispatch.py ctest --suite linux-main --catalogue BUILD/generated/models.json --source-root SOURCE --build BUILD --output MAIN.json --decimal-freeze FREEZE.json --decimal-freeze-sha256 SHA
python3 -B tools/check_native_fixture_dispatch.py ctest --suite recorded --catalogue BUILD/generated/models.json --source-root SOURCE --build BUILD --output RECORDED.json
```

Use macos-main on its reviewed platform. The wrapper preserves platform suite filters. Run the interpreter with assertions enabled and bytecode disabled. Historical14/15 strict delegation needs PYTHONOPTIMIZE unset; Decimal positive child and assessor receive its exact string0. All operation receipts must be required jointly by parent execution, never treating one positive export as the overall CI result.
