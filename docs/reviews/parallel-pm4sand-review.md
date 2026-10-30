# PM4Sand admission and capability review

2026-10-31. Bounded read-only technical review by a parallel Codex agent. No repository edits, builds, native execution, downloads, commits, independent-review promotion or redistribution of source PDFs. Recommendations are implementation tasks, not admission decisions.

## Selected variants and evidence boundary

| Stable catalogue ID | Selected author-listed identity | Pinned local documentary artifact | Admission scope |
| --- | --- | --- | --- |
| `pm4sand` | PM4Sand2D 3.3; Boulanger and Ziotopoulou; UCD/CGM-23/01; author listing mentions May 2024 revision | Vendor PDF, June 2023, 122 PDF pages; SHA-256 `59b94cf0ccc02beccc078fd0c612904692fb4635f75b0fc16efa314eeccd763e` | Plane strain using its published in-plane constitutive definitions |
| `pm4sand3d-1.0` | PM4Sand3D 1.0; Kippen, Boulanger and Ziotopoulou; UCD/CGM-26/01; author listing cites May 2026 | Vendor PDF, June 2026, 149 PDF pages; SHA-256 `6073a97a374d4b947e20a492b5009bbd01e3e5b0b773841b0f3b037c194f7453` | Separate 3D formulation and implementation contract |

