# Generic spectral primitive study v1 — results

Both serial standalone Release builds completed normally. Each backend executes the same1136 frozen calls:852 successes and284 expected checked failures. All11530 independent accuracy checks and222 exact diagonal eigenvalue checks pass per backend. Failed calls preserve prefilled outputs; injected nonfinite inputs cover all six primal positions and all38 derivative columns, with immediate valid recoveries. No request, policy, reference or source bound changed after observation.

Worst error/allowance fraction is0.240084 on dense-subnormal maximum value (both backends). Normalized eigenvalue-gap failures are numerical resolution diagnostics, not accepted physical restrictions. Repeated/hydrostatic value-only queries and isolated projectors with complementary repeats remain supported. Unrepresentable rounded values/derivatives return the frozen range diagnostics. The exact diagonal mixed-scale middle retains value1.

Independent references use the stored binary64 Mandel tensor, mathematical sqrt2 decoding and a characteristic-cubic method; the candidate uses24 cyclic Jacobi sweeps. The280/360-digit adequacy checks and two earlier failed reference attempts remain unchanged. The prospective freeze pins30 files before either compile. Logs and exact artifact hashes are retained separately.

Both backends pass independently against the same references. Their statuses agree on all1136 calls;1122 output records are exactly equal, while14 have floating differences inside their independently checked error bounds. Exact cross-backend bit equality was not an acceptance gate. No bit-identical output claim is made.

Run `python3 -B catalogue/investigations/symmetric-spectral-primitive-v1/verify_study.py`. It rehashes source/evidence/reference bindings, regenerates literal requests and replays the assessor and adequacy checks under a copied trusted source capsule without executing compiled artifacts. Native termination precedes Wasm start. Recorded artifact hashes are checked when the local binaries remain available; absence is explicitly reported. The separate verification report is reproducible metadata and excluded from the evidence manifest to avoid circular pinning.

An initial copied-source verifier failed on nested newline escaping before assessor execution. Its original script and child error are retained in verification-initial-failure/; the corrected metadata harness uses chr(10). No numerical source, reference, policy, request or compiled result changed.

This establishes bounded generic primitive accuracy and checked-output behavior, not production DSL integration, static qualifier enforcement, generated lazy/sticky semantics, MC floating branch/equality classification, update tangents, solver rollback, scientific admission or agreement with experiments. These remain separate roadmap gates. Installed/hosted model counts remain nine/five; nothing is pushed or deployed.
