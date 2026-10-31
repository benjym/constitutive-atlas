# Clay2005 instantaneous-rate v3 — retained parity failure

The frozen study **fails its cross-backend acceptance gate**. Both backends individually pass all70accuracy rows (41independent source cases plus29recovery controls),10finite-only output-support checks,29recognized material rejections and29same-instance full-response recoveries. Native and Wasm each retain110raw rows including their exact descriptor. Positive/negative minimum-subnormal inputs echo correctly and reach material rejection rather than a CSV parser error.

All41independent source cases pass the original unchanged budgets. The maximum source error/budget fraction across accuracy rows is0.1031687442712583native and0.09579954825188271Wasm. Nevertheless **five of ten finite-only support cases fail the separately frozen1e-10 scaled parity budget**, in17stress components. The largest scaled difference is0.00017286119375367192 (1,728,611.937536719times budget), at finite_only/margin-above. This failure prevents advancement toward a public laboratory candidate.

Affected retained IDs:

- finite_only/tiny-positive-interior
- finite_only/margin-above
- finite_only/scaled-positive-1.0
- finite_only/scaled-positive-1e+50
- finite_only/oblique-tiny-positive

These cases were support-only precisely because independent high-precision boundary rate accuracy was unresolved; finite output is not source accuracy. That distinction does not waive their prospectively required backend parity. No input, row, rate reference, support classification or budget was removed or adjusted after observation.

`prospective-freeze.json` and exact source snapshots precede compilation/observation. Native and Wasm builds ran serially with one explicit target and one compiler job, and generated headers/catalogues equal the frozen expected bytes. Build command/toolchain/artifact receipts, persistent-process/module raw journals and authenticated comparison are retained. `verify_study.py` reproduces **the failed outcome**, not a success claim; `verification.log` records it.

An initial read-only diagnostic found native fused multiply-add instructions and cancellation-sensitive model expressions such as detH=1/27-j2/6+j3/3. `diagnostic-notes-v1.json` records the exact artifact/inspection identity and limits. This is a hypothesis about sensitivity to arithmetic evaluation, **not proof of the causal operation or of either backend's boundary accuracy**. Next: freeze a separate contraction-controlled diagnostic and independently quantify actual-input determinant/rate conditioning before proposing an algebraic or generic arithmetic repair. Retain this study unchanged and use the same original gates in any follow-up.

No public model is installed. Finite integration, frame transport, tangents, preparation, calibration, experimental comparison and scientific admission remain open. The local runnable count remains8, hosted5; nothing is deployed.
