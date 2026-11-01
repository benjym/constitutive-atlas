# Independent native CI v2 and fixture composition v1 review

Decision: **BLOCKED**, source/mock only. Original B1/B2/B3/C1 corrections are accepted as resolving their exact witnesses; new R2 blocks dispatcher acceptance and R1 blocks composition execution readiness. No actual CI, CTest, compiler, material or backend call occurred.

Reviewed author manifest `24c1de6f57ec7694d326bf590aa959e2951cfcc0a82114058655eb97c9bcd865` and parent composition manifest `b18cfd1f256babe54161e56bb4c230b369b5f2fbbbbf933f32e15e8c8dbbd049`. Prior author/reviewer packets remain immutable.

## R2 — generated execution properties are not closed

`tools/check_native_fixture_dispatch.py::validate_registrations` validates all ten names/order/argv and rejects selected outcome properties, but accepts arbitrary `set_tests_properties` execution properties. An exact full-ten synthetic registry plus this appended line passes the Linux positive dispatcher:

```
set_tests_properties("atlas_time" PROPERTIES ENVIRONMENT "LD_PRELOAD=/unreviewed/inject.so")
```

The actual dispatcher executed with a supplied synthetic callback returns `status=passed`; receipt is `probes-final/R2-unreviewed-properties.json`. All artifacts are non-executable mock text; no injection/library/CTest process ran. This demonstrates acceptance of an unreviewed effective execution environment despite exact argv and immutable source. Similar unchecked WORKING_DIRECTORY/Python environment properties can change execution context. A pre/post hash of this already modified registry does not establish source-derived semantics.

Smallest correction: a new frozen identity must fail closed on generated properties/commands, allowing only exact canonical source-derived atlas_python WORKING_DIRECTORY/environment and ordinary proven backtrace metadata. Reject arbitrary environment/working-directory/custom CMake statements and semantic property changes before calls; preserve all original tests, filters and outcomes. Extend independent adversaries to metadata and property syntax, not just add_test argv. No author edits are made by this review.

## R1 — selected scalar test has two missing transitive scripts

Composition includes `tools/test_scalar_functions.py`, whose unconditional subprocesses invoke `tools/collect_scalar_functions.py` and `tools/check_scalar_functions.py`. Both are absent from the exact 592-file composition. `atlas_scalar_functions` belongs to the selected eight-test Linux suite, so excluding atlas_python does not avoid this gap. A scalar shared-library build cannot supply these scripts.

Exact available Git37d hashes are retained in `source-checks.json`. Both future scripts use standard-library imports; their literal `tests/fixtures/scalar-functions/requests.json` and `references.json` already exist. A separate exact-byte composition revision can add the two scripts without gate changes; independently review its complete inventory before calls.

## Accepted corrections and composition facts

All 23 author mock unittest methods reproduced. Twelve independent final checks confirm original abbreviated registries reject before any process on all three suites; selected CTest executable drift rejects; prefixed/suffixed/unterminated/duplicate/metadata-only positive labels reject; nonUTF8 timeout retains TimeoutExpired at process and overall levels, raw bytes and separate decoding diagnostics. The positive label is checked inside the actual numerical output region.

Independent byte checks verify all 591 prior files remain immutable; v2 changes only the three authorized helper/mock-test paths and adds the exact published37d scalar script. All 592 v2 files and all 592 composition files match their complete inventories. Composition changes exactly tests/test_solver.cpp to accepted fixture-v3 SHA `1b4555f246d6b572b8f653e5ca771c37177ee48883e2466fda96dc7665d85623`; all other bytes remain exact. Runtime/model/CMake/policy/workflow gates are unchanged. Actual composition source passes exact16/ten-registration context classification using synthetic generated/build artifacts only; this does not establish real build provenance.

The thirteen-stage composition plan contains nine explicit single-target serial builds, eight strict negative checks, Linux eight-test positive suite and separate recorded test. Selected C++ sources and recursive quoted headers are present; model/history generated headers remain future compiler outputs with present fixture JSON and recursively inspected atlas compiler/history modules. No further missing static selected-suite input was found in this bounded audit beyond the two scalar scripts. This does not prove generated outputs, external/toolchain availability, dynamic environment or arbitrary dependency discovery. Full Python/macOS workflow closure remains explicitly unqualified.

Exact14/15 unchanged delegation and OCC projection proof remain inherited and unchanged; full16 validation precedes published15 projection. Strict negative return/stdout/stderr contracts, selector sanitization, unknown catalogues, raw retention and post-context checks remain required. Historical failures, package16 admission, global qualification and live delivery remain separate.

## Reproduce and limits

Run `PYTHONDONTWRITEBYTECODE=1 python3 -B .../check_source.py` for read-only source/Git inspection. Run `.../probe.py --output <new empty directory>` for explicit process mocks only. It creates synthetic text artifacts and invokes no real CTest/backend. `probes/` preserves the initial successful independent replay; `probes-final/` includes the actual composed-source context check. Three reviewer-parser setup failures are retained separately; none is an author failure.

Smallest next actions: author a distinct R2 correction, compose the exact two R1 support scripts in a distinct source identity, independently review both and freeze actual toolchain/pre-post build receipts before coordinator serial execution.
