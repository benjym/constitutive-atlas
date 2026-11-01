# Ramberg–Osgood, ANSYS 2024 R2 — source packet v1

Task: ING-ramberg-osgood-ansys242-v1. Owner: separate source specialist `/root/ramberg_source`, 2 November 2026. Scope: source acquisition, transcription, v0.3 crosswalk and independent source algebra; no executable model, compiled test, approval or release is claimed here. The parent owns the full E0–E8 continuation and root delivery ledger.

## Identity and sources

The exact source is ANSYS, Inc., *Material Reference*, Release 2024 R2, §4.17 “Ramberg-Osgood Model”, especially §4.17.1 (theory) and §4.17.2 (input definition): [versioned primary HTML](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/ans_mat/ramberg-osgood.html). This identifies the vendor's three-dimensional isotropic nonlinear elasticity relation, rather than the original 1943 paper or a cyclic plasticity variant. No DOI is provided by this source.

The readable HTML and every referenced equation SVG and figure were privately retained under `.local/private-sources/ramberg-osgood-ansys242/`. [source-receipt.json](source-receipt.json) hashes the original HTML, 39 original SVGs and one original figure separately, with exact URLs, byte counts and access date. SVGs were rendered with `rsvg-convert -z 3` and visually read; private derivatives are not substitutes for original hashes. The HTML SHA is `5d8880123f58c57bf5929671d9411e70028ab4d2289f1deb5794f384e6c75227`; the receipt is authoritative. The release footer asserts copyright and proprietary/confidential status. Public access supplies no redistribution permission. Original HTML, equation artwork and figure remain private; the public packet contains own transcription and reasoning.

Downloads filenames were checked for Ramberg/Osgood/ANSYS. No relevant prior source was found there; the parent had obtained this HTML. Repository model/dossier searches found no existing exact Ramberg–Osgood packet. ROADMAP, STATUS and the charter were inspected for governing admission distinctions. Neither source access nor these algebra checks constitutes admission.

## Equations and locators

Here `σᴬ, εᴬ` denote source stress and infinitesimal strain, `pᴬ=−tr(σᴬ)/3`, `sᴬ=σᴬ+pᴬI`, and `q=σ_e=sqrt(3 sᴬ:sᴬ/2)`. The source's pressure definition establishes a compression-positive pressure in its standard tensile stress convention. Its §4.17 opening explicitly identifies small-strain isotropic nonlinear elasticity, reversible unloading along the loading curve, no path history, no yield surface and no irreversible plastic strain. Its stated application is monotonic proportional metal loading; mathematical reversible checks do not establish cyclic physical applicability.

| Locator: SVG basename under primary `graphics/` | Transcription / meaning |
| --- | --- |
| `eq13960ad5-7875-47e9-a171-01d7aed00286.svg` | `E εᴬ = (1+ν)sᴬ − (1−2ν)pᴬI + (3/2)α(q/σ0)^(n−1)sᴬ` |
| `eq7ae0e217-fe12-4cb3-a66b-4b810e13ed57.svg` | `pᴬ=−tr(σᴬ)/3`, `sᴬ=σᴬ+pᴬI`, `q=sqrt(3sᴬ:sᴬ/2)` |
| `eq36d21f43-5968-42e8-bed7-08cfc709c524.svg` | `E ε_vol I/3 = −(1−2ν)pᴬI`; `E eᴬ = [(1+ν)+(3/2)α(q/σ0)^(n−1)]sᴬ` |
| `eq4cc855de-a0bd-4b4c-a756-21b766321a64.svg` | `ε_vol=tr εᴬ`, `eᴬ=dev εᴬ`, `e_eq=sqrt(2eᴬ:eᴬ/3)` |
| `eq2c847a65-161e-4945-885e-e3766a634758.svg` | `pᴬ=−E ε_vol/[3(1−2ν)]` |
| `eq8c06d8a3-9633-47b2-9727-9e258077abd0.svg` | `E e_eq = (2/3)(1+ν)q + α(q/σ0)^(n−1)q` |
| `eq68a35aee-d1ba-488b-8703-86189192fd85.svg` | `sᴬ=(2/3)(q/e_eq)eᴬ`; this quotient is for `e_eq>0`; use the governing tensor law at zero. |
| `eq50708c16-c37a-4d9c-a27d-be061a7a96bf.svg` | Source postprocessing: `ε_elᴬ=(1+ν)σᴬ/E + 3νpᴬI/E`, `ε_plᴬ=εᴬ−ε_elᴬ`. Both are reversible pseudo-strains, not plastic history. |
| `eq772f1fc1-7074-4fcd-b9a2-45b3d07b9bd1.svg` | Literal source energy: `W=W_el+W_pl`; `W_el=(1+ν)q²/(3E)+(3/2)(1−2ν)q²/E`; `W_pl=[n/(n+1)]α q^(n+1)/(E σ0^(n−1))`. **The repeated q² in W_el is inconsistent with the governing hydrostatic relation; retained as a source defect below.** |

