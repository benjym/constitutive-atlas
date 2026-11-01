# Kelvin–Voigt COMSOL 6.3 — source and contract packet v1

Task ID: ING-kelvin-voigt-comsol63-v1  
Owner / date: kelvin_ingestion, separate source worker / 2026-11-02  
Scope: source acquisition, explicit declarative candidate and independent analytical checks only. The coordinating parent owns the [delivery ledger](../DELIVERY.md), implementation/builds, review, catalogue/browser integration and E4–E8. This packet does not close the full delivery assignment.

## Identity and sources

Exact identity: COMSOL AB, version **6.3**, ordinary isotropic Kelvin–Voigt spring and dashpot in parallel, **deviatoric viscosity with purely elastic bulk**, infinitesimal strain and fixed spatial frame/zero spin, dry total stress, without inelastic strain, initial stress offset or fractional derivatives. The documentation page does not assert a publication year or DOI; neither is invented. This is distinct from generalized Kelvin–Voigt elements in series, Burgers, Maxwell and the Standard Linear Solid.

Primary readable sources:

- [Linear Viscoelasticity, Kelvin–Voigt section](https://doc.comsol.com/6.3/doc/com.comsol.help.sme/sme_ug_theory.06.029.html#3441080): Figure 3-4, Eq3-36 / anchor3441129 / image074, eta=tau G / anchor3441131, no auxiliary DOFs / anchor3441130, dissipated power / anchor3960090 / image075. Opening isotropic elasticity and conventions: images002–004,008–010, anchor3440835.
- [Viscoelasticity settings](https://doc.comsol.com/6.3/doc/com.comsol.help.sme/sme_ug_solid.07.016.html#4898977): Kelvin–Voigt, anchors4898977–4898981; select Deviatoric and ordinary derivatives; relaxation time in s or viscosity in Pa s.

[source-receipt.json](source-receipt.json) records every original file URL, exact SHA-256, size and durable private path. The original HTML and actual equation images are retained under ignored `.local/private-sources/kelvin-voigt-comsol63/`. Existing durable SLS originals were copied without modification; only missing Kelvin figure/equation images073/074/075 were acquired, using actual URLs read from HTML. Equation images074/075 and elasticity/sign images were visually inspected with white-background enlarged private derivatives; originals remain unchanged. Downloads filename search returned no kelvin/comsol/voigt match. Sandbox DNS failure and successful approved HTTPS retry are retained in the receipt. No vendor code or binary was executed.

Copyright remains COMSOL's. Original HTML/figures are private, without an asserted right to redistribute. This public packet contains mathematical transcription, source locators and independent project analysis, rather than original vendor images or text. Numerical parameter values below are illustrative and are not vendor material data.

## Existing work and gaps

The [existing synthetic fixture](../../../../tests/fixtures/time/kelvin.json) is `test-kelvin`, schema0.2, with persistent elastic stress; it is engine verification, not an approved source model, and remains unchanged. The [timed schedule API](../../../TIMED_SCHEDULES.md) already describes Kelvin ramp/creep and rate-dependent transition semantics. The [SLS source receipt](../../sls-comsol63/source-receipt.json) contains the same version's primary elasticity/conventions, but SLS has a distinct branch-memory law. This packet creates a new source-linked identity and six-component strain state, without migrating or changing those records.

No unresolved source equation or convention gap remains inside the explicitly restricted identity. Native/Wasm qualification, scientific admission, public UI qualification and live delivery remain parent-owned work. Broad parameter extremes, finite strain/spin, volumetric viscosity, thermal/coupled behavior and experimental validation are unqualified.

## Equations and schema crosswalk

Target: [schema v0.3](../../../../schemas/model-v0.3.schema.json) and [formulation contract](../../../FORMULATION_CONTRACT.md). [candidate.json](candidate.json) declares every convention explicitly and has no legacy top-level integration field. [crosswalk.json](crosswalk.json) provides machine-readable mappings and limitations.

In source tension-positive Cartesian tensors, the viscous branch is

`σ_q = 2η ε̇_d = 2Gτ ε̇_d`, `η=Gτ` (Eq3-36).

Elastic stress is `K tr(ε_el)I + 2G dev(ε_el)` (image010); the branch is parallel and contributes additively. With no inelastic strain or offset, ε_el=ε. Under the joint convention conversion `ε_Atlas=-ε_source`, `D_Atlas=-ε̇_source`, `σ_Atlas=-σ_source`, the same positive-coefficient law results:

`ε̇ = D`

`σ = K tr(ε)I + 2G dev(ε) + 2Gτ dev(D)`.

Both stress and strain compression are positive. The source convention follows `p=-tr(σ)/3` and `p=-K tr(ε_el)` (images003/008); these are jointly converted, not interpreted as compression-positive source σ. Mandel order is `[xx, yy, zz, √2xy, √2yz, √2xz]`. Consequently engineering shear γ_xy=√2 ε_M,xy and physical shear stress σ_xy=σ_M,xy/√2, giving σ_xy=Gγ_xy+η γ̇_xy. The Mandel Euclidean contraction equals the Cartesian double contraction.

| Source locator | Equation / quantity | Schema representation / units | Status / ambiguity |
| --- | --- | --- | --- |
| Eq3-36 image074 | viscous stress 2Gτ ε̇_d | rate-dependent Pa `stress` observable | exact transcription with joint sign/basis conversion |
| image010; opening incompressible viscosity statement | elastic bulk and shear | `K` and `G`, Pa; elastic bulk only | exact selected isotropic deviatoric variant |
| anchor3441131; settings4898980 | eta=G tau | `tau`, s; eta derived, Pa s | source relation; no separate redundant eta parameter |
| anchor3441130 | no auxiliary strain DOFs needed | sole persistent symmetric `eps` state, six dimensionless entries | total strain retained by Atlas to supply elastic stress; no phantom q/gamma/history |
| image075 | dissipated power σ_q:ε̇_d | diagnostic relation 2Gτ dev(D):dev(D), Pa/s | independent energy check only, no production energy observable claimed |
| images002/003/008 | source tension-positive σ/ε, positive compressive p | explicit Atlas compression-positive σ and ε | simultaneous negation preserves law and work |
| source elastic strain definition and no geometric nonlinearity | infinitesimal strain | small_strain_3d, fixed_spatial, objective_rate none | restricted Cauchy realization; source's geometrically nonlinear second-Piola/Green branch excluded |

Parameter declaration order is **K,G,tau**, defaults **20MPa,12MPa,2s**; derived eta=24MPa s. Positive bounds `[1e-12,1e30]` in each SI unit are project representational limits, not a physically or numerically qualified envelope. The parent must freeze and qualify its actual parameter scope. The source supplies units and relation, not these project defaults/bounds. K>0,G>0,tau>0 enforce passive positive elasticity/viscosity; the degenerate tau=0 elastic limit is analytically meaningful but outside this selected strictly positive parameter record.

The state `eps` is persistent `infinitesimal_strain`, a symmetric spatial tensor under passive orthonormal re-expression, scale1. It is **not** constrained to be deviatoric. Initialization requires all six explicit finite components, all three parameters, finite physical time and all six finite prescribed stage rates. Zero eps is an example, not a preparation rule. An arbitrary explicit eps0 determines elastic stress; initial total stress also needs D0. A stress-only initial condition cannot uniquely substitute for missing strain/rate, and no inverse preparation or initial stress offset is inferred. There are no temporary states, branch choices, resets, yield constraints or hidden internal variables. The total-stress Cauchy observable is dry; no pore pressure conversion or effective-stress overlay is provided.

## Temporal integration and transactions

This is a physical-time ODE, in seconds, with the kinematic equation epsdot=D and a rate-dependent algebraic stress output. `time` is finite and sampled at stages, although the autonomous material formula does not use its value. Every stage requires all six Mandel D components in 1/s. Advancement declares finite start_time and positive finite duration, with a representably later endpoint required by the common driver. No strain-path fraction or finite increment is substituted for time.

For a piecewise constant D, eps(t)=eps0+(t-t0)D exactly; stress grows affinely while the rate stays fixed. A strain-rate jump leaves eps continuous and causes a finite viscous stress jump `2Gτ dev(D_right-D_left)` at the same time. A zero strain rate removes viscous stress immediately, then the elastic stress remains constant throughout a strain hold. There is **no Maxwell-like stress relaxation during a strain hold**. Pure volumetric loading has no viscous contribution. Under constant deviatoric stress s and zero initial deviatoric strain, eps_d=s/(2G)(1-exp(-t/tau)); stress hold therefore permits creep and does not mean D=0. The ideal strain step would require a rate impulse; it is outside finite rate/duration controls.

The source establishes the law, not Atlas numerical lifecycle policy. Under the common [time API](../../../TIME_ODE_API.md) and [schedule contract](../../../TIMED_SCHEDULES.md), every trial starts from the same committed complete state. Success commits state and time; failure restores incoming state and clock, without clipping/projection. Schedule output-interval failure preserves earlier committed samples, including any successfully committed entry transition. Restart requires state, accumulated strain, endpoint rate, time and parameters; state alone does not determine total stress. Parent trial/commit/rollback tests must qualify the actual transport rather than assume source equations establish these properties.

Discontinuities must be split into explicit segments; the existing schedule records left/right entry values at a shared physical time and uses rate-dependent algebraic solves for stress controls. Stress-controlled transition rates may be null by transport convention even though the viscous law constrains deviatoric rate. A fully stress-controlled volumetric mode has algebraic elastic stiffness but no viscosity; its admissibility and solvability are host/driver responsibilities. The parent freezes actual mixed-control histories, samples, step settings, tolerances and rollback/replay gates before compiled observations.

There is no material Newton solve for prescribed rates. The instantaneous constitutive derivatives are elastic stiffness with respect to eps and `2Gτ` times the deviatoric projector with respect to D. The latter has a zero volumetric eigenvalue; no general invertible viscous compliance is implied. Common-driver differentiation may use its normal AD; no finite-time consistent tangent, finite-rotation adapter, event locator or stress-control capability is created by this candidate. No shared schema/compiler/runtime capability change is requested by the source transcription.

## Independent checks

[reference.py](reference.py) uses 3×3 Cartesian Lame spring/dashpot equations and an integrating-factor solution, importing only math. It does not import Atlas, DSL parsing or generated kernels. [check_algebra.py](check_algebra.py) establishes nine groups: 100 Cartesian/Mandel/work cases; joint sign reversal; free-energy balance and nonnegative dissipation; all-six constant-rate solution; hydrostatic zero viscosity; engineering-shear factors; all-six creep; arbitrary-initial-strain stress ramps; and fixed-strain rate-jump/hold behavior. The energy identity is σ:D = d/dt[0.5K tr(eps)^2 +G dev(eps):dev(eps)] +2Gτ dev(D):dev(D).

[check_candidate.py](check_candidate.py) separately loads/validates the exact v0.3 candidate, checks standalone maker reproducibility, evaluates the common Python interpreter against the Cartesian oracle for120random states/rates /720stress components, and verifies23explicit initialization rejections followed by intact-parent recovery. Maximum absolute stress difference is1.1641532182693481e-10Pa, below prospective 2e-8Pa absolute /1e-12 relative component gates. The fixed-strain rate-jump expected values are96000→48000Pa in σ_xx, with unchanged eps_xx=.002. Oracle agreement and source checks are distinct from backend parity.

Reproduce from repository root:

```sh
python3 -B docs/ingestion/kelvin-voigt-comsol63/source-v1/make_candidate.py
python3 -B docs/ingestion/kelvin-voigt-comsol63/source-v1/check_algebra.py
python3 -B docs/ingestion/kelvin-voigt-comsol63/source-v1/check_candidate.py
python3 -B docs/ingestion/kelvin-voigt-comsol63/source-v1/check_packet.py
```

Saved [check-results.json](check-results.json), [candidate-check-results.json](candidate-check-results.json) and [packet-check-results.json](packet-check-results.json) retain exact checks. Scripts refuse to silently overwrite a differing result. [reference-cases.json](reference-cases.json) contains exact mathematical reference samples and proposed public histories, not observations of any compiled solver. Parameters/tolerances are frozen before parent compiled qualification; parent production verification has its own independently reviewed study identity. No compiled/native/Wasm/vendor execution, experimental match or calibration is claimed here. No algebraic check failed. The bounded source-download DNS failure is preserved in source acquisition history.

## Handoff

Public preset proposal: finite deviatoric rate `[.001,-.0005,-.0005,0,0,0]` for2s; zero-rate hold2s; reverse rate2s; zero-rate hold2s. At first end eps=[.002,-.001,-.001,0,0,0], stress=[96000,-48000,-48000,0,0,0]Pa; immediate first hold right stress=[48000,-24000,-24000,0,0,0]Pa. This visibly demonstrates finite rate jumps and elastic hold, with all six controls available. A second stress-ramp/creep example may use the source-derived integrating-factor references; the parent owns the precise mixed-control UI request and qualification.

Exact owned public files are listed and hashed by [manifest.json](manifest.json). Private originals remain ignored. No shared files, model fixture, approval registry or compiler were changed. The smallest next action is parent E2–E4: copy the unchanged candidate into its approved whitelist, freeze actual native/Wasm requests and comparisons (including all-six rates, hydrostatic and shear channels, holds, creep, rate jumps, invalid controls, rollback/recovery/restart), qualify common generated execution serially, then arrange separate-agent scientific checklist review. Approval follows that review, not this worker's assertions.

Status: **source-complete for the stated restricted variant**; **declarative validation and bounded independent Python verification pass**; **native/Wasm qualification not performed by this worker**; **scientific admission pending independent review**; **atlas/browser/live delivery pending parent integration**. No unresolved source blocker or new generic capability request was identified.
