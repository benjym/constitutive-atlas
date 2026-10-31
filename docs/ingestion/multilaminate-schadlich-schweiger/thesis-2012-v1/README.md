# Schädlich 2012 multilaminate thesis: source and capability inventory

Task SRC-multilaminate-thesis-2012-v1; coordinating parent, 1 November 2026. This completes a bounded acquisition/plane-history inventory, not ING-multilaminate full transcription or scientific admission.

## Identity and reading scope

Bert Schädlich, *A Multilaminate Constitutive Model for Stiff Soils*, doctoral thesis, TU Graz, April 2012. [Institutional repository / DOI](https://doi.org/10.3217/wmxdh-rg587), [repository record](https://repository.tugraz.at/publications/wmxdh-rg587), [alternative TU Graz publication record](https://tugraz.elsevierpure.com/en/publications/a-multilaminate-constitutive-model-for-stiff-soils/).

The complete 233-page PDF is acquired and stored privately. Its 7,724,452 bytes match the repository MD5; SHA-256 is `43d9a82e21523d303a684776580f57943277bc5fa9cb4d77648494e9daa876a9`. The rendered title page confirms author/title/date despite unrelated embedded PDF template metadata. The first truncated transfer was rejected; acquisition failures and successful retry are retained in [source-receipt.json](source-receipt.json). Open download does not establish redistribution permission; PDF, extracted text and rendered pages are not committed.

Complete pages visually inspected: PDF1; PDF26-30 (printed pp8-12); PDF79-80 (pp61-62); PDF180 (p162); PDF182-184 (pp164-166). A table of contents/text search locates further dependencies, but does not establish full reading. The separately downloaded earlier six-page paper is an unreviewed lead. The 2013/2014 papers and executable releases are not reconciled with this thesis.

This replaces the *source availability* gap in the [historical family triage](../../../reviews/parallel-candidate-triage.md), without rewriting that receipt. The [capability inventory](capability-inventory.json) targets [schema v0.3](../../../../schemas/model-v0.3.schema.json) and its [formulation contract](../../../FORMULATION_CONTRACT.md). It is not a model JSON or a complete executable crosswalk; unresolved signs/frame/kinematics are not filled with defaults.

## Plane integration and coordinates

The framework uses a static constraint: local normal/two-shear stresses are projections of the global effective stress (Eqs3-5, pp8-9). Local constitutive laws deliver normal/two-shear strains, and the global strain is a weighted plane reconstruction (Eqs10-16, pp10-11). This is not a kinematic microplane model that projects global strain directly to each plane.

The source global stress order is `(xx,yy,zz,xy,yz,xz)` with raw shear stress, while its global strain vector uses engineering shear (Eqs3,16). With `S=diag(1,1,1,sqrt(2),sqrt(2),sqrt(2))`, a proposed Atlas conversion is `sigma_M=S sigma_raw`, `epsilon_M=S^-1 epsilon_engineering`. Hence the local stress projection is `T^T S^-1 sigma_M` and reconstruction uses `S^-1 T`; their work pairing agrees. This algebraic coordinate conversion is not a source sign, objective-rate or finite-rotation decision.

Table1 (p12) lists 33 directions and weights for a symmetric **2 x 33** spherical rule. The listed weights sum to approximately one half. [quadrature.json](quadrature.json) preserves their printed decimals; the check includes both antipodes for spherical moments. Do not double history storage merely from that notation. Mapping the source's configurable NUMCP and exact implementation indexing remains a separate static review.

## Variant-dependent state budget

Table B.3 (p165) explicitly separates the following source implementation allocations. At NUMCP=33:

| Branch | Source history allocation | Values |
| --- | --- | ---: |
| Basic, no softening/small-strain stiffness | 3N+3 | 102 |
| MMSS, Hvorslev strength/softening | 7N | 231 |
| MMSC, Galavi-2007 softening | 8N | 264 |
| Any listed branch with small-strain stiffness, no recovery | 12N | 396 |
| Any listed branch with small-strain stiffness/recovery | 32N | 1,056 |

These are source host-history allocations, **not proved minimal mathematical states**. The host supplies global stress separately (Appendix B, p162). A direct Atlas layout would additionally store six stress components; the current engine limit is 32 components including stress (`atlas/model.py` at this checkpoint). Thus even the direct basic allocation exceeds it. No equivalent compressed state representation has been established. Increasing a constant alone would not implement plane quadrature, local active surfaces, history events or host coupling.

No smaller branch has been selected merely to fit the engine. The next full ingestion must explicitly select the intended thesis branch and distinguish small-strain anisotropy, recovery, Hvorslev/Galavi softening and nonlocal regularization. Later publications cannot silently replace it.

## Temporal/history and host contract

Appendix B p162 describes an increment interface receiving old stress, old history and the current strain increment. B.4 p165 labels the host implementation time-independent. Physical elapsed time, creep and rate effects are not introduced by this packet. Its reported stiffness is stress-dependent, symmetric and **not tangent**; that flag is not a proof of a consistent finite-update Jacobian.

Section4.4.3 pp61-62 stores strain history separately on each plane in local deviatoric-normal/two-shear space. A decrease in distance from the active contour centre creates an inner contour; later intersection with an outer history erases inner contours and reactivates the outer one. Four contours are implemented. This bounds nested stored reversals, not the total number of cycles. Exact event ordering, tolerances, coincident cases, saturation behavior and restart fields still need complete equation/code reconciliation.

Atlas trial/commit/rollback must preserve all plane histories and active contour identities together, including rejected global-control iterations. That is an implementation requirement inferred from the persistent history; no source-derived finite return algorithm or transaction proof is supplied here. Zero-load/hold behavior and any initialization-induced changes remain to be checked for the selected complete branch.

B.5 pp165-166 initializes local cap/cone positions from both current stress and a previous maximum state, with POP/OCR and K0nc inputs. It requires a plane-specific preparation procedure. Signs, POP/OCR precedence, parameter restrictions and complete initialization are not yet mapped; do not simply initialize all plane histories to zero or reapply preparation on restart.

B.2 p164 establishes a separate **nonlocal host dependency**: neighbouring point geometry, damage strains, weights and phase/iteration identity. A local material-point API plus larger state arrays cannot reproduce that regularized option. Any local-only restriction would need an explicit different scope, not an undisclosed omission.

## Independent bounded checks

Run from any directory:

```
python3 -B /absolute/path/to/thesis-2012-v1/check.py
```

Optionally add `--pdf /private/path/to/the/complete/thesis.pdf` to verify source SHA-256. [checks.json](checks.json) records the source-verified run. The standalone standard-library checker imports neither Atlas nor author code.

It checks the 33 printed direction norms, full spherical weight sum, all nine second and 81 fourth moments using exact rational arithmetic and a fixed 1e-8 printed-rounding tolerance. Maximum residuals are 2.675e-10 (norm), 3.4e-10 (weights), 1.918e-10 (second moments), 1.375e-10 (fourth moments). It independently checks one full-shear Cartesian traction projection and virtual-work witness, tallies all five state budgets, and rejects three deliberately corrupted transcriptions. The tolerance was chosen before calculation from printed coordinate/weight precision; it is not a constitutive accuracy threshold.

These checks do not validate yield surfaces, hardening, initialization, finite paths, objectivity, nonlocal regularization or experimental performance. No author Fortran/DLL, Atlas interpreter, native or Wasm model was executed; no build occurred.

## Next handoff and boundaries

Source access is now available; full source transcription is open. First complete Chapter3 yield/flow/hardening and the selected branch's parameter/domain inventory, then reconcile Chapter4 history/anisotropy and Chapter6 softening with Appendix B/D **statically**. Pin the exact NUMCP/state-index/event/preparation contract before proposing generic capacity or phase changes. Continue the 2013/2014 version comparison separately.

The output is source provenance, numerical geometry facts and a concrete capability gap. It adds no executable formulation, catalogue count, scientific acceptance, website deployment or data release. The broader ING-multilaminate task remains open.
