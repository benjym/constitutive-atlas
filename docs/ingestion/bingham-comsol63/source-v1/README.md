# Bingham COMSOL 6.3 — source ingestion packet v1

Task ID: ING-bingham-comsol63-v1. Owner: separate source specialist `/root/bingham_source`; 2 November 2026. Owned output: this new directory and ignored `.local/private-sources/bingham-comsol63/`. This closes only the bounded source handoff; the coordinating parent owns E0–E8. No compiled artifact, vendor program or vendor binary was executed.

## Identity and sources

Exact target: `bingham-comsol63-mises-perfect-zero-spin-ode`. COMSOL Multiphysics 6.3 Structural Mechanics Module documentation, **Creep and Viscoplasticity**, subsection **Bingham Model**, specialized to associative von Mises flow, isotropic linear elasticity, **Perfectly plastic**, **No kinematic hardening**, and thermal function **None**. This is an elastoviscoplastic solid with a positive constant yield stress, not a yield-stress viscous fluid, rate-independent return-map plasticity, Perzyna's differently normalized law, or the general family of every Bingham variant. The vendor documentation is the mathematical source; no historical Bingham publication identity is asserted. Version is 6.3; the inspected pages do not supply their own publication date or personal authors.

Primary readable sources:

- [Theory](https://doc.comsol.com/6.3/doc/com.comsol.help.sme/sme_ug_theory.06.039.html): Equivalent Stress/Creep Flow; Viscoplasticity; Bingham Model; Time Stepping. Exact equation image locators below.
- [Viscoplasticity interface](https://doc.comsol.com/6.3/doc/com.comsol.help.sme/sme_ug_solid.07.024.html): selected model and variants, viscosity units, source numerical alternatives.
- [Elasticity relations in Linear Viscoelasticity](https://doc.comsol.com/6.3/doc/com.comsol.help.sme/sme_ug_theory.06.029.html): introduction gives elastic strain as total minus inelastic strain; images008–010 give isotropic elastic stress. This packet uses those elastic relations only; it does not add a viscoelastic branch.

Private exact-byte HTML and PNG receipts, with URLs, SHA-256 and access date, are in `source-receipts.json`. Private files are not redistributed. No source PDF was needed or opened. User Downloads and existing private-source inventory were searched by name; no Bingham source was found. Existing SLS source inventory was read without modification. The first sandboxed URL acquisition failed DNS resolution; the permitted read-only network acquisition succeeded. No equation was inferred from a snippet: source PNGs were downloaded, flattened onto white solely for readable private contact sheets, and visually inspected. Receipt entries distinguish downloaded original bytes from derived contact sheets. Images concerning neighboring models were acquired for context but are not additional selected formulations.

## Existing work and gaps

The parent claimed this new model after Original Cam Clay delivery. There was no pre-existing Bingham dossier or definition under this identity. The existing SLS v0.3 timed record supplies structural syntax only; none of its constitutive equations or physical parameters defines this Bingham law. The explicit [v0.3 schema](../../../../schemas/model-v0.3.schema.json) and [formulation contract](../../../FORMULATION_CONTRACT.md) support this dry small-strain physical-time ODE without a new profile or handwritten kernel.

## Equations and schema crosswalk

Let ε be total infinitesimal strain, εvp viscoplastic strain, εel=ε−εvp, s=dev(σ), q=√(3s:s/2), Y>0 the constant yield stress, and η>0 the viscosity. In source tensor notation:

σ = K tr(εel) I + 2G dev(εel)

F=q−Y; λ=⟨F⟩/η; N=3s/(2q) when q>0

ε̇vp=λN; α̇=λ; ε̇=prescribed infinitesimal strain rate.

At q≤Y, ε̇vp=0 and α̇=0, including q=Y. At q=0 the product λN has its unique zero continuation; N itself is undefined there. Candidate evaluates the exactly equivalent expression `1.5 * lambda_vp / max(q,sigma_y) * sdev`: when flow is active q>Y the denominator is q; otherwise λ=0 and the strictly positive denominator prevents division by zero. This is an algebraically exact inactive-branch extension, not smoothing, a yield shift, clipping of stress, or a modified active law.

| Source locator | Confirmed relation or selection | Candidate mapping |
| --- | --- | --- |
| theory039 image016 | q=√(3J2)=√(3 devσ:devσ/2) | `sqrt(1.5)*norm(sdev)`, Pa; Mandel norm preserves tensor contraction |
| theory039 image022 | Ndev=3 devσ/(2q) | exact safe-product expression above |
| theory039 images057/059/060 | ε̇vp=λN; α̇=√(2ε̇vp:ε̇vp/3)=abs(λ); N:N=3/2 | persistent tensor εvp and scalar accumulated α; λ≥0 makes α̇=λ |
| theory039 images070/076/077/078 | F=q−Y; λ=⟨q−Y⟩/η, conditional F≥0; ε̇vp=λN | `max(q-sigma_y,0*sigma_y)/eta`; continuous zero at threshold |
| interface Bingham | η, SI Pa s | positive `eta`, SI exponent [1,−1,−1,0] |
| interface Plasticity Model | von Mises; associated potential | isotropic deviatoric flow; no pressure dependence |
| interface Isotropic/Kinematic Hardening | Perfectly plastic; No kinematic hardening | constant positive `sigma_y`; no back stress or hardening force |
| interface Thermal Effects | None is available | no temperature input or multiplier |
| theory029 introduction; images008–010 | elastic strain subtraction and isotropic elastic stress | observable `stress`, total dry Cauchy stress |
| theory029 images002–004/008 | source tension-positive stress/strain, compression-positive pressure p=−trσ/3 | simultaneous σatlas=−σsource, εatlas=−εsource, εvp_atlas=−εvp_source; q, α unchanged; same isotropic equations result |
| theory039 Time Stepping Eq3-149/150; Domain ODEs | time integration of εvp and equivalent strain | continuous `physical_time`/`ode`; no claim to reproduce vendor FE discretization |

Tensor storage is project Mandel `[xx,yy,zz,√2xy,√2yz,√2xz]`. Source tensor equations are representation-independent. The simultaneous sign mapping preserves flow, power and dissipation. The source stresses are mechanical stresses; this deliberately dry subset has no pore variable, Biot correction, thermal strain, initial stress offset or effective-stress reconstruction. `stress.scope="total"` is appropriate to that bounded selection.

K and G are elastic bulk/shear moduli (Pa), Y is yield stress (Pa), η is viscosity (Pa s). Mathematical domain requires all four strictly positive. The candidate's illustrative values K=20 MPa, G=10 MPa, Y=0.1 MPa and η=20 MPa s are project examples, not vendor calibration; finite bounds [1e−12,1e30] are an executable numerical envelope, not evidence that every combination is numerically qualified. No source admissible-range envelope was found. Equivalent E=9KG/(3K+G), ν=(3K−2G)/(2(3K+G)) gives E>0 and −1<ν<1/2.

State layout is ε6, εvp6, α1 = 13 persistent components. ε and εvp transform as symmetric spatial tensors, α as a scalar invariant. α retains accumulated equivalent strain under reversals; it cannot be reconstructed from the current norm of εvp. Examples are all zero. Explicit initialization must supply the complete state and current physical time/rate, including already flowing overstressed initial states if desired. εvp must be deviatoric (candidate trace tolerance1e−10 is project numerical tolerance); α≥0. The source does not specify every admissible prehistory. The candidate does not silently project states, solve preparation, or prove arbitrary εvp/α pairs realizable. Initial overstress is permitted for this viscous law: imposing F≤0 would incorrectly erase relaxation. A nonzero initial εvp represents an explicitly supplied inelastic strain history; no stress offset is independently added.

## Temporal integration and transactions

This is a rate law per physical second, not a strain-path derivative. Required stage inputs are `time` (s) and all six components `strain_rate` (1/s); advance context is finite `start_time` and strictly positive duration with representably later endpoint. The equation is autonomous, but advancement still requires a physical clock. ε integrates the total imposed strain rate. Current stage stress is computed from current stage strains; ε̇vp and α̇ use that same stress, with no lagged yield state. There is no dynamic yield-surface equation and no complementarity requirement F≤0 during active viscoplasticity.

A zero strain-rate hold can relax an overstressed deviator, stopping asymptotically at q=Y. Below/at yield it is stationary. Hydrostatic stress does not relax. At zero stress there is zero flow. Under maintained above-yield stress, strain grows at a constant viscoplastic rate; maintaining that stress requires the corresponding imposed strain rate or an independently qualified stress-control host. Reversals traverse the finite elastic interval before opposite flow; α remains nondecreasing. There is no reset or yield-surface translation on reversal. Loading jumps must be split into separate advances; state does not jump across a finite rate change. Instantaneous strain jumps are not supplied by a finite-rate ODE call.

Source offers backward Euler or domain ODE FE solution. Candidate selects the continuous law; the atlas generic adaptive integrator and its tolerances are a disclosed project numerical choice. Nonsmooth first derivatives at q=Y and potentially stiff time scale η/(3G) require refinement/step-budget studies. No closed-form physical-time tangent is promised by current contract; no vendor Newton iteration, FE weak form or source discrete update is being transcribed.

Trial/commit/rollback details are unspecified in inspected vendor mathematical pages. The atlas formulation contract supplies them: successful advance commits all13 persistent components; failed advance returns the complete parent; repeated trials begin from identical committed parent; restart carries all state, physical time, parameters and loading context. These are host semantics requiring executable checks, not source experimental claims. No finite-rotation transport or objective rate is selected: fixed Cartesian frame, zero spin, infinitesimal strain. Constant-basis rotational covariance may be checked; finite-rotation objectivity cannot be inferred.

## Independent checks

`build_packet.py` writes `candidate.json`, `analytical-references.json` and `analytical-check.json` without invoking the model interpreter or any compiled constitutive artifact. A separate scalar reduction takes s=zN with N:N=2/3, giving q=abs(z). For coaxial prescribed deviatoric strain rate dN:

ż = 2Gd − (3G/η) sign(z) max(abs(z)−Y,0).

Inside [−Y,Y] the solution is linear, z=z0+2Gdt; outside it is z=zss+(z0−zss)exp(−3Gt/η), zss=sign(z)Y+2ηd/3. The reference splits exactly at analytically computed boundary crossings. α increments integrate |λ|; equivalently on an active segment Δα=sign(z)[2GdΔt−Δz]/(3G). Tensor εvp follows from ε−s/(2G) for these zero-volume reference histories. The108cases span six tensor-direction seeds (three normal and three Mandel shear), zero/below/exact/above threshold and positive/negative flow, holds, inward reversal, outward rates and yield crossings. Four constant-stress creep references separately cover below/at/above threshold and negative stress.

Reproduce from repository root:

`python3 docs/ingestion/bingham-comsol63/source-v1/build_packet.py`

Result:108closed-form radial cases,324 algebraic identity checks passed,4creep references written. The checks establish trace preservation, stress reconstruction and nonnegative α for these exact references. They do not establish integration accuracy. Candidate also passed `atlas.model.load` and `validate`; that establishes schema/expression/unit compatibility only. No compiled, Wasm, browser, experimental or scientific-admission result is claimed.

Prospective accuracy proposal is recorded before compiled observations in the reference file: scaled component error≤2e−5 with stress floor1Pa and strain floor1e−8. Parent must freeze exact execution settings and the final policy before observing native/Wasm results. Additional required studies: noncoaxial piecewise changes, rates differing by scale, volumetric/hydrostatic channel, all tensor components, restarted/repeated trials/rollback, invalid state/domain and physical clock, step refinement and backend agreement. Generic midpoint full-versus-half error estimation alone is not independent equation verification. Very small/large permitted parameters may underflow/overflow or exceed budgets and must fail transactionally, not be silently clipped.

Dissipation follows analytically: σ:ε̇vp=qλ=q max(q−Y,0)/η≥0. Elastic energy ψ=K(trεel)^2/2+G devεel:devεel; σ:ε̇−ψ̇ equals that nonnegative term. This proof assumes positive moduli/viscosity and the declared source law, not any discrete energy guarantee.

## Handoff

Files: `README.md`, `candidate.json`, `source-receipts.json`, `build_packet.py`, `analytical-references.json`, `analytical-check.json`, `validation.json`. Private originals remain ignored; contact sheets are private derived reading aids. Source completeness: complete for the exact dry, isothermal, small-strain, fixed-frame associative constant-yield variant. Executable support: schema/expression validation passed on generic timed profile; compiled execution not run by source worker. Numerical verification: independent analytical references and identity checks only, with prospective gates. Scientific admission: pending independent separate-agent checklist. Experimental validation: none.

No generic capability gap identified for the selected law; numerical handling of threshold, zero deviator norm/AD and stress-control host must still be qualified by parent. Smallest next action: freeze this exact candidate/source/reference identity and execution policy, then coordinator-owned timed native/Wasm study. Parent must continue through independent approval, main atlas controls/catalogue/database, actual browser qualification and authorized E8 delivery.
