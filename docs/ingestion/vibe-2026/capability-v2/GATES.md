# Prospective generic capability gates v2

Frozen before implementation, generated code, builds or any controlled-time material/backend observations. These qualify generic transport, **not VIBE**. No tolerance may be relaxed after observing failure. Changed reference/policy needs a distinct reviewed study identity with original failure retained. Implementation source hashes and exact compiler/settings are added to the execution freeze before first compiled call, without replacing this design freeze.

## C1 — Contract and dispatch

Accept scalar external values with SI value units and derivative units/s, symmetric Mandel mechanical controls and persistent state derivatives/s. Reject missing/extra controls, stale/missing binding/duplicateorder, wrongshape/unit/rateunit, nonexistent controls, >32controlcomponents, >32statecomponents, invalidparameters/nonfinite/fullstate, relabelled pathclock, temporaryODEstate, `_n`/dt/de and unsupportedkinematics/frame. Reject controlledprofile in alloldexecutionroutes with actionablediagnostic. Validate exact max-capacity fixtures and one-above rejection. Accept net only in newprofile, reject in oldprofile schema/ordinaryconsumer. A zero-duration advance rejects, positive hold evolves where law specifies.

## C2 — Independent exact stage-transport oracle

Synthetic symmetric-stress system, all constants fixed prospectively:

```
sigma_dot = E*strain_rate + I*(A*suction_rate + B*temperature_rate + C*temperature/Tref)
E=2000000 Pa; A=0.3; B=100 Pa/K; C=7 Pa/s; Tref=300 K
sigma0=[10000,20000,30000,4000,-5000,6000] Pa
strain0=[0,0,0,0,0,0]
strain1=[.001,-.0003,.0002,.0004,-.0005,.0006]
suction0=200000 Pa; suction1=350000 Pa
T0=300 K; T1=330 K; t0=11s; duration=4s
```

Independent analytical endpoint: each component `sigma0+E*(strain1-strain0)` plus diagonal `A*(s1-s0)+B*(T1-T0)+C*duration*(T0+T1)/(2*Tref)`. Stage reference at fractional time uses exact linear endpoints and same integrated polynomial. Compute references with Decimal80 or Fraction outside production interpreter/generated code. Check all6components at start,mid,end;1/2/4partitions; varying stage time; controls all6nonzero including offdiagonal permutation; coupledTHM, suctiononly, temperatureonly, allhold4s and oppositeTHMrates. Explicit sign/map tests must show changing only xy does not change yz/xz. Pressure bounds/positive T validation both sides. Baseline finite stress abs tolerance `1e-7 Pa + 1e-12*abs(reference)`; exact time/endcontrols/rates and array layouts. Hold expectation has diagonal `C*T/Tref*duration`, never zero. Exact reference source never imports production numerical equations.

## C3 — Nonlinear/time/branch refinement

Synthetic scalar history `m_dot=-m/2s`, m0=2, exact exponential. State `e_dot=-(1+e)*trace(strain_rate)`, e0=.8, exact `(1+e0)*exp(-trace(delta_strain))-1`. Piecewise scalar field sign branch `b_dot=select(suction_rate>0, +1/s, -2/s)` with separately declared zero-rate branch0; check positive,negative,hold and two-step reversal. Absolute/reference tolerances on dimensionless states: `1e-8 + 2e-7*abs(reference)` at frozen rtol1e-8/atol1e-11 and appropriately declared scale1, with depth40/trial100000. Compare refinement maximumsteps1,.5,.25s using loose rtol1e-2/atol1e-6; require strictly decreasing nonzero endpoint error and last successive ratio between3 and5 for smooth exponential, unless errors already below1e-12 (then report roundoff rather than invent order evidence). No refinement claim across branch discontinuity; split prescribed transition exactly. This establishes method/stage behaviour, not VIBE branch-law choice.

## C4 — State lifecycle and rejection

All persistent scalar/tensor fields nonzero, plus heterogeneous parameters/controls and initial rates. Fresh initialization, repeated trial from same parent, full-context export/import, same replay twice, restart and continuation. Ratejump record checks left/right observables against synthetic instantaneous `stress=sigma+viscosity*strain_rate` while state/control/time identical; restart incoming rate cannot silently becomezero. Allfailures preserve exact parent objects and ABI inputs/outputsentinels: wronglength/nullpointer, wrongmetadata/modelindex, omittedfield, NaN/Inf, noninteger settings, startcontrolmismatch, unrepresentable endpoint, subtraction/rateoverflow, invalid positiveT/domain, failureafterfirsthalf, exhaustedtrial/depth/minstep, failedlateoutputsample. Recovery after every rejection must reproduce unchanged successful reference. Aliasing policy explicitly tested. Initialize with explicit nonzero rates and rate-dependent checks/observables to catch hiddenzero initialization. Evaluateflag rejects outside0/1.

## C5 — Cross-backend and compatibility

Pure Python reference contract/stage tests first. Native then Wasm serial builds/calls after coordinator slot; everyactualrawcase saved. Independent oracle compares allstates/observables/controls/rates/time; native/Wasm/Python agreement cannot replace oracle. Both64bitnative andWasm memory boundary/sentinel checks required. Frozen model+generic source+settings/layout hashes retained. Existing source-pinned ordinary/physicalODE/pathODE generated files must remain byteidentical excluding deliberately versionedmetadata, and meaningful representative existing native/Wasm analytic suites must pass unchanged. Existing path zero-progress identity remains legal; oldtimeABI and oldmixedstressschedule outputs/restarts retain semantics. Newprofile mixedcatalogue rejection mandatory. No oldmodelJSON migration.

## C6 — Actual normal package/browser/live (dependent full-delivery gates)

Package exact approved source/model/module/Wasm/review/approval/profile hashes; execute actual uploadedmodule with C2transport corpus plus independent VIBEsourcecases. Browser mainatlas supports all6mechanicalcomponents+temperature+suction, explicitseconds/initialfullstate/allparams, coupled/mixed/hold/reversal, source/limits/profile, exactcompleteexports/freshreplaytwice, invalid/tamper/recovery, latest-requestcancellation, catalogue/directroutes, mobile390+desktop1280plots/fullstate/readability and no consoleerrors. Existingordinary/timed/path routes preserved. Freeze exactVIBEreferences/acceptance separately before compiledVIBEcases. At release, exactCIallrequiredterminalsuccess +Pagesexactcommit, completepackageasset hashes/livefetchstatus200, actual live browsercontrols/profile/replay; independentreviewer reviews savedfulloutputs andscreenshots. Retain original failures/retries with distinctidentities, no proxy synthetic-only closure of E6–E8.