The named SVG anchors are persistent locators in this exact release; equations have no printed numbers. Fig.4.65 is illustrative, not digitized reference data. Example4.42 uses `E=390900 MPa`, `ν=0.3`, `σ0=50 MPa`, `α=0.5`, `n=5`; these are illustrative parameters, not a calibrated material.

### Parameters and domain

| Parameter | Units | Source / proposed scope |
| --- | --- | --- |
| `E` | Pa | Young modulus, §4.17 parameter table and §4.17.2; require `E>0` for positive elastic response. This section does not give a numeric range. |
| `ν` | 1 | Poisson ratio; proposed positive-definite elastic scope `−1<ν<1/2` is a mathematical restriction, not a range printed in this section. |
| `σ0` | Pa | Yield-strength scale; source table explicitly `σ0>0`. It is not a switching yield surface. |
| `α` | 1 | Source yield-offset coefficient; explicitly `α>0`. **Actual uniaxial nonlinear strain at q=σ0 is `α σ0/E`, not α.** |
| `n` | 1 | Source hardening exponent; explicitly `n>1`. Fractional values are mathematically allowed. Restricting to integer examples would be a narrower implementation scope. |

The source permits temperature tabulation of strength coefficients; this delivery should freeze coefficients, omit temperature coupling and disclose that scope. Finite values and the above bounds are required. The governing relation has no elastic/plastic switch. At `q=0`, `(q/σ0)^(n−1)=0` for `n>1`, so the nonlinear tensor term is zero. The apparent `q/e_eq` quotient is only a source stress-recovery formula, not an origin condition; at zero deviatoric strain/stress both are zero with finite linear-elastic tangent. `n=1`, `α=0`, `ν=1/2` and `E=0` are excluded boundaries even where some mathematical limits exist.

## Source-to-schema v0.3 crosswalk

Read [the v0.3 contract](../../../FORMULATION_CONTRACT.md) and [schema](../../../../schemas/model-v0.3.schema.json). This packet does not alter either. For atlas compression-positive tensors use `σ=−σᴬ`, `ε=−εᴬ`, `m=trσ/3`, `s=devσ`. Simultaneous sign reversal leaves the tensor compliance odd and gives

`F(σ) = [(1+ν)+(3/2)α(q/σ0)^(n−1)]s/E + (1−2ν)mI/E = ε`, `q=sqrt(3s:s/2)`.

This sign mapping follows by multiplying the source relation by minus one; the scalar invariant q is unchanged. Mandel order is the atlas transport choice `[xx,yy,zz,√2xy,√2yz,√2xz]`; ordinary tensor contraction becomes the six-component Euclidean dot product. The source does not name Mandel storage. Engineering shear inputs would require explicit conversion, never implicit substitution.

| Contract field | Proposed explicit value and rationale |
| --- | --- |
| `schema_version` | `"0.3"`; no legacy top-level `integration` |
| `time_dependence`, `equation_form` | `strain_path`, `incremental_residual`; project realization of a static total compliance relation, no physical clock |
| `kinematics` | `small_strain_3d`; source §4.17 small-strain and 3D relation |
| `frame`, `objective_rate` | `fixed_spatial`, `none`; selected zero-spin small-strain Cartesian realization; finite rotations are not established by the source equation |
| `tensor_representation`, signs | `mandel`, both `compression_positive`; explicit conversion above |
| `inputs` | Exact contract `de`: finite symmetric infinitesimal-strain increment, unit1, configuration current, sampling increment; empty advance object |
| `stress` | State `sigma`, Cauchy, `total`; dry mechanical standalone scope. Source has no pore-pressure model. Total stress is the selected uncoupled dry scope, not proof of poromechanical behavior. |
| persistent state | Six-component `sigma` followed by six-component accumulated total strain `epsilon`; both spatial symmetric tensors; units Pa and1, stress-first layout. `epsilon` is kinematic bookkeeping, not plastic history. |
| equations | `R_sigma=E*(F(sigma)−epsilon)` in Pa; `R_epsilon=epsilon−epsilon_n−de` in1. These eliminate to the source total relation at each accepted endpoint. |
| initialization | Explicit complete state; require `epsilon=F(sigma)` to numerical tolerance. Zero state is one reviewed preparation example. Nonzero stress with arbitrary zero strain is inconsistent. |

