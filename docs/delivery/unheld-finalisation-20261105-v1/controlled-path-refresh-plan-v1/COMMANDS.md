# Coordinator commands after independent source review

Install both exact guarded tool successors before current16 source-freeze/build, because the ordinary collector inventories all tools. Both builders remain byte-exact. Never overwrite the old VIBE plan or evidence. The new plan and execution records are generated from the actually installed current source; no new compiled result or plan hash exists in this packet.

From the candidate source root, in a fresh coordinator-owned serial slot:

```sh
python3 -B tools/qualify_controlled_path_refresh.py --plan docs/delivery/unheld-finalisation-20261105-v1/controlled-path-refresh-v1/plan-v1.json prepare
```

Freeze the actual emitted plan bytes/hash and independently accept that exact plan/source/command corpus before executing. Then use the same literal plan path and its real SHA256 on `verify`, `run --implementation-run <actual coordinator run id>` and, if needed, `collect`:

```text
python3 -B tools/qualify_controlled_path_refresh.py --plan docs/delivery/unheld-finalisation-20261105-v1/controlled-path-refresh-v1/plan-v1.json --plan-sha256 REAL_ACCEPTED_PLAN_SHA256 verify
python3 -B tools/qualify_controlled_path_refresh.py --plan docs/delivery/unheld-finalisation-20261105-v1/controlled-path-refresh-v1/plan-v1.json --plan-sha256 REAL_ACCEPTED_PLAN_SHA256 run --implementation-run ACTUAL_COORDINATOR_RUN_ID
```

These are templates, not executable authorization; the real hash/run identity must come from genuine preparation/review. Existing command allocations, native/Wasm numerical invocations and checker tolerances are unchanged. Only build/output prefixes change. Build directories are `.local/controlled-path-refresh-20261105-v1/{norsand,interface2016}-{native,wasm}`; each explicit target remains `atlas_path_capability --parallel 1`. All22 commands retain their original ordering and failure behavior. No new lifecycle wrapper was added. Coordinator execution must obey the shared serial slot/reap rules.

Fresh engine outputs are `docs/delivery/unheld-finalisation-20261105-v1/controlled-path-refresh-v1/execution-v2/norsand/engine` and the corresponding `interface2016/engine`. Obtain separate exact independent build reviews, then use unchanged `finalize ENGINE_DIR` for each; final package guards receipt-select only the original or this one new allowlisted plan with exact hash. New pending/review/qualification files retain the established compatible schema; the new plan has distinct identity and all outputs are new. No old receipt is relabelled or rebound.

Dependency guard after both genuine reviews/finalization:

```text
python3 -B tools/check_current_dependency_assets.py --controlled-plan docs/delivery/unheld-finalisation-20261105-v1/controlled-path-refresh-v1/plan-v1.json --controlled-plan-sha256 REAL_ACCEPTED_PLAN_SHA256 --output NEW_EXTERNAL_GUARD_OUTPUT
```

Default guard invocation still selects its old engine paths. The new option selects only the two fresh controlled engines; Maxwell remains `docs/ingestion/vibe-2026/maxwell-refresh-v1/execution-v1/engine`.

## Exact Pages routing instruction for coordinator

Current `.github/workflows/pages.yml` line73 uses the default dependency guard and line78 uses both old VIBE engine paths. After actual fresh plan/assets are retained, change ONLY that guard command by adding the exact new `--controlled-plan` and real accepted `--controlled-plan-sha256` above. In line78 replace only `--controlled-path-wasm-dir` and `--interface2016-wasm-dir` values with the two new engine directories above. Preserve Maxwell path, ordinary15-role flags, other actions/gates and environment exactly. Do not install a placeholder or guessed hash in runnable workflow. This packet supplies the exact two path changes and guarded command; a final workflow delta awaits the genuine new plan hash/compiled-asset review. Pure package guards must pass before any website build.
