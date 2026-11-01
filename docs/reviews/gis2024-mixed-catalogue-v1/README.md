# GIS2024 eleven-model compatibility

NUM-gis2024-mixed-catalogue-v1, 1 November 2026. Native and Wasm pass the
prospectively frozen compatibility checks for the existing ten exact model
definitions plus the separately qualified v0.3 GIS2024 research artifact.
This completes mixed-catalogue compatibility only. The public catalogue remains
ten models; browser installation, scientific review and deployment are separate.

The selected formulation is HP with extracted ASBS + GIS2024, f=0, from
[Mugele, Stutz & Mašín (2024)](https://doi.org/10.1016/j.compgeo.2024.106480).
Its [source/formulation crosswalk](../../ingestion/hypoplastic-generalized-igs-2024/README.md)
and [isolated qualification](../gis2024-v03-backends-v1/README.md) retain source,
initialization, strict-domain and scientific-review limitations.

## Bounded comparison

Each backend passes:

- Existing nine: unchanged 126 requests, 11,278 numeric fields, 27 expected
  failures and nine complete-state rollbacks. All five laboratory protocols,
  residual/rate evaluation, signed history/reversal, malformed inputs and recovery
  are represented. The baseline is the retained passing **ten-model native**
  response set; it is software regression evidence, not constitutive truth.
- Existing Tresca: unchanged 29 laboratory cases with 29 recoveries, 1,746
  independent state/strain comparisons and 97 admissible points; all 12 own-state
  history updates pass the original independent reference (288 comparisons).
- Added GIS2024: all 20 trajectories, 204 base updates, 272 same/fresh-context
  restart updates, nine probes and nine persistent recoveries. All 14 history
  components are transported; the original accuracy, volume, temporal/partition
  refinement, domain, zero, rollback-after-accepted-work and exact-restart gates
  remain unchanged. Each backend retains 516 raw descriptor/call receipts.

Native/Wasm parity covers 493 returned state pairs and their incoming histories.
The maximum scaled difference is 1.2473070195743015e-16 under the original 1e-7
bound. Scaling uses p_scale for stress, R for memory and 1 for scalar state.
See [summary](assessment.json) and separate full backend assessments.

## Identity and timing

The current ten model objects equal the previous qualified ten-model catalogue;
`existing-models.json` also pins their exact current raw bytes. `gis-model.json`
is byte-identical to the previously frozen v0.3 research candidate. All staged
production/fixture sources and generated headers/catalogues are checked.
No production source, model, schema or numerical policy was changed.

Forty-four synthetic assessor/transport corruption checks passed before freezing
and before either build. They test audit machinery, not scientific correctness.
An initial assessor syntax failure is retained in `preflight-initial-failure.txt`;
the syntax and canonical generation order were corrected before the freeze.
`prospective-freeze.json` pins policies, inputs, generated output and assessment
code; `dependencies.json` pins reused drivers, reference code and historical
packets. The independent GIS numerical audit differs from its isolated version
only by allowing an explicitly supplied catalogue and checking exact candidate
membership. It inspects **real eleven-model descriptors and catalogue hashes**;
no raw response is projected into a fictional singleton catalogue.

`collect_existing.py` invokes the original ten-model collection procedure with
new staging/output locations. `run_gis.py` uses the original own-state driver and
literal frozen request matrix. The native test entrypoint reuses the prior
persistent C ABI transport, adding only dispatch to the original CLI when command
arguments are present. It contains no model or solver mathematics. Wasm uses the
normal production C ABI and original transports.

Native was built, run and accepted before Wasm configuration/build/execution.
Both builds used one explicit atlas_solver target and --parallel 1; both passed
on their first attempt. Build/configure/run/assessment receipts and private
artifact hashes/compile/link flags are retained. New source stages and binaries
remain under `/private/tmp/atlas-gis2024-mixed-catalogue-v1/`. No running build or
integration process is required for evidence replay.

## Reproduction and handoff

```sh
python3 -B docs/reviews/gis2024-mixed-catalogue-v1/verify.py
python3 -B docs/reviews/gis2024-mixed-catalogue-v1/test_preflight.py -q
```

The verifier checks exact source/dependency/packet identities, safely extracts
both GIS raw-receipt archives, reruns saved-output regression and independent
reference assessors, compares parity and repeats the saved-reference audit.
It never builds, executes a model binary or reruns a constitutive ODE. Existing
model response files retain their original collection format; all 1,032 GIS raw
receipts are archived. Preserve this packet; fresh reruns need new exclusive
paths and identities rather than overwritten evidence.

Next is a bounded browser/preparation integration plan: explicit 14-component
initialization/import/export, source/review disclosure and guards for the selected
small-strain, effective-stress, zero-spin, rate-independent host. Keep software
fixtures labelled as examples, strict memory-boundary rejection visible, and
source-prepared specimen claims out of defaults. Wider model coverage, boundary
projection, parameter fits, scientific admission and deployment are outside this
completed compatibility task.
