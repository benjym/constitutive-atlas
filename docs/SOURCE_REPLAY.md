# Registered frozen-source replay

Historical evidence must execute its original source closure. Hash verification alone does not isolate imports from current code.

`atlas/source_replay.py` materializes the registered Python/data closure into a fresh temporary tree and starts a new Python process with `-I -S -B`. Original paths are preserved. Ambient `PYTHON*` and `ATLAS_*` settings are removed. The runner verifies every capsule member before execution and checks original members and external receipt documents afterward. It requires the exact registered process exit and original stdout, including retained negative findings.

The tracked registry is the trust anchor. Run only reviewed project registries: this executes trusted Python and is not a security sandbox. The Python interpreter and standard library remain external; recorded environment details do not establish cross-version or compiled binary reproducibility. No vendor code or native/Wasm artifact is executed by this registry.

## Transport audit v1

`catalogue/source-replays/transport-audit-v1.json` binds the original review manifest and result documents, capsule hashes/byte counts, and original assessor identities. Its two self-contained closures reproduce the preliminary five vulnerability findings and the fixed five witness results. Both use the original ten-file import/data closure. They run without Git, private papers or current assessor files.

```sh
python3 -B -m atlas.source_replay preliminary
python3 -B -m atlas.source_replay fixed
python3 -B -m unittest tests.test_source_replay -v
```

A successful preliminary replay means its five negative findings were reproduced. It does not approve the preliminary assessor. `tests/test_ingestion_packets.py` separately checks that the current assessor retains the five behavioral fixes and binds its current source hash. That regression is intentionally distinct from exact historical output reproduction.

## Adding another study

1. Enumerate its complete explicit Python import/data closure, receipt documents, models, schemas, raw companions and reference inputs. Resolve historical bytes through their original document-bound receipts; do not substitute current hashes.
2. Export reviewed source bytes with original paths and pins. `export` in the common module supports explicit pinned source inputs; it does not discover dependencies or authorize them. Use separate closures if one logical path has incompatible historical versions.
3. Register capsule and document hashes/byte counts, the trusted entrypoint, exact expected output and process exit. Review the registry as executable code. Preserve original negative reports and acceptance policies.
4. Demonstrate replay from a public export without `.git` or live source, and reject missing/corrupt inputs and changed source identity. Keep current-code regressions separate.

The transport audit and [sand/clay v2 source studies](../catalogue/source-replays/source-rates-v1/README.md) have registered closures. Source-study replay preserves complete original reports and all29 original Python test groups, separately from current-runtime rate/rejection/support checks. The [original compiled sand negative](../catalogue/source-replays/sand-negative-v1/README.md) also has a source-only re-audit closure preserving its full comparison, six original groups and negative CLI exit. Remaining finite-study verifiers and prospective mapping audits still need reviewed replay closures before shared arithmetic or auditor edits affect their frozen dependencies. The architecture inventory in [the design packet](reviews/frozen-source-evolution-v1/README.md) names those remaining migrations. A registered source replay does not reconstruct a compiler build, validate a constitutive model, or grant scientific admission.
