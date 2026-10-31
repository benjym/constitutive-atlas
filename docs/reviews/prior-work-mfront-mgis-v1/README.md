# Primary MFront/MGIS publication comparison — v1

1 November 2026. This closes one bounded primary-text comparison for PAPER-01,
not the wider prior-work search or a novelty assessment. It supplements the
[earlier eight-project screening](../../PRIOR_WORK.md) without changing its
historical eleven-source register or the unrelated manuscript tree.

## Sources and reading boundary

**F01:** Helfer et al. (2015), [MFront publication](https://doi.org/10.1016/j.camwa.2015.06.027).
Selected §§2.3, 2.4.3, 2.5 and 2.7 were read in the
[author-uploaded manuscript web text](https://www.researchgate.net/publication/282801181_Introducing_the_open-source_mfront_code_generator_Application_to_mechanical_behaviours_and_material_knowledge_management_within_the_PLEIADES_fuel_element_modelling_platform).
The publisher route was blocked; the author PDF link failed. No PDF bytes,
page-image inspection, equation transcription or identity with the published
version is claimed. Section locators refer to that manuscript, not journal pages.

**F02:** Helfer et al. (2020), [MGIS paper](https://doi.org/10.21105/joss.02003).
The published eight-page PDF was downloaded privately and hashed. Relevant body
sections were read as text; pages 1–4 were rendered and visually inspected.
The first-page archive hyperlink is retained as a lead, not an inspected software
release. [sources.json](sources.json) records versions, exact locators, access
failures and the private PDF identity. [references.bib](references.bib) provides
reusable citations. Neither paper identifies current 2026 runtime behavior.

## Source-supported overlap

| Topic | Primary-text observation | Locator |
| --- | --- | --- |
| Generation | MFront uses C++-based descriptions and generated algorithm/interface code. | F01 §2.3 |
| Integration/tangent | Implicit residuals, Jacobian alternatives and consistent-tangent computation are discussed. | F01 §2.4.3 |
| Material-point workflow | MTest supports component stress/strain constraints, tangent/reference checks, calibration embedding and failure reproductions. | F01 §2.5 |
| Knowledge/evidence | SIRIUS stores laws and references; expert assessment addresses document consistency and experimental results. | F01 §2.7 |
| Metadata/state | MGIS retrieves behavior/hypothesis metadata for checks, allocation and state access. | F02 pp2–3 |
| Integration API | Single/batched material-point integration and C++/Python/Julia/Fortran/C access are described. | F02 p3 |
| Geomechanics | The OGS example uses nonassociated Mohr–Coulomb with a tension cutoff. | F02 p4, Figure2 |

These establish relevant precedents. They do not establish numerical agreement
with Atlas, an equivalent formulation, or the absence of Atlas-like capabilities
elsewhere. In particular, do not treat the OGS example as the same uncapped law
or reuse its figure as an Atlas reference without a separate mapping.

## Consequences for the Atlas paper

Do not claim the first constitutive DSL, generated C++ material engine, generic
material interface, source-linked law database or automated material-point
verification workflow. The earlier traceability hypothesis must account for
SIRIUS; a database plus review procedure is insufficient evidence of distinction.

Atlas's testable contribution questions concern the admitted geomechanics
collection, explicit formulation/input contracts, and an auditable chain from
source interpretation through numerical and experimental evidence to browser
execution. Whether that combination is distinctive remains unproven. Compare
with the existing [formulation contract](../../FORMULATION_CONTRACT.md),
[accepted-update derivative scope](../../UPDATE_LINEARIZATION.md),
[record contract](../../EVIDENCE_RECORDS.md) and
[KFS development qualifications](../../benchmarks/kfs-development-review-v1/README.md).
The schema's declared semantics are not evidence that every record was faithfully
transcribed or that all execution paths are equivalent.

Working related-work paragraph, subject to manuscript/scientific review:

> MFront and MGIS are important precedents for reusable constitutive software.
> Atlas should be assessed through the fidelity and coverage of its geomechanics
> records, explicit assumptions, and reproducible evidence connecting source
> interpretation to material-point and browser results. Its present development
> comparisons are qualified evidence, with pending independent review. No
> general software, performance or scientific superiority follows from a common
> representation alone.

## Smallest remaining comparison

Before any executable comparator study, select an exact archived release and
one shared formulation, then freeze units, signs, tensor order/shear scaling,
initialization, loading coordinates, controls, integration settings, failure/
rollback behavior, tangent meaning and output tolerances. Start with a fully
mapped elastic case; do not start with differently capped plastic variants.
This is a future study requirement, not a frozen protocol or authorization to
install/run competitor software. No benchmark, build or performance observation
was collected here. Broader literature coverage and independent review remain
PAPER-01 work.
