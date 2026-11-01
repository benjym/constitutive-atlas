# Original Cam Clay delivery: source and constraint checkpoint

Task: SRC-occ-delivery-v1, child of MODEL-original-cam-clay. Lead: current root run, 1 November 2026. This additive checkpoint preserves the [earlier packet](../README.md), [receipt](../source-receipt.json), and [smooth reference](../smooth-reference-v1/README.md). The [delivery ledger](../DELIVERY.md) tracks E0-E8. This is a blocked full-delivery assignment, not a completed model ingestion.

## Selected identity and source acquisition

The target remains Schofield and Wroth, *Critical State Soil Mechanics*, McGraw-Hill 1968, Chapter6 Original Cam-clay, including its original zero recoverable shear and hydrostatic corner. Finite shear elasticity, MCC, and a post-vertex undrained trajectory are not substitutes for this complete formulation. Intended destination is the ordinary native/Wasm atlas and interactive browser after source, update and review qualification.

The existing 229-page electronic transcription is SHA-256 `638e0ee7dc238ae8922b79983433be7d12ad30450098efe395968f7eeed13cb2`. Its bytes were verified and copied to durable ignored private storage: `.local/private-sources/original-cam-clay/schofield-wroth-electronic-transcription.pdf`. The absolute path and direct acquisition attempts are in [acquisition.json](acquisition.json). `git check-ignore` confirms exclusion. Neither the original PDF nor page images/text are published. Hosting/read access does not establish redistribution rights.

Downloads filename search for cam, schofield, wroth, critical and soil found no matching book; existing private inventory supplied the retained artifact. The PDF skill was used: newly rendered printed pp95,101,114,216 (one-based PDF106,112,125,227) were inspected, and source text around Chapter6 and AppendixC was re-read. Earlier full-source coverage remains as recorded; this pass is not a new full-book review. The p101 image visibly contains an apparent transcription error in its discussion of equal principal strains, so exact 1968 print fidelity remains material.

New public leads checked on 1 November 2026:

