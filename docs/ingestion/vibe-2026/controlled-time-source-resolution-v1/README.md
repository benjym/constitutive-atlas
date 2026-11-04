# Controlled-time CI current-source amendment

The original prebuild CI failed on the old controlled-time test pin after the separately accepted full-Python contract repair. The original failure log and exact collector preimage remain here. The prospective plan was frozen before edits.

Only two exact `(document, path, old SHA)` triples qualify for historical receipt resolution: the old controlled-time test in StageA source-manifest-v3 and the old CI collector in its original CI source-manifest-v1. Each requires the canonical old bytes via the production receipt API and exact current bytes via this amendment. The current test additionally matches the immutable previously accepted `75d282ac…` source freeze and `b17632d5…` independent decision. The collector is bound externally by this new source manifest and a genuine separately authored review decision. The new decision must have accepted status, no blockers, independent:true, distinct author/reviewer runs and the exact source-freeze path/hash. No author-created accepted decision is used.

Every other source pin remains a strict current-file hash comparison, including runtime, compiler, kernel, schema, model and portable-plan inputs. An old runtime archive does not permit a changed runtime. The original INPUTS and selection, portable-plan reversal, cases/gates/settings, workflow, capture and CLI bodies remain unchanged. `source-invariance-proof-v1.json` binds exact source-segment and verify-body comparisons plus the complete source-loop scan.

Old collector preservation adds one new sidecar in the CI packet, whose previous state was absent. The old collector hash occurs in three documents: only the original CI source manifest declares a repository-relative path/hash consumer. The original review manifest uses an absolute historical worktree path; workflow-results has a scalar provenance hash. Those records remain unchanged and no unsupported API bindings are invented. The existing canonical old-test archive/StageA binding remains unchanged.

Reproduce the pure isolated tests:

```sh
python3 -B docs/ingestion/vibe-2026/controlled-time-source-resolution-v1/test_source_resolution.py
```

All 14 tests pass (`pure-tests-v3.log`). Missing/corrupt/unbound old archives, changed current test/collector/runtime, unknown amendment entries, missing or stale independent decisions, tampered prior acceptance and portable-plan changes reject. All mutations use owned temporary fixture copies. No production source is mutated by the tests. The accepted prior record uses its original schema; the stricter independence fields apply only to the new decision. Two initial schema-handling failures and exact failed collector sources are retained as v1/v2, rather than modifying the prior immutable decision.

The author retains a pending-review refusal for the full verifier. A passing full source-only verify is intentionally deferred until the reviewer creates a genuine exact acceptance decision; no fake positive approval is created to bootstrap this check. `source-manifest-v1.json` is the exact source handoff boundary. Final positive verification evidence belongs to the reviewer/coordinator and does not rewrite this freeze.

No compilation, native/Wasm loading, material execution, browser, remote or commit operation was performed. Temporary negative fixtures clean up automatically; no process or additional build tree was created. The coordinator owns integration and remote qualification.