The parent may choose algebraically equivalent scaled residuals or a smaller sufficient state, but must preserve total relation, source parameter meaning and consistent initialization. Keeping only `F(σ_new)−F(σ_n)=de` preserves any initial compliance offset indefinitely; without an initial consistency condition it does not enforce the source zero-reference material. Division-free zero behavior, fractional powers and automatic differentiation at exactly q=0 need parent implementation qualification. A norm expression may introduce a numerical derivative singularity even when the composed source tensor map is differentiable.

## Temporal integration and transactions

This is a static reversible constitutive map, not an ODE and not irreversible incremental plasticity. Incremental residuals are a project integration choice compatible with accumulated total infinitesimal strain. No duration, rate, thermal evolution or stress relaxation is implied. A hold with `de=0` retains the same consistent stress/strain; unloading to the original strain returns to the original stress. No yield events, hardening variables, lagged material coefficients, return mapping or reset events are justified. The source's “pseudo-plastic” postprocessing must not be introduced as an irreversible history field.

The source describes Newton solution of its scalar deviatoric equation and differentiating stresses with respect to strains for the material tangent. The scalar map is strictly increasing under the proposed elastic domain: `d(E e_eq)/dq = 2(1+ν)/3 + n α(q/σ0)^(n−1)>0`. Volumetric response is linear. Therefore the scalar inverse is unique and has finite origin limit; its deviatoric principal compliance limit is `(1+ν)/E`. The project common residual solver/tangent and substepping require separate verification, especially origin, fractional n and extreme parameters.

Trial, commit and rollback are project engine semantics, unspecified in the inspected ANSYS section. Required project contract: trials begin from one committed consistent parent; accept commits both stress and total strain; failure restores the entire incoming state; rejected trials cannot accumulate strain. Exact endpoint response depends only on final total strain, so subdivisions and different loading paths to a shared endpoint should agree within declared numerical tolerance. Rotations, large strain, thermo-mechanical fields, irreversible cycles and experimental claims are excluded.

## Independent algebra and retained source defect

Run `python3 docs/ingestion/ramberg-osgood-ansys242/source-v1/check_algebra.py`. [algebra-results.json](algebra-results.json) records **26 passing scalar/tensor checks**: source-example uniaxial and lateral relations at zero and both signs, nonlinear offset at σ0, hydrostatic trace, odd reversal, and four independent bisection inversions of the source equivalent-strain equation. No atlas import, native execution or Wasm result is used. These establish transcription/algebra checks, not numerical-engine qualification.

For hydrostatic pressure magnitude12MPa with source-example E and ν, the literal printed energy formula gives zero because q=0, whereas integrating the governing volumetric stress-strain relation gives positive energy `3(1−2ν)p²/(2E)` (about221.03Pa). The discrepancy is retained in the results. The likely intended second term contains p², but this packet does **not** silently correct or endorse the source energy formula. Mechanical governing relations, scalar reduction and pseudo-strain split are internally consistent. Exclude energy observables and any energy qualification claim from the present delivery; resolving that optional postprocessing equation needs an independently sourced correction.

## Handoff

Owned deliverables: this README, source-receipt.json, check_algebra.py and algebra-results.json. Private originals and render derivatives remain in the ignored source directory. Source mechanical relation is complete for the declared isothermal small-strain reversible scope; optional printed energy contains a disclosed defect. No new shared capability is requested by this packet, but exact-origin differentiation and initialization consistency require coordinator verification before claiming executable support. Executable status, compiled numerical verification, independent approval, atlas admission and live delivery are pending parent work. The smallest next action is a v0.3 common residual candidate with consistent explicit initialization, frozen independent reference/gates, then serial coordinator-owned native/Wasm qualification and actual independent checklist review.
