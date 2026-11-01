# Prospective main-laboratory browser qualification v1

Prepared before browser observations. This plan does not claim an actual browser pass. Model: `kelvin-voigt-comsol63-deviatoric-zero-spin-ode`. Browser actions, compiled execution and release verification remain coordinator-owned. Use the isolated packaged site with its real copied common Wasm engine; retain exact source/package/engine identities, exports, console and screenshots. Repeat essential route/default/export checks against the exact successful live deployment.

## Frozen acceptance

Retain failures without overwriting; a changed study gets a distinct identity. Numerical budgets remain absolute3e-8 for six strain states and1Pa for six total stresses, all samples including both initial event sides, over creep/rate/hold:360 scalar comparisons. No numerical result permits relaxing these gates. The separate state/strain transport roundoff allowance is64EPS×max(1,|a|,|b|); it does not replace physical accuracy. Saved/fresh replay remains exact full canonical output. Public v3 solver is rtol3e-11, absolute scale3e-14, budget1000000; retain exact remaining settings from exported request.

`expected-default.json` freezes elementary analytical values for ten points per mode, before actual browser execution. It was generated directly from exp formulas without compiled calls. For default incoming D=(.001,-.0005,-.0005,.0004,-.0002,.0003)/s, K20MPa,G12MPa,tau2s and zero initial strain:

- Creep holds all six incoming stresses=(48000,-24000,-24000,19200,-9600,14400)Pa; ε(t)=2D[1−exp(−t/2)]. At8s εxx=.0019633687222225315. No viscous instantaneous strain jump is expected.
- Constant rate gives ε=tD and σ=24MPa(t+2)D. Initial left/right stresses coincide. At8s stress=(240000,-120000,-120000,96000,-48000,72000)Pa.
- Strain hold starts with the same incoming left stress, immediately sheds viscous stress on the right event and remains at zero strain/stress for this zero-state preset. This is not exponential strain relaxation.

## Route, ownership and layout

1. Enter through the normal catalogue card/Explore link and direct main route `index.html#laboratory?model=kelvin-voigt-comsol63-deviatoric-zero-spin-ode`. Confirm selected model, meaningful model description, approval scope and source links; no standalone page or iframe. Refresh/deep link retains the selected Kelvin profile.
2. Confirm exactly one model workspace owns the visible laboratory. Ordinary plots/controls and incompatible experiment/import controls remain hidden while Kelvin is selected. Readable layout at desktop and narrow width; overflow confined to the full-state table, labels/units readable, no overlaid panels or clipped Run/Reset/Export controls. Screenshot both sizes.
3. Check two response plots have physical seconds and stress kPa/strain% axes, every six Mandel component can be selected, curves update, full table has time, event side, six strains and six stresses at all ten points. Both initial/start events remain distinguishable. Disclosures specify all-six compression-positive Mandel order, small strain, fixed frame/zero spin, dry total Cauchy stress, elastic bulk and instantaneous deviatoric viscosity. No experiment overlay/calibration claim.
4. Open source Eq3-36, exact model JSON, readable independent review, checklist and approval links. Confirm project-prefixed asset routes resolve and review explicitly states bounded synthetic approval. Identity table matches actual package hashes and fetched identity.

## Actual run controls and semantics

1. Run default creep, rate and hold independently. Wait for completed status, export each actual result, verify all360 state/stress scalars against expected-default.json within unchanged gates. Check samples/start/solver/request/full initial state and incoming rate in exported controls and provenance.
2. Select all six plot components; compare curve endpoints to matching table/export columns. Confirm reset restores the complete preset, including all three parameters, six initial strains, incoming six rates, loading six rates, mode, duration, intervals and start, and starts a new history.
3. Exercise each parameter: halve G (creep stress halves, default creep strain stays unchanged); change tau from2 to4 (incoming stress doubles and creep ε=4D[1−exp(−t/4)]); demonstrate K with hydrostatic initial ε=(.001,.001,.001,0,0,0), zero rates and hold: σnormal60000Pa at K20MPa and120000Pa at K40MPa. Restore defaults after each independent run. These are prospective analytical checks, not broad parameter qualification.
4. Exercise all six nonzero initial strains and hold. Example ε=(.002,-.001,-.001,.0004,-.0002,.0003), default incoming D: incoming stress=(96000,-48000,-48000,28800,-14400,21600)Pa; right/late stress=(48000,-24000,-24000,9600,-4800,7200)Pa. All states remain exactly the chosen strain within the physical gate. Initial and loading rates are separate controls: change loading rate alone in rate mode and confirm incoming left stress still uses initialRates while the right event uses new loading rates.
5. Set nonzero start3s with duration8s: ten points start3 and end11; stress/strain relative-time history unchanged. Change output intervals and duration; point count/timing track controls. Custom conditions remain exploratory; failures must display bounded error and preserve evidence.

## Invalid, replay and lifecycle gates

1. Enter bad vector length, nonfinite/invalid JSON, tau0, negative duration and noninteger intervals. Confirm invalid state, no stale plot/export, Run remains usable. Reset then valid completed run demonstrates recovery.
2. Export through the actual button, inspect downloaded JSON kind `atlas-kelvin-voigt-laboratory-v1`, complete controls/provenance/request/result. Import actual file, execute real replay, compare complete output exactly and allow export only after successful replay. Retain both original and replay files.
3. Import duplicate-key, overflow, wrong model/hash/provenance, modified request, truncated state and finite changed later stress. Reject mismatched transport immediately or changed numerical result after real replay; never silently accept edited saved output. Then valid import must recover. No fabricated download or screenshot substitutes for these actions.
4. While a run is pending, change input, rerun/reset, or choose another profile. Latest request only may publish; outgoing worker terminates; no late result restores an inactive workspace or enables its export. Repeat while asynchronous imported-file read/identity fetch is pending where browser automation permits deterministic delay.
5. Switch Kelvin to/from each installed ordinary/timed/J2/SLS/Maxwell/Burgers/explicit-path/implicit-path profile, including same-model reselection; validate model header, exactly one active panel, exports and successful real runs on returned profiles. Use actual available installed controllers rather than assuming list membership. Retain directed transition matrix. Confirm pending ordinary worker/experiment/import callbacks cannot replace Kelvin plots/header, and pending Kelvin callbacks cannot replace the next workspace.
6. Observe console across actual runs/navigation/import; unexpected errors/warnings fail until investigated. Worker constructor/postMessage fault cleanup is covered by pure fakeWorker tests; if platform injection is unavailable in the actual browser, label that limitation explicitly rather than inventing a browser pass.

## Evidence and closeout

Save exact controls and all three actual exports, comparison report with360 counts and maximum errors, tested package hashes, route/transition observations, invalid/replay artifacts, console, desktop/mobile screenshots and exact browser URL. Check offline evidence reproducibly. Model approval, current-build qualification, browser functional qualification and exact live deployment remain separate claims. E8 requires successful exact-source CI/Pages deployment plus actual served-asset equality and live Kelvin execution/export; this prospective plan alone closes no stage.
