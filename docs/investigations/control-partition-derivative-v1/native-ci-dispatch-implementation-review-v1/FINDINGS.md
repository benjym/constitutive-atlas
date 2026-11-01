# Independent native CI implementation review v1

Decision: **BLOCKED**. Exact implementation fb9fc1318324e6f542af5fe68ac058af18afc14a1364675c36efe52d5243767d has three independently witnessed false acceptance paths B1/B2/B3 and one nonblocking failure-diagnostic concern C1. The eighteen author mock tests pass; that does not resolve these findings. No real CTest, compiler, build, material/backend or remote CI call occurred.

Reviewer /root/md1997_source did not author the two helpers, tests or workflow implementation (author /root/md1997_review). The reviewer authored the accepted CI compatibility plan, independently accepted by review5e304443; this review checks another author's implementation against that fixed plan. The reviewer edited only this new review directory.

## B1 — omitted native CTest registrations can qualify (blocking)

check_native_fixture_dispatch.py:194–196 obtains both the registration inventory and expected selected coverage from the same generated CTestTestfile.cmake. It never asserts the complete required inventory from the unchanged source CMakeLists.txt. The isolated native CMake source registers ten tests. A registry containing only atlas_numerical and atlas_recorded is nevertheless accepted by macos-main, linux-main and recorded callbacks, with the correct positive MD label and returncode0. Eight required registrations disappear: atlas_tensor_square, atlas_python, atlas_time, atlas_capacity, atlas_recorded_fixture, atlas_expm_context, atlas_log1p_context and atlas_scalar_functions. The witness source CMake bytes are the actual reviewed unchanged CMake bytes; only generated registration/log transport is synthetic. Normal platform exclusions should affect selection, not the complete registration inventory.

Retained witnesses: probes-v2/witness-omitted-registration-{macos-main,linux-main,recorded}.json. All three receipts say passed. This violates preserving the canonical/portable test coverage; comparing a log with a truncated registry does not establish complete coverage. The original initial probes are also retained separately.

Smallest next correction: explicitly assert the complete source-derived native registration identity/order and relevant command/target correspondence before any CTest observation; derive the fixed platform selections from that validated inventory. Retain each required gate and reject missing/extra/duplicate/altered registrations before calls. Freeze mock cases with the full real native inventory, including omitted non-numerical tests, before observations. No CMake or numerical test gate change is warranted.

## B2 — CTest executable drift passes postflight (blocking)

The selected CTest executable is hashed once at dispatcher:179. The postflight context comparison at211 rechecks source/build/strict artifacts but omits that executable and its selected path. The independent full-ten-registration witness changes the non-executable mock-ctest file inside the explicit runner callback. Pre/post hashes differ; the receipt still says passed and contains only the old hash.

Retained full-inventory witness: probes-v2/witness-ctest-artifact-drift.json; before/after hashes in probes-v2/transport-probes.json. The earlier abbreviated-inventory witness remains separate. No executable was run or modified: the artifact is synthetic text.

Smallest correction: bind the selected CTest path and file hash into the observation context and recheck the same artifact after successful calls, preserving any mismatch receipt as a failure. Independently test both content and path/identity drift. This is transport integrity, not a numerical gate change.

## B3 — nonexact positive label qualifies (blocking)

check_md1997_native_fixture_contract.py:41 uses substring membership. With the complete ten-test registry and otherwise passing synthetic CTest log, its only positive profile line is:

```
WRONG-PREFIX Source-admissible MD1997 numerical fixtures; inherited explicit-gis20-occ-restart-duncan-v5; models=16
```

The entire dispatcher still reports passed. This is not the exact positive stdout line frozen in the accepted plan. The expected substring appears once, so both membership/count checks pass. The test's output identity cannot be established from a substring of a different line.

Retained witness: probes-v2/witness-nonexact-positive-label.json. Smallest correction: require exactly one complete matching line within the numerical test's actual output region, and retain the separate passing outcome/complete suite coverage checks. Reject prefix/suffix/metadata-only labels and duplicate labels; do not waive positive CTest success or the legacy expected-failure contract.

## C1 — nonUTF8 timeout loses terminal row diagnostics (nonblocking concern)

At dispatcher:121, timeout handling calls raw(), which strictly decodes before the exception handler sets row.status=failed/error_type=TimeoutExpired. A timeout with partial stdout byteff retains all raw bytes and fails overall, but UnicodeDecodeError supersedes the original timeout, leaving the process row status=started and no original error_type/details. This does not produce false acceptance; it loses the failure's terminal identity.

Retained witness: probes-v2/concern-timeout-nonutf8.json. Record the original exception/terminal row before any decoding that may fail, keep raw captures independent, and retain decoding failure as additional information. Retest timeout plus malformed UTF8 rather than only testing those cases separately.

## Verified source and mocked behavior

All38 source checks pass, including explicit assertions identifying the weak points. The exact591-file source inventory and every hash match the author freeze; all original582 bytes remain unchanged. The authorized three support overlays and published helper/policy match exact Git37d bytes. Only tests/test_ci_profiles.py changes among original582 paths; the nine added paths match scope. All public source copies match isolated bytes; no bytecode/cache/symlink appeared.

Workflow bytes exactly match the accepted proposal; restoring its bounded native block recovers the entire published37d workflow. All outside gates remain byte-identical, including scalar/orthotropic/Ramberg/Hill, portable/recorded, Wasm and deployment dependencies. Required strict contracts precede positive suites and evidence uploads use always(). Fixed macOS/Linux/recorded filters and selector sanitization are correct in the reviewed source.

All18 author unit methods independently reproduce with stand-in processes, covering all three catalogue routes/all nine suite combinations, strict8 row corruption, source/helper/policy/root binding, unknown/duplicate/reordered catalogues, default/unknown selector sanitation, nonzero/signaled outcomes, partial starts/timeouts/nonUTF8 raw retention, exclusive receipts, strict-artifact drift, delegated report corruption, positive omissions/failures and old contract tests. These are mocked operations, never numerical qualification. The independent additional probes expose B1/B2/B3 and C1 rather than merely repeating positive paths.

The exact14/15 matching unchanged helpers are delegated with both selectors removed and their four saved process rows rechecked. The exact16 map is asserted before removing only MD, asserting the exact15 projection and calling the unchanged source-derived OCC analytical proof. Strict eight expected-negative contracts remain distinct from required positive CTest returncode0 and label checking. Unknown catalogues abort before process dispatch. Main source/build/catalogue/header/strict-artifact hashes are checked before and after successful observations; B2 identifies the omitted CTest tool artifact. Separate actual build receipts remain necessary to establish how binaries were built; hashes alone do not prove compilation correspondence.

The CI source intentionally retains old582 tests/test_solver.cpp. It lacks accepted fixture-v3 MD changes and the published Ramberg block. This packet therefore cannot support a real positive CI run as-is, independently of these findings. Compose separately accepted fixture-v3 under a new source identity before actual calls. The16 qualification route currently locks exact published15 policy bytes; eventual E6 package16 integration needs a distinct exact reviewed policy context, without blind repinning or admission fabrication. Later published8cab changes are outside locally verified Git37d; fresh bounded drift reconciliation remains mandatory.

All author files, old fixtures, failed studies and prior review decisions remain immutable. Smallest next action: author correction in a NEW identity, retain this blocked packet and witnesses, then separate exact-byte review before any composed CI execution. No blocker is waived and no implementation edit is authorized by this review.
