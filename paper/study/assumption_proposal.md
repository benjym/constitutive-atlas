# Proposed assumptions for development analyses

Status: **core A01-A07 approved and activated for development**, 31 October 2026.
Optional scenarios B01-B02 remain pending. Approval recorded from the user reply "Yes" to the recommended core package; no optional-scenario approval inferred.
This proposal changes how development analyses may proceed, not what the
experimental sources are claimed to establish. Source conflicts remain logged.
No author contact, source-file correction, new final split or performance
ranking is authorized by this proposal.

## Approved core package

| ID | Approved development decision | Scope and consequence | Required sensitivity or limitation |
| --- | --- | --- | --- |
| A01 | Use numerical-file initial void ratio as the primary KFS development state where available. Retain original-table values as a separate scenario. For LEAP-2022 use individual report eac, never filename/group-average e. | Resolves a reproducible analysis convention, without declaring a source corrected. Existing KFS file/table diagnostics remain intact. | Compare KFS original-table and file states at fixed parameters. Do not select the convention by experimental fit. LEAP-2022 Table7 tests3/6 remain excluded from primary quantitative use. |
| A02 | Begin the Ottawa development panel with the32 LEAP-2022 tests having zero initial static shear (Tables2-6). Defer all22 static-shear tests. | Avoids an unobserved pre-static-shear state/history. The32 histories are candidate records, not32 independently verified physical specimens or newly admitted benchmarks. | Verify headers, units and file/state correspondence before replay. First pilot candidate is Table3 test1 (40kPa, CSR.15, eac.603), chosen by table order, not prediction error; no execution before approval and implementation checks. |
| A03 | At the start of zero-static-shear DSS, assume equal horizontal effective normal stresses with K0=.50 and zero shear stress. | Supplies the otherwise missing full initial effective-stress tensor for an idealized material-point experiment. K0 is imposed only at initialization; horizontal stresses subsequently evolve under the prescribed kinematics. | Repeat at K0=.35 and.65, plus1.0 as an isotropic diagnostic, with identical material parameters. Values are analyst-selected scenarios, not measured values or statistical bounds. Use the same scenarios across models; do not compute a different primary K0 from each fitted model's friction angle. |
| A04 | Treat cyclic DSS as ideal simple shear with constrained normal strains, following the documented constant-height/ring intent. Use the individual eac as the start-of-cyclic-shear density for the32 zero-static-shear tests. | Permits an explicitly idealized constitutive calculation. It does not assert perfect specimen-level constant volume in the apparatus. | Do not fit combined apparatus/specimen axial strain as volumetric strain. Assess prediction sensitivity to state/control assumptions; an uncorrected apparatus mismatch stays in the limitations and cannot automatically be attributed to model physics. |
| A05 | Use axial/vertical stress as the normal-response observable. If a stress-loss channel is algebraically verified, label it equivalent vertical-stress loss. | Avoids inferring a measured saturated pore-pressure history. Stress and its algebraically dependent loss are one objective family. | Do not score column6 until its actual header, units and normalization have been checked. A plotting ylabel is insufficient. No liquefaction/pore-pressure claim follows just from a normal-stress decrease. |
| A06 | Preserve all valid numeric acquisition rows for the primary analysis. Treat the source script's final10-row removal as a display convention, with a separate last10-rows-omitted sensitivity. Use cycle coordinate only as an ordered loading coordinate for rate-independent models. | Makes endpoint treatment reproducible without guessing the author's reason. Physical time is unnecessary for rate-independent path replay. | File-format validity checks precede use; retain partial cycles and report censoring. No interpolation of a physical frequency, rate dependence or creep inference. Do not copy the script's every-fifth-row plotting reduction into fitting. |
| A07 | Keep source campaigns as conservative dependency blocks and all phases/aliases/summaries of one specimen together. | Permits descriptive and conditional development comparisons without claiming unverified cross-campaign independence. | No cross-campaign pooling as independent replicates, specimen bootstrap or unseen-data claim until independence and exposure limits are addressed. This proposal does not change reservations. |

For oedometer initialization, K0=.50 with the same declared scenarios can be
used as a common comparison convention. Jaky's relationship can be a separate
published-convention sensitivity using an explicitly fixed, source-pinned
material friction angle. It must not become a model-specific fitted advantage.
A primary published numerical example uses Jaky and vertically mobilized
intergranular history, but does not measure the original specimen state:
[Machaček et al., Sec.2.3](https://doi.org/10.1002/nag.70375).
The current compression start/coordinate sensitivities remain in force; this
proposal does not resolve finite-strain scope or authorize arbitrary history resets.

## Optional additional scenarios

These provide exploratory calculations only and are not part of the recommended
primary panel. Approval can cover the core alone or core plus these scenarios.

| ID | Proposed scenario | Qualification |
| --- | --- | --- |
| B01 | For LEAP-2018 DSS, provisionally use the report preparation void ratio as start-of-shear e. Repeat with e reduced by.01 and.02 at fixed parameters. | These represent zero, modest and larger unmeasured densification scenarios, not confidence limits. The two ambiguous CSR.105 files remain omitted from specimen-state comparisons. Report conclusions only as conditional on assumed density; the actual post-consolidation state stays unknown. |
| B02 | For Ottawa torsion metadata only, adopt Gs=2.65 from the Ottawa literature and compute e=Gs*1000/rho_d-1. Compare Gs2.64 and2.66. | Borrowed material property, not campaign measurement. Preserve workbook density limits1491/1757kg/m3 and the article's1490.5/1757 alternative. This enables void-ratio scenarios but does not admit the torsion response curves or repair zeroing. |

## Gaps to retain rather than guess

- **Torsion zeroing:** do not replace the common-baseline source formulas by a
  guessed channel-specific correction and call the result experimental truth.
  Any future reprocessing would be a separately versioned reconstructed dataset,
  requiring its own validation. Full physical scoring remains deferred.
- **Hostun strain coordinate:** do not assume shear strain equals axial strain,
  or multiply by a guessed fixed factor. Missing volume histories cannot be
  reconstructed from peak dilation angles. Keep affected curves outside primary
  strain/dilatancy scoring.
- **LEAP-2022 static-shear tests:** do not initialize a cyclic calculation from
  post-static-shear density while silently erasing stress/fabric history. Defer
  their quantitative use until a separate preloading reconstruction is specified.
- **Internal model history:** zero or mobilized intergranular/fabric states are
  additional model assumptions. Each exact model must have a reviewed,
  model-specific initialization and an appropriate history sensitivity before
  physical interpretation. No universal history value is approved here.
- **No calibration-information shortcut:** a pilot can test file adaptation,
  controls and numerical completion before Ottawa parameter calibration is
  complete. It cannot establish physical accuracy using parameters silently
  borrowed from another sand. Model implementation, calibration-information and
  numerical-refinement gates still apply.

## Rules for reporting

Mark measured, adopted and assumed quantities separately in every run manifest.
Freeze assumptions before looking at model-comparison outcomes. Run the same
predeclared state scenarios across models, retain failures and report reversals
of conclusions. Sensitivity scenarios are not error bars or distributions.
If a mechanism benefit disappears or changes sign under plausible initialization
choices, report it as assumption-dependent; do not publish an unconditional rank.
Synthetic solver tests establish numerical behavior, not the correctness of an
assumed experimental state.

Approval would authorize activating the selected package in paper-only
development configurations and progressing through their existing execution
gates. It would not remove unresolved source questions, authorize contact,
change shared atlas records or grant final benchmark admission.
