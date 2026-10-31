# Frozen instantaneous-rate evidence transport

`tools/research_rate_observations.py` provides a generic native collector and
portable assessment for a predeclared literal-CSV rate corpus. It contains no
constitutive equations or model-ID dispatch. It does not admit a model or
establish finite integration, tangents or experimental validation.

## Current scope

Native collection and native/Wasm journal assessment are implemented. The
matching generic Wasm collector is still pending; a Wasm journal cannot be
accepted without the actual pinned collector source. Synthetic tests use
fabricated journals to verify assessment contracts, not compiled observations.
No model-specific compiled study has been run through this tool yet.

## Prospective protocol

A protocol has version `research-instantaneous-rate-protocol-0.1`, a
repository-relative `files` SHA-256 map including `model_file`, the exact parsed
`model_definition`, and ordered `cases`. Every case provides a unique `id`, four
literal `args` strings (model ID, parameter CSV, full-state CSV, six-component
increment CSV), and an `expectation` with a Boolean `ok`. Normal controls must
contain finite numeric CSV. A valid expectation supplies full `values`,
`absolute_budgets` and `parity_budgets`; all budgets are nonnegative and frozen
before collection. `parser_error: true` denotes a distinct malformed-input
contract; it cannot silently stand in for a finite domain rejection.

An optional `recovery_of` names a prior control and must reproduce its exact
arguments and response in the same persistent transport. Source studies must
separately justify their independent oracle and numerical policies. This tool
checks their transport and stated budgets; it cannot make those policies valid.

## Build and collection

Use the [isolated build target](ISOLATED_RESEARCH_BUILDS.md), one target and one
job. A pre-execution JSON build receipt records `backend`, `protocol_sha256`,
`all_commands_succeeded: true` and `artifacts` with path/SHA-256 pairs (native
role `native`; Wasm roles `loader` and `wasm`). The study also retains exact
commands, toolchain, logs, generated files and complete source dependencies;
a Boolean build field alone is not evidence of those facts.

Run from the repository root:

```sh
python3 -B -m tools.research_rate_observations \
  --protocol /absolute/path/protocol.json \
  --build-receipt /absolute/path/build.json \
  --collect-native --output /absolute/path/fresh-observation.json
```

Collection snapshots the frozen input and artifact bytes, runs one native
`--stream` process, retains raw stdout/stderr/status before numerical assessment,
and rejects changed inputs afterward. Fresh output paths are mandatory. A
retained transport receipt is not a passing scientific result.

## Assessment and failures

```sh
python3 -B -m tools.research_rate_observations \
  --protocol /absolute/path/protocol.json \
  --build-receipt /absolute/path/build.json \
  --observation /absolute/path/observation.json \
  --transport /absolute/path/observation.transport.json \
  --output /absolute/path/fresh-assessment.json
```

Assessment hashes and parses the same held bytes, verifies descriptor identity,
literal controls, full output/echo shapes, rejections and recovery. It writes
numerical failures and exits nonzero. An error exceeding finite binary64 range
is represented by `error: null` with `error_overflow: true`; it always fails a
finite budget. No NaN/Infinity is written to JSON. An unbounded parity-budget
fraction is similarly explicit. `parity()` compares complete, previously audited
assessment objects; it does not authenticate arbitrary caller-created objects.
Retain both raw inputs and assessments as provenance.

Run `python3 -B -m unittest tests.test_research_rate_observations -v` for synthetic
corruption/recovery/overflow tests. These never execute a compiled artifact.
