# Lade–Duncan 1975 source-identity correction

SRC-lade-duncan-identity-v1; coordinating parent, 1 November 2026. This corrects
bibliographic identity only. Full ingestion and scientific admission remain open;
no constitutive equation has been transcribed or inferred from metadata.

The candidate is Poul V. Lade and James M. Duncan, **Elastoplastic Stress-Strain
Theory for Cohesionless Soil**, *Journal of the Geotechnical Engineering Division*
101(10), 1037–1053 (October 1975), [DOI 10.1061/AJGEB6.0000204](https://doi.org/10.1061/AJGEB6.0000204).
The exact [publisher-deposited Crossref record](crossref-204.json) identifies the
matching authors/title/pages. [Primary metadata endpoint](https://api.crossref.org/works/10.1061/AJGEB6.0000204).

The previous DOI, `10.1061/AJGEB6.0000208`, belongs to Braja M. Das and Gerald R.
Seeley, **Uplift Capacity of Buried Model Piles in Sand**, the same journal/issue,
pp.1091–1094. Its [separate Crossref record](crossref-208.json) establishes that it
is a different paper, not a constitutive-model revision.
[Primary metadata endpoint](https://api.crossref.org/works/10.1061/AJGEB6.0000208).

The active catalogue's discovery URL and task-board acquisition target now use
0000204. Exact prior catalogue bytes are preserved in a content-addressed snapshot;
[receipt.json](receipt.json) binds both metadata responses and the original record.
Frozen historical discovery/evidence records are not rewritten. Source identifiers,
candidate status and executable count remain unchanged.

## Access and stop rule

No matching Lade/Duncan/1975/true-triaxial filename was found in Downloads. This
is a filename check, not proof that no ambiguously named local PDF contains the
paper. Both publisher landing-page requests returned 403 through the web tool.
One direct request to the corrected publisher PDF URL also returned 403 HTML,
not a PDF; its response digest and private temporary location are in the receipt.
The bibliographic correction does not certify full-text access or reuse rights.
No raw publisher HTML or third-party article PDF is bundled.

Next obtain a readable original via the corrected identity or a concrete new
access lead, then extract the full elasticity/yield/flow/hardening/preparation
and temporal integration contract under schema v0.3. Do not implement the failure
criterion alone, infer missing equations from abstracts, substitute the 1977
curved-surface extension or repeat the same failed requests without a new lead.
No author messages were sent.

## Verification

`python3 -B -m unittest tests.test_lade_source_identity tests.test_catalogue -v`
checks exact DOI/title/author/page identities, receipt/file hashes, preserved old
catalogue bytes, candidate status and SQLite source propagation. Temporary database
exports exercise the real catalogue exporter; no native/Wasm build, material call,
fit or website deployment is involved. [manifest.json](manifest.json) pins this
packet; changing this discovery link does not revalidate older scientific claims.
