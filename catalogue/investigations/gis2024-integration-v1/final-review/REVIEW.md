# GIS finish packet independent read-only review

Scope: staged archive/test finish packet and authoritative amended installed files at `/Users/bmar5496/code/constitutive-atlas`; reviewed content hashes in reviewed-hashes.json. No repo edits, native/Wasm execution, builds or acquisition. Review is bounded numerical/provenance assessment, not scientific admission.

## Findings

1. **Resolved test blocker:** initial tests/test_gis2024_integration_study.py:23 compared the raw native-report byte SHA with canonical-object digest. Retained raw SHA is a8ebcdc71ba3681aca9596fa6cfd3d7fa74feecc288fc7c9f532a7390f9caa03; canonical digest is82b1a8829717d319452100a727a89ea5f8c05a55350d80750af0e7753ed09252. The amended test correctly hashes PACKET/native.json bytes, matching tools/test_gis2024_paths_wasm.mjs's recorded semantics. Do not rewrite the historical receipt to disguise this difference.

2. **Remaining minor provenance action:** current integration manifest does not yet pin atlas/structure.py or schemas/model.schema.json. Both are actual model-load/generation dependencies: atlas/model.py:46–52 imports check and reads the selected schema, and CMakeLists.txt GIS generation DEPENDS names both. Add these current file hashes before calling dependency provenance complete. Solver/settings/main/model/init and immutable build-config snapshots have been added and were inspected. This missing-pin issue does not falsify observed numerical comparisons; it weakens the full dependency receipt.

3. **Optional standalone-runner hardening:** independent-review/audit_runner.py:26–32 catches any Exception for corruption probes and records 'accepted' if none is raised, but always exits successfully after printing. Its current documented use is diagnostic, and focused unit tests assert rejection independently. If intended as a CI gate itself, assert every corruption probe yields the expected rejection class after printing; avoid treating an unrelated exception as successful semantic rejection.

## Verified review conclusions

- tools/verify_gis2024_paths.py:9–18 separates historical receipt identity from fresh numerical trust correctly. It verifies report/model/catalogue identities; a supplied historical reference is hash-bound and checked against current protocol/source/dependency metadata and exact case inputs. Actual records are assessed against fresh reference.study(), not historical trajectory values. checked_reference() pins reviewed independent reference sources and checks fresh replay plus budget/branch requirements.
- tests/test_gis2024_path_reference.py:58–73 allows declared cross-platform numerical roundoff for archived trajectories, while independent stage/domain/three-grid/refinement/volume/covariance tests operate on fresh calculations. This avoids claiming bitwise portable reference results. Historical receipt metadata remains exact.
- Recovery checks bind control to an actual tight unpartitioned trajectory call, validate the normal response contract, and require exact request/response equality after ordered budget/domain/zero probes. Tests reject altered controls, altered recovered states, reversed/missing recoveries and false verification flag. Retained transcript supports these values; temporal ordering is supported by the pinned executed Node runner, not independently proven by JSON alone.
- Failure probes verify budget failure after accepted progress, rollback, zero update, finite echoes, settings, counters and partial coverage. Intermediate memory corruption is rejected even after rechaining, through the independent selected-domain check. Endpoint-domain checks do not establish every hidden production integration-stage domain.
- Numerical scope remains four strictly interior zero-spin cases, selected smooth segments,20trajectories/204updates per backend, empirical refinement and broad declared regression/reference floors. No boundary/origin/saturation, within-segment branch transition, general preparation, experimental or public admission follows.

## Execution evidence

I ran only `python3 -m unittest tests.test_gis2024_path_reference tests.test_gis2024_integration_study -v` before the authoritative amendment:17groups,16passed, one failed at the now-corrected raw/canonical hash comparison. No numerical/reference/recovery negative test failed. After amendment I inspected the changed code and hashes without repeating full tests, as requested. Parent reports57focused Python tests passing after its amendment; that wider run was not independently executed here.

No additional bounded numerical blocker identified. Add the two load-dependency pins; preserve the scientific scope gates and historical receipts.

## Parent finalization follow-up

Parent confirms it will add the two schema/load pins and make the diagnostic runner reject accepted corruptions with a nonzero exit while catching ValueError only. It additionally reports installed rejection of Boolean partition metadata and comparison of archive source URL/DOI/locators. These are straightforward provenance/validation changes and do not alter numerical kernels. With those changes, no remaining blocker was identified within this bounded review. reviewed-hashes.json intentionally identifies the snapshot I directly inspected; parent will pin the final snapshot rather than imply these are its final hashes.
