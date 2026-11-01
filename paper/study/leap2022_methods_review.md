# LEAP-2022 methods and processing review

Assisted development review, 31 October 2026. Sources: DesignSafe PRJ-3484,
DOI [10.17603/ds2-52dm-s780](https://doi.org/10.17603/ds2-52dm-s780).
The [machine-readable review](leap2022_methods_review.json) pins all five downloaded
assets. The [state transcription](leap2022_specimen_metadata.json) retains 54
printed test-state rows and candidate filename correspondences. Independent
scientific checking remains pending.

## Information recovered

- The report distinguishes post-consolidation void ratio and relative density
  from preparation measurements. Its symbol-list footnote says that, for tests
  with static shear, reported relative density includes the subsequent static
  shear stage (report PDF p.3).
- The preparation uses constant-height dry pluviation, a rubber membrane and
  Teflon-coated aluminium rings. Average preparation dimensions are diameter
  64.2 mm and height 23.5 mm; these are campaign averages, not individual
  post-consolidation dimensions (report PDF p.4).
- The loading sequence is vertical consolidation at 40 or 100 kPa, optional
  static shear with height free to change, then stress-controlled cyclic shear
  with vertical displacement constrained (report PDF p.5; setup PDF p.4).
  Applying the cyclic constant-height constraint during the preceding static
  shear stage would implement a different experiment.
- Reported axial strain combines material deformation and system compliance
  (report Sec.4, PDF p.12). It cannot be used directly as specimen volume strain
  or as proof of exact specimen-level constant volume.
- The sensor document identifies vertical/horizontal load cells, LVDTs and
  bender elements. It supplies an apparatus diagram, not sensor accuracy,
  calibration records or a compliance correction (sensor PDF p.1).

## State and identity qualifications

Tables 2-9 contain 54 test-state rows. All have a unique candidate in the
cached 54-file CSV listing using the filename's group void-ratio label,
vertical stress, CSR and static shear stress. This is a metadata correspondence,
not verified raw-acquisition or physical-specimen identity; CSV contents were
not opened.

In **42 of 54 rows**, the filename void-ratio token differs from the individual
table value. The tokens coincide with the rounded group-average void ratios
reported for the series. Preserve filename labels separately from specimen
state; do not initialize every specimen from its filename. This does not
establish whether a label describes a preparation value, nominal series value
or another state stage.

Table 7 tests 3 and 6 have incompatible printed void-ratio/relative-density
pairs: **0.604 / 68.2%** and **0.616 / 68.1%**. The stated index limits
emax=0.78, emin=0.51 imply central relative densities of about 65.2% and
60.7%. Incompatibility remains when allowing half a final printed digit for
both index limits, specimen void ratio and relative density. These are
source-table conflicts, not corrected states. Other overlapping rounding
intervals do not validate the measurements. The state stage of the dry-density
column is also insufficiently reconciled with post-consolidation void ratio
to treat their density/void-ratio relation as a same-stage measurement check.

## MATLAB source review

`CDSS_ResultsPlot.m` was inspected as text and was not executed.

| Source operation | Interpretation |
| --- | --- |
| `csvread(...,8,0)` (line 13) | Assumes eight leading rows are skipped; no CSV header was checked in this review. |
| Filename parsing (lines 14-20) | Extracts nominal e, vertical stress, CSR and static shear stress. The e variable is not used in the displayed plots. |
| `data(1:end-no,...)`, `no=10` (lines 23-28) | Drops the final ten numeric rows from all plotted channels; no reason is supplied. This is not an endorsed fitting-window rule. |
| Columns 1,2,3,5,6 (lines 24-28) | Plots cycles, shear strain, shear stress, axial stress and column 6. Axial strain in column 4 is unused. |
| Column 6 assigned directly to `ru` | The script labels it excess pore-pressure ratio without normalizing it. Sec.4 calls column 6 excess pore pressure. Units and pressure-reference timing remain unresolved without header/processing evidence. |
| `no2=5` and `1:no2:end` | Every fifth retained row is used in the second figure's histories; first-figure plots use all retained rows. No filtering, channel correction, compliance correction or threshold extraction is implemented in the inspected source. |

This source is a plotting recipe, not a complete raw-sensor processing chain.
Its conventions must not be applied retrospectively to the 2018 DSS release
without campaign-specific evidence. Reported axial stress is labelled vertical
effective stress in the script; that label alone does not prove a saturated
pore-pressure measurement or the equivalent-pressure interpretation.

## What changes for the paper

The 2022 campaign offers a candidate test of **density, overburden and static
shear transfer**, including a documented preloading path. That is a more useful
question than pooling curves into a universal cyclic-strength leaderboard.
Admission still needs resolved state/channel definitions and an independence
check; none is granted here. Published threshold summaries are derived outcomes,
not additional independent experiments.

The new documents do **not** close the earlier Ottawa DSS post-consolidation
state/reference-pressure questions, Ottawa torsion zeroing anomaly, KFS state
conflicts or Hostun strain-label conflict. GEOLAB's downloaded v2 change log
lists Darmstadt replacement data and Fontainebleau void-ratio corrections,
with no Hostun correction listed.

The report front matter, methods and summary tables were reviewed as text;
seven relevant pages were checked visually. Published threshold values and a
response-summary figure were exposed on those pages. Appendix response curves
were not reviewed. No raw CSVs were read, no MATLAB code was run, and no fits,
roles, admissions or shared atlas records changed. Clarification questions
remain logged and explicitly on hold; no contacts or copy requests were made.
