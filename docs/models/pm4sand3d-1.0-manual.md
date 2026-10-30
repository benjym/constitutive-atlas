# PM4Sand3D 1.0: manual and integration scope

The [vendor-linked manual](https://itasca-software.s3.amazonaws.com/udm-library/Kippen_et_al_PM4Sand3D_v1_CGM-26-01.pdf) is now locally pinned in the [source audit](../../catalogue/source-audits/pm4sand-manuals-2026-10-31.json). This is a partial documentary review, by Codex, with independent review pending. Neither constitutive code nor DLL has been inspected or executed. The candidate remains non-executable.

## Identity discrepancies

The downloaded cover and edition page say **June 2026**, unlike the May citation on the author release page. The file has 149 PDF pages, including five preliminary pages and 144 numbered pages. The vendor's object modification date is a transport property, not an edition date. The Box-linked manual has not been downloaded for byte comparison; equivalence remains unresolved.

The accompanying 2D vendor PDF says June 2023. It is not yet established to be the May 2024 revision in the author listing. Keep its checksum separate from the selected author-linked edition.

## Why integration belongs in the model record

Sections 3.1-3.3 and the algorithm on printed pages 76-77 distinguish subzone updates from zone averaging. Zone-level dilatancy and plastic modulus feed the following increment. The description uses explicit integration without constitutive substepping and includes parallel shear resistance for hourglass control. Printed page 73 warns that changing loading rate also changes FLAC3D's dynamic excitation; that comparison alone cannot isolate integration error. The introduction identifies the parent as PM4Sand 3.3.

For the atlas, this raises several implementation decisions that must be explicit before transcription:

- Separate continuous equations, the discrete material update, and the host program's averaging/stabilization. A material point using one homogeneous subzone needs a documented reduction; it cannot silently claim full FLAC3D equivalence.
- Represent lagged values as committed algorithmic history if reproducing this update. Recomputing them at every internal Newton or Runge-Kutta stage defines a different algorithm.
- Pin the caller increment and internal subdivision policy in comparisons. Adding adaptive substeps can change when lagged quantities and reversal memories advance.
- State whether the parallel resistance is included in reported stress. Separate its initialization and accumulated state from the main material, then verify their combined response.
- Keep zero-spin, infinitesimal-strain support explicit. The large-strain rotation operations in the manual do not confer that capability on the current atlas engine.
- Hold the prescribed path and physical duration fixed in a refinement study. Any comparison using the vendor host must also control inertia and its global timestep.

These are requirements for a future source-matched implementation, not extensions made in this work.

## Source ambiguities to resolve

The rendered algorithm contains inconsistent labels: printed page 76 points to Table 3.2 for initialization; printed page 77 is labelled Table 3.2 but continues the algorithm, while initialization starts as Table 3.3 on page 78. Use printed page, PDF page and step numbers together. The stress correction in step 7(b)(ii), including its tensor-product notation, needs reconciliation against Section 2 and a constitutive implementation; no equation is transcribed from that expression here.

Next extract the complete tensor law and history inventory from Section 2, reconcile the initialization and algorithm tables, establish the exact manual/DLL pairing, and define homogeneous and host-averaging reference cases. Original equation review and numerical admission remain open.

## First equation fragment

A [source-linked DSL fragment](../../catalogue/source-audits/pm4sand3d-1.0-surfaces.json) now represents the shifted stress-ratio direction, Lode cosine, adopted quarter-power shape factor, current stress-ratio magnitude and yield distance from Equations 15-18 and 23. The original PDF pages 28-29 were rendered and inspected to recover radicals and exponents damaged by text extraction. The fragment uses the existing tensor and scalar operators; no new DSL primitive is needed for these terms. It is not a complete constitutive model or registered executable.

Run `python3 tools/inspect_pm4sand_surfaces.py` for compression/extension/shear examples, and `python3 -m unittest discover -s tests -p test_pm4sand_surfaces.py` for Python-only checks. Separate Cartesian determinant algebra checks 40 general tensors and oblique rotations at three shape ratios. Additional checks cover endpoint values, translated backstress, scaling and rejection of zero/undefined directions. Trace tolerances and the tested parameter domain are explicit audit choices; no source regularization is inferred. Native/Wasm, AD, full tensor flow and history/integration remain unverified.
