# GIS2024 selected-host ingestion and v0.3 crosswalk

ING-gis2024-v03-crosswalk-v1; coordinating parent, 1 November 2026.
This consolidates the **HP/extracted-ASBS + GIS2024** research pairing and validates
an explicit v0.3 contract in memory. The existing model record is unchanged.
It closes this contract task, not complete ingestion, scientific review or public
installation. Other GIS hosts, the `S=Y` pairing, IGS97 and ISA remain distinct.

## Identity and sources

Mugele, Stutz and Mašín (2024), *Generalized intergranular strain concept and its
application to hypoplastic models*, Computers and Geotechnics173,106480:
[DOI](https://doi.org/10.1016/j.compgeo.2024.106480),
[KIT record](https://publikationen.bibliothek.kit.edu/1000171366),
[institutional published PDF](https://publikationen.bibliothek.kit.edu/1000171366/153009465).
[Sources](sources.json) preserve the private PDF path/hash and prior inspection
receipt. This task reuses the retained source reading; no new PDF-page inspection,
publication acquisition or author-code execution is claimed. The earlier
[source inventory](../../models/hypoplastic-generalized-igs-2024-source.md)
records the KIT date discrepancy and separate paper/code rights. No raw publication
or source images are bundled. The [author-code listing](https://soilmodels.com/download/generalised-intergranular-strain-concept/)
is not an acquired, licensed or reconciled implementation release.

## Existing work and what is new

The [typed host](../../models/gis-2024-hp-extracted-asbs-host.md),
[composition](../../models/gis2024-typed-composition.md),
[rate integration](../../models/gis2024-research-rates.md),
[finite-path study](../../models/gis2024-research-integration.md),
[flattened review](../../reviews/gis2024-flattened-review.md) and
[boundary review](../../reviews/gis2024-boundary-review.md) already exist.
Historical descriptions of “next” work and public model counts in those files
apply to their recorded revisions; they are not today's work board.

This packet adds a source-located [v0.3 fragment](crosswalk.json), explicit physical
history semantics, initialization contract, temporal/lifecycle inventory and
current-definition binding to the historical integration records. It adds no new
constitutive equation, compiler capability or material path. The existing
[research definition](../../../models/research/gis2024/hp-extracted-asbs-gis-2024-research.json)
is legacy v0.1 and remains owned by the separate migration/integration process.

## Equations and schema crosswalk

Target: [v0.3 schema](../../../schemas/model-v0.3.schema.json) and
[formulation contract](../../FORMULATION_CONTRACT.md). Source tensor signs are
mapped together: `sigma_A=-sigma_source`, `de_A=-de_source`, `h_A=-h_source`,
and `m_A=-m_source`; e,Omega,C,S,k are scalar invariants. Mandel shear entries
carry sqrt(2), preserving Frobenius contractions. Effective Cauchy stress is the
state field sigma. No pore-pressure evolution is included.

| Source locator | Selected quantity/equation | v0.3 representation |
| --- | --- | --- |
| Eq7, introduction objective rate, AppendixA signs | Degree-one rate law, restricted to zero spin | strain_path / strain_path_rate; small_strain_3d; fixed_spatial; objective_rate:none; compression-positive Mandel |
| Eqs8–12,26–32; AppendixB | `E=fs*L`, `m=-unit(L^-1:N)`, `C=norm(L^-1:N)*fdAstar`, `S=fd/fdAstar`, `f=0` | Flattened typed derived actions; no hidden host state or fourth-order storage |
| Eq40 | `sigma'=k*E:(de-m*C*S**(k**gamma)*norm(de))` for selected f=0 | sigma sym6 Pa; persistent cauchy_stress / symmetric_spatial_tensor |
| Eq22 | `e'=-(1+e)*trace(de)` | e scalar1; persistent void_ratio / scalar_invariant |
| Eqs33–35 | hdir=unit(h), or0 at h=0; rho=norm(h)/R; positive hdir:de subtracts hdir*rho^beta_R*(hdir:de), otherwise h'=de | h sym6 strain1; persistent intergranular_strain / symmetric_spatial_tensor; full trace retained |
| Eq39 | Directional k from rho, hdir:unit(de), m_R,m_T,chi_R | Derived scalar; recomputed at each stage, no reversal reset |
| Eqs41–43 | chi=chi_0+Omega*(chi_max-chi_0); gamma=gamma_chi*chi; Omega'=C_Omega*(1-rho^gamma_Omega-Omega)*norm(de) | Omega scalar1; persistent cyclic_preloading_memory / scalar_invariant |
| Table1 p8 | 18 physical parameters | Explicit named inputs with Pa hardness and radians angle; p_scale is a nineteenth, numerical parameter |

The nested exponent is `S**(k**gamma)`. Independent gamma_Omega is retained;
it is not silently tied to gamma. Omega can decrease and is not a cycle counter.
The projected current-state fdAstar evaluation is distinct from a numerical
search for an actual asymptotic boundary state.

## Initialization and declared domains

All sigma6,e,h6,Omega are required: 14 persistent components, no multiplier,
loading flag or reset anchor. The fragment declares `explicit_state`,
`examples_only`, all four named fields and `domain_and_initial_checks`.
Existing state initials remain software fixtures, not inferred specimen preparation.
The article's particular p8 prepared example and later cyclic example must be
transcribed as separate source-matched protocols before claiming reproduction.

Current support requires positive pressure, ed<e<ei, ordered limiting densities,
strict computed norm(h)<=R, 0<=Omega<=1, finite positive host factors and evaluated
denominators, and representable nonzero suppression for nonzero loading. Source
calibration and rectangular JSON ranges are different claims. See the pinned
model for every actual guard. No pressure floor, state projection or clamping is
introduced. A rotated mathematically saturated tensor can fail strict binary64
norm admission; exact continuous invariance does not guarantee valid explicit
stages. Near-singular ASBS, invariant underflow and large exponents remain scope
limits, not grounds for silently changing the equations.

## Temporal integration and transactions

The common caller supplies dimensionless de over a straight strain-path fraction
0..1. No physical clock, frequency dependence or creep is introduced. Recompute
host action, mobilization, h,Omega and e from the same 14-component stage. No
source-defined lagged old/new phase, discrete history event or endpoint reset is
present. Source objective notation does not establish finite-rotation transport;
this contract restricts spin to zero.

At exact zero de the selected f=0 pairing has 14 zero rates. Internal q/k or
suppression placeholders there do not define a unique loading direction or
smooth zero-direction tangent. Nonzero vectors whose norms underflow reject.
Material/rate derivatives and a full finite-update tangent are separate claims.

Adaptive integration, caller partitioning, tolerances, budgets and failure
semantics are project numerical choices. Trial state must be isolated; failed
advancement returns the entire committed state unchanged; successful steps carry
all histories forward. Reversals change instantaneous loading without resetting
memory. The article does not choose the common C++ solver's algorithm.

## Checks and evidence applicability

[checks.json](checks.json) records normal v0.3 validation of an in-memory copy,
unchanged parameters/equations/derived/domain/source/layout bytes, complete explicit
initialization and exact input isolation. All four omitted-field cases and invalid
Omega, radius and void ratio reject; a valid initialization succeeds afterward.
This is contract consistency, not a new independent source algebra oracle.

The saved native/Wasm finite-path records each contain 20 trajectories/204 updates,
with noncoaxial/reversal and fixed-rotation companions. Their model identifiers
are **canonical JSON hashes**, distinct from raw-file byte hashes. The packet
checks that they bind the current legacy definition. Existing compiled results
still use their historical engine/toolchain and do not automatically qualify a
future v0.3 model identity or current engine. No reference or trajectory is rerun.
The existing narrow interior paths, rollback/recovery and parity observations do
not establish arbitrary boundary advancement or experimental applicability.

```sh
python3 docs/ingestion/hypoplastic-generalized-igs-2024/verify.py
```

This checks public input/file hashes and repeats only in-memory contract and
initializer checks. No compiled artifact or trajectory integration is called.

## Handoff and next bounded work

Source status: selected published pairing has a substantial retained equation
mapping; author release/license/discretization and independent full equation
judgments remain unresolved. Executable status: existing isolated legacy research
record, no newly installed model. Numerical status: historical bounded rate/path
evidence plus this contract check. Scientific status: unreviewed, no promotion.

Next have the migration/integration owner stage a distinctly named v0.3 artifact
with an exact mathematical bridge and prospective current-backend/rejection/
restart policy. Source-based preparation and broader boundary support remain
separate decisions. Do not repeat the historical interior study as if it were
new source verification or borrow IGS97/ISA defaults to fill missing histories.