| Lead | Observation | Consequence |
| --- | --- | --- |
| [National Academic Digital Library of Ethiopia](https://ndl.ethernet.edu.et/handle/123456789/46322) | Lists the title but gives 1997/Taylor & Francis metadata. Its [23.pdf](https://ndl.ethernet.edu.et/bitstream/123456789/46322/1/23.pdf) returned web502; direct Python download failed DNS. | No bytes acquired; metadata does not authenticate the 1968 edition. |
| [Cambridge author seminar](https://soc-geotech.eng.cam.ac.uk/events/2016-04-29-Schofield) | Author seminar discusses Original Cam-Clay; linked [2016 slides](https://enggsoc.migrate.drupal.uis.cam.ac.uk/system/files/documents/2016-04-29-slides.pdf) returned web502. | No new equation or edition evidence. |
| [Cambridge legacy book URL](https://www.civ.eng.cam.ac.uk/geotech_new/publications/schofield8wroth81968.pdf) | Web reader inaccessible. | No source bytes or fidelity certification. |
| [Author-listed ResearchGate record](https://www.researchgate.net/publication/275027554_Critical_State_Soil_Mechanics) | Page lists two attachments, including unrelated software-license text and CSSM.pdf; the CSSM download and read links returned404. | Author-labelled metadata alone is not readable original-source verification. |
| [geotechnique.info lead](https://www.geotechnique.info/SchofieldWroth.htm) | Web inaccessible; direct Python DNS failure. | No additional source. |

These are access observations, not a claim the sources do not exist. Search snippets, third-party paid copies and bibliography metadata were not used to certify equations.

## Narrowed v0.3 and integration findings

Target [schema v0.3](../../../../schemas/model-v0.3.schema.json) and [contract](../../../FORMULATION_CONTRACT.md) were read. No existing definition is migrated and no runnable model is manufactured. The earlier [requirements crosswalk](../smooth-reference-v1/schema-crosswalk.md) remains useful, with these additive qualifications:

* A strain-path incremental residual is a plausible candidate. Persistent six-component effective Cauchy stress, specific volume and packing history would be explicit; temporary constraint multipliers need not use `plastic_multiplier`. `increment_unknown` avoids the engine's automatic zero-plastic predictor. No new primitive or schema extension is demonstrated necessary by this checkpoint.
* Chapter6 p114 explicitly points from OCC Eq6.17 to the AppendixC invariant generalization. AppendixC C3/C5 supply source-motivated geometry; they start with Granta-gravel. A documented combination with OCC packing-dependent critical pressure is plausible. Copying AppendixC's Granta-gravel `p_u(v)` as OCC hardening is incorrect. The blanket assertion that no 3D route exists is too strong; the exact combined identity and hydrostatic treatment still require reconciliation and review.
* Original interior shear compliance is zero, not zero shear stiffness. At fixed pressure/packing, different strictly interior shear stresses can correspond to the same zero strain. A strain-driven stress selection therefore needs an explicit policy. This does not prove every residual implementation impossible.
* The hydrostatic corner on p101 allows the cone between limiting directions, including isotropic compression. Two smooth signed axisymmetric inequalities `f+ = q + M p ln(p/pc)` and `f- = -q + M p ln(p/pc)` express this cone without differentiating abs(q). They do not automatically solve the full3D norm cone or prove Newton convergence.
* At the vertex the associated cone gives plastic volume `M(a+b)` and signed distortion `a-b`. Plastic work is `Mp(a+b)`; applying the smooth absolute-shear loss formula there would give `Mp abs(a-b)`. Equal positive a,b give nonzero compaction/work and zero distortion. The source's corner prescription must therefore be reconciled as a corner relaxation/selection, rather than claiming the smooth dissipation equality applies unchanged to every corner vector.

The [exact diagnostic](constraint_witness.py) and [saved results](constraint-witness.json) establish these limited algebraic statements. They use rational arithmetic and the analytical bound ln2>1/2. They are not a production update, runtime failure, or a native/Wasm qualification. An example has p=50000Pa, pc=100000Pa, M=1.2, v=2 and q in {-10000,0,10000}Pa, all strictly interior with unchanged packing and zero strain; the elastic p/q compliance has rank1. This isolates the missing selection decision without asserting unavailable expression syntax.

Future transactions must read one committed full state, isolate trials/branch choices, atomically commit on success and return the exact parent on failure; restart preserves packing and pressure-reference identity. The source does not specify a finite update, event tolerance, Newton strategy or discrete tangent. Those project choices need frozen acceptance cases before compiled observations. Zero imposed strain identity may be selected as an API policy but is not uniquely forced by shear rigidity alone. Physical time, creep, finite rotations, arbitrary pore-pressure evolution and experimental matching are outside the target claim.

## Reproducible checks and retained limits

From the repository root:

```sh
python3 -B docs/ingestion/original-cam-clay/check_packet.py --source .local/private-sources/original-cam-clay/schofield-wroth-electronic-transcription.pdf --output /private/tmp/occ-packet-replay.json
python3 -B docs/ingestion/original-cam-clay/test_packet.py
python3 -B docs/ingestion/original-cam-clay/smooth-reference-v1/reference.py --output /private/tmp/occ-reference-replay.json
python3 -B -m unittest tests.test_occ_smooth_reference -v
python3 -B docs/ingestion/original-cam-clay/delivery-v1/constraint_witness.py
```

Both existing suites pass, six tests each. The private-source hash check passes. The smooth reference retains its original16/32/64step gates and errors; no acceptance bound changed. Saved replays are [packet-replay.json](packet-replay.json) and [smooth-reference-replay.json](smooth-reference-replay.json). Original source-access failures, source fidelity gaps, the initial smooth-reference test failure in its historical log, and its excluded vertex/critical region remain preserved. No compiled calls or builds occurred.

The separate [technical audit](../delivery-review-v1/README.md) evaluates these blockers independently. It is not E5 approval of an absent candidate. Source completeness, executable support, independent full-law qualification, approval, atlas inclusion, browser and live delivery remain open. The original analytical trajectory is useful evidence and does not complete any of those gates.

## Next handoff

Acquire a readable authenticated1968 edition or authenticated author copy to cross-check the corner and AppendixC statements, then record a source-bound complete closure decision: invariant OCC mapping, corner dissipation convention and strain/control selection. Assess that exact decision independently before freezing a declarative constrained residual and generic-solver qualification. Do not add finite G, smooth the corner, or launch another post-vertex trajectory study to bypass the decision. Lead/coordinator retains MODEL-original-cam-clay as blocked at E1/E2; all later E3-E8 stages remain unstarted, and remote publication is not authorized by this request.

Coordinator integrity review: all six reviewer-authored artifact hashes and all 36 reviewed dependency hashes verified; the independent constraint checker replayed successfully. Review manifest SHA-256: `1484e61f409214d5541f17f0a5f25f7b927d881899f9cdf4a7bd20bae2cf4a9e`. See [the precise handoff](HANDOFF.md).
