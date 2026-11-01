# TMD2 process-status guard

1 November 2026. The supported `tools/benchmark_tmd2.py` command now checks saved process evidence before invoking the unchanged frozen numerical assessor. This closes **FIX-tmd2-process-status-v1**, not independent scientific review.

## Reproduced defect

The frozen runner journals all process return codes but does not fail its own invocation when a material process fails. The frozen assessor reports those codes but omits them from its acceptance decision. A saved successful response can therefore pass its source/refinement gates even when the corresponding process receipt records a nonzero exit.

[Witness](witness.json) records a replay with just `tmd2-400`'s receipt return code changed from zero to23. The original assessor exited zero and reported both gates passing. [Original false-pass summary](old-false-pass-summary.json) retains its result; stdout/stderr are included. Only saved native predictions were replayed. There was no solver execution, build, new fit or change to numerical bounds. The local normalized measurement file was used for the original assessor's descriptive aggregates; no measurements are copied here.

## Correction and scope

Before the original assessor runs, the supported command now requires, for each requested path:

- A JSON integer return code exactly zero, excluding booleans, strings and floating zero.
- Receipt hashes matching the expected artifact, input freeze and saved stdout/stderr bytes.
- An exact JSON boolean `ok=true` in the saved response.
- Strict unique-key and finite-number decoding of receipts and responses, using the existing observation reader.

The input freeze records the observation decoder hash alongside the command hash. Successful checking writes `process-check.json`; failure raises into the existing nonzero CLI failure path and leaves `run.json` and process outputs for inspection. All three original attempts may already have run when a failed receipt is detected; this is a pre-assessment guard, not an early-stop runner change.

Receipt hashes detect substitution relative to declared identities; they are not authenticated attestations. This guard does not replace the frozen assessor's schema/numerical checks or establish a complete adversarial audit of that historical assessor. Source precision/refinement policies and original packets are unchanged. The [command-routing check](command-routing-results.json) intercepts the material-runner stage and supplies saved observations with fresh receipt bindings. The valid route invokes the original Python assessor and yields a byte-identical summary; exit23 stops before the assessor. Its retained local check script reads the preexisting artifact only for identity and invokes no native process. This is a routing check with replayed data, not a fresh backend run.

The successful original frame remains accepted; [guard results](guard-results.json) and tests cover process failure, signals, type confusion, byte/hash substitution and inconsistent response success.

## Reproduce without native execution

```sh
python3 -B -m unittest tests.test_tmd2_benchmark tests.test_strict_observation_json tests.test_evidence_archives -v
python3 -B docs/reviews/tmd2-process-status-v1/replay.py
```

The replay needs the original pinned ZIP already at `data/raw/KFS-TMD1-5.zip`; it normalizes into a temporary local directory and reruns only the frozen Python assessor. No download, compiler or native executable is invoked. Numerical output remains subject to the existing historical-coordinate and scientific-review qualifications.

The previous supported command was copied byte-for-byte into the content-addressed source archive before editing; the DP preview's unchanged prospective receipt is bound through its new adjacent archive map. `manifest.json` pins the changed implementation, tests, witness and original reference files.
