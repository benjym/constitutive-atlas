# Original Cam Clay: one smooth undrained reference

1 November 2026. **REF-occ-undrained-smooth-v1** adds a separately integrated source-constraint reference for the next Original Cam Clay implementation step. All three resolutions pass the [prospective policy](prospective.json) unchanged. This is mathematical verification authored in the project, not independent scientific review, a general constitutive update or experimental validation.

## Source and scope

The existing [dossier](../README.md) pins a readable2005 electronic transcription of Schofield and Wroth's *Critical State Soil Mechanics*. Its [university-hosted source](https://fme.hcmuaf.edu.vn/data/critical_state_soil_mechanics.pdf) is SHA256 `638e0ee7dc238ae8922b79983433be7d12ad30450098efe395968f7eeed13cb2`; authenticated1968 print fidelity remains open. Printedpp95,99,103 were visually rechecked for this task. No source PDF, text extract or page image is redistributed.

The fixture uses the earlier dossier's illustrative parameters and analytical virgin-undrained prefix. It starts at epsilon_s=.002 and ends at .03, on positive-q wet-side compression. It never numerically traverses the hydrostatic vertex. The specific volume is held constant by the imposed undrained infinitesimal control; it is not independently integrated. Parameter values and preparation are diagnostic choices, not a source soil calibration.

## Independently integrated constraints

The retained Chapter6.30–6.31 analytical helper supplies only initial state and pointwise comparison targets. The new RK4 path evolves p, q and c=ln(pc/p_ref), rather than evaluating that trajectory formula at each step. Source6.7 makes recoverable shear strain zero, so total distortion equals plastic distortion here. With prime denoting derivative per positive distortion increment, set D=M-q/p. Undrained volume balance and packing hardening give

```
p' = -v p D / kappa
c' = v D / (lambda-kappa)
f = q + M p [ln(p/p_ref)-c]
f_p = M [ln(p/p_ref)-c+1]
q' = M p c' - f_p p'
```

The last equation imposes differentiated yield consistency. At intermediate RK stages, f_p uses its literal logarithmic form; substituting the on-yield value D off the surface would be a different numerical extension. This continuation and classical RK4 are declared project choices, not a claimed original finite-step algorithm. Every stage requires finite positive pressure/volume and `0 < q/p < M`. No stress projection, finite shear stiffness, corner smoothing or critical-state substitute is used.

## Frozen result

Maximum scaled state error is the largest p/q error divided by100000Pa or dimensionless c error across every grid point. Yield residual is scaled by100000Pa. Acceptance bounds and16/32/64steps were written before the first integration of this named fixture; no bound changed after observation.

| Steps | Maximum scaled state error | Maximum scaled yield drift |
| ---: | ---: | ---: |
| 16 | 3.12585827e-06 | 3.98552868e-06 |
| 32 | 1.80769729e-07 | 2.28737823e-07 |
| 64 | 1.0864288e-08 | 1.37007989e-08 |

Adjacent error improvements are17.29 and16.64, consistent with fourth-order convergence over this finite interval. All115stored points are retained in [results](results.json); packing-identity drift is diagnostic, not an additional retrospective acceptance gate. The work/dissipation residual stays below1.46e-16 on the declared scale. This checks the selected numerical reference, not the original code or arbitrary strain controls.

[Six tests](../../../../tests/test_occ_smooth_reference.py) cover the frozen result, hardening corruption, path completeness/order, undrained state changes, excluded vertex/critical states and invalid inputs. The [v0.3 crosswalk](schema-crosswalk.md) records the still-unselected full executable profile and constrained-shear/3D gaps.

```sh
python3 -B docs/ingestion/original-cam-clay/smooth-reference-v1/reference.py --output /private/tmp/occ-smooth-reference.json
python3 -B -m unittest tests.test_occ_smooth_reference -v
```

No native/Wasm build or call, shared-engine change, model admission or deployment occurred. Next: resolve the source-edition and complete closure/corner decisions before freezing any production finite-update study. This reference must not be counted as another browser model or a complete3D formulation.
