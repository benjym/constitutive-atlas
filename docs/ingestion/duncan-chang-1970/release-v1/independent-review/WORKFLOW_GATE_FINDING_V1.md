# Final source-scope finding: missing baseline ensemble gates

Reviewer `/root/duncan_complete_review`, 2026-11-02. **Do not stage/commit the currently proposed workflow as the final reviewed release scope.** This finding does not alter accepted package v6, its bounded E6/E7 metadata closeout or scientific model approval.

All 5,643 selected files in `public-source-allowlist-final-v1.json` match their exact isolated file sizes and hashes (800,807,672 bytes). The required qualified NorSand Wasm exception is included. The 769 exclusions are explicit and separate from the selected list. The updated status documents accurately retain E8 as pending and report fourteen definitions, four transcribed and ten draft.

Comparing `.github/workflows/verify.yml` against the explicitly named base `f4fce681aeec90c963ce69152b5e59b6094f8cc0` reveals that both `wasm` and `wasm-linux` jobs lose three existing ensemble gates:

```
node --test tests/test_ensemble.mjs
python -B -m unittest tests.test_ensemble_package
node tools/test_ensemble_wasm.mjs --wasm build-wasm/atlas.js --experiment web/dist/ensemble-experiment.json --output "$RUNNER_TEMP/ensemble-wasm.json"
```

They are absent elsewhere in the proposed workflow. The historical donor workflow predates these baseline additions; a source-frozen donor is not automatically equivalent to the release base's CI policy. Restore all three commands in both jobs after the standard package builder. Preserve this finding and the proposed workflow's current identity, then refresh the explicit allowlist. This restores the baseline gates rather than introducing a new numerical acceptance criterion after observing results. Their actual results remain for CI qualification on the intended revision.

No reviewer build, compiled execution, browser control, staging or shared modification occurred. The next review can accept the bounded final source scope after verifying the exact restored workflow and refreshed allowlist; E8 still requires terminal CI, Pages deployment and actual live evidence.
