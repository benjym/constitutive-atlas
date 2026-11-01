# Independent original-source and contract review v2

Review ID: REVIEW-lade-duncan-original-v2. Reviewer run: `/root/lade_source_review`, 2026-11-01. This separately dispatched run did not author the core source packet or its algebra checker. Scope: original-source identity, complete available equation/table inventory, conversion and proposed integration pitfalls; existing interpreter/type capability probes. **This is not E5, an accepted model checklist, candidate qualification or model approval.**

## Verdict and exact source

The original-source access blocker is resolved. I independently read the supplied original through all seventeen rendered pages, including the title, Equations1–19, Table1, Figures1–8 and reference appendix. The title/authors, October1975 issue and article pagination agree with DOI10.1061/AJGEB6.0000204; the attachment's filename year2021 does not identify a revision. Attachment and retained private copy both hash to `bdebd928dbe9e4bac47c0a0328ed0bab79ab3e440a25390f1d646e9ed3749fc5`. The first-page upper left carries article number11670; the footer and following printed pages establish1037–1053. No later1977 equation was substituted.

I inspected `/tmp/lade-original-inspection/full-01.png` through `full-17.png` with the PDF skill; embedded OCR was only navigation. The hashed private PDF, rather than temporary images, is the authoritative source. No copyrighted originals, images or complete extracted text are added to the public packet. Earlier unavailable-source findings remain true historical observations, superseded only for current access.

The frozen core packet accurately inventories the available source and its explicit silences. All Table1 entries and the equation/page locators in its crosswalk agree with the original. Relative links to identity-v1, the separate1977 receipt, schema and formulation contract resolve structurally; no clerical locator/path correction is requested. The source-level inventory is suitable for an E1 handoff. E2 remains open: the actual proposed model must freeze mechanical-stress scope, pressure evaluation/discretization, history initialization and repeated-minimum numerical/tangent behavior. These are bounded project interpretation and qualification work, not proof that no implementation is possible.

## Independent findings

1. **Engineering shear and work are consequential.** Printed Eq9 on1043 differentiates with respect to the six independent stress coordinates; the shear rows contain2. Eq14 on1046 uses six-vector work, and Eq15 uses Euler's3g identity. Reading the source shear strain entries as engineering shear makes those equations mutually consistent. Tensor strains therefore have half those off-diagonal entries; their Mandel entries are source engineering entries divided by sqrt2 and reordered from yz,zx,xy to xy,yz,xz. The source does not explicitly label every entry gamma, so retain the packet's explanation that this is a conjugacy interpretation. Our exact witness reproduces every component using polynomial differentiation, verifies work=3g and covariance under a rational rotation. Treating the factor2 entries as tensor shear fails both work and rotation covariance; that counterexample is retained.

2. **Freeze κ2 only in the potential derivative.** Eq7 explicitly treats κ2 as constant for a given f. Eq12 supplies its updated value, not permission to differentiate the composition κ2(f(S)) when constructing the source flow direction. Substituting it first simplifies the scalar potential to `(1-A)(I1^3-27I3)` and changes the direction of its gradient, despite preserving the scalar value. Our witness demonstrates nonparallel directions. This does not prohibit differentiating the completed constitutive residual through its coefficient evaluation when constructing a solver Jacobian; the two operations serve different purposes.

3. **Pressure-dependent hardening needs an explicit interpretation.** Eqs13/16 describe a Wp–f curve, but Eq17 changes its fitted coefficient with pressure. The derivative of `Wp=a*x/(1-d*x)` at fixed a gives Eq19. Its total derivative when a varies adds `x*da/(1-d*x)`. The paper's literal Eq19 lacks that term, and page1050 explicitly predicts only elastic strain for proportional stress changes with constant f. Therefore the packet's proposed local Eq19 interpretation, without imposing a global current-pressure algebraic Wp constraint, is defensible and respects the stated neutral-loading behavior. It still needs a declared pressure sampling rule and refined varying-pressure reference study. This is an interpretation to record and qualify; a separate author clarification or new human scientific permission is not intrinsically required.

4. **General pressure is not just a fixed test constant.** The paper uses sigma3 as both least principal stress and experimental confining pressure. Replacing it by a fixed cell pressure outside those tests silently changes Eqs2/17. Current least principal stress is a reasonable explicitly disclosed3D embedding; it has nonsmooth dependence at repeated minima. A fixed preparation-pressure variant would need its own declared identity/scope and source reconciliation. Neither implementation can be inferred merely from a pressure parameter label.

5. **Retain the prior maximum and threshold separately from current f.** Page1042 holds the yield surface at the maximum previously reached stress level on unloading/neutral loading; page1046 adds a threshold below which plastic work is set to zero. Reloading inside the retained surface is elastic even when df>0. Updating h from current f after unloading erases memory. A finite step crossing ft or prior h must count only newly reached plastic excursion, with the selected event/substep scheme. An explicit prepared example may choose `h=ft,Wp=0` after isotropic consolidation as a relative shearing reference, but must not assert arbitrary state/history compatibility from current stress alone.

6. **The paper supports pre-failure illustration, not an invented continuation.** f=κ1 is the failure condition, while the fitted hyperbola asymptote lies beyond it. rf<1 makes the Eq19 denominator finite at that event; it does not authorize post-failure softening, a perfect-plastic branch or continuing past failure by the same fit. Stop/reject at the qualified event unless a separately identified extension is supported. Hydrostatic f=27 gives g=0 and zero potential gradient; the elastic/threshold branch must bypass the plastic division.

