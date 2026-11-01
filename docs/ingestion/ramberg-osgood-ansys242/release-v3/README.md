# Strict Linux regeneration correction v3

Release8cab145b/run41350895734 passed both Wasm jobs and full macOS native qualification. Linux completed1493Python tests with one failure: exact prospective request regeneration. Its original log/status and v2 test bytes are retained here. The earlier coverage correction passed.

An official Python3.12 Linux amd64 container with read-only repository access reproduces18 differences, all1–2ULP in n2.5-uniaxial prepared loading strain. Intermediate diagnostics establish identical q and ratio, but Apple/libm and Linux/libm pow(ratio,1.5) differ by oneULP. The algebraically equivalent ratio*sqrt(ratio) has identical original frozen bits on both platforms.

The test's scoped preparation helper declares this operation order and explicit fsum, with no stored-value lookup. Entire-object exact equality remains mandatory. The83case frozen corpus, independent stress oracle, production model/solver, canonical50artifact review and all numerical acceptance gates remain unchanged. Nine focused checks pass on macOSPython3.12, macOSPython3.14 and Linuxamd64Python3.12. Separate review accepts the controlled correction; failed attempts remain retained. Full new CI/deployment/live qualification is still required.

The local Docker startup UI call stalled; no author code or binary was executed. Docker diagnostics use the official python:3.12-slim image digest aa943ce411423c7582288f18707ff66eddcbaeb510502d747a72aeb34f30d159 and read-only repository mount. Containers are removed after execution.
