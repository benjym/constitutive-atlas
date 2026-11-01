# j2-linear-hardening — ingestion packet

Task ID: ING-j2-linear-hardening-v1  
Owner / date: ingestion worker, coordinating parent / 2026-11-01  
Scope: first bounded source/schema/algebra packet. Executable qualification and independent scientific review are separately owned by the coordinator. This packet does not grant scientific admission.

## Identity and sources

The exact law is the **small-strain, three-dimensional, associative J2 model with linear isotropic hardening**, specialized from [OpenSees J2Plasticity](https://opensees.github.io/OpenSeesDocumentation/user/manual/material/ndMaterials/J2Plasticity.html) by setting `sigInf=sig0` and `eta=0`. The equivalent specialization `delta=0` is algebraically possible but is not needed for this identity. `H=0` is the included perfect-plastic boundary. Saturation hardening, viscosity, softening, plane-stress enforcement, plate fibers and finite deformation are excluded. This is an ingestion of the published mathematical backward-Euler law, not a port of the vendor algorithm's floating-point details.

The pinned implementation source is OpenSees commit **955ceb0a55f7b5764856ea82fc9a9cc7f07a1eea**, dated 2026-10-31T17:06:15Z. Its J2 source headers identify Ed Love and CVS revisions dated 2008-10-20; these are implementation identities, not a claim of a new 2026 model publication. No foundational-paper DOI is inferred from the documentation's unresolved `[[1]]` reference.

[Source receipts](source-receipts.json) record exact titles, identities, immutable implementation links, access date, byte sizes, SHA-256 digests and locators. Three primary originals and the API pin receipt are retained unchanged in ignored `.local/private-sources/j2-linear-hardening/`. Downloads filenames and existing repository model/source inventories were checked first; no dedicated earlier J2 model/receipt was located. The existing Drucker–Prager zero-friction specialization is related but lacks this persistent hardening history. Original vendor code and web HTML remain private. Their copyright/usage terms are not replaced by the project's license; no vendor code/binary was executed or redistributed.

## Existing work and gaps

The live board's ING-j2-linear-hardening-v1 is a new task. The existing [Drucker–Prager](../../../models/drucker-prager.json) uses related invariant conventions but is neither the source identity nor the implementation reference for this packet. [Research charter](../../RESEARCH_CHARTER.md), [status](../../STATUS.md) and [roadmap](../../../ROADMAP.md) distinguish transcription, numerical evidence, independent scientific signature and experimental validation. The candidate stays `draft` and its exact bytes must be preserved after handoff.

Primary-source ambiguities retained explicitly:

1. The web elastic equation omits the identity tensor after its scalar trace term. The base implementation's diagonal bulk-stress addition supplies the unambiguous tensor interpretation `K tr(epsilon_e) I` (J2Plasticity.cpp lines 589–591).
2. The J2ThreeDimensional.cpp header's saturation formula reverses the two stress constants compared with the web documentation and executable base `q()` at lines 665–672. The base equation is authoritative for the full family; both forms reduce to the same `sigma_y+H alpha` when `sigInf=sig0`, so this discrepancy does not alter the selected specialization.
3. Source notation uses `q` for the hardening radius; this packet uses `q_VM` for the von Mises stress. They must not be confused.
4. The source implementation multiplies its solved multiplier by `(1-1e-8)` at line 550. Atlas omits that deliberate small under-return and instead transcribes the exact mathematical consistency relation. Native/vendor bitwise agreement is therefore neither required nor claimed.
5. The web input synopsis omits viscosity although the pinned parser accepts optional `eta` and initializes it to zero. Here `eta=0` is an explicit identity choice.
6. The source's flow statement `dot(xi)=-gamma dphi/dq` treats `q` as a force/radius argument, not differentiation of the composite `q(xi)` with respect to `xi`. The executable update `xi_new=xi_old+sqrt(2/3) gamma_src` resolves the hardening normalization.

## Equations and schema crosswalk

Target: [schema v0.3](../../../schemas/model-v0.3.schema.json), [formulation contract](../../FORMULATION_CONTRACT.md). [candidate-v03.json](candidate-v03.json) validates structurally and semantically with `atlas.model.load`; it has no legacy `integration` field. All symmetric tensors are Mandel `[xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz]` with compression-positive stress/strain and SI units.

Let `s=dev(sigma)`, `q_VM=sqrt(3/2 s:s)`, and `r(alpha)=sigma_y+H alpha`. The elastic law is `sigma=K tr(epsilon_e) I+2G dev(epsilon_e)`. Yield is `f=q_VM-r(alpha)<=0`. Plastic flow in the Atlas multiplier is `d epsilon_p=(3/2) d alpha s/q_VM`; `d alpha>=0`, `f d alpha=0`. Alpha is the accumulated equivalent plastic strain, since `sqrt(2/3 d epsilon_p:d epsilon_p)=d alpha` on associated flow.

The source writes `phi=||s||-sqrt(2/3)r(xi)`, `d epsilon_p=gamma_src s/||s||`, `d xi=sqrt(2/3)gamma_src`. Hence `alpha=xi`, `gamma=d alpha=sqrt(2/3)gamma_src`. Multiplying the source consistency equation by `sqrt(3/2)` gives

`q_trial - 3G gamma - sigma_y - H(alpha_n+gamma)=0`.

Therefore the independent exact return is

`gamma=max(0,(q_trial-sigma_y-H alpha_n)/(3G+H))`,
`alpha=alpha_n+gamma`,
`sigma=sigma_trial-3G gamma s_trial/q_trial`,
`sigma_trial=sigma_n+K tr(de) I+2G dev(de)`.

For `q_trial=0` the positive initial radius makes this branch elastic and gamma zero. The candidate uses `trial_q_safe=select(q_trial>0,q_trial,p_ref)` solely to define evaluation at that point, without perturbing any positive trial invariant or introducing a material regularization. The candidate stress residual uses trial direction; this is the analytical elimination of the implicit final radial direction, valid because `K,G,sigma_y>0`, `H>=0`, alpha_n>=0 ensure the radial factor is positive. Its temporary gamma equation is the Fischer–Burmeister complementarity residual `sqrt(gamma^2+(f/p_ref)^2)-gamma+f/p_ref=0`. It enforces gamma>=0, f<=0 and gamma f=0; it is a numerical representation, not a different yield law.

| Source locator | Equation / quantity | Schema representation / units | Status / ambiguity |
| --- | --- | --- | --- |
| Web THEORY elastic law; base lines 492–495, 589–591 | Bulk and deviatoric elastic stress | `K,G`, Pa; elastic trial tensor in stress residual | Explicit I interpretation from executable diagonal addition |
| Web yield/hardening; base `q()`, lines 665–680 | `phi=||s||-sqrt(2/3)r`; linear specialization | `q=sqrt(1.5 dot(dev(sigma),dev(sigma)))`; `r=sigma_y+H alpha`, Pa | Positive rescaling to VM yield preserves cone and complementarity |
| Base lines 528–556 | Source gamma and xi increment | `alpha` persistent scalar; `gamma` temporary scalar, both dimensionless | Exact sqrt(2/3) conversion; no accumulated gamma slot |
| Base lines 492–495, 558–560 | Trial deviator and plastic correction | `trial_s=dev(sigma_n)+2G dev(de)`; stress residual | Plastic-strain tensor eliminated using constant elasticity |
| Base eta condition lines 531–537 | Time dependence | `strain_path`, `incremental_residual`; only `de` input, empty advance context | Eta explicitly zero; no clock/rate law inferred |
| 3D `setTrialStrain`/`getStress` | Source strain engineering shears and stress physical shears | Common Mandel six-vectors | Both full-tensor norms and tensor work preserved |
| Source isotropic tensor equations | Signs/frame/stress | compression-positive stress and strain; small_strain_3d; fixed_spatial; objective_rate none; total Cauchy stress bound to sigma | Simultaneous stress/strain sign reversal leaves this centrosymmetric law invariant; dry uncoupled material specialization, no pore-pressure/effective-stress conversion |

Parameter order is `p_ref,K,G,sigma_y,H`. Units are all Pa. The default example is `(1e8,1.6666666666666666e11,8e10,2.5e8,1e9)`. The finite schema bounds are **project execution envelopes**, not published material calibration or a numerically qualified full range: p_ref in [1,1e15], K/G in [1,1e15], sigma_y in [1,1e13], H in [0,1e15]. Physical assumptions are positive K/G/sigma_y, nonnegative H. `p_ref` is a positive numerical residual scale and does not enter the physical return map. No density, pore pressure, temperature or physical-time parameter is supplied.

State layout has eight numbers: sigma occupies six persistent Pa slots, alpha one persistent dimensionless slot, and gamma one temporary `plastic_multiplier` slot. Stress transforms as a spatial symmetric tensor; alpha and gamma are invariant scalars. Explicit initialization requires sigma and alpha, with alpha>=0 and `f/p_ref<=1e-10`; gamma is filled with zero. That finite initial tolerance is a project admissibility tolerance, not an equation change. The solution constraint alpha>=0 enforces admissibility; gamma sign is enforced by complementarity because temporary symbols are unavailable in solution constraints. Derived invariants can be evaluated for negative Newton trial alpha; residual evaluation domain is intentionally separate from physical admissibility. No projection onto the yield surface, physical preparation recipe or specimen calibration is implied. The zero-stress, zero-alpha literals are illustrative only. Arbitrary preloaded sigma/alpha must be inside/on the isotropic surface; no accumulated tensor plastic strain can be reconstructed uniquely from these two state quantities alone.

## Temporal integration and transactions

This is a rate-independent incremental law on the supplied straight infinitesimal strain increment. No duration, strain rate, aging or relaxation occurs. A hold `de=0` leaves an admissible state unchanged, with a zero plastic increment; pressure changes elastically under volumetric loading because plastic flow is isochoric. Hydrostatic stress is unrestricted by J2 yield. Unloading/reversal is elastic until the expanded centered surface is reached; there is no kinematic hardening/Bauschinger translation. A large increment spanning a path corner must be split by the caller. Nonproportional paths can depend on subdivision; the closed radial map is the backward-Euler solution for one supplied step, not an exact solution of every finite curved path.

Committed sigma_n/alpha_n form the elastic predictor; current alpha and gamma solve the correction, so hardening uses alpha at the new endpoint. Each internal residual solve resets temporary gamma. The plastic predictor first sets gamma=0; a yielded predictor activates complementarity. Accepted updates commit sigma/alpha; failures must restore the entire incoming layout. Repeated trial updates must start from the same committed state; restarts persist sigma/alpha and reset gamma for the next solve. There is no model reset rule or event locator. This transaction contract is the Atlas contract and must be qualified by the parent; it is stronger than merely citing vendor behavior.

The vendor base `commitState()` copies xi and plastic strain, `revertToLastCommit()` simply returns zero, and `revertToStart()` depends on initial-state-analysis mode. Its wrapper accepts total strain. These behaviors are recorded to prevent falsely claiming an identical host transaction lifecycle. The closed stress+alpha recurrence is sufficient for future incremental stress evolution with constant elasticity; it does not export vendor total/plastic-strain fields.

The source computes a consistent tensor tangent and has a 25-iteration warning, stress-scaled tolerance and gamma shrink. None is silently imported as an Atlas solver default. The candidate's generic nonlinear solve requires an elastic predictor, complementarity handling and a Jacobian/tangent; tangent and adaptive solver qualification remain parent work. Yield switching and norm zero are nonsmooth: rotated fixed-basis covariance is meaningful, but cannot establish finite-rotation objectivity. Dynamic integration, coupled drainage, finite strain, arbitrary parameter switching and H<0 require separate work.

## Independent checks

Run from repository root:

```sh
python3 -B docs/ingestion/j2-linear-hardening/check_algebra.py
```

The retained [algebra-checks.json](algebra-checks.json) records 296 passing independent checks, all four original-source hashes and candidate validation. Exact rational arithmetic tests 72 coaxial elastic/plastic combinations across three moduli, three hardening choices including H=0, two alpha histories and four trial amplitudes. It verifies complementarity, nonnegative radial magnitude, alpha monotonicity, source normalization and nonnegative discrete associated plastic work. A separate physical 3x3 tensor calculation tests arbitrary shear-containing source/Atlas multiplier and stress corrections; Mandel norm/work equivalence is checked directly. No generated residual evaluator, native/Wasm kernel or vendor implementation is used as the algebra oracle. Structural validation is reported separately. These checks are not solver/tangent/path convergence or experimental validation.

One candidate construction failure was retained in [retained-failure.json](retained-failure.json): placing temporary gamma in `solution_constraints` is rejected by the v0.3 validator. The final candidate uses complementarity for gamma and restricts explicit physical constraints to persistent alpha; no shared capability modification or gate relaxation was needed.

## Handoff

Owned files are README.md, candidate-v03.json, source-receipts.json, check_algebra.py, algebra-checks.json, retained-failure.json and manifest.json. [Manifest](manifest.json) binds the exact packet bytes other than itself. Originals are private under the receipt paths and excluded from public source archives; rights restrictions remain attached to them.

- Source completeness: bounded mathematical specialization, conversion and implementation differences are source-complete against readable pinned primary sources. Foundational bibliography and experimental calibration are not claimed.
- Executable support: v0.3 validation passes; no compiled run performed by this worker. Existing generic incremental profile appears sufficient; no shared capability request is necessary.
- Numerical verification: independent algebra only in this packet. Parent owns prospective exact radial references, finite loading/unloading/rotation paths, native/Wasm replay, tangents, initialization and rollback qualification.
- Scientific admission: pending independent review and explicit bounded project decision; no human scientific signature or experimental validation.

Smallest next action: freeze the candidate and prospective acceptance study, build one isolated serial explicit generic target, qualify radial references plus path/transaction/tangent checks, then commission an independent source/evidence review. Do not edit the historical candidate to update its draft status or later provenance.
