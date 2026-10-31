# Clay2013 v0.3 laboratory candidate and prospective consumer study

Task SRC-clay2013-preview-plan; owner clay2013_source_closure;2026-10-31. Source-only packet. **No compiled observations have been made.** Candidate `model.json` is not installed in the runnable root or admitted scientifically.

## Candidate identity and preserved mathematics

ID `hypoplastic-clay-2013` matches the existing catalogue entry. Name declares Appendix law/zero spin and status is `draft`. It represents Mašín2013 author-manuscript Appendix43-58, compression-positive effective Cauchy stress plus void ratio, restricted to infinitesimal3D fixed spatial coordinates at zero spin. It is the same literature formulation as the old research target, not an additional model family.

[Primary DOI](https://doi.org/10.1007/s11440-012-0199-y); [pinned author manuscript](https://web.natur.cuni.cz/uhigug/masin/download/Masin_AG12-pp.pdf), SHA256 `21834ab9da81ec2cdebdf3a3d7f97b691d47bf481a24432bc0562aca9f503281`, PDFpp13-14 Appendix43-58 and p3Eq7. The [source closure packet](../README.md) records actual readable manuscript inspection, publisher HTML Appendix agreement, source/preparation limits and failed publisher-body acquisition. No copyrighted full text is bundled.

`equations`, `derived`, `domain` and `parameters` are **exactly equal as JSON values** to `models/research/clay2013/hypoplastic-clay-2013-research.json`. No bounds, magnitudes, numerical guards, coefficient ordering or examples are altered. The old research definition and receipts remain unchanged. Added metadata records new ID/name/description/source links; v0.3 makes the strain-path, stress/input/state lifecycle and initialization semantics explicit. All seven state components are persistent: symmetric spatial Cauchy sigma6 and scalar invariant void_ratio e. There are no incremental unknowns or physical-time inputs. Explicit stress/e is mandatory; field literals remain examples.

The existing research five soil defaults are30degrees,.12,.025,1.1,.2 for phi_c,lambda*,kappa*,N,nu. They are illustrative software fixtures and **do not equal Table1 `eval.`** (25degrees,.1,.01,1,.2), which itself is fictitious. Fixed p_ref=1000Pa is source normalization; p_scale=100000Pa is numerical error scaling. Project min/max ranges are not universal source/calibration domains. Extra source links cover original research evidence, source closure, initial-state/ASBS policy and precision restrictions.

The domain remains the old numerical policy: stable invariant reduction, double deviator projection, exact-isotropy continuation and rejection of unresolved arithmetic. It does not certify eigenvalue signs arbitrarily near a singular binary64 stress. No arbitrary-SPD accuracy, near-boundary retention, finite rotation, IGS,2014 anisotropy, source-matched specimen preparation, experimental fit or validated zero/near-isotropic update tangent is claimed.

## Prospective literal request matrix

`requests.json` freezes **18 calls/backend**, with literal positional parameter/state/settings CSV and exact expected Boolean outcomes. Recovery annotations are assessor metadata; pass only supported arguments to the actual C ABI/CLI.

- Ten32-increment histories: all five controls, monotonic and one sinusoidal cycle. Start from unchanged research state10kPaI/e=.8; amplitude .002 normal strain for protocols0,1,2,4, and100Pa signed deviatoric stress change for protocol3. These are selected modest software paths; their success is prospective, not established here.
- Actual browser reset/default request: drained1%/100increments/zero cycles,100kPaI/e=.8 and unchanged default parameters/settings. This differs from the research state example because `web/index.html` confinement is100kPa and `web/app.js::valuesForState` builds stress from that control. Keep both cases.
- Exact zero-update; indefinite initial run then identical valid drained recovery; omitted v0.3 state then identical valid drained recovery; negative-density integrate then zero-update recovery. The invalid integrate must return its supplied complete incoming state bitwise. The omitted-state exception need not return a state array; it must reject without example substitution.

The actual browser default is outside ASBS at these examples: pe≈71410.4673Pa and f≈+0.12131194. That is an algebraic diagnostic, **not** a new universal initial-state permission or justification to project the state. Both model10kPa and browser100kPa states pass the explicit declared initializer. A physical preparation claim requires a separately declared source-matched construction/history. If the default compiled request fails, retain the negative result and address the consumer/preparation choice explicitly; do not silently swap the request to the prepared NCL state or lower its amplitude to get a pass.

## Actual APIs, settings and collection

Use current production `cpp/main.cpp` with a frozen generated candidate catalogue. Run calls must use **atlas_run_with_settings** (eight arguments) and integrate calls **atlas_integrate_with_settings** (five arguments), matching the browser's current versioned numerical-settings path. Native CLI uses `--integration-settings` with the same literal six-value CSV. Settings are residual2e-10,rate1e-6,max_iterations45,max_depth14,max_substeps20000,max_backtracks11, matching `settings.hpp` and `web/numerics.mjs`; these are execution settings, not source material constants or global error guarantees.

Before the coordinator observes any compiled response, freeze the actual engine/compiler/schema/main/generated model bytes, requests/policy/collectors/assessor/toolchain and source receipts under a new investigation identity. Keep descriptor then all18 ordered opaque response strings; parse only after journaling. Use one persistent Wasm instance to expose contamination; native calls are separate processes. Duplicate JSON keys, nonfinite values and bool-as-number aliases reject. Bind the complete descriptor, exact candidate bytes/hash, **parameter insertion order**, echoed request/settings and actual catalogue hash. Do not infer descriptor identity from sorted object equality alone. Preserve commands, build/runner stdout/stderr, statuses, artifact hashes, raw failures and assessed summaries. Builds stay serial, one target/job, under the coordinator.

This packet's manifest pins inspected inputs and literal prospective plan; it is not the complete isolated compiled-execution closure. The coordinator must make that separate freeze, including any actual-driver descriptor wrappers needed for collection.

## Acceptance policy fixed before compiled execution

`acceptance.json` is machine-readable policy, supplemented by these explicit independent checks. Failed required gates remain failures; no test selection or budget relaxation after observations.

Every successful run must have steps+1 points, exact supplied initial state with zero control/strain, finite seven-state/six-strain shapes and finite p/q/q_signed/u/control. Check e>=0, p>0 and independently assembled Cartesian stress principal minors>0 as bounded output diagnostics; these floating calculations are not an arbitrary-conditioning positivity proof. Check the full loading curve independently as target*i/steps or target*sin(2*pi*cycles*i/steps), absolute tolerance1e-12*max(1,abs(target)).

At every point independently check incompressible-grain closure `e=(1+e0)*exp(-tr(strain))-1` within1e-6 absolute. Source p3Eq7 supports that density identity; it does not supply an exact stress-history oracle. Check axial strain equals control for0/1/2/4; oedometric radial strain zero; undrained2/3 trace zero; isotropic4 equal normal strains; all with1e-7 absolute strain tolerance. For all axisymmetric cases radial normal strains should coincide and Mandel shear strains remain zero within the same bound.

For drained1, mean radial stress remains its initial value within `.002Pa+1e-8*max(1Pa,abs(initial_radial))`. For stress-control3, `q_signed-q0=control` within `.002Pa+i*1e-8*max(1Pa,abs(initial_radial))` at point i. The i factor recognizes accumulated stepwise stress-control residuals: `controlled_step` solves q change relative to the preceding committed state, while drained control uses the original radial reference. These limits derive from actual solver1e-8 radial-reference stopping scale plus a stated .002Pa arithmetic allowance; they are not a constitutive accuracy bound. A point-count-independent tight q bound could falsely characterize permitted controller accumulation.

Reconstruct p=tr(sigma)/3, q=sqrt(1.5*devsigma:devsigma), q_signed=sigma_xx-(sigma_yy+sigma_zz)/2 and u=initial_radial-current_radial for undrained2/3 (otherwise0), comparing1e-10*max(1,abs(expected)) absolute. Stress controls are mechanical constraints; u is a fixed-radial-total-stress/incompressibility reconstruction, not independent pore-fluid evolution. All physical state/strain/observable/control channels compare native/Wasm at scaled difference `abs(n-w)/max(1,abs(n),abs(w))<=1e-10`. Exclude wall time and work counters from numerical parity.

Zero update and invalid-integrate rollback require all incoming state bits unchanged. Recovery calls require bitwise-identical physical channels to their earlier same-backend baseline, excluding time and diagnostic counts. No expectation of zero residual deformation after a sinusoidal cycle: the constitutive response is dissipative. The prospective request sequence does not force failure after accepted nonisotropic substeps; that stronger rollback study remains separate.

## Source-only validation and retained failure

Run:

```sh
python3 -B docs/ingestion/hypoplastic-clay-2013/preview-plan-v1/check.py --root /Users/bmar5496/code/constitutive-atlas
```

`checks.json` records complete v0.3 validation, exact old mathematical-field equality, catalogue-ID match,18unique requests with all ten control/history combinations, identical recovery inputs and declared initializer acceptance/rejection. Fifteen positive initializations pass; the three invalid initializations reject. This performs **no finite trajectory integration, compilation or compiled calls** and does not establish expected protocol success. No completed rate/isotropic/nonisotropic study is repeated.

The first checker invocation failed an internal dictionary comparison because the baseline `id` had not been excluded while the recovery `id` was excluded. `checker-initial-failure.txt` retains that diagnostic. Correcting the checker to exclude metadata on both sides made the source-only run pass; no candidate, request, acceptance threshold or compiled observation changed.

## Remaining gates and handoff

Files: model.json,requests.json,acceptance.json,check.py,checks.json,checker-initial-failure.txt,README.md,manifest.json. Staged under `/private/tmp/atlas-clay2013-preview-plan-v1/packet/`; coordinator owns copy/review and any actual-driver study.

Required next: independently review candidate identity/source limitations and prospective plan; freeze/execute serial native/Wasm actual production APIs; retain failures; check a complete combined catalogue; render packaged browser selection/default plots/source links. Only after those software checks should a draft enter the public-root catalogue. This does not authorize push/deployment.

Open beyond that preview: full publisher-body reconciliation, calibrated physical initial/preparation history, independent human scientific review, source-matched experiments, nonisotropic late-failure recovery/partition and broader parameter/pressure/boundary precision studies, finite objective transport and general update-tangent support. Current schema supports the named restricted contract without new capabilities; unsupported full-source physics must remain explicitly named rather than inferred from the preview.
