# Scope-aware native laboratory contract

Completed 1 November 2026. This implements the laboratory response portion of the [total-stress design](../total-stress-profile-v1/README.md) using the [generated scope metadata](../stress-scope-metadata-v1/README.md). The public atlas remains at nine executable models; total incremental validation remains disabled.

## Opt-in API

The new C exports are:

- `atlas_run_scope_with_settings(id, parameters, initial, protocol, target, steps, cycles, settings)`
- `atlas_run_controls_scope_with_settings(id, parameters, initial, protocol, controls_bits_csv, settings)`

Native CLI `run` and `run-controls` select them with `--response-contract stress-scope-0.1`. Omitting the option retains the old contract. Unknown values and use in other modes reject. Both new APIs echo integration settings; explicit controls keep the existing numeric values, bit encoding and cumulative-control semantics.

The response retains schema_version 0.1 and adds api_version `experimental-laboratory-scope-0.1`, a closed stress descriptor and a pore-pressure availability descriptor. State stress is Cauchy sigma in compression-positive Mandel components. Scope is effective or total, as declared by generated metadata. An otherwise valid failed run retains the same committed prefix with its scope descriptor; errors before run construction retain the existing plain failure envelope.

| Scope/protocol | Pore descriptor | Every point's u |
| --- | --- | --- |
| Effective, 2 or 3 | quantity change, availability reconstructed; assumption fixed_radial_total_stress_incompressible_fluid_and_grains | Existing reconstruction, including initial zero |
| Effective, 0/1/4 | quantity change, availability unavailable; reason not_reconstructed_for_protocol | null |
| Total, all five | quantity change, availability unavailable; reason total_stress_without_pore_pressure_law | null |

Unavailable values are never serialized as numeric zero. The core only calculates the radial-stress pore reconstruction for effective scope. Its effective arithmetic is unchanged. Total protocols are mechanical controls: one-dimensional strain, fixed radial total stress, zero volume change, prescribed signed q change with zero volume change, and isotropic strain. No pore law, drainage classification or experimental equivalence is inferred.

All three legacy laboratory C exports require effective scope before parameters/state are parsed or material evaluation begins. Both contracts require a first persistent incremental sigma6 field; physical-time/unspecified/no-stress cases reject. Scalar evaluate/integrate and timed APIs retain their existing contracts. Recorded/browser scope integration is a later task.

## Prospective native gate

[freeze.json](freeze.json) fixes contracts, cases and tolerances before observation. One explicit CMake target was built with `--parallel 1`; it contains the new CLI, archived pre-change CLI and a direct C API driver. All use an identical private ten-record catalogue: the nine unchanged public definitions plus one synthetic total-elastic transport fixture. Source/generated pins and raw configure/build/process receipts are retained.

The synthetic fixture is not an atlas addition or production admission. Its schema is checked and its effective mechanical twin passes the unchanged full validator; the private test preparer then lowers the explicitly total record through a narrowly scoped loader adapter. This is necessary to test the new interface while the production total profile remains disabled. It supplies no Tresca or scientific validation. Existing public records are copied byte-for-byte and both binaries bind the same catalogue hash.

The gate passes 48 process calls:

- Nine public-model zero-increment cases compare old/new legacy responses exactly.
- Five nonzero elastic protocols and one ordered/reversing explicit-control path compare old/new legacy responses exactly. Saved replay additionally verifies raw serialized bytes after replacing only elapsed_ms. New effective scope results retain exactly the same mechanics/settings/diagnostics, with the declared pore policy.
- Five synthetic total-elastic protocols satisfy independent closed-form stress/strain checks. Maximum stress error is 2.6193447411060333e-10 Pa against the frozen 0.002 Pa gate; maximum strain error is 5.45700976268583e-18 against 2e-10.
- Legacy total requests reject; direct calls to all three legacy C exports return the scope error despite malformed parameters/state. Both new C exports succeed on the total fixture. Unknown/misplaced contract options and nonfinite control bits reject.

[Saved summary](observations/summary.json) lists every raw receipt and binary SHA. No binaries or private measurements are distributed. [Prior sources](previous-sources.json) retain exact old main/solver bytes. No gate was relaxed and no model equation, numerical setting or controller algorithm changed.

## Recheck without native execution

```sh
python3 -B docs/reviews/laboratory-scope-contract-v1/assess.py
python3 -B -m unittest tests.test_laboratory_scope_contract tests.test_stress_scope tests.test_formulation -v
```

Saved replay passes with subprocess execution denied. Fifteen focused tests pass, including six corruption cases: wrong scope, numeric zero replacing unavailable u, changed control bits, changed mechanics, nonzero process exit, and a missing receipt. These tests never build or invoke a material process.

For a new explicit native run, use a fresh private destination and respect serial build policy:

```sh
python3 -B docs/reviews/laboratory-scope-contract-v1/prepare.py /private/tmp/atlas-lab-scope-reproduction
```

Before compiling, write assessment-freeze.json in that directory with `exercise_sha256` and `policy_sha256` identifying the exact exercise.py and freeze.json bytes. Then configure CMake and build only `atlas_laboratory_scope_gate --parallel 1`; run exercise.py with the stage directory and a new observations directory. The original pre-build and assessment freezes remain unchanged.

## Stop and next dependency

This slice establishes the native laboratory interface and effective legacy compatibility. It does not activate total models, add Tresca, build Wasm, update browser rendering/import/export, push, deploy or provide scientific admission. Next implement the separately versioned recorded request/response contract and effective-only recorded legacy guards. Browser scope semantics and the source/reference/backend gates still precede public Tresca installation.
