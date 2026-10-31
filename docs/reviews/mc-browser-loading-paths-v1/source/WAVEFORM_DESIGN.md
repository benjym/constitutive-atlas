# Generic reproducible caller loading

## Recommendation and compatibility

Implement the additive explicit-control foundation first (FOUNDATION_REVIEW.md). Exact shared caller bits remove this observed source of backend difference without changing a constitutive law or controller. The committed common-literal intervention establishes exact identity for this one288-call/65-point corpus, not arbitrary model/controller reproducibility.

Keep existing atlas_run/atlas_run_with_settings, schema0.1 exports and browser/import paths unchanged. Their catalogue_hash/settings contain no waveform producer identity. Absence of new loading metadata therefore means legacy semantics; do not reinterpret an old cyclic export through a new producer. Retain the failed original sine gates and all frozen studies unchanged.

An explicit path is the primary loading input; a waveform generator is merely one producer of that path. The first API can echo canonical64bithex controls/version without selecting a deterministic producer now. A later producer should identify its algorithm/version, exact amplitude bits, integer steps/cycles, initial signedzero policy and complete produced controlbits. Any import claiming that producer should verify its output sequence. Raw arbitrary literal paths need no waveform claim. Model schema0.3 constitutive records are unaffected; provenance belongs to the caller/run artifact.

## Optional future producer specification

Working identity `cyclic-sine-rne12-v1`, prospective only; not installed or executed as production code. For steps1..5000,cycles0..100,index0..steps, use integer `phase=(cycles*index)%steps`. Compute `quadrant,rem=divmod(4*phase,steps)` and reflected numerator `j=rem` for even quadrant, otherwise `steps-rem`. Maximum cycles*index500000 and4phase19996 fit signed32bit. Check bounds before arithmetic. Helper tests include integer combinations that existing run validation rejects; existing cyclic sampling rule steps>=16cycles stays unchanged for the actual laboratory API.

If j0 return wave+0; if jsteps return exact+1 in quadrant1 or−1 in quadrant3. Otherwise evaluate:

```
ratio = RN(double(j)/double(steps))
x     = RN(0x1.921fb54442d18p+0 * ratio)
z     = RN(x*x)
term=x; sum=x
for n=1..11:
    term=RN(RN(-term*z)/double((2*n)*(2*n+1)))
    sum=RN(sum+term)
wave=sum with exact negative sign in quadrants2/3
```

RN means one independently rounded binary64 operation, nearest/ties-even. No reassociation, multiply-add contraction or retained extra precision is allowed across those boundaries. Zero amplitude or exact phasezero gives control+0; otherwise control=RN(amplitude*wave). Nonzero product underflow preserves IEEEproduct sign. Target can be negative; it flips the physical waveform. The pure helper's cycles0 result is allzero and is **not** the legacy cycles0 monotonic mode. Monotonic generation remains a separate existing producer.

This changes old libm caller bits and makes full/half-period zeros exact, whereas the legacy float-pi/libm expression can leave small endpoint residuals. It therefore requires a new caller identity and fresh reference/backend/default/regression study; it is not a patch to the old failed parity gate. Do not silently switch defaults.

## Conditional error proof

Let u=2^-53. All assumptions are explicit: supported IEEEbinary64, correctly rounded basic operations, nearest/ties-even, gradual underflow, exact conversion of integers<=5000, exact hex pi/2 constant, no contraction/reassociation, and per-operation binary64 narrowing. `volatile` result helpers can help express boundaries but C++ alone does not establish every assumption; supported toolchain/runtime profiles and tests are required. In particular the C++ draft warns constant/runtime evaluation need not have identical floating results. [C++ draft constant evaluation](https://eel.is/c++draft/expr.const). WebAssembly's specified numeric semantics provide a useful target contract; native support needs its own profile. [W3C WebAssembly numeric semantics](https://www.w3.org/TR/2024/WD-wasm-core-2-20240305/).

Exact rational Machin-series enclosures prove the chosen pi/2 constant differs from mathematical pi/2 by<u. Two argument operations then give absolute angle error `u+pi2_float*(2u+u^2)<5u`. Computed x<8/5. On the finite allowed grid, the smallest nonzero x and all degree23 recurrence terms remain normal; the minimum-term certificate is included. Thus ordinary relative-rounding bounds apply internally.

The polynomial includes powers1..23. Alternating-series remainder at x<=8/5 is at most `(8/5)^25/25! <1e-20`. The recurrence has z error plus two operations per term, so each term's relative error is bounded by gamma_(3n), n<=11. Eleven rounded additions yield total arithmetic absolute error <=gamma44 times the sum of exact term magnitudes. Here gamma44=44u/(1−44u), and the exact finite positive sum at8/5 is<12/5. Combining argument, arithmetic and remainder gives a rigorous conditional bound1.20645e-14 <128u=1.42108547152e-14. check_proof.py verifies all rational inequalities, using alternating atan series to enclose pi. This is a proof for the specified arithmetic contract, not a proof that an arbitrary compiler executes it.

No clipping is required. A nonquarter grid sample has reflected fraction<=1−1/5000. Its true sine is at least `1/(2*5000^2)=2e-8` below1, via `1−cos(t)>=2t^2/pi^2`;128u is much smaller. Quarter extrema are directly exact. Positive interior values are likewise separated fromzero. Therefore |wave|<=1 over the allowed grid. Multiplication adds at most u*|amplitude| plus halfminsub, yielding the simpler declared absolute control bound `130u*|amplitude|+minsub`. Only the final multiplication may underflow for a subnormal amplitude; the absolute minsub allowance handles it. No overflow is introduced for finite amplitude if |wave|<=1, though existing run amplitude caps remain stricter.

## Independent fixtures and prospective gates

reference.py is an independent specified-semantics oracle: exact Fraction arithmetic plus integer ties-even rounding and explicit IEEEbit encoding. It does not run C++ or use host sin to define expectedbits. Separate Decimal Machin/Taylor mathematics supplies the true sine. policy/source bytes were frozen before either reference run.

The corpus includes1080phasecases,9720amplitude-controls: all indices of steps1..32 and63/64/65; boundary neighbors for127/128/129/4999/5000 and cycles1/2/3/7/100; amplitudes±1,0.01,200000,1e8,±0,minsub,minnormal. Both140/180digit source runs satisfy the bound. Maximum observed wave error2.611e-16 is a corpus observation, not the bound used for acceptance. The140/180 cross-precision gate is1e-110 with max(1,abs(value)) normalization. Additional phase checks span all steps1..5000,selectedcycles/endpoints; not every possible integer triple or amplitude is numerically enumerated. The proof covers the specified grid and arithmetic assumptions.

Before any future producer execution freeze supported compiler flags/profile, rounding/subnormal diagnostics, exact corpusbits, all parse/encode and subtraction-bit checks, exact native/Wasm/oracle equality, mathematical bound checks and corruption probes. Include FMA-sensitive values, negativezero/minsub transport, invalid inputs, counts/overflow boundaries and all waveform endpoints. Test the compiled producer independently of model integration, then freeze a separate full5protocol/nine-model legacy/default/browser/import/export/recovery corpus. Do not equate producer exactbits with a proof of arbitrary solver exactness or scientific admission.

One checker failure is retained: the initial recursive comparator interpreted hexadecimal bitstrings containing `e` as Decimal scientific notation and overflowed. The comparator was fixed to compare *_bits/*_hex fields as strings; references, policies and numerical bounds were unchanged. It is a test parsing failure, not a waveform bound failure.
