# Controlled physical-time Stage A implementation

IMPL-vibe2026-controlled-time-stage-a-v1. Owned implementation worktree:
`/private/tmp/atlas-vibe2026-controlled-time-v1`, branch
`codex/vibe2026-controlled-time-v1`, base
`31125e2e809dad1af8dd30805af7b8c2937197d4`.

This packet records generic profile implementation and **pure Python/code-generation checks only**. No native/Wasm build, compiled material call, author/vendor code or browser execution was performed. MDv6 owns the serial build slot. Parent owns the separate VIBE candidate and source packet; those files are not this worker's deliverable. No staging, commit or push occurred.

The separate `physical_time` / `controlled_ode` profile preserves symmetric Mandel mechanical controls and scalar external fields with explicit value/rate dimensions. It provides complete initialization/restart context, physical stage times, positive-duration holds, explicit rate-jump observations and all-or-nothing rollback. Net stress is permitted in the new profile without converting total/effective stress. Existing profiles and native ABI signatures are unchanged. Actual native/Wasm qualification and scientific/browser admission remain pending.

## Frozen design and retained failures

The coordinator retains the accepted design at the main checkout's
`docs/ingestion/vibe-2026/capability-v2/`, including the immutable v3 clock/alias supplement. This worktree's base predates those root documentation files, so they were read by absolute path. Alias policy rejects input/output and output/output overlaps while permitting read-only input/input overlap.

`baseline/` contains exact common generated files and a SHA-256 manifest captured **before implementation edits**. The pure generator regression compares every baseline output byte. Generated synthetic controlled-time source and metadata are retained in `generated/`; generating them does not compile or execute C++.

- Initial fixture-creation helper failed to import `atlas` when launched from `/private/tmp` without `PYTHONPATH`; rerun with the repository on the import path. A fixture initially used reserved state name `z`; semantic validation rejected it and its actual state is named `clock_memory`. Neither attempt generated compiled output or changed the frozen analytical equation.
- `pure-attempt1.log`: first eleven-group run retained nine passes, one missed old-interpreter guard and the frozen C3 exponential global-bound failure. The missing guard was fixed; it now rejects with the dedicated API diagnostic.
- The original local `rtol=1e-8` exponential endpoint error was `3.446802001594307e-7`, exceeding the unchanged bound `6.413411329464508e-8`. Local error control did not guarantee that global bound. **No acceptance bound, oracle, default setting or original gate file was relaxed.** `stricter-execution-v2.json` was recorded before the second pure run, tightening this study's relative execution tolerance to `1e-10`. Parent and reviewer were told the run started before their additional request for review-before-rerun arrived; no compiled observation occurred. The revised execution study is included in the separately reviewed source snapshot; compiled observations remain pending.
- `pure-attempt2.log`: all eleven groups pass under that stricter full-state analytical study; the original failed run remains intact. Other tests continue to exercise the original default and explicit refinement settings.
- `branch-attempt1.log`: directional suction-rate and zero-rate branches pass; a domain failure after an earlier internal half-step leaves the full parent unchanged, with successful recovery.
- `pure-regression-attempt1.log`: 45/46 targeted tests passed; the historical migration test discovers the parent's newly added controlled-time research candidate and incorrectly feeds it to the ordinary generator. The generator's dedicated-profile rejection is correct. Coordinator granted a narrow test dispatch update: exact before bytes are in `preimages/test_formulation.py`, and the new branch asserts ordinary rejection plus dedicated-generation byte identity. `pure-regression-attempt2.log` records all46 selected pure tests passing, preserving the original failure.

## Reproduction and pending execution

Pure checks (no compiled programs):

```sh
python3 -B -m unittest tests.test_controlled_time -v
python3 -B tools/generate_controlled_time.py --output OUTPUT tests/fixtures/controlled-time/transport.json
node --check tools/test_controlled_time_wasm.mjs
```

Targeted regressions use explicit pure classes in time/state/schedule tests; do not run compiled classes incidentally. The native test module is deliberately opt-in through `ATLAS_CONTROLLED_TIME_MODULE` and `ATLAS_CONTROLLED_TIME_CATALOGUE`. `NativeEngine` executes no binary at import; instantiation is a future explicit coordinator handoff. The Wasm tool likewise executes only when explicitly invoked with exact module/catalogue/output paths.

