# Whole-test development allocation contract

1 November 2026. **CAL-whole-test-allocation-v1** adds a shared [study-allocation schema](../../schemas/study-allocation-v0.1.schema.json), [semantic validator](../../atlas/study_allocation.py) and metadata-only checker. It is a prerequisite for controlled calibration, not a new optimizer or a completed scientific study freeze.

## Run without experiment responses

```sh
python3 -B tools/check_study_allocation.py studies/kfs-development-v1/allocation.json --policy studies/kfs-development-v1/reservation-policy.json
python3 -B -m unittest tests.test_study_allocation tests.test_strict_observation_json -v
```

The supported command reads exactly the allocation and reservation JSON files. It does not follow experiment paths, load measurements, run a model or release reserved tests. Optional `--output /path/to/new-report.json` writes a new report without overwriting an existing file. Invalid input exits nonzero and produces no success report.

The schema defines structural fields. Semantic checking additionally requires the exact reservation-policy byte hash and ID, unambiguous policy roles/IDs, nonempty unique whole-test lists, no calibration/evaluation overlap and only known development IDs. Different calibration packages may share a test; the union of all packages must remain disjoint from evaluation. Case/zero-padding aliases are not normalized into another ID. Row/sample selectors, unsupported final/blind claims, duplicate serialized keys and nonfinite JSON values are rejected. Policy version1 is the only supported reservation format.

This development-only contract cannot certify source/model applicability, preparation independence, prior exposure, a genuine prospective freeze or release permission. It has no reserved-test release operation. A future fitting driver must call the checker before its data loader; this increment does not retrofit the separate manuscript prototype or every atlas data command.

## Existing metadata used to exercise the contract

[Allocation](allocation.json) preserves the completed matched-count pilot's selections:

| Role | Whole-test IDs (KFS prefix) |
| --- | --- |
| pressure3 calibration | TMD2, TMD3, TMD4 |
| density3 calibration | TMD3, TMD8, TMD13 |
| Shared development evaluation | TMD1, TMD5, TMD7, TMD9, TMD12, TMD14 |

The exact [reservation policy](reservation-policy.json) was copied from the archived96-budget run, and its hash matches that run's report. [Receipt](source-receipt.json) identifies the local historical source; the command does not need the original private run. The policy registers37tests (TMD1–25 and TMU1–12); fourteen reserved IDs remain excluded. Unknown IDs also fail. The current manuscript policy may extend this historical registry; this snapshot does not replace or modify it.

This is a reconstruction after those fits occurred. Evaluation tests were excluded from fitting but previously inspected, and published material constants may encode additional test information. There is no blind, final or independently held-out evaluation claim. Whole-test grouping prevents splitting one recorded test across fit and evaluation; it does not prove independent specimens or preparation batches.

[Successful check](allocation-check.json) and [test log](tests.log) are retained. Nine new test groups exercise overlap, reserved/unknown selections, ambiguity, source-policy identity, row/blind claims, metadata-only file access and CLI failure status. Together with five strict-reader tests,14tests pass. The schema JSON parses and the example contains its exact required properties; no independent JSON Schema engine validation is claimed.

CAL-01/02 remain open for a scientifically justified prospective allocation and complete model/data/parameter/objective/optimizer freeze. No fit, response-data acquisition, numerical result, manuscript edit, build or scientific admission was added.
