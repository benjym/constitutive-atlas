# Prior work: bounded comparison for the paper

Reviewed 1 November 2026. This is the first documentary screening for **PAPER-01**, which remains open. It covers eight relevant tools or projects selected in the [research charter](RESEARCH_CHARTER.md), not a systematic literature search. The [source register](../catalogue/source-audits/prior-work-2026-11-01.json) records eleven primary pages, section locators and limitations.

The evidence supports substantial overlap with Atlas's intended functions. A constitutive DSL, generated C++, material-point verification, calibration or online model comparison cannot by themselves justify a novelty claim. This conclusion concerns those broad functions; it does not establish equivalence between implementations.

## Documented capabilities and implications

“Unassessed” means this screening did not establish the capability or comparison. It does not mean another tool lacks it. No external software was installed or executed.

| Project | Documented overlap with Atlas | Implication and remaining comparison |
| --- | --- | --- |
| MFront / TFEL | Related DSLs describe material knowledge and translate it to C++; interfaces connect generated behaviours to solvers. [P01: overview](https://thelfer.github.io/tfel/web/index.html) | Constitutive code generation is established prior work. Compare representation semantics and supported equation classes before claiming a language contribution; expressiveness and runtime behaviour were not tested. |
| MTest | Material-point calculations allow component constraints on driving variables and stresses; histories, numerical tangent checks, reference comparisons and CI reporting are documented. Failed MFront integration steps can generate reproduction inputs. [P02: material point](https://thelfer.github.io/tfel/web/mtest.html) | Mixed controls, automated verification and reproducible failure inputs already have precedents. Compare precise preparation, event and rollback contracts on a pinned case; numerical equivalence remains unassessed. |
| MGIS | A generic interface retrieves behaviour metadata and integrates using beginning/end state, with support for groups of integration points. [P03: C++ library](https://thelfer.github.io/mgis/web/index.html) | A common state/integration API is established. Compare units, conventions, state ownership and error semantics explicitly; API compatibility was not evaluated. |
| OpenSees | The nDMaterial catalogue provides named model commands. The SANISAND-MS page documents a specific implementation and a cyclic drained triaxial script, including a distinction between its formulation and the cited publication. [P04: catalogue](https://opensees.github.io/OpenSeesDocumentation/user/manual/material/ndMaterial.html), [P05: SANISAND-MS](https://opensees.github.io/OpenSeesDocumentation/user/manual/material/ndMaterials/SAniSandMS.html) | Soil-model implementation and scripted element comparisons are precedents. Preserve exact variants: SANISAND-MS is not interchangeable with SANISAND-2004. A source-to-source equation crosswalk remains unassessed. |
| numgeo | Versioned tutorials include oedometer, monotonic drained/undrained triaxial, unloading/reloading and cyclic element tests. [P06: 2026-09 tutorials](https://j-machacek.github.io/numgeo/2026-09/tutorial/index.html) | Laboratory element-test reproduction is established. Select a matching model, preparation and controls before any comparison; no tutorial was reproduced here. |
| numgeo-ACT | Calibration uses numgeo simulations. Laboratory documentation describes Excel metadata, selectable tests, candidate-parameter curve comparisons and weighted objectives. [P07: overview](https://j-machacek.github.io/numgeo-ACT/), [P08: laboratory tests](https://j-machacek.github.io/numgeo-ACT/laboratory-tests/index.html) | Automated multi-test calibration is established. Any future Atlas comparison must declare fixed/fitted inputs, objective and information budget. Optimizer or fit superiority is unassessed. |
| SoilModels | Its constitutive-model directory distinguishes numerous named families and extensions. [P09: database](https://soilmodels.com/constmodels/) | A soil-model discovery catalogue is established prior work and a useful inclusion lead. Individual entries require source/formulation checks; this screening does not assess repository completeness or executable coverage. |
| ExCalibre | Project documentation describes online calibration and a laboratory element-test driver. Its January 2023 announcement documents simultaneous model predictions on shared graphs and fixing selected parameters during optimization. [P10: project](https://soilmodels.com/excalibre/), [P11: dated announcement](https://soilmodels.com/new-features-in-excalibre/) | Online soil-model exploration and multi-model comparison are established precedents. Current service availability, full supported-model coverage and numerical results were not tested. |

These are documentary observations. Except for the versioned numgeo tutorial path and dated announcements, the URLs identify floating documentation, not frozen releases. The source register contains reading notes rather than archived webpage bytes. Recheck and archive permitted evidence before a publication comparison is frozen.

## Atlas's defensible scope today

Atlas has an [explicit formulation contract](FORMULATION_CONTRACT.md), a shared [code generator](../atlas/compiler.py), and a [portable TMD2 benchmark packet](benchmarks/kfs-tmd2-portable-v1/README.md). The [website snapshot](reviews/tmd2-web-snapshot-v1/README.md) links a plotted result to archived inputs. These are concrete project artifacts, not evidence that the approach is unique or scientifically admitted. [Current status](STATUS.md) retains pending source, historical-coordinate and independent-review limitations.

Potential contributions to investigate are:

- Traceable links from a publication variant and equation locators to conventions, state, preparation, executable definitions and plotted evidence.
- Reproduction across native and browser execution using frozen inputs, acceptance policies and retained failures.
- Comparisons that disclose inherited and fitted parameters, calibration information and applicability limits.

These are contribution hypotheses. This screening has not established that other projects lack those combinations, nor that Atlas implements every part completely. Shared-backend agreement does not independently verify the equations.

A suitable working description is **an auditable geomechanics model atlas and reproducible comparative study**. Avoid claims of a first constitutive language, first online comparison, new constitutive law, superior numerical performance or exhaustive literature coverage.

## Primary-publication follow-up

The [MFront/MGIS primary-text comparison](reviews/prior-work-mfront-mgis-v1/README.md)
adds section-located reading and reusable bibliographic records. MFront's SIRIUS
example means source-linked law storage and review procedures also have a direct
precedent; the traceability hypothesis above is not an established distinction.
The author manuscript and published MGIS PDF have different access/preservation
boundaries, recorded in that packet. No executable comparison or superiority
claim was made. This supplements, rather than revises, the historical eleven
project-document reading notes.

## Remaining PAPER-01 work

1. Extend the literature search to peer-reviewed software and comparative-method papers, record search dates, inclusion boundaries and model/data repositories, and inspect full texts for claimed distinctions.
2. Select exact comparator releases and a small common formulation/protocol. Freeze convention, initialization and parameter mappings before collecting results. Software execution needs its own bounded task.
3. Review the comparison independently and align proposed claims with the admitted release evidence. Keep M1–M3 source, representation and experimental-review gates in force.

This document completes only **PAPER-prior-work-v1**. It adds no numerical results, admissions or release gate, and does not modify the manuscript work in `paper/`.
