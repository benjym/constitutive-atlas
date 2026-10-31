# Full-path Terracotta preparation and captured-stress hold reference

REF-terracotta-preparation-hold-v1; 2026-10-31; worker `terracotta_journal_source`. Source-only mathematical reference for the simplified Figure1 variant, **not** a new scientific admission or source-complete transcription. The original nine-case prepared-creep evidence is unchanged. No Atlas module, author implementation, compiled solver or prior reference generator was imported or executed. All code here uses Python's standard library.

**Use `refinement-v2/references.json` as the passing reference candidate.** Root-level `references.json` and `checks.json` retain the original failed convergence study. They must not be silently substituted for the passing candidate. Both have their original producing source and pre-observation freeze.

## Source and formulation identity

Equations were independently written from the visually inspected [pinned author equation image](https://github.com/MaxWiebicke/Terracotta-pq/blob/a4039d0124d8ff61e766f5201f44ddc163c4cff5/images/theModel.png), SHA256 `e019012545c5fb0bb80c8f95bad68d35f458c9094ea471d8f42616a170dcc071`. The rounded kaolin preset comes from the [pinned author example](https://github.com/MaxWiebicke/Terracotta-pq/blob/a4039d0124d8ff61e766f5201f44ddc163c4cff5/code/Terracotta_main.py), SHA256 `62c45ae3ba7d556956e4e29d940371a5f1a39b8feeb0d1a0c59db80fbe44a888`, lines12–25. Full source URLs, locators and hashes are embedded in each reference. Raw images and author code are not redistributed.

Journal identity remains [Wiebicke & Einav2024, JMPS192,105789](https://doi.org/10.1016/j.jmps.2024.105789). Journal page-image, strictness and calibration reconciliation remain unresolved. The unhalved image temperature equation is used; the known author mixed-control routine halves it. This study neither executes nor reproduces that routine, its BDF discretization or its outer-partition strain acceleration. AppendixB is excluded.

New-work schema target is **v0.3**: `physical_time`, `ode`, `axisymmetric_x`, `fixed_spatial`, objective rate `none`, Mandel tensor encoding, compression-positive stress/strain, algebraic observable `stress` with total-stress binding. Explicit stage time/rate and advancement start/duration are required. Four persistent material states are `(ev_e,es_e,Tm,phi)`, units `(1,1,K,1)`; elastic volumetric strain/Tm/phi are scalars, signed axial shear is fixed-component. The initial state is explicitly supplied, never inferred from a browser default. No existing record is migrated here.

## Independent equations and dimensions

Let `(v,s,T,f)` denote the four states and `(Dv,Ds)` the signed invariant rates. Fixed-axis axial/radial tensor components are `Dxx=Dv/3+Ds`, `Dyy=Dzz=Dv/3-Ds/2`; all shears vanish. The same map produces accumulated strain from its two integrated invariants. The signed stress reconstruction is `sigma=pI+q*diag(2/3,-1/3,-1/3)`, so power is `pDv+qDs`.

The independent implementation evaluates:

- `pe=f^6*(K*v^2+3G*s^2)/2`, `qe=3G*f^6*v*s`, `pc=p1*f^Lambda`.
- `a=sqrt(eta/alpha)`, `b=-a*qe/(M^2*pe)`, `c=sqrt(eta/gamma)/(M*omega)+a/M^2`.
- `v_dot=Dv-T*(a*pe+b*qe)/pc`, `s_dot=Ds-T*(b*pe+c*qe)/pc`.
- `T_dot=alpha*Dv^2+gamma*Ds^2-eta*T^2`, `f_dot=f*Dv`.
- `p=pe+(2alpha*T*Dv+T^2)/Gamma`, `q=qe+2gamma*T*Ds/Gamma`.

Intrinsic K/G,p1 and stresses use Pa; alpha/gamma use K*s, eta uses1/(K*s), Gamma usesK²/Pa, and a/b/c use1/(K*s). `Gamma=.001` is the SI conversion of1K²/kPa. K=13e9,G=5e9,p1=543e6,M=.73,omega=.6,Lambda10,alpha=gamma6e5,eta150. These rounded code values are not silently replaced by a phi1-derived journal preset. Binary64 values, hex strings and exact IEEE754 bytes for parameters, initial extended state, durations and rates are retained.

Initial elastic pressure100000Pa,q0,T0,phi.423 gives `v=sqrt(2*100000/(K*phi^6))`,s0. Total accumulated strains start at zero. Initial temperature zero is valid for **prescribed-rate preparation**. Instantaneous total-stress inversion at T0 is singular and explicitly rejected; no floor, clipping, projection or hidden regularization is introduced.

## Complete carried trajectory

Three paths prepare for10s at `(Dv,Ds)=(0,+2e-5),(0,-2e-5),(6e-5,0)`, then hold for20s. Samples occur at physical times0,1,…,10 in preparation and10,12,…,30 in hold. Each path retains22 observations, including both one-sided t10 observations.

At t10, total targets `(P,Q)` are computed from the **computed preparation state and incoming prescribed rate**. The four states and accumulated strain are copied without modification. Hold rates follow exact positive-temperature algebraic elimination:

`Dv=[Gamma*(P-pe)-T^2]/(2alpha*T)`, `Ds=Gamma*(Q-qe)/(2gamma*T)`.

At the captured endpoint these recover incoming preparation rates up to floating rounding. Thus there is no intended stress or strain jump. The left sample records prescribed rates and the right sample records inverted hold rates. Both state and strain are bitwise identical. Time is never reset to hold-elapsed time. Each RK4 level and midpoint run carries **its own** preparation result and captures **its own** targets; none receives a frozen externally converged preparation state. Phase-separated hold errors therefore include upstream preparation/capture uncertainty, as an end-to-end comparison should.

## Frozen policies, retained failure and passing refinement

Root `source-freeze.json` pins policy and producing code before the first source observations. RK4 used32,64,128steps/s and midpoint2048steps/s. The unchanged analytical temperature gate was1e-12K. Root `checks.json` retains **FAIL**,957 assertions with one failure: isotropic preparation temperature. Its maximum errors were5.5464e-12K for RK4-32 and1.5761e-11K for midpoint2048; RK4-64 and128 gave3.4392e-13 and2.1409e-14K. This is quadrature accuracy, not evidence for changing the source equation.

A distinct `refinement-v2/` freeze changes only identity and quadrature resolutions: RK4 uses64,128,256steps/s and midpoint16384steps/s. Physical inputs, equations and every numerical acceptance bound remain unchanged. Its checks pass957 assertions plus explicit zero-temperature rejection. Across all retained v2 runs:

- Maximum analytical preparation temperature error3.44e-13K.
- Maximum density/accumulated-volume closure error1.25e-14.
- Maximum capture left/right tensor-rate difference8.5e-19/s.
- Maximum midpoint/fine-RK4 stress difference6.95e-8Pa.
- Captured total P/Q closure is zero at binary64 precision for the evaluated observations.

Both RK4 successive pairs and crossmethod differences are recorded separately for preparation/hold, by component. The v2 reference gates are state `[2e-11,2e-12,1e-9,1e-10]`, tensor strain1e-10, rate1e-11/s,stress1e-5Pa. These are numerical study bounds, not rigorous error estimates. Analytical checks use `T=sqrt(A/eta)*tanh(sqrt(A*eta)*t)` and `phi=phi0*exp(Dv*t)` during preparation; full paths use `phi=phi0*exp(accumulated volumetric strain)`. Compression/extension symmetry and exact isotropic zero-shear invariants are checked.

`audit.py` additionally checks original freezes, exact input bytes, all finite/mistyped scalar channels, alias equality and completeness, with five retained corruption-rejection probes. Its ten assertions pass. This supplements numerical checks; it is not independent scientific authorship.

## Reproduction and integration requirements

Run `python3 -B refinement-v2/check.py` and `python3 -B audit.py` from this directory. To regenerate rather than merely reassess, copy the frozen producer/policy to an empty private directory, run `python3 -B reference.py`, then check. The generator refuses to overwrite an existing reference. Full bytes/hashes are in `manifest.json`; no mutable global dossier is a frozen equation input.

Parent integration must make a **new prospective compiled study**, freeze producer/model/schema/control requests and these reference bytes, and preserve any failures. Suggested backend tolerances1e-4,1e-6,1e-8 and separate preparation/hold fine bounds are recorded in both policies: state `[2e-9,2e-10,1e-7,1e-8]`, strain1e-8, rate1e-9/s, elastic/total stresses.01Pa, captured targets.01Pa, clock1e-12s. Require exact backend state/strain carry at t10; never replace its preparation state with these reference values. Capture targets must derive from its actual incoming rate. Retain left/right rate metadata, both grids, full phases and positive-temperature singularity behavior. This packet contains **no compiled observations**.

Source-domain and source-version limits remain as before. Reference stage checks enforce the current nonstrict Figure1 draft domain without expanding it; they do not settle journal equality admissibility. No general3D, finite-rotation, pore-pressure, experimental-validation or public timed-browser claim follows. The smallest next action is coordinator review/freeze of a full-path native/Wasm study using the passing v2 reference, followed by serial one-target observations under the existing Cortex precautions.
