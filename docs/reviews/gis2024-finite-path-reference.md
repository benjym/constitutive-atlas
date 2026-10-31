# GIS2024 strictly interior finite-path reference

Draft numerical diagnostic,31 October2026. This packet supplies independent fixed-step path references for a later comparison with the isolated full14-state common engine. It executes no common solver, native code or Wasm and admits no model to the public catalogue. It does not establish material preparation, author-code equivalence, calibration, experimental validity or independent human scientific review.

## Constitutive dependency and source

The generator `tools/gis2024_path_reference.py` uses only the Python standard library plus `tools/reference_gis2024_coupled.py` as its constitutive dependency. That independent Cartesian coupled rate imports its own stdlib Cartesian/dense HP host; both dependency files are hashed. The generator imports no Atlas DSL, production material law or numerical integrator. It adds classical RK4, tensor rotation, endpoint bookkeeping and diagnostics; it does not recode or adjust the material equations.

The pinned primary source is Mugele, Stutz and Mašín(2024), *Generalized intergranular strain concept and its application to hypoplastic models*, DOI [10.1016/j.compgeo.2024.106480](https://doi.org/10.1016/j.compgeo.2024.106480), [institutional PDF](https://publikationen.bibliothek.kit.edu/1000171366/153009465), SHA256 `39ec8356a26b82ae651be8feb4cdb3e49bb86ded9a850adc4c7eee5e9ec3bdc3`. Source locators: p3 Eqs8-12 and p4 Eqs26-32 for the selected extracted-ASBS host, p5 Eq33/p6 Eqs34-35 for memory, p6 Eq39 for k, p7 Eqs40-43 for coupled rates and Omega, p12 AppendixB for HP. This packet relies on the previously reviewed source-rate extraction; it is not a fresh full source audit. No copyrighted source is bundled. The source receipt is pinned metadata; the private original PDF was hash-verified during packet preparation, not required on every replay.

The selected host uses fdAstar from current-state substitution in source Eq31, C=norm(B)*fdAstar and S=fd/fdAstar, with explicit f=0. It is distinct from S=Y,C=1. Compression-positive stress/strain/memory signs are those of the reviewed independent rate. Spin is zero.

## Contract and paths

JSON contract: `gis2024-independent-cartesian-path-reference-v1`. Each case has `input:{id,initial:[14],increments:[[6],...],parameters:{18}}`, its canonical input hash, and three grids. Each grid retains every caller-segment endpoint as `{segment,state:[14]}`, including segment0 initial state, along with stage diagnostics and exact volume residuals. State order is sigma6,e,h6,Omega. All symmetric six-vectors use Mandel xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz; stress is Pa. Each prescribed full6 strain increment is constant over its own normalized coordinate0..1, so the RHS strain direction equals that full increment. This coordinate is not physical time.

Two distinct paths and their oblique rotated companions are included. The noncoaxial path has three different full6 directions with volumetric and shear components. The shear-reversal path changes sign at a caller-segment boundary, followed by another mixed shear direction. It is a dissipative load history, not an elastic-return test. Both begin from stress `[180000,100000,70000,12000,-8000,4000]`Pa,e=.595,memory `[2e-5,-1e-5,.5e-5,.8e-5,-.4e-5,.3e-5]`,Omega=.25. These are explicit software fixtures, not inferred experimental preparation. Every case repeats all18 physical parameters; there is no hidden default state, scale, endpoint projection or memory reset. The full inputs are retained in the JSON and generator.

The orthogonal oblique rotation is applied to both stress and memory and to every prescribed strain tensor; scalar e/Omega remain unchanged. A fixed rotation checks material covariance, not objectivity under finite physical spin. Four cases therefore comprise two distinct physical paths with two frame companions, not four independent physical calibrations.

## RK4 and stage domains

Each caller segment is integrated by classical RK4 with16,32,64 equal steps, retaining the same direction at all stages. Every stage and each segment endpoint calls the independent coupled-rate domain checks. The diagnostic additionally requires strictly positive e/pressure/S/fdAstar, positive memory radius gap1-rho, nonzero rho and0<Omega<1, recording their minima. This deliberately excludes both boundary/saturation starts and the memory origin from this particular smooth-reference packet; it does not declare them invalid source states. It retains the independent rate's bounded positive-parameter/HP domain, without adding a physical tensile-stress policy.

Each grid records3*(4*n+1) constitutive evaluations, including an explicit final-domain evaluation per segment. Per-segment q minima/maxima report whether a loading-branch sign change was observed. For these fixtures every sampled stage stays on the same loading/unloading branch within a segment, well away from q=0. The reversal occurs exactly at a segment boundary. This supports use of fourth-order refinement diagnostics for these smooth segments. Stage sampling/domain checks do not constitute a rigorous continuous-domain enclosure or proof that no unsampled event is possible.

All grids have radius gap above.713 and rho above.20; Omega remains about0.25..0.25079. All source/selected-domain evaluations succeed. These generous interior margins avoid the known interaction between an accepted floating-point memory-radius margin and strict Omega>=0. They do not resolve that boundary integration policy. The reference itself enforces strict radius and strict interior Omega; no norm margin, clipping or projection is introduced.

## Observed numerical evidence

Separate coarse/fine maximum absolute differences are retained for stress(Pa),e,h,Omega. For these inputs,32→64 differences range approximately:

- stress:1.14e-9..2.86e-8Pa;
- h:5.36e-16..2.50e-15;
- Omega:1.28e-14..8.05e-14;
- e:0..2.22e-16, already at floating-point scale.

Observed difference ratios for stress,h,Omega lie about15.58..16.13, consistent with fourth-order refinement on these selected smooth paths. e ratios are not evidence of temporal order. Fine-difference/15 is retained as a **conditional smooth fourth-order Richardson estimate**, not a rigorous error bound. No hard global reference uncertainty is invented. Endpoint errors should be judged against the observed inter-grid changes, covariance residual and numerical scale, and refined again if a future comparison reaches that floor. The true source/transcription uncertainty is not bounded by numerical refinement.

The exact density relation `1+e=(1+e0)*exp(-sum(trace(increments)))` is checked at all grid endpoints; maximum residual is2.22e-16. At64steps, oblique rotation discrepancies are at most1.17e-10Pa in stress,7.29e-20 in h and zero observed e/Omega. These are finite floating-point results, not exact-arithmetic identities or backend parity claims.

Eight pure-Python test groups cover explicit matrix/hash identities, groupwise three-grid refinement, all recorded stage margins/branch signs, exact volume evolution, covariance in all state groups, Cartesian/Mandel rotation and input isolation, selected boundary/invalid step rejection, and source-bound retained-reference replay with explicit per-channel roundoff allowances. Source/protocol/input identities remain exact; current convergence and domain diagnostics are recomputed. A different Python/libm result may change last bits. The production-study gate uses an exact fresh local replay; archived reassessment binds the historical receipt and evaluates numerics against the current independent oracle.

## Reproduction and downstream gate

From the repository root after installing the staged paths:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m tools.gis2024_path_reference --output catalogue/investigations/gis2024-path-reference-v1/reference.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_gis2024_path_reference.py -v
```

The evidence JSON binds source, exact case inputs and generator/coupled/HP dependency hashes. The manifest additionally binds documentation/tests/evidence and records the reference's observed margins and limits. No source PDF is distributed.

The next common-engine comparison must supply every state and parameter explicitly, preserve all14 channels, fix caller path ordering, chain requests from actual returned committed states, and compare every segment with the independently chained reference. Stress,e,h,Omega need separate physical/numerical tolerances, complete native/Wasm provenance, validated request/response identity, actual substep coverage and strict reference replay. Local solver tolerances are not global error guarantees. Broad acceptance bounds must be reported beside actual component errors. Successful-path agreement does not establish failed-step rollback or persistent-state isolation.

Still unresolved: full-memory and Omega endpoints, zero/tiny memory norm behavior, within-segment loading-branch crossings, large paths and source-domain exits, pressure/density/parameter sweeps, exact native/Wasm integration/refinement/transaction behavior, author implementation reconciliation, source preparation/calibration and experimental/human scientific review. Public/scientific admission is unchanged. These smooth interior references provide a bounded next numerical comparison, not a workaround for boundary-domain policy.
