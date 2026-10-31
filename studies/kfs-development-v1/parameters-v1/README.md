# Development parameter information accounting

1 November 2026. **CAL-parameter-accounting-v1** adds a shared [structural schema](../../../schemas/study-parameters-v0.1.schema.json), [semantic validator](../../../atlas/study_parameters.py) and allocation-first checker. The example reconstructs the completed development pilot; it does not freeze new fits or complete CAL-02.

## Run without fitting or responses

```sh
python3 -B tools/check_study_parameters.py studies/kfs-development-v1/parameters-v1/parameter-policy.json --allocation studies/kfs-development-v1/allocation.json --reservations studies/kfs-development-v1/reservation-policy.json --models studies/kfs-development-v1/parameters-v1/models
python3 -B -m unittest tests.test_study_parameters tests.test_study_allocation tests.test_strict_observation_json -v
```

The command first runs the existing whole-test allocation check. A reserved/invalid allocation stops before reading the parameter policy or model files. It then reads parameter metadata and exact model definitions, never experiment responses or a solver. Optional `--output /path/to/new-report.json` preserves existing outputs.

Every parameter must appear exactly once with an explicit fitted/fixed role, value (fit seed or fixed constant), unit, information category and provenance. Fitted parameters also require finite ordered bounds containing the seed, a supported transform and positive bounds for log search. Values and search intervals must fit the exact definition's declared ranges; unit conversion is never inferred. Literature provenance requires a persistent HTTP source link, and a claimed definition default must equal that default. Exact definition and allocation hashes prevent silent substitution.

These checks do not prove scientific provenance, parameter identifiability, coupled domain admissibility, model applicability or equal information between models. Callers still need complete initialization, objective, optimizer, budget, failure and evaluation policies. The core validation API expects digests computed from the corresponding decoded bytes; the supported checker computes them from the files itself.

## Retained historical example

[Policy](parameter-policy.json) uses the exact three [historical definitions](models/) recorded by the96-budget pilot. They retain their original schema/version bytes and are not migrated/new model records or current-engine equivalence claims. [Source receipt](source-receipt.json) pins the original local report and describes metadata extraction. New executable definitions continue to target schema v0.3.

| Historical formulation | Fitted parameters | Literature-fixed material inputs | Other fixed input |
| --- | --- | --- | --- |
| Elastic diagnostic | E, nu | None | p_ref numerical scale |
| Cohesionless Drucker–Prager | E, nu, M, Md | None | c=0 specialization; p_ref numerical scale |
| Base VW96 | phi, hs, alpha, beta | n, ed0, ec0, ei0 | p_ref numerical scale |

VW96's four fitted parameters also start from literature-derived values; the [generated check](parameter-check.json) preserves that seed information. Four fitted constants therefore do not mean four total material inputs or equal calibration information to another model. Existing values and source citations come from the completed pilot and [input review](../../../docs/benchmarks/kfs-development-checkpoint-v1/input-review.md), not a fresh primary-table review. Scientific classification/provenance decisions remain reviewable metadata.

Nine new test groups cover exact input coverage, units, range/seed/log errors, fixed-role misuse, source/default provenance, changed definition/allocation identities and allocation-first metadata-only access. With nine allocation and five strict-reader groups,23tests pass; [log](tests.log) is retained. Schema JSON parses and example root keys match its declared fields; no independent JSON Schema engine validation is claimed.

No fitting, model execution, measurement acquisition, source-model migration, manuscript edits, build or deployment occurred. The next CAL-02 work is the complete initialization/objective/optimizer/failure-budget contract and a scientifically justified prospective study freeze; these historical accounting records are not that freeze.
