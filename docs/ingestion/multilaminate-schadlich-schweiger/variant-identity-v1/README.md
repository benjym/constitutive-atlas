# Multilaminate publication and variant identity v1

This closes a bounded identity task, not ingestion or scientific admission. The working transcription target is the **April 2012 thesis**, with spectral cross-anisotropic small-strain stiffness, history/recovery, Hvorslev strength/softening and regular post-peak nonlocal regularization. This selection preserves the source's host requirements; it is not yet a complete executable definition or a claim that every thesis option is simultaneously active.

| Source | Identity and role | Evidence available |
| --- | --- | --- |
| [Thesis, 2012](https://repository.tugraz.at/publications/wmxdh-rg587) | Schädlich, *A Multilaminate Constitutive Model for Stiff Soils*. Primary working source. | Complete private PDF; selected pages read visually. |
| [NAG, 2013](https://doi.org/10.1002/nag.2089) | Schädlich & Schweiger, *A multilaminate constitutive model accounting for anisotropic small strain stiffness*, 37(10), 1337–1362. Companion stiffness formulation paper. | Primary metadata/abstract; full equations unavailable. |
| [IJG, 2013](https://doi.org/10.1061/(ASCE)GM.1943-5622.0000286) | Schädlich & Schweiger, *Influence of Anisotropic Small Strain Stiffness on the Deformation Behavior of Geotechnical Structures*, 13(6), 861–868. Applications. | Primary metadata/abstract; full equations unavailable. |
| [Geotechnik, 2014](https://doi.org/10.1002/gete.201300016) | Schädlich & Schweiger, *Modelling the shear strength of overconsolidated clays with a Hvorslev surface*, 37(1), 47–56. Strength formulation. | Primary metadata/abstract; full equations unavailable. |

[SoilModels](https://soilmodels.com/multilaminate/) cites the thesis, the IJG application paper and the Geotechnik paper. Its 2013 reference is **not** the NAG stiffness paper. The NAG paper appeared online in April 2012 and in the 2013 print volume; these dates do not establish separate equation versions. The chapter associations above follow subject scope only: no journal/thesis equation equality has been verified.

## Source selection and boundaries

The thesis introduction (printed pp.2–4; PDF20–22) maps Chapter4 to small-strain stiffness, Chapter5 to structural applications and Chapter6 to Hvorslev strength and regularization. Chapter4 starts at printed p.34/PDF52; Chapter6 at p.95/PDF113. The conclusion (pp.145–146/PDF163–164) supports the combined research scope, not Atlas validation.

- **Selected for subsequent transcription:** spectral compliance decomposition rather than the alternative microstructure-tensor stiffness branch; retain stress dependency, logarithmic degradation and reversal-contour history/recovery. The thesis conclusion reports limitations of the tensor alternative (p.145).
- **Selected nonlocal branch:** regular averaging after local peak strength is reached. Section6.5.5 (pp.143–144/PDF161–162) distinguishes modified averaging that can weaken points before their own peak. It prefers regular averaging for its biaxial studies because of band-position behaviour, while retaining imperfect mesh independence and practical boundary-value uncertainty. This is a working branch choice, not universal validation.
- **Related alternatives:** retain modified pre-peak averaging, microstructure-tensor stiffness and Galavi strength/softening as separately identified alternatives. Do not merge them into a synthetic formulation. Strength anisotropy and stiffness anisotropy are distinct; the introduction says strength anisotropy is incorporated but not investigated in the thesis (p.2).
- **Cyclic boundary:** reversal recovery does not establish a new cyclic kinematic-hardening extension. Implementation of kinematic hardening for large reversals/cyclic loading is listed as further research (p.146).

## Retained gates and next bounded action

Read alongside the immutable [thesis inventory](../thesis-2012-v1/README.md), [base laws](../base-laws-v1/README.md) and [host contract](../host-contract-v1/README.md). Their cap-hardening/sign conflicts, omitted helpers, state/allocation discrepancies and trial/history ambiguities remain unresolved. The current engine's 32-state capacity cannot justify selecting a reduced variant or dropping nonlocal inputs.

Next: one equation-transcription packet for the selected Chapter4 spectral stiffness and degradation branch, with source locators, explicit v0.3 conventions and source-derived independent checks where justified. Leave Chapter6 and full execution open. Full journal texts would permit a later equation comparison; lack of access does not prevent thesis-specific transcription. Stop repeated access attempts until a new source lead appears.

## Receipt and verification

[identity.json](identity.json) records identities, exact source hash, inspected page/render hashes and seven access receipts. All three publisher PDF requests returned HTTP403 HTML, despite curl exit0; none is an acquired article. Institutional pages provide metadata, not equation verification. Downloads filenames and first pages of ambiguous candidate manuals/articles were checked without finding these papers; this was not a full-text search of every download.

Raw PDFs, HTML responses and renders remain private; no redistribution permission has been established. [manifest.json](manifest.json) pins this packet and its source/schema dependencies. Validation is limited to hashes, structured metadata, expected failed-access classification and local links. No author code, compiled solver, build, curve comparison or admission was run.
