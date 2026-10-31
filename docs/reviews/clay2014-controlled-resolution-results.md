# Controlled hydrostatic resolution: native and Wasm results

The separate frozen controlled-resolution experiment passes in both backends.
Each backend returned315 chained updates plus one descriptor, and every update
used exactly two half-step fractions with zero rejected recursive steps. All
caller accuracy gates and all18 physical-endpoint contraction inequalities pass.
Native/Wasm states and actual parents are identical in the retained observations.

This establishes a bounded numerical mechanism: refining the effective midpoint
mesh produces approximately second-order endpoint convergence on this isotropic
hydrostatic reversal path. It does not establish that merely tightening an
adaptive tolerance changes the mesh, and does not change the outcome of the
[original failed study](clay2014-path-results.md). Source discrepancies,
anisotropic trajectories, preparation, material-axis transport, scientific review
and experimental/public admission remain open.

## Frozen design and execution

The [analytical protocol/reference](clay2014-controlled-resolution.md) was frozen
in local commit `f1bcf2c`; collectors and the corruption-tested assessor were
frozen in `b7c3774`, before the new compiled observations. The source model,
solver, default settings and reference gates were unchanged. Existing native and
Wasm artifacts matched their exact prior build-receipt hashes before and after
collection. Execution was serial, native followed by Wasm; no rebuild occurred.

Every resolution starts from the original parent and chains actual returned
states. Dyadic subdivision preserves every original caller-piece loading sum
exactly. The analytical references solve the scalar original initial-value
problem at90/140-digit precision, with empirical precision and binary64 rounding
receipts. Observed state differences are separate from those reference receipts;
the latter are not rigorous error bounds.

## Results

The table shows stress Frobenius errors at the three physical endpoints, in Pa.
All quantities refer to the original fixed stress scale173205.08075688774Pa.

| Subdivision factor | Calls | Endpoint1 | Endpoint2 | Endpoint3 |
| --- | --- | --- | --- | --- |
| 1 | 21 | 0.05436738 | 1.89101329 | 1.92966074 |
| 2 | 42 | 0.01360797 | 0.46925325 | 0.47882468 |
| 4 | 84 | 0.00340402 | 0.11687834 | 0.11925996 |
| 8 | 168 | 0.00085126 | 0.02916537 | 0.02975937 |

Absolute void errors at the same physical endpoints:

| Subdivision factor | Endpoint1 | Endpoint2 | Endpoint3 |
| --- | --- | --- | --- |
| 1 | 1.01415654e-9 | 7.18203608e-10 | 8.41908099e-10 |
| 2 | 2.53477794e-10 | 1.79477211e-10 | 2.10399476e-10 |
| 4 | 6.33617603e-11 | 4.48601156e-11 | 5.25900434e-11 |
| 8 | 1.58394409e-11 | 1.12136966e-11 | 1.31462619e-11 |

The maximum error across all315 caller points is1.9296607433Pa in stress and
1.0141565366e-9 in void ratio. Both backends give the same figures. The18
contraction comparisons use the predeclared .35 successor factor plus fixed
floor/reference allowances. Their exact values, signed errors, every state,
actual parent and accepted fraction are retained in the assessments.

## Retained evidence and replay

The [result manifest](../../catalogue/investigations/clay2014-controlled-resolution-v1/manifest.json)
pins both raw journals, observation receipts, assessments, parity result,
pre-observation freezes and this review. It also pins the original failed-study
manifest so that the relationship remains explicit. The unbundled executable
artifacts are identified by exact historical build receipts; portable replay does
not reopen them or run compiled code.

Run `python3 -B -m unittest discover -s tests -p 'test_clay2014_controlled*.py' -v`
for reference regeneration, synthetic corruption tests and fresh assessment of
both retained journals. To assess a journal independently, run
`python3 -B -m tools.clay2014_controlled_study --receipt catalogue/investigations/clay2014-controlled-resolution-v1/native.json --transport catalogue/investigations/clay2014-controlled-resolution-v1/native.transport.jsonl --output /private/tmp/new-controlled-native-assessment.json`.
Use the corresponding `wasm` filenames for that backend and a fresh output path.

Future work should address the remaining full-matrix/source/preparation gates.
This hydrostatic follow-up cannot supply that evidence by extrapolation.
