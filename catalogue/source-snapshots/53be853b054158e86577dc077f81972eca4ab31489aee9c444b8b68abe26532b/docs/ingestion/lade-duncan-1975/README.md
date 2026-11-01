# lade-duncan-1975 — ingestion packet

Task ID: ING-lade-duncan-1975 / MODEL-lade-duncan-1975.
Owner: author-source parent contributor; claimed 1 November 2026 after the user
redirected this session away from concurrently owned Original Cam Clay.
Tracking: [E0–E8 delivery ledger](DELIVERY.md).

Scope: the complete original Lade–Duncan 1975 elastoplastic law. The source
identity is established, but governing equations are not yet readable in this
session. This is an acquisition checkpoint, not source-complete ingestion or an
executable model. The existing [identity correction](identity-v1/README.md) is
preserved unchanged.

## Identity and sources

Poul V. Lade and James M. Duncan, *Elastoplastic Stress-Strain Theory for
Cohesionless Soil*, Journal of the Geotechnical Engineering Division 101(10),
1037–1053, October 1975. [DOI10.1061/AJGEB6.0000204](https://doi.org/10.1061/AJGEB6.0000204).
The matching publisher-deposited Crossref record is retained and hashed in
[identity-v1](identity-v1/receipt.json). The formerly assigned DOI0000208 is a
different pile-uplift paper; do not restore that binding.

A new [author-associated publication record](https://www.researchgate.net/publication/282368437_Elastoplastic_Stress-Strain_Theory_for_Cohesionless_Soil)
offers a PDF and attributes its upload to Poul V. Lade on 3 June 2017. Its
[direct file link](https://www.researchgate.net/profile/Poul-Lade/publication/282368437_Elastoplastic_Stress-Strain_Theory_for_Cohesionless_Soil/links/59332843a6fdcc89e7ca934b/Elastoplastic-Stress-Strain-Theory-for-Cohesionless-Soil.pdf)
was recognized by the web reader as a 17-page PDF with no readable lines.
Screenshot requests returned cache misses. A normal network-enabled download
returned HTTP403 and browser navigation stopped at a device check. No challenge
was solved and no access restriction bypassed. Therefore the PDF's actual title
page, printed pagination, equations, file bytes and SHA-256 remain unverified.
Seventeen reported pages alone do not certify complete original content.

Current ASCE .org and indexed .com landing routes returned HTTP403. The original
historical publisher PDF denial remains a distinct receipt; this follow-up does
not replace its response identity. [Source-access record](delivery-v1/source-access.json)
distinguishes current observations from historical outcomes. No author contact,
purchase, login, supplied code execution or remote publication occurred.

The article remains copyrighted; author upload/read access is not redistribution
permission. No paper bytes or raw copyrighted response are included in the
public packet. Ignored private destination, if acquisition succeeds:
`.local/private-sources/lade-duncan-1975/`.

## Existing work and gaps

The earlier identity task corrected bibliographic metadata only; it contains no
full law. No current executable definition, numerical reference or approved
Lade–Duncan 1975 model was identified. Discovery status and model counts stay
unchanged. This follow-up adds a concrete author-associated original-file lead,
a broader local front-matter check, per-model delivery tracking and a separately
scoped source-gate review.

[Local inventory](delivery-v1/local-inventory.json) records first-two-page text
checks of all 23 PDFs in Downloads and current attachments, including ambiguous
filenames. No target title was found. This is not proof that a paper cannot be
embedded later in another file or available in some unsearched private collection.
The later 1977 curved-yield-surface paper, the 1972 dissertation, 1973 cubical
tests and 1976 stress-path study are separate identities; none substitutes for
the original without a source-located reconciliation.

## Equations and schema crosswalk

Target: [model schema v0.3](../../../schemas/model-v0.3.schema.json) and
[formulation contract](../../FORMULATION_CONTRACT.md). There is no candidate
JSON yet. A future model must use `schema_version: "0.3"`, a complete explicit
`formulation`, persistent/temporary state semantics and explicit initialization;
it must not use legacy top-level `integration` or guessed convention defaults.

| Required source content | v0.3 mapping to establish | Present evidence |
| --- | --- | --- |
| Elastic law and pressure dependence | Parameters/units/domains; stress-strain equation and tensor action | Governing pages unreadable |
| Yield and failure conditions | Separate functions, loading criterion and admissible domain | No equations transcribed |
| Plastic flow/potential | Normalization, association/nonassociation, tensor/shear and sign conversion | No source-located flow law |
| Empirical hardening and history | Persistent state, evolution, stress-path dependence and reversals | No source-located history inventory |
| Parameter tables/calibration | Complete parameters, units/ranges, initial density and source presets | Not acquired |
| Kinematics/conventions | Frame, objective rate, stress measure/scope, Mandel conversion | Not verified from governing source |
| Initialization/preparation | Required complete state, loading history and admissibility checks | Not verified |
| Rate/increment form | Time dependence, required equation/advance inputs and dimensions | No executable profile selected |

The publisher abstract advertises a full elastoplastic theory with distinct
failure, yield, flow and work-hardening ingredients. That establishes the
acquisition scope; it supplies none of their formulas or numerical conventions.
A failure criterion alone must not be counted as the requested constitutive law.
The [requirements ledger](delivery-v1/requirements.json) keeps every unresolved
mapping explicit. No shared-engine capability gap is asserted before reading
the actual equations.

## Temporal integration and transactions

The original rate versus finite-increment law, loading/unloading switches,
hardening ordering/lagging, zero/hold behavior, critical or failure events,
initialization and tangent requirements are unknown pending source access.
No physical clock, creep law or rate independence is inferred from the title.

Future Atlas integration must specify immutable complete trial parents, atomic
commit, full-state failure rollback, repeatable retry and complete restart
history. Those are intended software requirements, not verified descriptions
of the original author's algorithm. Step size, discretization, active sets,
solver tolerances and numerical acceptance policies cannot be frozen against
unread governing equations. The complete source-derived contract precedes any
native/Wasm build or browser integration assignment.

## Independent checks

No constitutive algebra or numerical test is invented for inaccessible equations.
Existing identity/catalogue checks are replayed with exact commands and output
in `delivery-v1/check-log.json`; these verify metadata and publication bindings,
not model physics. All three Lade identity tests pass; the broader six-test run has two catalogue failures, retained with a [read-only diagnosis](delivery-v1/catalogue-diagnostic.json). No shared files were repaired. [Historical hashes](delivery-v1/historical-hashes.json)
preserve the identity packet. Independent source-gate review is distinct from
E5 model approval; there is no candidate to approve. The [separate review](delivery-v1/independent-review/README.md) supports the publication identity and confirms the bounded source blocker.

## Handoff

Owned additions: README.md, DELIVERY.md and delivery-v1/. Historical identity,
other model packets and shared compiler/runtime/catalogue/web files remain
outside this assignment. The board remains open until actual delivery gates
are met.

Smallest resumption input: a legally readable copy of all original printed pages
1037–1053, preferably the author-uploaded PDF above or an institutional copy,
including figures, parameter tables, appendix/notation and any continuation.
Then verify title/pages/file hash, visually read equations, inventory the full
law and select its explicit v0.3 contract before implementation. A new concrete
access lead also permits resumption; repeatedly retrying the same denied routes
does not advance this gate.

Source completeness: metadata only; readable governing original absent.
Executable support: none for this formulation. Numerical verification: none;
identity checks only. Scientific admission, atlas/browser integration and live
deployment: none. Experimental validation: unassessed.
