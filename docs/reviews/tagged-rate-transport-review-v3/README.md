# Independent tagged rate transport v3 review

Task: REV-tagged-rate-transport-v3. Scope: source inspection and fabricated protocol/raw-evidence adversarial checks only. No native/Wasm binaries, loader, material oracle, build, or model references are executed by this packet. Fabricated values are test fixtures, never scientific reference data. The coordinator owns fixes and integration.

## Contract reviewed

The v0.3 tagged protocol separates `accuracy`, `finite_only`, and `reject`. Accuracy retains source values and existing absolute/parity budgets. Finite-only forbids source values/budgets, requires explicit scaled component parity policy, and makes no source-accuracy claim. The clay2005 planned policy is 1e-10; this generic transport may consume another explicitly frozen nonnegative budget. Material rejection requires full finite echoes and `unsupported research rate request`; parser rejection has only status/message and `invalid research CSV`.

The independent fixture uses the actual candidate model parameter/state/increment arities 9/7/6. Its 7-component fabricated accuracy vector is 1 with synthetic .01 budgets, solely to test the transport gates. Native/Wasm artifacts are nonexecuted paths and synthetic hashes. The complete wrapper re-audits both raw bundles and verifies held source/build/protocol/transport identities; assessment JSON is not accepted as independent evidence.

The original clay2005 corpus and model remain unchanged. Its 41 accuracy rows, 10 finite-only rows, 29 rejection/recovery pairs yield 109 calls plus descriptor. Its existing reference budgets remain independent of the synthetic values used here.

## Findings and retained history

1. Initial v3 `checked_protocol` accepted underscore and whitespace numeric CSV via Python `float`, while the original C++ `std::stod` plus full-consumption parser would not accept these tokens consistently. The coordinator added strict ASCII decimal grammar. Source-only observations-v3 records both corrected rejections.
2. A recovery row could drop `after_rejection` and follow an unrelated successful call while retaining `recovery_of`; exact baseline arguments/expectation still passed. Require the immediate rejected-call relation for recovery rows. This is distinct from checking exact full decoded response recovery, which already rejects a changed response even inside the accuracy budget.
3. Authenticated raw bundles could retain genuine output plus contradictory exception/error markers and pass: Wasm journal `exception`, native raw `exception`, and completed native/Wasm observation `error`. Hash rebinding does not resolve contradictory transport status. Close successful raw shapes or explicitly reject these markers.
4. The clay2005 corpus contains positive/negative minimum-subnormal literals. Original `std::stod` can throw on ERANGE underflow, confusing parser and material rejection. This is a source-level portability concern, not an observed platform failure. A distinctly named `tests/research_rate_driver_v3.cpp` now uses a strict ASCII decimal scanner and full-consumption finite `strtod`; source inspection confirms it ignores ERANGE alone and retains finite subnormal conversions; original driver and historical evidence must remain unchanged. Actual native/Wasm handling of those literals remains an explicit gate in the separately frozen compiled study.

`observations-v1.json` is preliminary: the first two lexical probes accidentally shared fixture argument lists and failed for an unrelated recovery mismatch. They are not lexical witnesses. The harness was corrected; `observations-v2.json` reproduces the initial recovery, lexical, and Wasm exception gaps. `observations-v3.json` records the ASCII grammar fix and extends raw exception/error probes. Preserve these reports and their embedded reviewed hashes. Later reports identify the exact source state checked and never replace these failures.

Other probes check closed expectation tags and fields, finite numeric inputs/outputs, complete CSV arities/echoes, duplicate JSON keys, descriptor parameter order, command and CABI argument identity, full decoded recovery, matching backend errors against source budgets, finite-only huge matching values, and opposite extreme finite values whose subtraction overflows. Matching huge finite-only values intentionally pass support/parity without implying source accuracy.

## Final bounded result

`observations-final.json` records **44/44 expected observations**, with no unexpected rows. The final source state requires `after_rejection` whenever `recovery_of` occurs, closes successful native raw and Wasm row shapes, and rejects `error`/`exception` markers on completed observations. All previously reproduced contradictory bundles now reject. The strict decimal grammar rejects underscores, surrounding whitespace and Unicode digits; omitted/unknown tags and tag/status contradictions also reject. The old driver hash remains unchanged.

Final observed source hashes are embedded in `observations-final.json`, including the distinct new driver. Source inspection confirms its scanner accepts decimal forms with optional sign, decimal point and exponent only; conversion requires full token consumption and finite binary64. It does not reject a finite representable subnormal merely because libc sets ERANGE. This is source review only, not a compiled parser equivalence test. Decimal values that round to zero are treated as finite binary64 inputs, consistently with Python float conversion; exact subnormal preservation in the frozen corpus remains a compiled observation gate.

No remaining transport-contract gap was reproduced in this bounded fixture. This does not claim exhaustive security testing or authenticate that an actual binary ran: fabricated bundles intentionally demonstrate structural evidence checking. Real build/collection receipts and the separately frozen compiled study are still necessary.

## Reproduce

From any directory:

```sh
python3 -B /absolute/path/to/packet/audit.py --root /Users/bmar5496/code/constitutive-atlas --output /private/tmp/fresh-tagged-v3-independent-review.json
```

The output must be fresh. Inspect `all_expected_observations`, `unexpected_rows`, and `reviewed_hashes`; a successful Python exit alone is not review approval. The test reads current source, so source hashes identify each report. It is independent of the coordinator's synthetic test suite and does not replay constitutive references.

## Remaining gates

The coordinator must review/fix all retained contradictions, freeze the new v3 tools/driver/protocol/build identities, and execute the distinctly identified native/Wasm study serially. Actual minimum-subnormal echoes and material rejection, same-instance recovery, 41 original source budgets, finite-only support/parity, and all rejection messages must pass without refitting/relaxing policy. Source-only transport tests do not establish compilation success, scientific admission, integration accuracy, experimental validation, or full-SPD boundary certification.
