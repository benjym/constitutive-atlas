# Independent MC browser-loading finite-path references v1

This is a new source-only loading/reference identity for the same14 laboratory requests as the original MC axisymmetric study. It implements the specified `linear-rne-v1` and `cyclic-sine-rne12-v1` caller producers using the independent exact Fraction oracle, then propagates their exact stored binary64 increments through the unchanged independent scalar MC source mechanics. No production JavaScript, Atlas model evaluator, spectral eigensolver, compiled backend or browser was imported/executed. No material admission is implied.

## Input and loading identity

`requests.json` preserves the original14 request bytes, including IDs, protocols, targets, steps/cycles, parameters, initial stresses and integration settings. Those are historical request metadata; their `mode:run` is not a claim to call the old sine-generating API for this new study. The executable caller controls are specified by this packet's `source-input.json` and per-path producer IDs. A collector must use exact controls_bits through the explicit-control API, and identify the new producer separately.

The original source input is retained in `source/original-source-input.json`; the original study and all its results remain unchanged. Physical parameters are the exact stored binary64 defaults E30MPa,nu.25,c10kPa,phi stored(pi/6),psi stored(pi/18),p_ref100kPa, initial100kPaI. Effective stress, small strain, zero spin and six stress components follow the copied FORMULAS/DERIVATION convention.

For cycles0, `linear-rne-v1` starts at canonical+0, evaluates each nonendpoint as RN(RN(target*i)/steps), sets the endpoint to the exact target, and uses canonical+0 throughout when amplitude is numeric zero. For cycles>0, `cyclic-sine-rne12-v1` uses integer phase/quadrant reduction, exact quarter extrema, fixed hexadecimal pi/2 and individually RNE-rounded twelve Taylor terms from the frozen source design. Initial/full/halfperiod nodes are canonical+0. Nonzero products rounding to zero preserve their sign. There is no host libm sine, production producer import, clipping or branch adjustment.

Each path exposes `controls_bits` for all points including initial+0, plus `control_targets` excluding the initial point, and both hex/bit forms of the exact RN difference of consecutive controls. The mathematical reference consumes those literal increments; it does not silently impose an absolute target on the q controller. All834 caller controls and820 deltas are explicit.

There are225 changed cyclic controls relative to the original intended Python libm input (45 of64 on each of five cyclic paths), including exact zero-node semantics. All nine noncyclic path sequences happen to match the earlier inputs. This observed finite coincidence does not make the producer identities interchangeable. This packet does not replace old failed source/parity gates.

## Reference method and prospective freeze

`waveform_oracle.py`, `axisymmetric.py`, `check.py`, `check_algebra.py` and DERIVATION are exact copies of the already reviewed independent sources; `sources.json` records their provenance/SHA pins. The waveform oracle performs rational arithmetic and explicit integer ties-to-even rounding. The MC oracle uses reduced axial/radial source equations, independent drained plateau/strain decomposition and inverse constant-volume q control, without a spectral/Newton solve. `generate_reference.py` adds a distinct reference identity and exact input SHA binding around unchanged source mathematics.

`pre-input-source-freeze.json` pins the source/policy/checkers before generating caller controls. `prospective-freeze.json` additionally pins the complete new input before either280/360 numerical reference run. Source precision/defect bounds are the original1e-60 normalization; no backend acceptance budget was selected here. Source/checker/input bytes remain unchanged after those freezes. Supplemental corruption/replay checkers were added separately afterward, without altering frozen source, inputs, policy or outputs.

## Results and limitations

Both initial precision runs pass with14paths/834points/820updates:577elastic,147compression-plastic,48extension-plastic,48apex updates. The unchanged checker compares21,711 numeric fields; maximum normalized precision difference is approximately1e-274 and maximum source defect8.89e-280, below the frozen1e-60 bounds. Per-step equilibrium, yield, nonnegative multiplier, complementarity, flow/subgradient, ordering and protocol constraints are checked by the unchanged source generator.

The algebra replay passes12,000 exact rational checks. Adapted input/adequacy checks pass3,883 conditions, including source yield plateaux, both plastic reversal sides, accumulated elastic/plastic volume, constant-volume mean-stress behavior, protocol3 cumulative q, isotropic apex and drained100/200 stress/strain endpoint consistency. In these new finite inputs the exact accumulated-delta minus displayed-control discrepancy is zero at every point; this is a reported input property, not a requirement imposed on arbitrary caller sequences.

Binding checks pass4,782 assertions and reject12 independent input/reference mutations. Supplemental numeric corruption checks reject six altered stress/strain/q/branch/source-defect/shape witnesses. A fresh isolated copied-source replay regenerates the new input and both precision files byte-for-byte. There are no unresolved source cases or reference numerical failures in this bounded packet.

Finite paths do not establish universal numerical robustness, physical calibration, experimental agreement, unique nonsmooth tangents, browser integration, or native/Wasm behavior. The original MC near-apex limitations remain independent. The next step is coordinator review, then a separately frozen collector/assessor using these exact bits and source references before observing production producer/material results.

## Reproduce

Use Python3 with `-B`. No third-party package is required.

- `python3 -B replay.py` performs portable clean-stage input and dual-reference replay.
- `python3 -B check.py reference-p280.json reference-p360.json reference-policy.json` checks precision/source defects.
- `python3 -B check_adequacy.py` checks input/source-law adequacy.
- `python3 -B check_packet.py` checks bindings, exact input semantics and12 corruption probes.
- `python3 -B check_algebra.py` checks12,000 rational identities.
- `python3 -B check_reference_corruptions.py` checks the six supplemental numerical mutations.

The generators intentionally refuse to overwrite outputs. `replay.py` creates a clean temporary tree and checks every frozen dependency before generation. Manifest excludes itself; all exact source URLs and original/current byte identities are recorded without pinning mutable coordination documents.
