# Hoek–Brown, Itasca 9.0.182 — bounded source packet

**Task:** ING-hoek-brown-itasca900. **Owner/date:** coordinating parent, 1 November2026. **Scope:** first rock-family source/formulation inventory, not source-complete ingestion, a runnable model or scientific admission.

## Identity and sources

The selected target is the implementation documented as [`hoek-brown` in Itasca Software9.0](https://docs.itascacg.com/itasca900/common/models/hoek/doc/modelhoek.html), footer **9.0.182**, updated12November2025. This particular implementation uses confinement-dependent tangent Mohr–Coulomb coefficients, a tensile branch, selectable dilation and optional strength evolution. It is distinct from the strength criterion alone and from the [PAC implementation](https://docs.itascacg.com/itasca900/common/models/hoekbrownpac/doc/modelhoekbrownpac.html). Do not borrow PAC's nonlinear iteration or composite gamma flow rule to fill gaps in the selected target.

The target explicitly delegates to its [Mohr–Coulomb dependency](https://docs.itascacg.com/itasca900/common/models/mohr/doc/modelmohr.html) and [strain-softening/hardening dependency](https://docs.itascacg.com/itasca900/common/models/ssoft/doc/modelssoft.html). All four primary HTML pages were acquired privately, read and hashed in [source-receipts.json](source-receipts.json). No vendor code, binary or example was executed. Manual HTML stays private; public commentary, algebra and locators are original packet material. These public pages do not establish redistribution rights for the manual or vendor implementation.

The manual cites the2002 Hoek–Carranza-Torres–Corkum criterion edition and earlier Hoek–Brown work. Those original publications were **not** acquired or reconciled here. The manual implementation must retain its own identity rather than being attributed in full to a criterion paper.

A request for the Hoek–Brown tangent figure returned403; the second figure was not requested after that failure. Neither figure was viewed. The mathematical HTML displays and adjacent text were inspected; a graphical composite-branch divider remains unavailable. [Acquisition notes](acquisition-notes.json) retain the failed request and the subsequent failed attempt to display a missing image. No unavailable graphic is represented as inspected.

## Existing work and gaps

The charter includes intact/jointed rock, while the existing canonical catalogue and execution work concentrate on soil formulations. This packet starts one named rock implementation without increasing executable counts. Existing Mohr–Coulomb spectral/branch work is relevant infrastructure, but is not proof that this staged tangent law, tensile treatment or strength evolution already works in Atlas.

The packet closes a bounded reading/inventory task. All eight [HB-01–08 gates](gaps.json) remain open. The target is preserved in full, including optional evolution and host dependencies; no reduced perfect-plastic fragment is substituted for it.

## Equations and schema crosswalk

[Equation ledger](equation-ledger.json) covers all fifteen displayed main-page equations with exact source anchors and the delegated elasticity, return and hardening sections. [The v0.3 crosswalk](crosswalk-v03.json) is an explicit capability inventory, **not a schema-valid model definition**. Its unresolved stress scope is deliberately null rather than guessed.

| Source | Representation / mapping | Required decision |
| --- | --- | --- |
| HB Eqs1–4 | Nonlinear strength envelope and GSI initializer; stress constants inPa, dimensionless coefficients | Original criterion reconciliation and admissible initializer range |
| HB Eqs5–11 | Tangent friction/cohesion computed at capped confinement | Parent/trial/iterated sampling and refresh chronology |
| HB Eqs12–15 | Dilation/potential and plastic-volume meaning | Total versus deviatoric increment interpretation; selector discrepancy and dilation limiting |
| MC Eqs1–15 | Isotropic elastic predictor and shear correction in principal axes | Composite branch/equality and repeated-spectrum policy |
| MC Eqs16–30, apex section | One-, two-, three-direction tensile corrections and apex handling | Correct active region, order and cap semantics |
| SSoft Eqs1–6 and procedure | Plastic shear/tension measures, zone average and post-stress property updates | Exact HB delegation, especially evolutionflag0 and multi-tension events |
| HB property/notes sections | Tables, current/constant parameters, brittle failure, length scaling and FISH updates | Full history/host/event ownership and versioned external updates |

Use compression-positive ordered values `p1 >= p2 >= p3`. The MC dependency uses negative compression with `t1 <= t2 <= t3`: set `ti = -pi` and flip strain signs together. Do not also reverse the labels. Then the shear condition is `p1 - Nphi*p3 - B`, and the full flow gradient in the smooth principal branch is `(1,0,-Npsi)`. Physical tensor storage would be six Cartesian Mandel components. A principal frame derived during a trial is not a persistent orientation state or finite-rotation objective update.

The crosswalk lists thirteen parameter/property groups, persistent versus transient inventories and unsupported interfaces. A full adapter needs stress, selected evolution history, tensile history/current strength, irreversible brittle state and any lagged properties, plus coordinated subzone/zone state if that source option is selected. No unsupported state capacity claim is inferred from the scalar yield equation.

Important unresolved readings include: HB Eq12's mean subtraction; a self-referential dilation expression in a property line versus the earlier fractional-friction prose; exact evolutionflag0 measure and table-multiplier action; unstated sampling/update details; the graphical branch divider; effective versus total stress and specimen preparation. These are source/algorithm gates, not approved corrections.

## Temporal integration and transactions

[Temporal contract](temporal-contract.json) separates inspected source ordering from proposed Atlas requirements. The loading variable is a mechanical increment, with no physical-time creep law established. Source stage ordering, coefficient refresh and table evolution can make a finite step differ from subdivided steps; the appropriate acceptance is refinement and recorded accepted-partition replay, not subdivision invariance.

A future adapter must evaluate all trial states from an immutable parent and atomically commit stress, every history field, current strengths, irreversible events and host-averaged changes. Failed caller increments restore the complete parent. Restart cannot reset current coefficients to initial constants. Host property/FISH changes need explicit versioned events, rather than hidden mutation during Newton trials.

For an admissible zero-load parent and no external event, identity is a proposed rate-independent contract. Source behavior for an invalid/overstressed or externally edited parent is unverified; do not install a blanket zero-increment shortcut. A duration field would not supply missing creep physics. Full finite rotations, general staged discrete updates, tabulated evolution policies and zone averaging are not established by the existing v0.3 residual profile.

## Independent checks

```sh
python3 -B docs/ingestion/hoek-brown-itasca900/check_algebra.py
python3 -B docs/ingestion/hoek-brown-itasca900/verify.py
```

Nine exact/rational or60-digit diagnostic groups reproduce [algebra-results.json](algebra-results.json), with zero Atlas/vendor calls:

- Tangent value/slope checked independently through an implicit squared-envelope identity.
- A finite-step witness retains a25Pa difference between the nonlinear envelope and its frozen tangent. This prevents treating the two return algorithms as interchangeable.
- MC sign/order conversion, elastic correction, yield closure and work conjugacy checked exactly.
- Total versus deviatoric flow diagnostic retains nonzero plastic volume separately from zero-trace projection; it does not correct Eq12.
- Shear invariant reduced independently from principal increments; zero-confinement tensile bounds, geometry scaling and the intact GSI100 limit checked.

These are smooth scalar/algebra checks. They do not verify a complete return algorithm, source branches, softening, rotations, material tangents, finite histories or vendor equivalence. Source availability, software verification and scientific admission remain separate.

## Handoff

Owned files: this README; source/claim/acquisition receipts; equation, v0.3, temporal and gap ledgers; independent checker/results; manifest and portable verifier. Four source HTML pages remain private and are optional to reopen by hash with `verify.py --private-sources`. No raw HTML, figures, vendor source or PDFs are bundled.

**Source status:** primary manual text/equations inventoried; figures/original criterion and eight decisions unresolved. **Execution:** none added. **Verification:** nine bounded independent algebra groups only. **Scientific admission:** pending/unassigned. No model/schema/solver migration, builds, canonical candidate insertion, push or deployment occurred.

Smallest next action: resolve HB-01–08 from exact authoritative implementation documentation, starting with sampling/update chronology and strain/history conventions. Obtain the mathematical branch graphic or an equivalent explicit primary-source definition. Then define a separately named complete material-point/host contract, an independent finite-path reference and prospective acceptance policy before any generic implementation or compiled observations. Stop this reading pass here; do not run a rock-model fitting campaign or add an approximate criterion-only implementation.
