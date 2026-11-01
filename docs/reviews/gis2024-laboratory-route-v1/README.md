# GIS2024 laboratory-route qualification

NUM-gis2024-laboratory-route-v1, 1 November 2026. **Native and Wasm pass the
unchanged prospective laboratory/preparation route gates.** This closes Stage A
of the [browser integration plan](../gis2024-browser-preparation-v1/INTEGRATION_PLAN.md).
It does not install the model, qualify the actual browser, establish specimen
preparation, validate experiments or supply independent scientific signoff.

The exact v0.3 candidate is HP/extracted-ASBS+GIS2024,f=0,
`research-hp-extracted-asbs-gis-2024-v03`, from
[Mugele, Stutz & Mašín (2024)](https://doi.org/10.1016/j.compgeo.2024.106480).
The [institutional source](https://publikationen.bibliothek.kit.edu/1000171366/153009465),
[source/formulation ledger](../../ingestion/hypoplastic-generalized-igs-2024/README.md)
and [mixed-catalogue qualification](../gis2024-mixed-catalogue-v1/README.md)
retain publication, selected host, zero-spin conventions and scientific limits.
No model/schema/compiler/runtime source or tolerance was changed here.

## Before observations

The previous plan froze inputs and numerical budgets. `rate-references.json`
adds26 literal independent Cartesian14-component rates: six positive and six
negative Mandel basis directions at1e-6 plus zero, for each of two states.
The first is the unchanged model example: sigma=100kPa I,e=.595,h=0,Omega=0.
The second has the same stress/density and full axisymmetric memory
h=[2e-5,-1e-5,-1e-5,0,0,0],Omega=.25. Both are software examples; neither is a
source-prepared or experimentally calibrated specimen.

All60 laboratory requests were materialized before execution using the existing
exact loading producer. Both preparations span all five protocols, zero loading,
small monotonic loading and one cyclic reversal, each through exact and legacy
routes. Monotonic paths use eight steps and cycles use16. Nonzero amplitude is
1e-5 strain (0.001%) for protocols0/1/2/4, or20Pa signed deviator stress for
protocol3. These limits do not establish accuracy at larger strains or across
the full interactive slider range.

`freeze.json` pins the driver, independent saved-output assessor, literal inputs,
parity comparator and20 passing synthetic corruption tests before compiled
observations. `dependencies.json` pins reused source/reference/plan/artifact
records. Synthetic fabricated trajectories test audit logic only; they are not
constitutive evidence. Acceptance gates were not relaxed after results.

## Executed checks

| Check | Native | Wasm |
| --- | --- | --- |
| Independent instantaneous origin/interior rate comparisons |26 pass|26 pass|
| Complete laboratory requests |60 pass|60 pass|
| Invalid state/geometry requests, no initial commit |8 reject|8 reject|
| Immediate clean recoveries |9 pass|9 pass|
| Forced update-budget failure, full initial prefix retained |1 pass|1 pass|
| Full-state points assessed |581|581|
| Raw descriptor/API receipts |106|106|

The26 instantaneous rate comparisons use absolute+relative component budgets
1e-10+1e-10*abs(reference). Maximum absolute rate error is2.8422e-14 on both
backends; this is instantaneous algebra, not derivative or update-tangent proof.
Every successful point passes finite14-state layout and independent Cartesian
source-domain checks. The audit checks exact zero/hold state, density/volume
closure, initial/history/parameter/settings identities, stress observables,
controller constraints, exact-loading bit echoes, legacy context, stress scope
and pore-pressure assumptions. Maximum absolute volume error is7.7716e-16.

Missing h/Omega layouts, negative e,Omega outside[0,1], memory norm outside R,
zero pressure and nonaxisymmetric initial stress all reject without recording an
initial point. The distinct valid-initialization/update-budget failure records
only its exact complete initial14-state point. Every recovery matches the clean
zero control exactly. No invalid input is clamped, projected or filled.

All581 returned native/Wasm14-state pairs pass the original scaled1e-7 bound;
maximum difference is6.7763e-17. Scales are p_scale for sigma, R for h and1 for
scalars. Exact and legacy cyclic waveforms retain separate arithmetic; no
claim of identical controls across those APIs is made.

The frozen legacy audit checks range/controller/domain/volume/parity. A separately
labelled **post-run** saved-data supplement additionally checks every legacy
control against the unchanged C++ sine/linear expression:280 points/backend,
maximum difference0. Its synthetic corruption check passes. This strengthens
review of actual loading records; it is not retroactively presented as part of
the prospective freeze and it changes no old gate or result.

## Engine reuse, context and reproduction

All three native/loader/Wasm artifact hashes exactly match the previous mixed
catalogue. Native was run and independently accepted before Wasm execution.
**No compilation occurred.** Native calls each use the original CLI in separate
processes; its clean-recovery evidence is cross-process and does not establish a
persistent native global-context check. Wasm keeps one module/process alive for
all106 calls and demonstrates same-context rejection/failure recovery. Within
both laboratory engines, each constitutive trial starts from its own last
committed state; explicit initial/history values are bound in the raw receipts.

```sh
python3 -B docs/reviews/gis2024-laboratory-route-v1/verify.py
python3 -B docs/reviews/gis2024-laboratory-route-v1/test_assess.py -q
python3 -B docs/reviews/gis2024-laboratory-route-v1/test_waveform_review.py -q
```

The verifier checks original/final/source hashes, safely extracts both archives,
binds every raw response to its literal request, replays unchanged backend audits
and parity, recomputes the independent instantaneous references and repeats the
labelled saved-waveform supplement. It does not execute a model binary or ODE.
Both archives contain full results, raw receipts and transport/wire files;
process and engine-reuse records supply acquisition identity. Re-execution needs
a new exclusive directory and prospective identity; preserve this packet.

Next is the separately claimed local draft integration (Stages B/C): exact
candidate installation, pending review and unassessed applicability, preparation
and experiment-matching disclosure, exact engine packaging and actual browser
B01–B12 checks. Wider finite-trajectory accuracy, default larger loading choices,
saturation/boundary arithmetic, source preparation, author algorithm/license
reconciliation, scientific review and experimental validation remain open.
No push, deployment or automatic scientific admission follows from this pass.
