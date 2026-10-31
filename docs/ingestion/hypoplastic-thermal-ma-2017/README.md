# hypoplastic-thermal-ma-2017 - ingestion packet

Task ID: ING-hypoplastic-thermal-ma-2017
Owner / date: review_sanisand / 2026-10-31
Scope: exact-source acquisition, displayed-equation/parameter crosswalk and bounded thermal-input/integration inventory. All ten equations in the institutional accepted manuscript were visually inspected. This packet does not close the cited mechanical host or add an executable/admitted model.

## Identity and sources

Q. J. Ma, C. W. W. Ng, D. Mašín and C. Zhou (2017), **An approach for modelling volume change of fine-grained soil subjected to thermal cycles**, Canadian Geotechnical Journal 54(6), 896-901, [DOI10.1139/cgj-2016-0459](https://doi.org/10.1139/cgj-2016-0459). [PolyU archive](https://ira.lib.polyu.edu.hk/handle/10397/95203) identifies its PDF as the accepted manuscript; [direct institutional PDF](https://ira.lib.polyu.edu.hk/bitstream/10397/95203/1/Approach_Modelling_Volume.pdf). Crossref and archive say June2017; a Scholars Hub Jan1 date is not evidence of a manuscript revision.

The privately acquired PDF is 27 pages, 1,318,429 bytes, SHA-256 `c9e190d2315a76db158a072a7859781ec1be24868bae28a08af96a0c3ec0df39`. PDF/printed pages8-11 contain Eqs1-10, page21 Table1, page22 Figure1. Those pages were rendered and visually inspected under the PDF skill; extracted text was used for navigation only. The accepted manuscript has a repository-added pre-published notice and PDF metadata from2022; neither establishes a new constitutive version. Do not relabel it final publisher PDF.

The source explicitly delegates the host to Mašín (2005), DOI[10.1002/nag.416](https://doi.org/10.1002/nag.416), and Mašín & Khalili (2012), DOI[10.1002/nag.1058](https://doi.org/10.1002/nag.1058). The [author bibliography](https://web.natur.cuni.cz/uhigug/masin/bib/DMbib.htm) provides a [May9,2011 submitted preprint](https://web.natur.cuni.cz/uhigug/masin/download/MK_IJNAMG11-pp.pdf) of the latter. That dependency PDF was privately pinned: 52 pages, 806,815 bytes, SHA-256 `26bb19e1fbeb3b9891e2b7f3bfd40b5405847f53b92638a114202f5565417265`. Relevant thermal/void-rate and final saturated thermal-tensor pages were visually checked; this is not a complete host audit or final2012 comparison.

[source-receipts.json](source-receipts.json) records exact private paths, routes, hashes, versions and inspection scope. Twenty top-level Downloads PDFs were screened over their first two text pages for the exact title/DOI/thermal-cycle terms; none matched. This bounded check is not a claim about all files or embedded archives. Direct DOI/publisher PDF routes returned403 in this session; direct institutional acquisition succeeded despite web-tool PDF timeout. SoilModels exposes a login-gated preprint/package route, not an inspected author implementation. No login bypass, code-package execution or third-party contact occurred.

Rights remain with authors/institution according to the archive. Only original commentary, typed algebra inventories and independent diagnostics are included here; private PDFs, extracts, renderings and route HTML are excluded. Public availability does not establish redistribution permission.

## Existing work and gaps

The discovery entry is in [catalogue/manifest.json](../../../catalogue/manifest.json); prior triage [C3](../../reviews/parallel-candidate-triage.md) lacked a matching primary receipt. This packet establishes exact identity and readable source. The existing2013 explicitly-asymptotic-state and2014 anisotropic clay research models are different mechanical hosts; their equations cannot be substituted for2005 by matching a hypoplastic family name. This thermal-cycle law is also distinct from VIBE2026 and from a general unsaturated THM model.

## Equations and schema crosswalk

[equation-ledger.json](equation-ledger.json) contains every displayed2017 equation, source locators, units, parameters and Table1 rows. These are mathematical source notes, not a valid production model schema.

| Source locator | Quantity | Required representation / status |
| --- | --- | --- |
| M17 p8 Eqs1-3 | Temperature-dependent NCL | Scalar dimensionless `N(T)`, `lambda(T)` and log-specific-volume; pressure ratio uses reference1kPa =1000Pa. |
| M17 pp8-9 Eqs4-5 / Fig1 | TSL anchored by `p_o,e_o`, slope `kT`, additional shift `cT*nT*log(T/Tr)` | Dimensionless log volume; positive pressure anchor. Anchor reset/update lifetime is not given. |
| M17 p9 Eqs6-7 | Anisotropic NCL through `Nstar`, `pSBS` | Exact radial SBS mapping from selected2005 host. Isotropic `p_o=pSBS` recovers Eq1. |
| M17 p10 Eqs8-9 | Jaumann effective stress rate | Symmetric tensors, Euler stretching, compression-positive; full `fs,L,fd,N_tensor,H_T` supplied by exact host. |
| M17 p11 Eq10 | `fu=positive_part((e-eTstar)/(eT-eTstar))^gamma` | No printed upper clip. Thermal-cycle accumulation enters through this modified factor, not an explicit cycle counter. |
| MK11 PDF10 / printed9 Eqs6-8 | Reversible thermal strain and void rate | Host sign is compression-negative. In Atlas compression-positive notation `E_TE=-alpha_s*theta*I/3`; `e_dot=-(1+e)*trace(E-E_TE)`. |
| MK11 PDF14 / printed13 Eqs30-31 | Final saturated `H_T` includes correction `ci` and `positive_part(theta)` | Preprint dependency, not a closed host. Earlier Eq18 lacks `ci`; do not select it as final by convenience. |

M17 p5 lines53-54 explicitly selects positive compression. MK11 PDF4 / printed3 uses continuum-mechanics negative compression. All tensor signs must be transformed together; a scalar positive pressure in the host does not mean its tensor stress is compression-positive. First implementation may declare zero spin; the paper's objective rate alone does not authorize ignoring spin in general rotations. Mandel norm/contraction can represent Euclidean symmetric-tensor operations without engineering-shear ambiguity.

Mechanical parameters in Table1 are friction angle, NCL slope/intercept, unloading slope and shear-stiffness `r`. Thermal host inputs are `nT,lT,alpha_s,Tr`; new2017 parameters are `kT,cT,gamma`. The source suggests `gamma=.1` after sensitivity study (p12), not a universal constant. Printed Nil* entries for the isotropic clay example mean irrelevant to that simulation, not zero. `alpha_s` is a **volumetric skeletal** coefficient; the tensor isotropic strain uses `/3`. Its thermal contribution must be removed from void-ratio transport because solid and bulk thermal expansion move together. Reusing the usual isothermal `e_dot=-(1+e)*trace(E)` would spuriously change porosity during reversible thermal expansion.

### Unresolved source/domain choices

- **THERM-01:** Complete2005 host and final2012/2017 versus inspected manuscripts remain unverified. The2017 paper delegates `L,N,fs,fd,H_T` rather than restating their closure. A manuscript-selected research variant can be named explicitly only after that exact host is closed; no equation borrowing from2013/2014.
- **THERM-02:** Eqs2,3,5 use `log(T/Tr)` while Table1 labels `Tr` in degrees Celsius; the cited preprint also labels temperature in Celsius. Neither inspected formulation specifies an absolute-temperature conversion. Celsius and Kelvin ratios differ, so merely adding273.15 changes calibration. Preserve this convention issue and restrict any declared scalar fragment to a named positive temperature coordinate. Negative/zero coordinates are outside a positive-ratio branch, irrespective of physical water state.
- **THERM-03:** Figure1 puts pointO on the NCL at `p_o`; Eq5 defines pointO' relative to its void ratio. The source does not prescribe whether these are initial/preconsolidation anchors or evolving stage quantities, nor a reset/commit algorithm. Do not infer `p_o=pe` or freeze it without a named interpretation.
- **THERM-04:** At `T=Tr`, `p=p_o`, and NC pointO, Eqs4-5 and the NCL coincide, giving numerator and denominator zero in Eq10. Likewise the stated limiting no-accumulation case `cT=0,kT=lambda` can make the surfaces coincide. The source's first-heating statement `fu=1` (p10) needs a source-backed continuation/order; an arbitrary epsilon or initial temperature perturbation is not established.
- **THERM-05:** M17 p10 states `0<=fu<=1`, but Eq10 clips only below zero. Above the NCL it gives `fu>1`; either domain restrictions or additional saturation would be needed. No upper clip is selected in this packet. With `gamma=.1`, the one-sided derivative at the TSL diverges, so no smooth threshold tangent is justified.
- **THERM-06:** Exact host admissibility, preparation path, initial void ratios/lateral stresses, discrete algorithm and thermal-cycle data are not fully pinned. The1D example says in-situ vertical149kPa then specimen loaded to125kPa (p14); preserve that wording rather than inventing a preload or K0.

Safe mathematical regular support requires positive pressure/log arguments, `1+e>0`, a finite positive `lambda(T)` for host inversions, and noncoincident ordered NCL/TSL void ratios. These are regular evaluation requirements; they are not a complete experimentally validated domain or a silently added physical surface.

## Temporal integration and transactions

[state-integration-ledger.json](state-integration-ledger.json) distinguishes physical state, prescribed temperature, unresolved anchors, and stage-derived values. Core retained physical fields are symmetric effective stress and void ratio. Temperature is an additional host state or prescribed endpoint with exact provenance. No equation in the2017 packet establishes a cycle counter, maximum-temperature state, IGS tensor, suction state, or an independent viscosity clock.

The source modifies a thermal-collapse response **relative to the heating rate** (p11 lines153-156). Its reference to possible viscous behaviour in the schematic discussion (p7) does not add a physical-time creep equation. A joint path parameter `s` can drive mechanical stretching `E=d(epsilon)/ds` and scalar `theta=dT/ds`; the cited saturated host is positively homogeneous under common positive scaling of both rates. Temperature-dependent state and the sign of `theta` matter; merely supplying elapsed seconds to a de-only law is insufficient. A hold is zero mechanical **and** zero thermal rate. Heating at zero imposed strain is a constrained thermal problem, not a duplicate/zero-load bypass.

Split heating/cooling extrema explicitly. At each stage compute temperature-dependent NCL parameters, exact host mapping, TSL/NCL bounds, collapse factor, and stress/void-rate from one consistent state. This is a proposed transaction contract, not a discrete scheme printed in the paper. All mixed-control candidates must start from the same committed stress, void ratio, temperature and anchors; internal subdivisions update a local candidate; failure restores the full parent and exact accepted prefix. No hidden preparation, first-cycle reset, or maximum-temperature update is permitted without source closure. Joint mechanical/temperature tangents must retain thermal-volume correction and branch derivatives; singular thermal thresholds require explicit support/continuation decisions.

The smallest source-shaped constrained study after closure is drained constant hydrostatic effective stress200kPa, starting about20C and applying three60-to5C cycles (M17 pp13-14/Fig5). Six strain components respond to fixed stress and the prescribed temperature. Exact20/60/5 knots are a proposed protocol until source plot/data coordinates are pinned. The1D counterpart fixes vertical effective stress125kPa and lateral normal strain, permits lateral stresses to respond, and uses the actual source preparation. Neither can run meaningfully with guessed initial e/anchors or Nil-to-zero parameter replacements.

Three separate generic needs follow: a prescribed scalar temperature channel synchronized with mechanical constraints; explicit temperature-coordinate/affine-unit semantics; and model-defined thermal-corrected void-ratio transport. `atlas/model.py` currently exposes legacy `de` or physical `time,strain_rate` environments, without a general temperature path/control binding. Encoding a scheduled temperature as a state derivative is not equivalent to verifying and transporting caller-provided thermal knots. No shared schema/solver edits are made here.

## Independent checks

Run `python3 docs/ingestion/hypoplastic-thermal-ma-2017/check_packet.py` after installation; the script runs standalone from any cwd and prints JSON without changing retained evidence. Nine scalar diagnostic groups pass and exactly replay [check-results.json](check-results.json). They cover pressure units/reference NCL, Celsius-versus-Kelvin ratio, isotropic reduction of Eq7, anchor TSL gap, uncapped collapse factor, exact NC reference0/0 with Decimal, diverging threshold derivative, independently differentiated temperature-dependent NCL, and reversible-thermal porosity transport.

These are algebraic witnesses and deliberately conditional anchor readings, not simulated thermal cycles or validation of the complete constitutive model. No production DSL/kernel, author code, native artifact or Wasm module was imported/executed. The0/0 and out-of-range witnesses are retained findings, not failures corrected by numerical regularization.

## Handoff

Seven public files: README.md, source-receipts.json, equation-ledger.json, state-integration-ledger.json, check_packet.py, check-results.json, manifest.json. Manifest `files` are local relative paths and hash exact bytes; private materials and this packet's construction helpers are excluded.

Source availability: all2017 displayed equations readable/visually checked; complete coupled source closure remains blocked on THERM-01 through06. Executable model: none. Numerical evidence: nine independent scalar diagnostic groups only. Scientific admission: none.

The next smallest task is an explicitly named, supplied-anchor **NCL/TSL/collapse-factor scalar fragment** on a declared positive temperature coordinate, with singular/reference cases rejected rather than guessed, followed independently by final2005/2012 host reconciliation and thermal-input API design. A full constrained cycle must wait for anchor chronology, first-heating continuation, exact host and preparation. This allows useful isolated transcription without presenting the2017 extension as a complete runnable material.