7. **Host conventions remain project decisions.** Positive compressive stresses/strains and negative expansion are evidenced by the figures. Additive strain and fixed Cartesian equations support the disclosed infinitesimal, zero-spin restriction. Rotating principal stress directions in torsion is not a finite-deformation objective-rate prescription. The article has no pore-pressure evolution, general effective/total decomposition, arbitrary preparation constructor or transaction algorithm. A bounded zero-pore-pressure/drained mechanical embedding can resolve a v0.3 stress binding, but the model must name it explicitly and cannot claim coupled or undrained delivery. No broad experimental validation follows from the original author plots.

## Reproducible minimum-operation limitation

The existing generic DSL already offers spectral minimum primitives; claiming that minimum evaluation is wholly missing would be wrong. The exact current limitation is demonstrated by `check_spectral_contract.py` and its retained results. At source-normal triaxial compression stress `(100000,60000,60000,0,0,0)`Pa:

| Probe | Observed result |
| --- | --- |
| `principal_min(sigma)` | `ValidationError: selected_eigenvalue_unresolved` |
| `principal_min_value(sigma)` |60000Pa |
| `principal_max(sigma)` |100000Pa |
| `principal_min_repeated(sigma)` |true |
| Synthetic v0.3 residual using ordinary minimum |Type validation passes; repeated-minimum primal evaluation above still rejects |
| Synthetic residual using `principal_min_value(sigma)` |`ValidationError: sigma: equation shape or dimensions mismatch` |
| Synthetic residual using `principal_min_value(sigma_n)` |Same rejection; value-only numeric dependency is disallowed even from this committed-state expression |

The synthetic equations are in-memory type carriers based on an existing elasticity record, not a Lade model and not changes to that record. No compiler/generated/native/Wasm call was made. The test stress has repeated minimum already in an elastic region, where Eq2 still needs pressure. The problem is therefore not limited to an obscure plastic corner. A differentiated minimum's absence at ties is mathematical; rejection of every admissible triaxial state is a current numerical-contract limitation, not a source domain bound.

The coordinator proposed the following lazy expression, which I independently evaluated at hydrostatic, triaxial compression/extension and distinct diagonal states; it returns the correct values and passes complete synthetic v0.3 residual type validation using existing DSL only:

```
select(principal_min_repeated(sigma),
       select(principal_max_repeated(sigma), trace(sigma)/3,
              (trace(sigma)-principal_max(sigma))/2),
       principal_min(sigma))
```

At an exact repeated lower pair it selects derivative `(I-Pmax)/2`; at a hydrostatic triple it selects `I/3`. These are averages of rank-one projectors in the minimum eigenspace, hence permissible Clarke generalized gradients of the minimum. They are not the unique classical derivative, actual directional derivative or necessarily an element of the limiting B-subdifferential. For example, at `S=diag(100,60,60)` in direction `H=diag(0,1,-1)`, the one-sided minimum derivative is−1 while the selected average contraction is0. That exact counterexample is retained. This policy does not by itself guarantee Newton convergence or invertibility of the completed residual's chosen Jacobian.

**Bounded policy assessment:** this is an acceptable explicit generalized branch policy to take into an isolated candidate and prospectively frozen nonsmooth qualification. It removes the need to declare a missing generic minimum operation or require a shared-runtime edit merely to start transcription. It does not make E4 numerical gates pass in advance. Near-but-distinct unresolved gaps can still raise numerical failure under the existing spectral isolation policy; preserve that diagnostic rather than calling it a physical domain boundary. Do not perturb stress, round apart a tie, export a value-only quantity as a differentiable residual, or promise a unique classical minimum derivative.

The smallest next handoff can therefore be model-local: declare this branch policy together with pressure sampling and the local Eq19 interpretation, freeze independent stress-driven references and acceptance metrics, then transcribe an isolated v0.3 pre-failure candidate under coordinator ownership. A separate generic capability task is needed only if those concrete checks demonstrate a genuine deficiency.

Acceptance criteria for that handoff: retain the normal triaxial witness above and an active-plastic witness `(180000,60000,60000,0,0,0)`Pa; include hydrostatic starts, extension, off-diagonal Cartesian rotations, coordinate permutations, and approaches to a tie from both sides. Require correct pressure values, explicitly declared selected/generalized or directional tangent behavior, finite useful updates for both Table1 examples, refinement against an independent stress-driven reference, and failure/rollback/recovery without state mutation. Preserve nonsmooth diagnostics. Freeze exact inputs, references, derivative metric and tolerances before compiled observation. Broader native/Wasm qualification belongs to E4 under the coordinator's serial build handoff.

## Evidence and disposition

`review-receipt.json` binds the frozen five core files, source bytes, exact reviewed runtime files, this report and the four reviewer scripts/results. The lead's frozen checker records15 source-algebra checks passing; I inspected its independent cubic-difference construction and the report. My separate exact-rational script checks conjugacy/covariance and retains contrary-interpretation witnesses; the spectral script records current actual interpreter/type errors. None is a finite stress-update reference or backend/model acceptance. I did not run or promote the earlier catalogue suite; its two historical failures remain separate evidence.

Reproduction from the repository root:

```
python3 -B docs/ingestion/lade-duncan-1975/delivery-v1/supplied-original-v2/independent-review/check_algebra.py
python3 -B docs/ingestion/lade-duncan-1975/delivery-v1/supplied-original-v2/independent-review/check_spectral_contract.py
```

Disposition: E1 readable-source blocker resolved and complete available inventory supported. No core source correction requested. E2 choices and spectral qualification remain open. No candidate exists in this review, so E3–E8, model approval and Atlas experimental validation are unestablished. The coordinator should continue with a model-local contract/candidate task using the explicitly reviewed repeated-pair branch policy and a prospective stress-driven reference, not request the original paper again or close the delivery umbrella. A shared runtime change is not a prerequisite established by this review.
