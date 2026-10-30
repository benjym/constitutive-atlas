# PM4Sand: separate 2D and 3D candidates

Author-source screening on 2026-10-31 changes the earlier assumption that the
PM4Sand listing was only an unspecified plane-strain family. The
[author site](https://pm4sand.engr.ucdavis.edu/) distinguishes PM4Sand2D from
PM4Sand3D. The initial author-page screening is now supplemented by a
[partial manual and integration audit](pm4sand3d-1.0-manual.md). Complete
equation extraction and reference execution remain open.

| Atlas candidate | Selected documentary identity | Authors | Scope reported by authors |
| --- | --- | --- | --- |
| `pm4sand` (existing stable ID) | PM4Sand 3.3, UCD/CGM-23/01; citation year 2023; download page notes a May 2024 revision | Ross W. Boulanger; Katerina Ziotopoulou | Plane strain |
| `pm4sand3d-1.0` | PM4Sand3D 1.0, UCD/CGM-26/01, May 2026 | Marie-Pierre Kippen; Ross W. Boulanger; Katerina Ziotopoulou | Three dimensional |

The [2D author release page](https://pm4sand.engr.ucdavis.edu/pm4sand-files)
describes changes from 3.1 to 3.2 in initialization and elasticity and says that
calibrations require revision. Version 3.3 further limits a term in the shear
modulus expression and requires calibration checks. Keep release-specific
parameter sets and initialization; these versions are not interchangeable.
The [references page](https://pm4sand.engr.ucdavis.edu/pm4sand-references)
links the corresponding reports and the 2013 formulation and implementation
papers. Exact author-linked manual bytes and any errata remain to be reconciled with the pinned vendor copies.

The [3D author release page](https://pm4sand.engr.ucdavis.edu/pm4sand3d-files)
lists a separate manual, a FLAC3D 9.X binary and example drivers. It includes
triaxial as well as simple-shear and plane-strain paths. A 3D version is therefore
a relevant candidate for the atlas's 3D release target; it is not an admitted
formulation merely because a binary exists. The
[author driver repository](https://github.com/katerinaziot/PM4Sand3D_drivers_auto)
generates FLAC3D inputs and processes results. It is not evidence that the full
constitutive implementation is available there.

The author-linked manuals are
[2D 3.3](https://ucdavis.box.com/s/op92sb4hxh9zzw8imfsvib16hjuepzuk) and
[3D 1.0](https://ucdavis.box.com/s/l1i2qm704l6ii9g3v6lodx6uwwu8x5t1).
The web reader could not access those Box redirects during this screening.
That initial failure is preserved in the discovery snapshot. Vendor-hosted copies
are now pinned in the [manual audit](../../catalogue/source-audits/pm4sand-manuals-2026-10-31.json):
the 2D PDF says June 2023 and the 3D PDF says June 2026. These are not yet
established to be identical to the author-linked editions above. Identity,
contents and selected implementation sections have been inspected; complete
equations, binary compatibility, execution and redistribution rights remain
unresolved. No binaries were downloaded.

The [lineage record](../../catalogue/discovery/pm4sand-2026-10-31.json) preserves
source URLs, selected identities, version differences and unresolved work. The
older SoilModels discovery snapshot remains unchanged. The catalogue now has
32 entries, with 5 executable definitions and 27 candidates; the executable
release target remains 20.

Next steps are to reconcile the pinned vendor copies with the author-linked
revisions, complete their distinct state/initialization/integration contracts, and select
source-matched verification cases. A plane-strain formulation needs an explicit
kinematic contract and must reject unsupported 3D protocols. The 3D candidate
needs its own tensor, history and parameter audit; reusing the 2D equations or
calibration is not sufficient evidence. Public driver and DLL availability does
not establish reuse rights for other linked artifacts or replace an independent
equation and numerical review.
