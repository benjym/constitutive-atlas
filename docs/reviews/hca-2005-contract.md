# HCA-2005: recording-cycle and accumulation-block contract draft

Status: source-located design draft, 2026-10-31; not an accepted JSON schema, executable formulation, complete source transcription, or independent scientific review. No repository files were edited and no native code was built or executed.

Source identity: Niemunis, Wichtmann & Triantafyllidis (2005), *A high-cycle accumulation model for sand*, Computers and Geotechnics 32(4), 245–263, [DOI](https://doi.org/10.1016/j.compgeo.2005.03.002). [Author-hosted manuscript](https://www.torsten-wichtmann.de/paper/journal/2005-CG-a-high-cycle-model.pdf), inspected locally as: `paper/results/sources/niemunis-2005-hca.pdf`, SHA-256 `ecf856384f0c77d5440a2aeb28c96420e609ed7cefffab9f19a0b8e141a796ce`. All page numbers below are **author-manuscript PDF pages**, not journal pagination. This packet visually inspected pp. 1, 3, 4, 7, 8, 10–15. Full journal/manuscript equivalence remains unverified. No PDF, extracted text, or page images should be copied into the public repository through this packet.

Existing supporting records: `paper/study/source_formulations/hca-sand-2005.json` and `paper/study/hca_normalization.md` are partial paper-side audits; the canonical catalogue still identifies this as a non-executable candidate. They may be absent from a clean checkout and do not close the equations, calibration, initialization or solver admission gates.

## 1. What is being modeled

The constitutive output is the average accumulation of strain and/or stress over many load cycles. It is not obtained by executing every oscillation in the accumulation mode.

The manuscript has three algorithmic modes (p. 12, Section 4):

1. **Implicit cycle resolution:** a companion constitutive model establishes static equilibrium and resolves irregular cycles. Here “implicit” means resolving the load cycle; the manuscript explicitly distinguishes its terminology from Euler forward/backward integration (p. 2, footnote 4).
2. **Recording:** resolve a regular cycle with the companion model while retaining the tensorial logarithmic-strain trajectory.
3. **Accumulation / pseudo-creep:** compute increments over a package of cycles using the amplitude descriptor and HCA histories. Re-enter cycle resolution periodically for a control cycle that refreshes amplitudes and checks admissibility.

Flowchart p. 3, Fig. 3 requires at least the first two cycles to be resolved, with the second cycle recorded as the first regular cycle. One recording-cycle packet therefore needs a parent already prepared through the irregular first cycle, or an explicit declaration that its measured loop supplies equivalent preparation information. Supplying only one scalar axial strain amplitude is insufficient for general out-of-phase loading.

## 2. Coordinates, units and frames

| Quantity | Required meaning | Source / unresolved conversion |
|---|---|---|
| `cycle_count N` | Continuous nonnegative count coordinate; rates have meaning “per cycle”; an accumulation block has positive finite `Delta_N` | p. 1 after Eq. (1). Fractional cycle increments are allowed by the numerical formulation; p. 14 reports starting at 0.01, later increasing to 500 or more. These example increments are not accuracy guarantees or proposed defaults. |
| `cycle_phase` | Ordered samples within one resolved or measured recording cycle; may carry physical seconds when measured, but that metadata is separate from N | pp. 1, 3; no conversion of `N` into physical seconds is licensed. A rate-dependent companion would require its actual time contract. |
| `T` | Effective Cauchy stress, Pa after explicit unit conversion; source uses tension positive | Appendix A, p. 14. Atlas compression-positive storage requires an explicit sign map. |
| `epsilon` | Symmetric logarithmic strain `ln(U)` on the recorded cycle, dimensionless | pp. 1, 3, 12–14. The paper warns stretching `D` is not generally the derivative of this strain; Eq. (4), p. 2, remains to be reconciled for finite rotations. |
| `D`, `D_acc`, `D_pl` | Total, cumulative and monotonic-plastic stretching per cycle in accumulation mode | Eqs. (5)–(7), pp. 3–4. Do not identify them with within-cycle oscillatory strain rates. |
| Source tensor vector | Orthonormal order `11,22,33,sqrt(2)12,sqrt(2)13,sqrt(2)23` | Appendix A, p. 14; differs from Atlas order `xx,yy,zz,xy,yz,xz`. Reorder the last two shear slots explicitly. |
| Average `T_av`, `epsilon_av` | Source's center of the smallest enclosing hypersphere; footnote 1 permits a midpoint of two most distant states as an alternative | p. 1. Do not silently substitute an arithmetic sample mean, which changes with sampling density. Record the chosen center definition. |
| `A_epsilon` | Fourth-order tensorial amplitude; dimensionless strain magnitude; norm defines scalar amplitude | Eqs. (21)–(23), p. 10. Not a second-order component-amplitude vector. |
| `pi` | Fourth-order back-polarization history; normalization/representation issue below remains open | pp. 10–11 and Appendix A. |

An initial executable research scope could deliberately restrict to small strain and zero spin, but that would be a project restriction, not proof that the manuscript's large-deformation/corotational formulation has been implemented.

## 3. Draft data objects and ownership

These are required information fields for design review, not field names accepted by the existing API.

### `prepared_parent`

- Complete effective stress and void ratio, with source units/sign/frame.
- Full companion-model persistent state, including intergranular strain when that companion is selected; all companion parameters, source/version and initial preparation history.
- HCA `g_A` and `pi`, each with a provenance/initialization declaration, plus cycle-count origin and how explicitly resolved preparation/recording cycles are counted.
- Initial admissibility checks and any accumulated-strain bookkeeping needed by the intended experiment. Initial equilibrium or boundary conditions are separate from a local material point.

HCA `g_A` is not recoverable from `e,T` alone (p. 5, Section 2.4). In-situ history must not default silently to zero. Do not infer `g_A=f(N)` merely because a numerical count origin is available.

### `recording_cycle`

- ID, source hash/provider, generation route (`companion_resolved`, `measured`, or `separate_dynamic_solution`), cycle ordinal and parent-state identity.
- Ordered, unmodified sample records carrying phase and **all six** symmetric logarithmic-strain components in a declared basis; stress and void-ratio samples when available, so average conditions/admissibility are auditable.
- Sample resolution/convergence evidence; start/end residual drift and any yield-surface contact. Do not force closure, detrend, sort by strain or delete repeated samples without a separately recorded processing operation.
- Companion model/parameters, loading controls, initial state, integrator and trial/rollback policy when generated. A measured loop instead needs calibration/measurement metadata and a statement of how parent state and average stress were established.
- Declared recording filter. **First draft proposal: retain every provided sample**, since the source's filtering statements conflict; this is an explicit project choice preserving evidence, not the paper's exact implementation.

The source permits directly measured strain amplitudes or amplitudes from a separate dynamic calculation (p. 3, footnote 5). Such a route does not automatically supply the full local strain loop, back-polarization, average stress, or companion state needed by every benchmark.

### `amplitude_descriptor`

- Source recording-cycle ID, extraction method/version, basis and Frobenius metric.
- Six span radii `R_i` and mutually orthonormal symmetric-tensor directions `r_i`, including degeneracy metadata; zero spans need no invented normalized direction.
- Fourth-order `A_epsilon`, its norm `epsilon_ampl`, normalized polarization `A_hat`, and all validation diagnostics.
- Average stress/density descriptor and provenance; interval for which the amplitude is frozen; next scheduled/admissibility-triggered control-cycle policy.

Do not encode fourth-order amplitude as `sym[6]`. In a symmetric-tensor Mandel basis it is representable by a symmetric positive-semidefinite 6×6 operator, provisionally 21 scalars. Its back-polarization relationship still requires the separate 6D/9D review below.

### `accumulation_block`

- Positive finite `Delta_N` and count origin, immutable parent-state identity and amplitude-descriptor ID.
- Average loading/control path over N, including which components are stress/strain controlled and any monotonic loading. Fixed total strain can produce pseudo-relaxation; stress control can produce pseudo-creep; mixed controls can produce both.
- HCA constants and their source/calibration; accumulation-mode elastic stiffness and monotonic Matsuoka–Nakai flow/yield choice; companion/cycle model separately identified.
- Numerical policy for updating `T,e,g_A,pi`, stress/strain mixed controls, material stages, block subdivision, local error tests, domain rejection, budget limits and refresh triggers. These are **open design requirements**, not supplied by declaring a cycle coordinate.
- Optional prescribed/measured amplitude schedules only at explicit block boundaries; no silent interpolation between amplitude tensors or memory reset at a change.

### `block_result`

Return complete committed histories, total strain/stress, void ratio, `g_A`, `pi`, cycle endpoint, amplitude identity, source/numerical policy versions, accepted partitions, failure diagnostics and accepted prefix. Preserve accumulated strain separately from an increment-local multiplier. Record the amplitude-refresh decision and any completed companion/control cycle. Failed trial states must not overwrite the parent: this transaction rule is an Atlas design requirement, consistent with the source's start-of-increment trial convention (p. 12).

## 4. Recording one regular cycle: source algorithm and boundaries

1. Establish a physically admissible initial stress state using a conventional constitutive model, rather than assuming an elastic preparation guarantees admissibility (p. 3, step 1).
2. Resolve at least two initial cycles with small-strain nonlinearity; the paper uses a hypoplastic model with intergranular strain (p. 3, step 2; p. 12, mode 1). Record the second cycle (p. 3, step 3). Current Atlas VW96/IGS97 defaults are not automatically this source-matched companion.
3. Preserve the full logarithmic strain trajectory; validate symmetry, units, finite components, basis, ordering and recording resolution. Check whether the Matsuoka–Nakai boundary is encountered. The manuscript says Eq. (9) becomes inapplicable when cycles encounter the yield surface and proposes direct residual extrapolation instead (p. 5, discussion before Section 2.4). That alternative needs a distinct model/algorithm identity and is outside this packet.
4. Extract amplitude using the span/projection construction (p. 10, Eqs. (21)–(23)):
   - Find a pair of most distant sampled points; their distance is `2 R_6`, and their normalized difference is `r_6`.
   - Project the entire path onto the hyperplane orthogonal to `r_6`; repeat to obtain subsequent radii/directions down to rank one.
   - Form `A_epsilon = sum_i R_i (r_i outer r_i)`.
   - Compute `epsilon_ampl = ||A_epsilon|| = sqrt(sum_i R_i^2)` and, when nonzero, `A_hat=A_epsilon/epsilon_ampl`.
   - Preserve span ordering, pair/direction choices on ties, and all sample indices. The source suggests terminating small remaining spans below about 10% of the largest; do not adopt that optional approximation silently. Full sampled-rank extraction is the proposed first diagnostic.
5. Freeze the descriptor for the subsequent accumulation block. Recompute it on an explicit control cycle, not on every HCA substep (p. 3, steps 4–6 and right-column control-cycle discussion).

Required acquisition/algorithm gaps: pair selection for continuous versus sampled loops, tie/degenerate-radius behavior, recording resolution and source filter conflict. For arbitrary sampled loops, a global farthest-pair search is not the same as a covariance/PCA amplitude estimator. The source's harmonic examples (p. 8, Eqs. (19)–(20)) provide a separate test oracle, not permission to replace the span definition for all waveforms.

## 5. One accumulation block: kernel, histories and companion evaluations

### HCA kernel and history, visually checked

The accumulation rate is `D_acc = m f_ampl dot(f_N) f_p f_Y f_e f_pi` (p. 4, Eq. (7)). `m` is a **unit second-order direction**. Eq. (8) gives its proportional expression using source stress, Roscoe invariants and M. Normalize that expression explicitly; do not use the proportional expression's stress-valued magnitude as an extra amplitude factor. General 3D treatment of M/compression-extension choice and singular direction limits needs reconciliation before code.

For changing amplitude, use the history-dependent product in p. 7, Eq. (14), rather than substituting count N into constant-amplitude Eq. (11). With `a=f_ampl` and `b=a C_N1`, the combined scalar rate is

`r_N = b C_N2 exp(-g_A/b) + b C_N3`,

where `dot(g_A)=b C_N2 exp(-g_A/b)`; the constant-rate term is not added into persistent `g_A` (pp. 5–7, Section 2.4, Eqs. (13)–(14)). For constant amplitude during a block, Eq. (37), p. 12 gives

`Delta_g_A = b log[1 + C_N2 Delta_N exp(-g_A/b)]`.

This is an exact history increment for fixed amplitude under that scalar equation, not an exact update of stress, density, polarization or the full accumulation strain. A stable implementation should use `log1p`; zero amplitude makes `A_hat` and some printed ratios undefined and needs an explicitly derived limiting branch before admission. The existing paper-side scalar diagnostic chooses a zero-rate/history-increment limit; that does not resolve full `pi`/direction behavior.

The literal amplitude factor (p. 4, Eq. (9)) uses `(epsilon_ampl/epsilon_ref)^2` up to `1e-3`, and **100** above that threshold. Preserve the cap and threshold as printed; do not turn it into a generic `min(...,100)` if varying the reference amplitude, since that changes the formula. Source applicability is limited to small/moderate cycles; this literal algebra does not validate arbitrarily large amplitudes.

Other scalar factors: `f_Y=exp(C_Y Ybar)` (Eq. (15)); `Ybar=(Y-9)/(Y_c-9)`, `Y=-I1 I2/I3` (Eq. (16)); `f_p=exp[-C_p(p_av/p_atm-1)]` (Eq. (17)); density factor in Eq. (18), all p. 7. Appendix A pp. 14–15 defines **`I2=(T:T-(tr T)^2)/2`**, the negative of another common second-invariant convention. Do not combine the printed minus sign in Y with the opposite I2 convention. `I3=det T` requires a nonsingular stress domain or a separately justified limit. The original laboratory range of pressures must not be promoted to arbitrary stress-domain validity.

### Back-polarization memory, visually checked but representation unresolved

`cos(alpha)=A_hat :: pi` and `f_pi=1+C_pi1(1-cos(alpha))` (p. 10 Section 3.2; p. 11 Eq. (27)). For fixed amplitude and direction, Eq. (24), p. 10 gives `dot(alpha)=-C_pi2 alpha (epsilon_ampl)^2`; hence `alpha_out=alpha_in exp[-C_pi2(epsilon_ampl)^2 Delta_N]` while these inputs stay fixed. Eqs. (25)–(26) rotate `pi` toward `A_hat` in the higher-order tensor space. This is not a physical rigid-body rotation and is not equivalent to linearly blending two Mandel vectors.

A complete block must record how that rotation, scalar history and stress/density factors are coupled numerically. Freezing all `m,f_p,f_Y,f_e,f_pi` at the parent would give `Delta_epsilon_acc = m f_p f_Y f_e f_pi (Delta_g_A+b C_N3 Delta_N)`; **this is only a proposed frozen-factor diagnostic**, not the full manuscript algorithm when state and polarization evolve. Do not label it an exact accumulation update.

### Stress response and monotonic plasticity

Eq. (5), p. 3: `T_circle = E : (D-D_acc-D_pl)`, with all rates per cycle. The source uses pressure-dependent isotropic hypoelasticity, approximately constant Poisson ratio 0.2 and Young modulus proportional to `(p/p_atm)^(2/3)`. The absolute stiffness coefficient, full source-matched evaluation and initialization must be pinned rather than inferred from this proportionality.

Monotonic plastic stretching `D_pl` uses the Matsuoka–Nakai surface with associated flow, and the modified loading criterion `n:E:(D-D_acc)>0` (Eq. (6), p. 3; rationale p. 4 Section 2.2; invariant/yield definitions Appendix A pp. 14–15). It cannot simply be omitted for arbitrary combined monotonic/cyclic or spatially constrained problems. A no-`D_pl` material-point diagnostic must explicitly restrict to paths remaining admissible.

The companion hypoplastic law resolves recording/control cycles and initial state; it is not automatically evaluated in every accumulation substep. Conversely the accumulation-mode stiffness and Matsuoka–Nakai plasticity are not identical to replaying the companion law under tiny cyclic increments. Source mode handoff, complete companion-memory retention/reinitialization and constitutive state synchronization must be documented; source Section 4 does not by itself settle every API detail.

## 6. Initialization and source conflicts that must remain visible

### Recording-filter inconsistency

- **p. 12, Eq. (36):** recording condition printed as `cos(beta)>0.9` and `||epsilon_R||>1e-5`.
- **p. 13, Fig. 22:** drawing labels recording when `beta>10 degrees` and the same norm threshold.

These are not equivalent turning conditions. This packet does not choose a correction. Retaining all original samples avoids committing to either filter while source/code clarification is pending. Any later filtered mode must record its own exact rule, verify loop/amplitude refinement and distinguish its status from the printed original.

### Back-polarization representation / isotropic initialization

- p. 10 states `pi` and `A_hat` are unit tensors and gives the rotation construction.
- p. 11, Eq. (28) allows rank-one `pi=r outer r` for known vertical cyclic preloading.
- p. 11, Eq. (29) prints `pi_iso=J/3`; its preceding spectrum discussion explicitly has **nine** eigenvalue slots.
- Appendix A p. 14 distinguishes unsymmetrized fourth-order identity `J_ijkl=delta_ik delta_jl` from symmetrized identity `I_ijkl=(delta_ik delta_jl+delta_il delta_jk)/2`.

Literal `J/3` has unit Frobenius norm as an operator on all nine second-order components. Restricting it to symmetric six-dimensional Mandel space gives `I_6/3`, whose norm is `sqrt(6)/3`, not one. Silently replacing it with `I_6/sqrt(6)` changes `A_hat::pi`, the enhancement factor, and the subsequent rotation. Nor may the antisymmetric-sector components be dropped when they contribute to the source norm/rotation. This is a representation and initialization reconciliation gate, **not a confirmed typographical correction**. A general full-tensor representation or a source-justified reduced representation must be chosen and checked before an executable `pi` schema.

### Case-specific initialization is not a universal default

p. 13 sets `K0=0.43` and `g_A=0` for the particular freshly pluviated centrifuge sand. Back-polarization initialization is not established by that paragraph. Table 2, p. 14 does not list the polarization constants that appear in laboratory Table 1 (p. 9). Do not borrow a laboratory material's `C_pi1,C_pi2` silently, infer a global default from zero history, or claim the centrifuge case is fully specified by Table 2 alone. Table 3 is a **separate companion-law parameter set**; some parameters were adjusted using the second cycle (p. 13). Keep that calibration information visible in any validation split.

The complete source-aligned evolution of void ratio and its finite-deformation mass/strain bookkeeping remains to be extracted. The manuscript makes density an evolving influence, but this packet does not assign a new continuity closure merely because one exists in another Atlas model. Likewise the count/history handoff across resolved irregular/recording/control cycles must be specified explicitly; no implicit reset of `g_A` or `pi` at each block is justified.

## 7. Minimum next implementation-independent checks

1. Independent sampled-loop amplitude calculation: uniaxial in-phase loop, translated loop, orthogonal harmonic circle/ellipse, circulation reversal, rotated tensors with correct Mandel metric, zero loop, repeated samples and equal-span ties. Compare with source pp. 8 and 10 and expose convergence under within-cycle sampling refinement. Do not claim this tests every nonharmonic waveform.
2. Scalar fixed-amplitude history: Eq. (37) composition across subdivisions, nonnegative history, zero-amplitude limiting branch, a two-amplitude sequence, and invariance under shifting only the reporting count origin while preserving `g_A`.
3. Resolve the 6D/9D identity issue before testing isotropic `pi`; independently verify full tensor norms/contractions, alignment, orthogonal polarization change, constant-direction angle decay and zero-angle limits. Do not normalize away the conflict to make tests pass.
4. A frozen-stress/density/polarization scalar diagnostic can integrate the history factor exactly, clearly labeled as restricted. It is not a pseudo-creep/relaxation constitutive benchmark.
5. Pin accumulation stiffness scale and complete monotonic closure. Then define one controlled local point path with declared initial `T,e,g_A,pi`, measured/extracted amplitude, count interval, domains and an independent reference.
6. Only after these checks, propose a cycle-count API distinct from physical-time and recorded path-order modes. Count actual persistent components including companion histories. A symmetric 6×6 `pi` alone would occupy 21 scalar slots, but the unresolved full-space identity makes that count provisional; do not assert the present 32-component engine is sufficient.

This packet advances acquisition/extraction and representation design. Complete equation reconciliation, paper-version comparison, source/implementation permissions, continuous/discrete algorithm choice, independent scientific review, executable admission and source-matched experimental validation remain open.
