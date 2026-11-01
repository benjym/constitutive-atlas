# Legacy divergence bounded diagnostic result

Both exact two-call diagnostic responses preserve their own uninstrumented
backend complete JSON, including all diagnostics and status. Native9184trace
rows; Wasm3776. Both calls finish inside120seconds and64MiB caps; hashes,
source mirrors, actual build/link/configuration inputs and rawstreams retained.
Independent review db859f365d08deb69ddedf3140e74485a5ad7429acca6ed7f03bef28ce49e14f.

Earliest bit difference is a tiny initial history-row Jacobian derivative;
the first3x3stressJacobian and stressresidual are identical. Independent
Python math.fma Gaussian replay reproduces native's first8componentdelta,
while separate multiply/subtract reproduces Wasm's. Crossusing either
historyrow gives the same respective stressdelta. First observed branch
difference is native admitting backtrack7 while Wasm rejects its evaluation.
This localizes a demonstrated linear stress-direction source, not every
later divergence or the earlier history derivative's primitive cause.

New fused-linear-v1 changes exactly three generic Gaussian updates to explicit
std::fma on both backends. It must first preserve native whole-response legacy
compatibility, all57legacybackend gates, unchanged120second hardcases and every
original fullgate. No diagnostic observation grants repair/qualification.
Original outer-predictor aggregate parity remains FAIL.
