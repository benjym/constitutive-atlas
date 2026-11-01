# Original Cam Clay delivery: source and contract checkpoint

Task SRC-occ-author-source-v1, coordinating parent `/root`, 1 November 2026.
Full task: MODEL-original-cam-clay; [delivery ledger](../DELIVERY.md).

The next unstarted source-ingestion row was Original Cam Clay. This follow-up
preserves the existing packet and smooth reference. It does not choose finite
shear elasticity, substitute Modified Cam Clay, or restrict delivery to the
already checked positive-q trajectory. A complete executable formulation has
not yet been selected.

## Source acquisition and retention

The exact historical university-mirror PDF is now retained durably at ignored
`.local/private-sources/original-cam-clay/schofield-wroth-electronic-transcription.pdf`.
SHA-256: `638e0ee7dc238ae8922b79983433be7d12ad30450098efe395968f7eeed13cb2`,
7,886,630 bytes, 229 pages. The receipt continues to describe a later electronic
transcription, not an authenticated 1968 print scan. No copyrighted PDF, extract
or rendered page is included in these public outputs. Downloads and existing
private-source filenames were checked; no new matching edition was identified.

New lead: the [ResearchGate publication record](https://www.researchgate.net/publication/275027554_Critical_State_Soil_Mechanics)
attributes its CSSM.pdf upload to Andrew Schofield, dated 17 March 2016. Its
[direct PDF link](https://www.researchgate.net/profile/Andrew-Schofield-7/publication/275027554_Critical_State_Soil_Mechanics/links/56eada3208aeb65d75937245/Critical-State-Soil-Mechanics.pdf)
was readable as extracted text through the web reader (228 pages). Local sandbox
retrieval failed DNS; a normal network-enabled download returned HTTP 403. The
web reader's screenshot attempts mostly returned cache misses. This establishes
a concrete author-associated lead, not retained exact PDF bytes, a source hash,
verified printed equations, or edition authentication. No login or restriction
bypass was attempted. See `source-follow-up.json` and the original failed
`author-acquisition.json`.

The [Ethiopian national library record](https://ndl.ethernet.edu.et/handle/123456789/46322)
links a 7.7 MB PDF, but its metadata says 1997/Taylor & Francis; the web-reader
download returned 502. Those conflicting fields do not authenticate the selected
1968 edition. The [Cambridge institutional history](https://www.eng.cam.ac.uk/node/4054)
confirms the authors/book/year but supplies no equation-page facsimile.

## Reading and source decisions

The available local Chapter6 pp93–114 and AppendixC pp216–218 were read as text.
Page images pp95 and98 were inspected to check zero recoverable shear and the
interior rigid response; pp101–102 inspect the corner and one-dimensional
compression branches. These source facts support the existing packet's
constraint interpretation. The web-reader author-associated text is corroborative;
it is not a substitute for exact-byte/page-image reconciliation.

Chapter6.1–6.7 define the selected material; 6.8–6.10 also discuss a distinct
critical-state idealization and empirical soil-property relationships. Those
relationships are not extra mandatory evolution equations. Section6.11 postpones
the general stress-invariant construction; AppendixC starts with Granta-gravel.
OCC-specific recovery/hardening must be carried explicitly when reviewing a
generalization. The historical [equation inventory](../README.md) and
[v0.3 requirements crosswalk](../smooth-reference-v1/schema-crosswalk.md) remain
the source/schema inventory. Neither is an executable v0.3 model instance.

The following decisions remain open, rather than being silently supplied:

| Gate | Required resolution | Current consequence |
| --- | --- | --- |
| OCC-SRC-01 | Retain/authenticate author electronic bytes or a 1968 facsimile, and reconcile key equation/corner pages | E1 stays open; author-associated lead is now concrete |
| OCC-CLOSE-01 | Review complete axisymmetric law and any intended 3D generalization, preserving zero recoverable shear | No general 3D identity or changing-principal-axis claim |
| OCC-CONTROL-01 | Define caller-controlled stress/strain constraints and selection/nonuniqueness semantics | Ordinary deterministic strain-to-stress update is not established |
| OCC-VERTEX-01 | Select source-consistent corner normal cone and finite active-set/event policy | No smooth absolute-value derivative or unique corner normal is invented |
| OCC-ENERGY-01 | Reconcile p101 cone interior with smooth Eq6.9/6.10 dissipation equality and AppendixC10 limiting statement | Isotropic plastic work cannot be silently tested against zero net shear dissipation |
| OCC-NUM-01 | Freeze independent full-branch references and finite-step/tangent/rollback gates after closure | Existing smooth-path accuracy is not full-law qualification |

## Minimal source-derived capability requirement

At fixed effective pressure p and fixed packing, the interior law has no
recoverable distortion while different interior q values are permitted. Thus
the same prescribed zero strain history can be compatible with different
externally controlled q histories. This is a constrained material relation;
the missing interface decision is how controls and reaction stresses select a
solution. An ordinary stress-valued rate function cannot infer that selection.
See [the capability specification](capability-requirements.md) and the separate
reviewer's independently constructed witnesses.

This is not proof that every residual encoding is impossible. A reviewed
constraint formulation and appropriate host could represent the law. The
current residual solver's forced zero-multiplier predictor and its return of a
single state must be assessed explicitly. Bypassing a singular predictor,
adding finite G, retaining q by convention, or treating an arbitrary Newton
root as source-mandated is not an approved solution.

## Existing evidence replay

`replay-log.json` records the exact commands, return codes and output for the
existing packet checker/tests and smooth-reference checker/tests. They are
replays, not a new numerical campaign. Packet source-hash validation succeeds;
six packet tests and six smooth-reference tests pass. All 115 stored smooth
reference points reproduce. No native/Wasm build or compiled call was made.

`prior-evidence-hashes.json` binds the pre-existing OCC packet and smooth-study
files before this work. The integrity check confirms they remain byte-identical.
Historical failures, source receipts and policies are untouched. The fresh
review is a source/contract review; it is not E5 acceptance of a nonexistent
candidate.

## Handoff

E0 is tracked; E1/E2 remain open. Next retain and reconcile the author-associated
source or authenticated facsimile, then review the full constrained closure and
freeze a bounded experiment with current residual algebra and increment unknowns.
A generic runtime change is justified only after a demonstrated capability gap. Implementation, qualification,
independent model approval, atlas/browser integration and live release remain
dependent stages. No change to scientific admission, catalogue counts or
deployment status follows from these diagnostic passes.
