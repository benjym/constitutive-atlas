# Tagged instantaneous-rate evidence contract 0.3

Freeze the complete protocol, source/build closure and policy before compiled observation. Collection retains opaque responses and termination/exception evidence before assessment. A complete transport is not a passing numerical assessment.

## Scope and literal inputs

A protocol has version `research-instantaneous-rate-protocol-0.3`, pinned repository-relative files, one exact `model_file` and full `model_definition`, and ordered uniquely named `cases`. Supported models are instantaneous strain-path-rate definitions; physical-time and residual profiles require different transports. Parameter insertion order, ordered state layout, descriptor and canonical model hash must all match. No physical preparation is inferred.

Each case carries four literal strings in `args`: model ID, parameter CSV, state CSV and six-component Mandel increment CSV. No embedded tabs/newlines are allowed. Non-parser cases require exact declared arities and finite binary64 decimal conversion. Tokens use ASCII sign/digits/decimal point/exponent with at least one mantissa digit and at least one exponent digit when present; surrounding whitespace, underscores, hex, Unicode digits and NaN/Infinity are excluded. Finite subnormals are accepted; decimals rounding to zero are finite inputs. Numeric comparison is decoded binary64 equality, not bitwise/sign-of-zero identity. Backend echoes are checked against actual converted literals.

## Closed expectations

- `accuracy`: exactly `kind`, `ok:true`, `values`, `absolute_budgets`, `parity_budgets`. All vectors have full state-rate width, finite real non-Boolean entries and nonnegative budgets. Source differences use the frozen absolute budgets; backend parity uses separately frozen absolute parity budgets.
- `finite_only`: exactly `kind`, `ok:true`. It forbids source values and source budgets. Require a full finite real non-Boolean output vector. The protocol must explicitly declare `finite_only_parity:{"norm":"scaled_component_max","budget":...}` with a finite nonnegative real budget. Compare each backend component by abs(a-b)/max(1,abs(a),abs(b)); use normalized subtraction when raw subtraction overflows. Passing support/parity establishes no source accuracy.
- `reject`: exactly `kind`, `ok:false`, optionally `parser_error:true`. A material rejection requires full finite echoed controls, `values:null`, and exact message `unsupported research rate request`. A parser rejection carries only `ok:false` and `message:"invalid research CSV"`. Type/arity/parser failures do not count as demonstrated material-domain rejection.

## Recovery and raw records

A recovery has `recovery_of` naming a prior accepted control and `after_rejection` naming the immediately preceding rejected case. Literal args and complete expectation must equal the accepted control; complete decoded output must reproduce its earlier response within the same native stream process or persistent Wasm module. This is call-contamination recovery, not finite-update rollback.

A successful native raw companion has exactly argv/stdin/stdout/stderr/returncode, exact artifact plus --stream command, exact input stream and integer returncode0. A successful Wasm journal row has exactly name/types/args/raw and exact ordered CABI controls. Completed observations cannot carry error/exception markers. Failed/trapped/incomplete records are retained but cannot be assessed as successful complete transports.

Audits reread held protocol/source/build/artifact/raw bytes, enforce strict duplicate-free JSON and source/descriptor parameter layout, and reject changed inputs. The comparison wrapper re-audits both complete raw bundles; equally wrong backends still fail source budgets. Hashes bind evidence identity/integrity; fabricated receipts cannot prove real execution. Real frozen build and collection evidence is required separately.

Historical versions remain unchanged. This document and tooling precede the next compiled material study; no compiled results were used to choose or revise its numerical gates.
