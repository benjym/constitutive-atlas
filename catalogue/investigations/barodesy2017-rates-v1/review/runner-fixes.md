# Barodesy runner hardening packet

Staged replacement runner and Node collector plus new hardening tests. Do not replace core/model/originalreference. Requires already installed tools/barodesy2017_reference_check.py and tools/retain_barodesy2017_reference.py. All23Python tests (16existingwithdynamicinvalidcount plus7newgroups) pass against the corrected installed model using a staging import overlay; no native/Wasm/build calls were made. Node source was reviewed statically, not executed.

## Changed contract

- reference() regenerates the independent111case corpus at80/140digits and verifies160digit refinement/rejections before any frozen values can be accepted. The original reference bytes stay unchanged.
- collect() checkpoints a partial report before each request and after each response. Native CLI records stdout/stderr/arguments/returncode in OUTPUT.transport.jsonl before JSONparse/status validation. Native status must equal strict response.ok (descriptor must exit0). Node likewise writes raw CABI text to a companion and checkpoints report rows before structural/numerical assertions. Failed collection leaves partial evidence for diagnosis rather than a misleading successful report.
- Native/Wasm reports now contain support_records: three valid diag(1,1,1e-10)stress states scaled1e-50,1,1e50, computed freshly by the independentCartesianoracle. Six dynamic boundary invalids supplement the original10: negative-diagonal cancellation reproduction; ±1e-16/zero third diagonal; two rounded oblique ±1e-16 directions. All16invalids require rejection and control recovery. This exercises the corrected conservative64epsiloninterior in real native/Wasm requests once root runs collectors. It is not an exact-SPD certification.
- Keep the original2e-13 seven-component norm budget. Additional component checks require every oracle exact-zero channel to be exactly zero, void rate to be within4representable binary64 steps of `-(1+e)*sum(de[:3])`, and each stress component absolute error <=2e-13*S. Here S=||sigma||||de||*|c3|*(|f|+|g|), a finite source term envelope with correct stress-rate units. No absolute-one floor hides small-pressure cases; zero input requires exact stress zero. Density magnification makes an unweighted ||sigma||||de|| scale inappropriate over the requested1e±50pressure cases. This envelope criterion is absolute relative to possible source contributions, not a relative-to-each-small-component claim. Existing norm criterion remains independently enforced.
- Artifact records always require exactfields, nonemptydistinctstringpaths and64lowercasehex hashes, including when current file checks are disabled. `--historical-numerical-replay` with --verify skips only current artifact byte access and reports `artifacts_verified_now:false`. Validate retained provenance/receipts separately; this mode establishes historical numerical reassessment only.
- `--native-report PATH` overrides the embedded historical native path for portable archive replay; pinned native reportSHA remains mandatory, native transcript is fully reassessed, all114validrecord parity is checked. Historical original embeddedpath can remain a receipt.

## Root commands

```
python3 -m tools.barodesy2017_rate_study --native /absolute/probe --output /private/tmp/barodesy-native.json
node tools/test_barodesy2017_rates_wasm.mjs --native-report /private/tmp/barodesy-native.json --wasm /absolute/barodesy.mjs --output /private/tmp/barodesy-wasm.json
python3 -m tools.barodesy2017_rate_study --verify /private/tmp/barodesy-wasm.json --native-report /private/tmp/barodesy-native.json
python3 -m tools.barodesy2017_rate_study --verify catalogue/investigations/barodesy2017-rates-v1/wasm.json --native-report catalogue/investigations/barodesy2017-rates-v1/native.json --historical-numerical-replay
python3 -m unittest tests.test_barodesy2017_rates tests.test_barodesy2017_runner_hardening -v
```

Retain new runner/collector/test/helper/generator hashes in provenance. The companion transport is diagnostics, not a successful-verification receipt. Parent should revise existing source-dossier statement that verification does not rerun the oracle, and update10invalid references to16plus3support witnesses. NoAD/integration/public/scientificadmission is established.

Python assessment:111canonicalrates,3support witnesses,16invalids; maximum norm error2.6375055313110176e-15; maximum component envelope-scaled error1.3782729346896245e-15; void closure0ULP. No native/Wasm claim is made in this packet.
