# Independent current-profile execution plan v2 review

Decision: **BLOCKED for execution**, with accepted exact source/path/numerical rebind. No builds, backend calls, collectors or assessment mains ran. Two prospective receipt/environment findings need a distinct corrected identity; the original v2 packet remains unchanged.

Reviewed manifest `eebf5d8be93aa8d385fdf74d793d6dde22d6f571e21889f7a924fa2429455669` against v1 and accepted v1 review `9790e300caf9aaec84949f1dcf86b66df50b78b0738944e4fb765e393c668505`.

## B1 — inherited Python optimization disables mandatory gates

`toolchain.json::ambient_exact` omits PYTHONOPTIMIZE; none of the frozen command environments sets it. `stage_receipt.py` uses assertions for source, toolchain, environment, packet, cwd and pre-receipt validation without a nonassert `__debug__` guard. The unchanged scientific assessments also contain mandatory assertions.

`source-checks.json::B1_witness` executes only the exact unmodified verify function AST with Python's optimize=1 source option. It accepts PATH=/unreviewed/no-tools, EMCC_CORES=999 and EM_CACHE=/unreviewed/shared-cache and returns the source/tool identity. No planned command or process ran in this witness. This reproduces the validation semantics of a stage Python process launched with inherited PYTHONOPTIMIZE=1; the plan currently does not exclude it.

Required correction: explicitly freeze PYTHONOPTIMIZE='0' in every stage and post-review stage environment and tool environment policy. Both verify() and script entry must use an ordinary conditional raising an error when __debug__ is false before assertion gates. Retain original assessments unchanged and run them unoptimized. A read-only exact Python startup query retained in python-unoptimized-startup.json confirms PYTHONOPTIMIZE=0 gives __debug__=true and sys.flags.optimize=0. No scientific result is inferred.

## B2 — post accepts malformed or unrelated pre receipts

The only pre-receipt validation is `q['passed'] and q['command'] == st`. `receipt-precondition-witness.json` evaluates that exact AST condition with synthetic data. It accepts a pre object missing every identity field; it also accepts passed='false' (a nonempty string), or a pre object with wrong identity, phase, profile, stage, packet, source and toolchain identities. Hashing that object after acceptance does not establish the claimed successful matching pre observation.

Required correction: before linking the pre hash, require a strict pre schema, literal boolean true, identity/phase/profile/stage/command and all packet/plan/source/toolchain identities matching the current frozen context; retain/reject malformed or incompatible receipts with explicit failure evidence. Preserve raw log/exit-status semantics: a passing identity receipt is not numerical acceptance and may honestly record a failed stage. This finding concerns receipt provenance, not a numerical tolerance or model change.

## Accepted scope

9,927 independent checks pass: exact manifest inventory, all 14 copied adapters/assessment files reverse exactly, full JSON plan restores exact v1 after declared metadata/environment changes, all 65 numerical commands unchanged, all 2,722 source bytes and complete source inventory, resolved original 94 missing documentary/host paths, pinned collector closure, all 6,821 tool files/resolved targets and command resolution, input pins, explicit PATH/EMCC_CORES/private cache and serial one-target build shape. No source/model/reference/gate changed.

The bounded source closure and Maxwell149/NorSand121 sets remain those independently accepted in v1 review; all original source bytes survive, all added inputs are documentary/host bytes. The new tool freeze candidly excludes a hermetic complete OS/SDK/runtime archive. Actual configure/compiler/linker/SDK metadata, version/path/flag correspondence and generated dependencies must still be verified against the freeze before the first build. A mismatch requires a new identity, not silent substitution. Mutable private cache inventories and single ownership remain mandatory.

Maxwell and NorSand real fresh evidence and distinct independent build reviews remain prerequisites before guarded final bundle/CI calls. Unreviewed Maxwell metadata is not an approval. Lade/Hill preserve their exact historical reviewed assets and source identities. Existing raw-format limitations are unchanged and honest; no strict wire linkage is invented. Two global canonical archive gaps, latest upstream reconciliation, package/browser/live qualification and scientific admission remain outside this prospective study.

## Reproduce

`PYTHONDONTWRITEBYTECODE=1 python3 -B docs/investigations/control-partition-derivative-v1/current-profile-execution-review-v2/check_source.py` prints independent checks and exact optimizer witness without modifying author packets. The precondition witness is a pure AST expression evaluation, not receipt-collector or assessment execution. No compiler/toolchain build command ran; the only child interpreter query was read-only startup with PYTHONOPTIMIZE=0.

Smallest next action: separately freeze and review an environment/receipt-only correction addressing B1/B2, retaining exact numerical and path reversal proofs, then coordinator-reserved serial execution with actual configure/build receipts and independent evidence review.