The written native/Wasm gates include the independent six-component THM polynomial, explicit nonautonomous clock, nonlinear history, hold, component ordering, partitions/restart, shape and alias rejection, output sentinels and recovery. Source review must inspect these adapters before any coordinator builds. Subsequent raw native/Wasm reports must retain exact input/model/source/module hashes, all failures and unchanged reference limits. Python/backend agreement does not replace the analytical oracle.

## Resources

No server or background preview was created. Test temporary directories are managed by `TemporaryDirectory` and removed after each check. The two small task-owned helper scripts in `/private/tmp` were removed at handoff after their resulting implementation and fixture were retained here; their initial import/reserved-name failures are recorded above. Durable baseline/generated source, logs, references and failures remain in this packet. The implementation worktree is coordinator-owned and retained for review/build; this worker will not remove it or the parent's candidate files.

## Final source qualification handoff

`pure-regression-attempt4.log` records **48/48 pure tests passing**. The additional coverage includes exact maximum and one-above checks for 256 parameters, 32 state components, 32 controls, 65 bound equation-input components and 24/144 observables, old-profile direct stress-binding isolation, and a fake-CDLL stale same-shape identity rejection without loading a binary. `node --check` and Python AST parsing validate qualification sources without executing compiled code.

`make_reference_corpus.py` is a standalone standard-library Decimal closed-form reference generator. `reference-corpus-v1.json` freezes 18 complete analytical cases, including all six mechanical directions, scalar fields, opposing THM, nonzero-start-time clock, holds, branches, partitions and highest-capacity coupling. Exact fixture bytes and per-case execution settings are included. Native and Wasm source gates consume the same corpus; their actual execution gates remain **open**.

Before any compiled qualification, freeze and supply `source-manifest-v1.json`. Native qualification requires `ATLAS_CONTROLLED_TIME_SOURCE_MANIFEST`, `ATLAS_CONTROLLED_TIME_RAW_OUTPUT`, `ATLAS_CONTROLLED_TIME_MODULE` and `ATLAS_CONTROLLED_TIME_CATALOGUE`; it hashes all inputs before loading the library and writes separate per-test raw receipts, including after failed tests. Use a new output identity for each attempt. Wasm invocation requires `MODULE CATALOGUE OUTPUT SOURCE_MANIFEST`; it refuses an existing output, writes its receipt before module loading, checkpoints every raw call, and retains exception details on failure. Receipts bind exact compiled library or mjs+wasm bytes, exact catalogue bytes, frozen reference corpus and final source manifest, and contain settings, observables, diagnostics and unchanged-output evidence. All three embedded identity exports bind the compiled law and catalogue; the Wasm metadata-tamper case rejects edited external descriptors before material calls.

No compiled/native/Wasm result, capacity execution pass, browser pass or scientific model approval is claimed by this handoff. Parent-owned Stage B files and the VIBE candidate are outside this Stage A manifest. Four small temporary helper scripts were removed after preserving their outputs; no preview process or additional worktree was created. Coordinator-owned worktree and shared Python caches remain in use and are retained.


### Source addendum v2: prospective C4 coverage

The immutable `source-manifest-v1.json` preceded the reviewer's final coverage
finding. Its changed exact bytes are retained under `preimages/source-freeze-v1/`.
This source addendum adds a fourth synthetic fixture with domain
`time < 14*tau/2`, starting at 11 seconds. A four-second hold uses explicit loose execution settings (absolute 1e-6,
relative 1e-2, max step 1 second, depth 8) so earlier one-second internal
steps are accepted before reaching the forbidden domain; native and Wasm tests require full
rollback, unchanged output sentinels and a successful two-second recovery. The
Wasm runner additionally freezes trial and maximum-depth exhaustion, zero and
negative duration, nonfinite time, nonpositive temperature and negative suction,
with unchanged-buffer checks and a valid recovery after every rejection. These
are prospective tests, with no compiled observations and no runtime or acceptance
policy changes. The subsequent v3 supplement also checks Wasm highest observable output22 at offsets 138..143 against sigma + E*history22*I. Final independent source review must bind source-manifest-v3.json;
v1 remains retained as the original snapshot.
