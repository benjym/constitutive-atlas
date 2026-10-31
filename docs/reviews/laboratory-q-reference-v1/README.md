# Stored-value laboratory q reference v1

REF-laboratory-q-cancellation-v1. Independent source-only packet; no candidate, producer, material/backend call, build, shared edit or numerical admission. Original failed browser study remains unchanged. Source, 35 exact inputs, reference program and acceptance policy were SHA-frozen in `prospective-freeze.json` before reference construction.

## Diagnosis and exact identity

For stored orthonormal Mandel stress `(a,b,c,u,v,w)`, trace `t=a+b+c` and exact mean `m=t/3`,

`q² = (3/2)[(a-m)²+(b-m)²+(c-m)²+u²+v²+w²]`

`= (3/2)[a²+b²+c²-t²/3+u²+v²+w²]`

`= ((a-b)²+(b-c)²+(c-a)²)/2 + (3/2)(u²+v²+w²)`.

The last form avoids cancellation through a rounded mean. Mandel shears are sqrt(2) times Cartesian shear, so their coefficient is3/2; applying Cartesian-shear weights directly would be incorrect. For equal stored diagonal values and zero shears every difference is exactly zero, independent of the mean's representability. Axisymmetric diagonal stress with b=c gives q=abs(a-b). This is the nonnegative q observable; signed_q is a separate existing quantity.

Current main.cpp serializes sqrt(1.5*dot(dev(sigma),dev(sigma))). tensor.hpp dev subtracts rounded(trace/3). Even a correctly rounded trace does not make division by3 recover the original equal diagonal. For parent-reported native diagonal `0x1.66b187563dbbap+18`, exact stored-value replay gives RN(trace)/3 rounded to `0x1.66b187563dbbbp+18`, leaving each diagonal residual −2^-34. Therefore q=sqrt(9/2)*2^-34=1.2347709524675985e-10. The reported Wasm diagonal `0x1.66b187563dbb7p+18` rounds back to itself and gives zero. Both stored tensors have exact q=0. `diagnosis.json` independently reproduces this from exact rationals; no backend journal or backend was executed/read by this worker.

## Reference and prospective gate

`inputs.json` contains35binary64 tensors with exact bits and hex:12exact isotropic cases including both reported stored tensors and signed zero, one-ULP perturbations, large/tiny/mixed diagonal values, pure/general Mandel shear, large hydrostatic values with unit/minsub shear, and planar/spatial rational orthogonal rotations. Rotated Cartesian tensors are rounded independently into stored Mandel components; references target those stored values, not an unrounded ideal rotation.

All six components are finite with absolute value<=1e300, including minimum normal/subnormal. This bound keeps pairwise differences and weighted shears finite and leaves generous norm headroom. It is a bounded observable reference domain, not an expansion of model admissibility and not a full-range guarantee for every finite binary64 tensor.

`reference.py` forms q² exactly with Fraction. Decimal sqrt at800/1200digits agrees on final binary64 bits. Every rounded answer is certified independently against exact rational squared midpoints of adjacent floats, including ties-even. `references.json` retains q² numerator/denominator, both decimal results, rounded bits/hex and certificates. `check.py` independently checks the expanded trace identity, finite/range conditions, rounding cells and accuracy gate.

The frozen gate requires finite nonnegative output and absolute error<=32*2^-53*q_exact+8*minsub, with positive zero exactly for every isotropic stored tensor. This is a prospective acceptance budget, not an assertion that an untested libm helper is globally proven to meet it. The implementation-independent checker uses exact inequalities: if alpha=32u and beta=8minsub, a candidate c passes iff q² lies between max(0,(c-beta)/(1+alpha))² and ((c+beta)/(1-alpha))². Isotropic q²=0 uses the stronger exact +0 rule. No observed candidate error set this budget.

## Smallest implementation and frozen replay requirements

Add a double-only serializer observable helper, leaving constitutive dev/dot, DSL, Jet/AD, generated material expressions, controller and integration untouched. A bounded-domain implementation can form pairwise differences first, then use a scaled norm/hypot on `(a-b,b-c,c-a,sqrt(3)*u,sqrt(3)*v,sqrt(3)*w)` and divide by sqrt(2). Explicit all-zero features return +0. A scaled norm avoids overflow/underflow from squaring large/tiny inputs; do not scale the original hydrostatic tensor before subtracting, which can destroy small differences/shears. This is an algorithm recommendation, not executed candidate code. Supporting a wider domain needs explicit overflow-safe difference handling and a separately justified gate.

Before candidate execution pin exact helper/serializer/toolchain inputs, these source references/policy and all negative/isotropic tests. Require both native/Wasm outputs independently to satisfy the exact source gate; retain current physical parity gate unchanged. Preserve state, strain, controls, p, signed_q, u, diagnostics, settings, model/catalogue/API/loading identity, success/message exactly between matched before/after runs; exclude elapsed_ms and revised q only. Use identical literal loading and all previous nine-model/failed-prefix/recovery schedules. Existing saved observations and failed gates remain immutable. A new observable study cannot close unrelated material/controller or loading failures.

Run `python3 -B reference.py` then `python3 -B check.py`. Current checks:198pass, no retained failed reference/check run. No C++ helper or candidate execution was produced. Parent's smallest next action is review/pin this packet, implement the isolated observable helper, then freeze a distinct replay study before serial builds.
