# GIS2024 browser and preparation integration plan

PLAN-gis2024-browser-preparation-v1, 1 November 2026. The exact selected
HP/extracted-ASBS+GIS2024,f=0 model is a source-linked v0.3 research draft.
[Mixed eleven-model qualification](../gis2024-mixed-catalogue-v1/README.md)
passes, but does not qualify laboratory-controller routes or establish
source-prepared initial memory. This plan makes those prerequisites explicit.
All implementation and browser checkboxes below remain unexecuted.

## Fixed identity and evidence

Use `docs/reviews/gis2024-v03-research-freeze-v1/model.json` byte-for-byte,
ID `research-hp-extracted-asbs-gis-2024-v03`; its hash is in `policy.json`.
Do not rename/rewrite the candidate just to remove the research label: doing so
would require a distinct identity and renewed catalogue/build binding. The
existing generic `hypoplastic-generalized-igs-2024` discovery entry remains a
separate, non-executable family/extension record. Link the selected pairing;
do not count discovery aliases as additional executable formulations.

Maintain primary hyperlinks and locators in schema, model page and source review:
[Mugele, Stutz & Mašín (2024), DOI](https://doi.org/10.1016/j.compgeo.2024.106480)
and [institutional PDF](https://publikationen.bibliothek.kit.edu/1000171366/153009465).
Source SHA, source sign conversion, selected host and limitations remain in the
[formulation crosswalk](../../ingestion/hypoplastic-generalized-igs-2024/README.md).
No new source correction, author-code equivalence or scientific signature is
implied. Pending reviewer remains unassigned.

## What current code already does and what it does not establish

`web/state-contract.mjs` consumes the full declared example; `populate` exposes
all persistent fields after sigma, including six h values and scalar Omega.
`valuesForState` reconstructs sigma from axisymmetric stress controls, never from
a general tensor editor. `validateSpec` rejects unsupported shear stress.
`laboratory-scope.mjs` validates shape, finite values, parameter bounds and stress
scope; **it does not evaluate model-domain equations**. Engine-domain failures
must therefore be tested in the actual engine, not credited to JS preflight.

Scoped JSON documents retain complete initial/point state and matching catalogue
identity; import replays from supplied initial state. CSV currently exports
observations and is not a full history restart representation. Keep that contract
clear rather than claiming CSV roundtrips h/Omega. Page reload and model switching
must not create DOM/input/model mismatches or implicit continuation.

The example is sigma=100kPa I,e=.595,h=0,Omega=0, with19 explicit parameters
(18 physical plus numerical p_scale). The previous finite-path qualification
used nonzero full-tensor memory. The default origin, axisymmetric mixed
controllers and preparation workflow need separate route evidence. Existing
strain-increment passes do not justify a source-prepared or universally stable
laboratory default.

`matchExperiment` changes observed stress/e and protocol, retaining other memory
edits. Its current button wording can imply complete initial preparation. The
integration must visibly state which fields were matched and that h/Omega remain
explicit user/example inputs. This should use declared state metadata, not a
handwritten GIS-specific material branch. Experimental overlays retain their
existing protocol, axis, scope and reuse restrictions; no new measurements or
validation claims are introduced.

## Stage A — laboratory-route qualification, before installation

- [ ] Claim NUM-gis2024-laboratory-route-v1. Verify existing native/Wasm engine
  hashes and generated catalogue against mixed-catalogue receipts. Reuse the
  qualified engines if unchanged. A missing artifact permits a new isolated
  serial one-target build, not use of stale build/ defaults.
- [ ] Freeze a driver, independent saved-output assessor, corruption tests and
  literal expected rates **before** compiled observations. Bind the Cartesian
  origin-rate oracle and all inputs. Test six positive/negative Mandel basis
  directions at1e-6 plus zero for both origin/interior states (26 rates).
  Use `policy.json` component budgets. This addresses instantaneous algebra;
  it is not an origin derivative/tangent or full-trajectory accuracy claim.
- [ ] Execute native first: the60 prospective cases in `laboratory-cases.json`,
  eight `guard-cases.json` rejections with immediate clean recovery, and the
  distinct forced update-budget failure/recovery. Cases span both complete
  preparation examples, all five protocols, zero/monotonic/cyclic loading and
  exact/legacy wire routes. Exact controls come from existing `createLoading`;
  legacy cyclic arithmetic is retained separately, never relabelled as exact.
- [ ] Assess every14-component state, domain, zero equality, exact density/volume
  relation, committed prefix, finite outputs, controller constraints, response
  scope, settings and exact-loading identities under `policy.json`.
  Invalid initialization must produce no initial point. The valid forced-update
  failure must preserve its initial full-state point and failure status.
- [ ] Only on native acceptance run the same cases in Wasm; require unchanged
  full-state native/Wasm scaled parity1e-7 at all comparable points. Record
  real raw outputs and artifact identity. No reduced successful subset or
  post-result tolerance/default tuning. If any required case fails, retain it
  and stop installation with the smallest diagnosis; this planning task does
  not pre-approve a model, solver, boundary or preparation correction.

These are bounded software/controller/branch-route checks plus instantaneous
source algebra. They do not replace independent finite-trajectory accuracy,
scientific admission, calibration or experimental validation. Original isolated
and mixed-catalogue evidence keeps its original scope.

## Stage B — exact local draft installation and preparation disclosure

Depends on passing Stage A, not merely completing its execution.

- [ ] Before shared edits, identify and archive exact historical bindings for
  `catalogue/manifest.json`, source/applicability records and changed web assets.
  Preserve all prior pinned packets and failed reports; append new identities.
- [ ] Copy the exact candidate into top-level models under its unchanged ID;
  register a distinct executable draft entry linked to the existing discovery
  family. Add a current-definition pending source review with a canonical
  selected-pairing dossier. Keep reviewer/signature absent. Link the DOI,
  institutional source, crosswalk, qualification and limitation records.
- [ ] Update `catalogue/applicability/kfs-development-v1.json` with exact new
  definition coverage and explicit **unassessed** preparation/calibration/
  experiment status. Do not infer eligibility from effective stress alone.
- [ ] Add visible initialization/preparation and strict-domain notes using
  existing generic formulation/state metadata where practical. Required fields
  are sigma6,e,h6,Omega; no implicit persistent-history fill or memory projection.
  Example loading/reset must visibly replace the whole example. Preserve the
  model's source math,18physical+1numerical distinction and units as stored.
- [ ] Clarify experimental initial-state matching: only supplied observed fields
  change, h/Omega remain explicit and unprepared. Preserve effective-stress and
  pore reconstruction assumptions and compatibility guards for every model.
- [ ] Package with `tools/build_web.py --wasm-dir <hash-verified-eleven-engine>
  --output <fresh-local-package>` after exact installed catalogue generation
  matches the engine. Do not relink an engine under different definitions.
  Package source review and dossiers, schemas, all definition JSON and links.

## Stage C — actual packaged browser acceptance and stop

- [ ] Freeze the package/source inventory and browser driver before execution.
  Serve a fresh local package at the GitHub Pages project prefix
  `/constitutive-atlas/`; host-local development is not deployed Pages evidence.
- [ ] Execute **B01–B12 in `browser-cases.json`** in the actual browser. Capture
  literal worker requests, downloaded scoped JSON, rejection/recovery results,
  link targets and screenshots. Node-Wasm and DOM-free tests are not substitutes.
  Compare full history and identities rather than just plausible plot shape.
- [ ] Run focused consumer/package/formulation/state/document/experiment/source
  review/applicability checks and the existing ten default smoke cases. Add
  meaningful generic preparation tests only for behavior actually changed.
  No unrelated refactor or new fit/numerical campaign belongs here.
- [ ] Retain original failures and corrections, exact artifact/package identities,
  commands and stop/go report; update counts and board consistently and commit
  only owned work locally. Stop after local draft integration. No push, hosted
  CI, deployment, author contact, scientific admission or experimental release.

## This planning packet's executed checks

`python-preflight.json`: both complete initializations pass; five invalid domain
states reject without mutation. No constitutive integration or compiled call.
`node-preflight.json`: all60 prospective specifications pass existing consumer
shape/scope/loading validation; missing-h and missing-Omega shapes reject; six
engine-domain/geometry checks are explicitly deferred. The complete example
retains14components. None of these preflights executes a laboratory controller.
`verify.py` checks frozen identities and case coverage; it does not run a model.