Identity evidence: [version dossier](../models/pm4sand-versions.md), [manual receipt](../../catalogue/source-audits/pm4sand-manuals-2026-10-31.json), and manifest candidates at [2D](../../catalogue/manifest.json) and [3D](../../catalogue/manifest.json). Local PDF hashes were recomputed and match the receipt. The [2D vendor manual](https://itasca-software.s3.amazonaws.com/udm-library/Boulanger_Ziotopoulou_PM4Sand_v3.3_CGM-23-01.pdf) and [3D vendor manual](https://itasca-software.s3.amazonaws.com/udm-library/Kippen_et_al_PM4Sand3D_v1_CGM-26-01.pdf) remain distinct from the unverified author-linked Box editions. Do not silently label the vendor bytes the May 2024 or May 2026 revision.

Current repository status remains appropriate: both are non-executable candidates. The 3D Lode/surface fragment establishes only selected algebra. Existing documentary screening records describe the inspection scope at their creation; subsequent receipt/manual work supplements them rather than making their historical access-failure entries false.

This review visually inspected 2D PDF 21–22 (printed 16–17), 3D PDF 34 (printed 29), and 3D PDF 81–84 (printed 76–79). Additional section selection used existing local extracted text and the pinned repository audits; that material is not claimed newly reviewed equation by equation. No live author-page availability, licence or implementation revision was reverified.

## What can be transcribed next without an engine redesign

The [existing surface fragment](../../catalogue/source-audits/pm4sand3d-1.0-surfaces.json) covers `r-alpha`, normalized direction, Lode cosine, quarter-power `g`, current stress ratio magnitude and yield distance (3D Eqs. 15–18 and 23, printed 23–25/PDF 28–30). Its tests do not establish a complete flow, state law or numerical update. The [manual dossier](../models/pm4sand3d-1.0-manual.md) correctly limits its claims.

The best next small transcription is the **3D flow-direction fragment**, Eqs. 35–37, printed 29/PDF 34:

- `Rdev = B*n-C*(tensor_square(n)-I/3)`;
- `B = 1 + (3/8)*(c^4-1)/c^4*g^4*cos3theta`;
- `C = (3*sqrt(6)/8)*(c^4-1)/c^4*g^4`;
- `R = Rdev+D*I/3`, with `D` an explicitly supplied audit input at this stage.

These are visually verified source expressions. Existing DSL operations suffice. They must not be replaced by SANISAND-2004's different B/C expressions or rational g. For `c<1`, the displayed PM4Sand3D C is negative; copying SANISAND's positive C would change the law. Independent acceptance cases: c=1 gives Rdev=n; tr(Rdev)=0; tr(R)=D; compression/extension reduction; general Cartesian matrix-square oracle; oblique rotational covariance; dimension checks; and explicit zero-direction rejection. Add native/AD checks only in a later separately authorized verification step.

A source ambiguity should remain separate from this safe fragment: Table 3.1 step 7(b)(ii), printed 76/PDF 81, visually shows a stress correction involving `B*n*(n^2-I/3)` rather than Eq. 35's `B*n-C*(n^2-I/3)`. The existing dossier already flags this. Do not transcribe the algorithm expression literally or silently correct it without recording the conflict and a reconciliation source.

## Dimensional and kinematic scope

**2D is not a 3D law with an unused strain component.** The 2D manual Sec. 2.1, Eqs. 1–4, printed 16–17/PDF 21–22, explicitly uses a 2×2 in-plane stress tensor and `p=(sigma_xx+sigma_yy)/2`. It limits that implementation to plane strain. Eq. 6 on printed 17 still subtracts `epsilon_v/3` in the displayed in-plane strain components. Preserve and reconcile these definitions rather than substituting either an ordinary 2D trace-free strain projection or Atlas's full 3D stress deviator. Unsupported triaxial and arbitrary 3D paths must be rejected. A new explicit plane-strain state/control contract is needed; current `axisymmetric_x` support is not a substitute.

**3D has six Cartesian/Mandel stress components**, and Sec. 2.1 uses trace/3 (printed 20–21/PDF 25–26). Define the exact stress/strain sign and shear conversion at the boundary. In particular, initialization Table 3.3 uses FLAC3D's tension-positive stress/strain convention and negative compression pressure, while the general formulation contains positive-pressure square-root expressions. A local sign map must cover pressure, stress ratio, backstress and fabric, not just negate plotted stress. Reject finite-spin use initially; host rotation operations in algorithm step 22 do not give Atlas a large-strain capability.

## State, history and event requirements

Build a field-by-field inventory before an executable model. Distinguish physical/internal history, lagged numerical history, supplied inputs, effective resolved parameters and quantities that can be derived without changing chronology.

3D source anchors:

- Sec. 2.5, Eqs. 26–27, printed 26–27/PDF 31–32: reversal predicate `(alpha-alpha_in):n<0`; current and previous initial backstress; apparent initial memory using component extrema; separate true/apparent/previous distances for plastic modulus. This is richer than the one-memory SANISAND reset fixture.
- Sec. 2.8, printed 35–43/PDF 40–48: z, reversal z_in, cumulative fabric z_cum, peak fabric z_peak, pressure associated with fabric production, and further fabric/stiffness effects. PM4Sand's modified fabric law must not inherit SANISAND's dilation-rate equation unchanged.
- Table 3.3 steps 4–7, printed 79/PDF 84: current alpha; alpha_in, alpha_inP, alpha_inMin and alpha_inMax; z, z_in and z_alpha; pressure/fabric scalars; initial G, K, Kp and D.
- Algorithm steps 12–23, printed 77/PDF 82: ordered reversal detection, fabric/history update, new Lode shape, next-step material coefficients, strain accumulators, commit, optional rotation and post-shaking adjustment.

That table alone names nine tensor-valued records including stress, before scalars and lagged coefficients. This is a **storage audit trigger**, not a canonical independent-state count: identify aliases/derivable values and whether extrema tensors are actually trace-free before choosing a basis. Atlas currently has `max_state=32` ([tensor.hpp](../../cpp/include/atlas/tensor.hpp)); likely capacity pressure cannot be dismissed by reusing SANISAND's 25-component layout. Do not assume componentwise extrema of a deviatoric tensor remain trace-free.

The existing [parent-increment reset contract](../PARENT_INCREMENT_RESETS.md) supports simultaneous parent-snapshot assignments before internal integration. PM4Sand3D's displayed chronology includes post-update zone-level history and next-step lagging. Recasting all these operations as one pre-increment reset changes the update. An ordered discrete-update/history contract is an admission gap even if all scalar/tensor algebra fits today's DSL.

Events to specify explicitly: first initialization, FirstCall reinitialization, elastic/plastic branch, reversal, extrema updates, stress-ratio penalties/projections, fabric activation, dense/loose critical-state branches, and caller-selected post-shaking mode. Do not invent an elapsed-time trigger for post-shaking adjustments; Sec. 2.9, printed 44–45/PDF 49–50, describes user activation after shaking.

## Initialization is part of the selected variant

Table 3.3, printed 78–79/PDF 83–84, is the next bounded extraction after flow:

1. Map supplied host stress and its sign convention; record any tensile replacement or pressure bound explicitly.
2. Resolve apparent relative density and pressure-dependent relative state index, initial Lode shape, bounding/dilatancy ratios and Ado.
3. Apply and log any initial stress-ratio projection; initialize alpha consistently with the selected branch.
4. Initialize all reversal memories and fabric memories, including nonzero small seed values and pressure-associated history.
5. Resolve G, K, `Kp=100*G`, `D=0`, and the parallel shear-resistance properties.
6. Define FirstCall=0 reset semantics separately from ordinary constitutive updates and restarting a saved state.

Unresolved boundaries are visible in the simplified table: zero initial deviator leaves a normalized Lode invariant undefined; the dense/loose Ado expression needs a limit at the critical state; equality cases use strict inequalities; initial pressure notation and p_min bounds need reconciliation with implementation. Treat them as unresolved source/domain policies, not implicit epsilon floors.

A concrete DSL gap: Ado initialization uses inverse sine (printed 78/PDF 83). [atlas/dsl.py](../../atlas/dsl.py) has sin/cos but no inverse-sine primitive. Its emitted C++ `atlas::asin` name is the existing **sine** wrapper, not mathematical arcsine. Choose between a properly named, dimension-checked inverse-sine primitive with domain/AD tests and an explicit, versioned parameter-resolution stage. Do not hardcode the displayed default Ado as universal.

## Integration and host equivalence

The 3D manual Secs. 3.1–3.3, printed 70–73/PDF 75–78, and algorithm printed 76–77/PDF 81–82 specify a host-dependent explicit update:

- Subzones supply different deviatoric increments while volumetric behavior is mixed/averaged by the host.
- Zone-level D and Kp are computed at step end and used by all subzones in the **next** timestep.
- Drift/bounding penalties are applied before and after averaging.
- A parallel elastoplastic shear resistance has its own initialization and stress contribution; it is not automatically zero for a homogeneous material point.
- Constitutive substepping is absent in the documented implementation. Atlas midpoint/implicit adaptive integration would define another numerical variant unless separately derived and identified.

The immediate target should be a documented zero-spin homogeneous-subzone reduction with explicit lagged state and no claim of full FLAC3D equivalence. Full mixed-zone averaging needs its own adapter/reference experiment. A fixed single-point path refinement study is useful for its chosen update, but varying host loading rate also changes dynamic excitation; it does not by itself isolate integration error.

This model need not be declared physically time-dependent merely because FLAC3D uses dynamic timesteps. Preserve the distinction in [TEMPORAL_INTEGRATION.md](../TEMPORAL_INTEGRATION.md): rate independence, equation form, and numerical update are separate choices.

## Reference access and reuse boundary

Existing evidence identifies author-linked DLLs and the [author driver repository](https://github.com/katerinaziot/PM4Sand3D_drivers_auto), not an audited constitutive-source release. Driver generation/postprocessing does not establish constitutive-code availability or permissions. The local audit records no DLL download or execution. No conclusion is made here that source can never be obtained.

3D manual Sec. 3.4, printed 73–74/PDF 78–79, describes C++/Visual Studio 2019 and the FLAC3D 9.0/9.X UDM host, including `cmodelPM4Sand3D009.dll`. The 2D edition page identifies separate FLAC 8.1 and FLAC2D 9.00 binaries. Pin exact DLL bytes, metadata, architecture, host version and plugin configuration before source-matched execution. Independently record rights for manuals, DLLs, driver code, calibration files and any extracted numerical outputs. No redistribution permission follows from public download links.

If obtaining a reference requires contacting authors, prepare the questions first; do not send messages without explicit user authorization. Useful questions: exact May/June edition relation; errata for the stress-correction table; constitutive-source access/licence; matching DLL hashes; and prescribed homogeneous-element initialization/update ordering.

## Prioritized bounded work packages

| Order | Deliverable | Completion evidence |
| --- | --- | --- |
| 1 | 3D flow fragment Eqs. 35–37, building on existing surface fragment | Typed JSON with source locators; independent Cartesian/rotation/triaxial Python checks; no executable catalogue promotion |
| 2 | 3D state/event/lag inventory and initialization contract | Every field has shape, units, lifetime, source locator, dependencies, initialize/reset/commit timing; explicit 32-component-capacity calculation after dependency review |
| 3 | 3D source ambiguity ledger | Cross-check Section 2 versus algorithm step 7(b)(ii), initialization signs/zero/equality cases, fabric-update denominator expressions and table labels; preserve alternatives |
| 4 | Version and reference artifact reconciliation | Author/vendor byte comparisons, errata, exact host/DLL identity and per-artifact reuse record; no binary execution required for this documentary step |
| 5 | Homogeneous material-point update design | Explicit choice of continuous-law variant versus manual-matched lagged explicit update; parallel shear component and penalties accounted for; independent one-step hand cases |
| 6 | Separate 2D 3.3 extraction | Published in-plane operators and plane-strain controls, own history/init/integrator; no reuse of 3D calibrations or 3D admission credit |

Admission remains blocked by missing complete equations/history/init/domain/algorithm contracts and source-matched verification. The first two work packages can progress now using existing local sources, without builds or waiting for DLL access. Broadly implementing PM4Sand as a model-specific solver escape hatch should not be the next step.
