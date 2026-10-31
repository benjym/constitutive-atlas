# Wider finite paths: independent reference and proposed study

This is a bounded staging packet for the zero-spin Barodesy 2017 body-law research variant. It contains source mathematics, independent scalar/Cartesian references, and a predeclared future study protocol. It does not change the candidate model, shared solver, authoritative repository, regular or hydro drivers. No native/Wasm build or execution occurred. There is no integration, AD, physical-validation, or admission claim.

Source selection: [Medicus and Fellin 2017](https://doi.org/10.1007/s11440-016-0458-4), body Eqs. 1–10 (pp. 366–367), Table 2 (p. 368), incompressible-grain closure (footnote 13, p. 374). Body 2p density is retained; the Appendix 6p discrepancy and printed spin expression remain unresolved. The private publisher PDF's SHA256 is recorded in the evidence; no source PDF/text/rendering is included.

## Bounded matrix and evidence

`tools/reference_barodesy2017_wider_paths.py` adds an exact **signed scalar branch** solution and a full seven-state fixed-grid RK4 integrator of the existing independent Cartesian/Decimal rate oracle. It imports independent reference utilities, not Atlas/model/DSL/compiler code. Their source hashes and this generator/protocol hash are retained in `catalogue/investigations/barodesy2017-wider-reference-v1/reference.json`.

Six scalar cases cover three Table 2 soils, each with off-NCL monotonic compression and off-NCL compression/unloading/reloading. Initial pressure is explicitly 100 kPa. The independent NCL void ratio is rounded to binary64, then `(1+e)*0.9−1` is performed in binary64 and supplied as the initial state. That is a declared initial preparation, not a simulated compaction path or a hidden NCL reset. Every actual p/e/parameter/increment value is retained.

Each scalar case supplies actual isotropic Mandel increments obtained by binary64 `dv/3`. The exact scalar solution integrates their **exact Decimal trace**, converting the original binary64 initial state once and carrying Decimal state across physical knots. It rounds only displayed knot outputs. Nominal dv, actual trace, and nearest-binary64 scalar RK4 trace input are separate fields. Their tiny discrepancy is recorded; it is not silently called an identical path. The existing independent scalar log-pressure RK4 provides a numerical cross-check rather than the primary exact reference.

Two tensor cases use London clay with anisotropic SPD stress and three nonproportional/reversal increments, plus a dense coordinate rotation of initial stress and all increments. The full seven-state RK4 evolves all stress components and void ratio. It does not insert the exact void solution into the evolving state; exact volume closure supplies a separate error diagnostic. Every intermediate RK stage and candidate endpoint is checked by the independent source oracle. Minimum pressure, void ratio, and three Cartesian leading principal minors are retained. These are safe interior cases, not an investigation of the candidate model's stress-support boundary.

Grids 8, 16, 32, and 64 per original segment were declared in `catalogue/investigations/barodesy2017-wider-reference-v1/protocol.json` before the reference study. The tensor refinements' last endpoint-difference ratios are approximately 15.9226 and 15.9255. Last stress differences are approximately 1.67626e-6 and 1.67596e-6 Pa. Maximum tensor void-closure discrepancy is 5.56e-16. Tensor actual step values and exact Decimal accumulated loading are stored; these power-of-two grids preserve the bounded input increments exactly, with any residual explicitly checkable.

The scalar 100/160-digit solutions round to identical binary64 outputs. Scalar RK4 errors decrease across all four grids; ratios are checked only above the declared 1e-7 Pa floor. The finest Dresden off-NCL compression error is about 9.42e-6 Pa; some Weald results are already below the floor and must not be assigned a measured fourth order. None of these observations certify all-input rounding or rigorous RK4 error bounds.

Twelve pure Python tests pass, including both-sign scalar-rate agreement with the independent Cartesian law, exact-solution/RK4 comparisons, full-path covariance, stage support, full seven-state void closure, entire retained-evidence regeneration, and unchanged supplied-parent values on a failing reference attempt. That last check concerns only this local reference function; it does not establish the common solver's transactional behavior.

## Signed scalar solution, without NCL assumptions

Let v be compression-positive accumulated volumetric loading, y=log(p), V=1+e, `z=[V exp(−N) (2p/1000Pa)^lambda]^c5`, `t=c5 lambda`, `K=c3/sqrt(3)`, `B=2^t`, and `D=500^(−t)`. Incompressible grains give `dV/dv=−V`.

The source's hydrostatic reduction is

- compression: `dy/dv = 1/lambda + K(z−B)`;
- unloading: `dy/dv = 1/kappa − K(B+z−2)`.

Using the published coefficient identity `K(B+D−2)=1/kappa−1/lambda` yields `dz/dv=tK z(z−B)` in compression and `dz/dv=−tK z(z−D)` in unloading. For a branch with equilibrium C and coefficient a, where `(C,a)=(B,tK)` or `(D,−tK)`, the actual rounded initial state determines z0 and

`p(v)/p0 = exp(v/lambda) [1+(1−z0/C) expm1(a C v)]^(−1/t)`.

The bracket must remain positive; V and p must remain supported. The implementation uses high-precision exponential differences within a bounded nonzero segment. It selects a new branch at each ordered physical reversal knot and carries the actual previous state. It never treats unloading as an NCL exponential or assumes universal 1/kappa slope. The latter depends on z; a dedicated test distinguishes both incorrect simplifications. No missing formula was replaced by a guessed law.

## Proposed common-engine study, not implemented here

The unchanged candidate's midpoint/adaptive integrator should later replay these supplied increments, comparing every original physical knot. Use the predeclared tolerances 1e-4/1e-6/1e-8 and caller partitions 1/7, with the inherited proposed global stress-error bounds 5e-3/3e-4/2e-5. These are future wider-path gates, not measured solver guarantees. Do not relax them after observing compiled outputs. Reference grid uncertainty must first be at most 10% of the smallest global budget.

Partition requests must retain actual binary64 subincrements and exact accumulated loading. A residual final piece may preserve the target when representable; otherwise report the discrepancy rather than claim identical loading. Keep every reversal knot in its given order, even though cumulative volumetric strain decreases. Do not sort by strain, blend across a reversal, or repeat preparation. Compare the common solver's scalar off-NCL/reversal endpoints with the exact branch solution; compare nonisotropic endpoints with the independently refined Cartesian reference.

For rollback, accept the first two valid nonisotropic increments, retain their exact committed parent, then request `[0.9,0.9,0.9,0,0,0]`. From this prefix e_parent<0.8, the exact final void ratio is bounded above by `1.8 exp(−2.7)−1<0`. The whole caller increment must fail: preserve the exact parent stress, e, external strain and history/generation, and retain the successful prefix. Internal accepted subdivisions must not escape. The future driver should retain failure diagnostics and raw/partial responses, then replay a valid control from that same parent to show recovery. A separate synthetic budget/domain fixture may be needed to prove failure after at least one accepted internal subdivision; this source reference does not fabricate such an event.

Also check reset-to-explicit-initial replay, exact duplicate-target identity with no artificial increment/history change, and partition replay without inherited trial state. These are integration transaction gates, not zero-loading AD claims. Require compiled full-model identity, parameter order, exact requests/knots/partition values, binary/Wasm hashes, finite output, and native/Wasm parity. Retain raw and partial evidence before numerical acceptance. No native collector, CMake target, or generated solver change is included in this packet.

## Reuse

Run tests from repository root with `python3 -B -m unittest tests.test_barodesy2017_wider_reference`. Explicit evidence generation uses `python3 -m tools.reference_barodesy2017_wider_paths --output /chosen/path/reference.json`; tests never regenerate retained files in place.

The [independent review](barodesy2017-wider-independent-review.md) found no blocking discrepancy in this bounded reference. Installation adapted only repository evidence paths; fresh regeneration matches every staged field except the generator receipt, which reflects that path change. This reference packet supplies no compiled wider-path result. Caller-point references and the common-engine comparator require separate review. Neither can resolve the body/Appendix discrepancy, finite spin, experimental comparisons or public admission.
