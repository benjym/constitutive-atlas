# Independent determinant core review v1

Task REV-determinant-core-v1; 2026-10-31. Read-only review of `cpp/include/atlas/numerics/determinant.hpp` and `atlas/numerics/determinant.py`. Staged for coordinator integration into `docs/reviews/symmetric-determinant-core-v1/`. No implementation edits, builds, compiled C++/Wasm calls, material rates, Atlas interpreter evaluation or production integration changes.

## Findings and source identities

The initial C++ structural interface required six input components and38output derivatives but did not require38input derivatives. A structurally matching tensor with a smaller input derivative array could pass the range-based finite checks and then be indexed at0..37. The coordinator added an input derivative arity assertion before study freeze. The original header SHA256 `b6d70475d6fd4e48eb4fefc02b5fefdb03e278508b32b851a4f1d5c4de473b67` was reconstructed by removing the single new assertion from the immediately following header; the coordinator independently confirmed it against the original initializer artifact. It was not a worker-captured pre-edit hash. Intermediate arity-fixed header SHA256 was `3e4fe6ce6d41b07b12199cce3e9cdfd43da570b266b575e8157c51655739feb1`.

The coordinator then added compile-time rejection of `__FAST_MATH__` and nonzero `__FINITE_MATH_ONLY__`, because those optimizer assumptions undermine the explicit finite-input contract. Header SHA256 `61595c89b0eb39ae761b6b5d649487ec60c82f678b8a4f0ded00f8d155cdaa54` includes both changes and was reviewed/probed as recorded in the initial probe receipt. These macros cover the intended compiler configuration, not every possible compiler's unsafe-math option. Build receipts still need to identify actual flags.

A second structural API edge was reported: checking a long-double input for finiteness before implicit narrowing to `Dyadic::from(double)` can permit a finite source scalar outside binary64 range to become infinity and be decoded as an ordinary dyadic. Production Tensor<double>/Jet<double,38> uses are unaffected. The interface should constrain scalar input and Jet primal/seed elements to exact double, or explicitly constrain the supported types; platform double size/IEC559 assertions alone do not constrain the input type. The coordinator added exact-double assertions for scalar input and Jet input/output primal/seed elements before compilation. Final header SHA256 `60cfdf8d1449838b330dc5377b55237a661c76f6f0f6ec4c7429916ac925eea4` contains this fix as well as the arity and unsafe-math guards. The final rerun again passes1524/1524probes; the earlier receipt remains retained. A manifest-time source identity check caught this concurrent source update and prevented pinning the prior source as final; no output packet was produced by that failed identity check.

Python core SHA256 at the first full probe run: `5842571983e5c7ecd16e6b730c678ef4e2b67346916ba96ad87f841d6429781c`. The Python entry point explicitly validates arity, finite real int/float values and rejects Boolean/type aliases; finite integer inputs are converted to their binary64 value before exact-ratio construction.

## Independent algebra/rounding assessment

The generic Mandel determinant and its six gradient components agree with the Cartesian cofactor definition used by the independent78case reference packet. The off-diagonal directional derivatives contain the required half-irrational cross factor; contracting six gradient components with one seed column is equivalent to the full Cartesian cofactor:seed contraction. It differentiates the exact real polynomial and rounds each resulting direction independently, not a floating rounding map.

For a+b*sqrt(2), when one coefficient is zero or both have the same sign, the exact sign is immediate. For opposite signs, comparing a² to2b² and multiplying the relation by sign(a) is valid. The implementation squares only after this sign split. Because nonzero rational a/b cannot equal sqrt(2), a nontrivial irrational radical cannot tie a rational midpoint; the exact comparison still handles rational equality when b=0. All coefficient arithmetic remains exact dyadic/integer arithmetic.

The positive nearest-even selector first rejects values at or above the midpoint between maxFinite and the conceptual2^1024 upper neighbour, namely2^1024-2^970. This correctly rejects the halfway overflow case. Candidate interval lower and upper midpoint comparisons permit equality only for an even least-significand bit. Zero has no positive lower neighbour and correctly accepts the positive half-minimum-subnormal tie; final zero is assigned literal+0 even for negative exact input. A negative nonzero result is selected by rounding its positive magnitude and applying the sign bit. The monotone fallback binary search finds the greatest positive binary64 <= exact magnitude, then applies one exact midpoint test. The prior overflow check prevents selection of infinity.

Approximate floating guides can underflow, overflow, cancel, become negative, or be wrong by many ulps. They are not an accuracy assumption: each proposed neighbour is accepted only by exact interval comparisons, otherwise a complete exact binary search runs. This also makes the final result independent of a libm sqrt approximation and the floating evaluation order of the guide. This review does not require floating exception flags or errno to be preserved.

## C++ integer and exponent inspection

The following is source-level reasoning, not execution or a formal machine proof:

- Big limbs are little-endian uint32 magnitudes. Producers trim high zero limbs; comparison relies on that canonical representation. Addition's limb total is <=2^33-1. Subtraction assumes a>=b; its subtrahend plus borrow can equal2^32, still fitting uint64. Unsigned wrap followed by the low32-bit cast supplies the correct result limb, and the unsigned comparison supplies the borrow.
- A multiplication inner step is at most(2^32-1)^2+(2^32-1)+(2^32-1)=2^64-1, fitting uint64 exactly. The terminal carry word for row i is untouched before that row; the prior row's terminal carry is consumed at the next row's last inner product. Assigning that terminal word therefore does not discard a previous carry.
- Left shift separates whole words and0..31remaining bits. The rest=0 branch avoids a shift by32. Adjacent source limbs populate disjoint high/low bit ranges of the same destination word, so OR is appropriate. Right normalization scans to a nonzero low limb after trim has guaranteed one exists, then shifts upward-index source limbs before they are overwritten; the high next limb is still the original value.
- Normalization canonicalizes zero to sign0/exponent0 and removes powers of two from nonzero magnitude. The normal/subnormal bit decoder correctly uses the explicit hidden bit only for nonzero exponent fields and exponent e-1075 or-1074. Public checked entry points validate finiteness before decoding.
- Within the checked binary64 determinant/cofactor-directional call graph, each polynomial term contains at most three finite binary64 factors, plus a fixed half factor and a small finite sum. The smallest raw dyadic exponent is about-3223; largest term magnitudes are about2^3072, with only a few sum carry bits. Exact sign comparisons square these bounded expressions and may require roughly twice their aligned bit span. These are comfortably within ordinary32-bit signed exponent/bit-length arithmetic; dynamic vectors avoid a fixed limb truncation. This is a bounded-call-graph argument, not a claim that exposed internal helpers accept arbitrary user-constructed dyadics of unbounded size safely.
- The guide only extracts at most53high bits and uses ldexp. Any overflow or underflow there affects search speed rather than certified selection. Candidate unsigned offsets remain bounded for a finite nonnegative guide; out-of-range candidates are rejected before interpretation.

The structural checked interface constructs a local Result candidate. It validates all input primal/seed finiteness, computes the exact determinant, then every38directional result, before the single final `out=candidate`. A false return from finite validation or any final rounded overflow therefore leaves caller output unchanged, including if input/output storage aliases in ordinary Tensor/Jet types. Allocation exceptions are not converted to false; the API does not claim a no-throw resource-failure contract. Generic user-defined throwing assignment types are outside the intended plain Result contract.

## Source-only probes

`probes.py` imports only the isolated Python primitive file and the independent private/staged reference module by file path. It does not import the Atlas interpreter. The first complete run passes1524/1524 checks:

-78primal entry calls on frozen literal inputs. Seed-invalid rows are tested as finite-value **primal** calls; this Python scalar API has no Jet input. Their independent full-Jet rejection expectations remain unchanged.
-1326exact radical rounding/sign calls, one for every independently certified primal and38directional component of each finite-input reference case, including final overflow expectations.
-48positive/negative rational midpoint and irrational near-midpoint probes at zero, minimum subnormal, subnormal/normal transition, normal binades and the overflow boundary. Irrational offsets use400-bit dyadic sqrt brackets, far below the guide's precision; independent512decimal-digit rational enclosures certify the expected result.
-64calls with the Python guide deliberately forced to NaN or a grossly wrong finite sqrt value. Correct results persist through exact certification/fallback; no production source was modified.
-Eightinvalid type/arity cases, including Boolean, None, complex, string, oversized integer and wrong sequence lengths.

The initial probe fixture raised KeyError for seed-invalid rows that deliberately lacked full-Jet certificates. `probe-initial-failure.txt` retains that development failure. The corrected harness derives their separate primal-only reference from finite inputs with zero seeds. It does not alter any frozen78case expectation. No determinant-core numeric failure was observed in these probes.

These Python probes verify the exact sign/rounding design and Python implementation, not the custom C++ limb execution, C++ undefined-behaviour freedom, template instantiation, native/Wasm bit equality, code-generation flags, memory safety instrumentation or all possible algebraic inputs. The separately frozen124row native/Wasm study remains required:78unique requests plus46immediate complete known-good recoveries, exact expected bits, invalid status and all unchanged-output sentinels. It must retain every failure.

## Remaining proof, performance and integration limits

The source reasoning supports the design, conditional on the intended bounded binary64 types and ordinary integer semantics. Native/Wasm compilation and exact corpus results remain separate gates. Tests should exercise limb carry/borrow/word-shift boundaries directly if the implementation becomes a widely used generic arithmetic library; this read-only review did not run translated copies of limb code and call that independent C++ execution evidence.

The exact binary search can require about63comparisons per nontrivial rounded component; each opposite-sign radical comparison performs big-integer squares and may allocate multiple dynamic vectors. A38direction Jet may therefore be much more expensive than a naive floating determinant, especially with high exponent span or cancellation that defeats the guide. No compiled timing or throughput claim is made. Profile the frozen primitive and whole material workloads before production use; any caching/fast path must preserve the exact certified fallback and output atomicity.

Correct primitive rounding does not prove complete material source-rate accuracy or supply a support/domain theorem. This stage should leave production DSL/compiler and global floating flags unchanged. A source-preserving candidate rewrite and whole-rate study require a new prospective identity, the original109calls and unchanged41accuracy budgets/parity gate, plus prospectively declared boundary source-accuracy requirements. Human admission remains separate.

## Reproduction

Set ROOT to the repository root and REF to the installed/staged `symmetric-determinant-reference-v1` packet:

```sh
python3 -B /absolute/path/to/this/packet/probes.py --root "$ROOT" --reference-packet "$REF" --output /private/tmp/fresh-determinant-core-review.json
```

Fresh outputs are required. `source_hashes` identify the exact current files; a later rerun can review changed source without replacing prior receipts. The packet manifest pins all worker files. No shared edits, git mutations or compiled calls were made.
