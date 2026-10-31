# Clay2005 corrected-plus/SPD candidate - prospective compiled plan v3

Task SRC-clay2005-compiled-plan-v3; owner clay2013_source_closure;2026-10-31. This packet supplies a **new schema v0.3 instantaneous-rate research candidate and prospective corpus**, not a public laboratory addition, compiled result or scientific admission. No source oracle is rerun, fitted or rederived.

## Source and candidate identity

[Mašín2005, A hypoplastic constitutive model for clays](https://doi.org/10.1002/nag.416), IJNAMG29(4),311-336; [accepted author manuscript](https://web.natur.cuni.cz/uhigug/masin/download/MasinIJNAMG05-pp.pdf),718767bytes/26pages, SHA256 `8650dd58a4b5725dc0176ab9cf3a034ed211847b840524254876c2652bdf9ff3`. AppendixC Eqs73-85 PDFpp24-25 is the selected base; p10Eqs38-41 provides coefficient/unloading interpretation. Manuscript footer2004 and publication2005 are not distinct formulations. Final-publisher equation equivalence remains unverified. Raw private source remains `/private/tmp/atlas-ingest-clay2005-20261031/private/masin-2005-author.pdf`; no full text, extracted text, render or author code is bundled.

Read existing [v2 source study](../rate-study-v2/README.md), [additive correction](../rate-study-v2/SOURCE_CORRECTION.md), [original independent audit](../rate-review-v1/README.md) and [guard audit](../guard-review-v2/README.md) before preparation. This pass relies on those existing exact-source visual reviews; it does not claim a new PDF inspection. The pinned Eq38 unloading bracket is **Q+f_di*a*sqrt(3)**. The historical claim of a printed minus was an Atlas extraction error, not an author typo; Eq40 and AppendixC agree. No constitutive sign change is made now. Old packets, false-positive SPD witnesses and historical corrections remain unchanged.

Candidate ID `hypoplastic-clay-2005-appc-plus-spd-interior-v3-research` is deliberately separate from both the frozen v2 research identity and the public candidate `hypoplastic-clay-2005`. It is draft, not public-root executable. `model.json` preserves **exact JSON values** of v2 `equations`, `derived`, `domain` and `parameters`, including their insertion order. Metadata, source/limitation links and explicit v0.3 formulation/state/initialization contract identify the new record.

## Explicit contract, parameters and scope

The source stress T and Euler stretching D map to T=-sigma,D=-E. The selected zero-spin restriction is strain_path/strain_path_rate,small_strain_3d,fixed_spatial,objective_rate:none,orthonormal Mandel xx/yy/zz/sqrt2xy/sqrt2yz/sqrt2xz,compression_positive stress and strain. `de` is a symmetric dimensionless strain increment used over path fraction0..1, not a physical per-second rate. Effective Cauchy stress is bound to persistent state sigma6; void ratio e is a persistent scalar invariant. No pc/plastic strain/fabric/IGS/spin/history resets are introduced. Source objective tensors do not authorize a finite-rotation transport in this restricted profile.

The source five soil parameters are phi_c,lambda*,kappa*,N,r; r is initial Ki/Gi, **not** the later model's nu. Default22.6degrees,.11,.016,1.375,.4 corresponds to the main TableI London-clay base calibration identified by the source packet; it is not a universal clay fit or a matched Wichtmann preparation. p_ref=1000Pa is fixed reference normalization; p_scale is numerical error weighting; lode_allowance and j2_floor are fixed numerical support metadata. All nine positional slots remain in order p_ref,p_scale,phi_c,lambda_star,kappa_star,N,r,lode_allowance,j2_floor.

Require explicit sigma/e, with examples_only and domain_and_initial_checks. Default100kPaI/e=.8 is an illustrative state, not a verified prepared specimen. The companion [2005 study](https://doi.org/10.1016/j.compgeo.2005.09.001) supplies density/preparation context; SOM must not be substituted for SBS or imposed as a universal initial yield barrier. No hidden density reconstruction, OCR interpretation, consolidation history or projection is supplied. The five defaults and source applicability to reconstituted/stable-structure clays do not establish arbitrary initial-state validity.

V2's conservative normalized Cartesian/Mandel positive-diagonal/leading-minor64epsilon guard is retained exactly. It fixes the demonstrated invariant-only support vulnerability without changing the source rate algebra. It is a numerical interior, not an all-SPD classifier or certified determinant theorem. Finite intermediate norm overflow/underflow, j2floor and raw-Lode allowance restrict support. Accepted near-singular witnesses need finite outputs only; high-precision near-isotropic/near-singular **rate accuracy remains unresolved**. No clipping, stress floor or generic source-domain claim is added.

## Retained inputs and literal corpus

The five files `source-reference.json`, `source-invalid-cases.json`, `source-support-inputs.json`, `source-support-reference.json`, `source-protocol.json` are **byte-identical copies** of the corresponding v2 files. Their provenance stays v2; the source-reference version/diagnostics/expected values are not relabelled as new evidence. `corpus.py` reads retained literals and expands only positional arguments and already declared budgets; it never imports or evaluates the source oracle, interpreter or an integrator.

`corpus.json` is a **tagged proposal**, version clay2005-tagged-instantaneous-corpus-v3. It is intentionally not mislabeled as a currently accepted generic-v2 protocol. `requests.tsv` is the exact tab-separated stream: `--describe`, then109four-string calls to the generic `atlas_research_rate` C ABI/stream driver.

Order and count:

1.41original accuracy cases, preserving all original expected seven-rate vectors and source input scales.
2.10accepted support-only cases, requiring finite seven-rate outputs with **no expected vector or source numerical tolerance**.
3.29negative/recovery pairs:10historical finite numeric invalids and19excluded support cases. Each rejection is immediately followed by the identical known admissible baseline (the first original accuracy case), linked through recovery_of and after_rejection. Duplicate physical vectors retain distinct original-case identities.

Total109calls/backend plus descriptor=110raw response rows/backend. The repeated29controls do not increase the independent source-accuracy count beyond41. No parser/type/malformed-CSV cases are counted as material-domain coverage. Every argument has finite numeric CSV arity9parameters/7state/6increment. Origins bind exact retained-file hashes and case IDs; literal .17g CSV preserves each actual binary64 number. No rereferenced ideal spectrum or rounded intended stress replaces actual source inputs.

## Prospective acceptance and recovery

For each original accuracy case, retain source budgets **without refit**:

- Six stress channels: `1e-10Pa+2e-12*S`, where S is the unchanged retained input-based stress_scale.
- Void channel: `1e-15+2e-13*V`, where V is the unchanged retained void_scale.

Reference.json documents S=max(1Pa,norm(sigma0))*norm(E) and V=max(1,(1+e0)*norm(E)); this packet uses the saved scales, not new compiled outputs. Exact spheres and the nonisotropic j2>=1e-8 accuracy restriction remain unchanged. Recovery controls carry the same reference/budgets as their baseline. For cross-backend parity on those accuracy rows, this prospective plan chooses those same absolute budgets; this is a separately declared parity choice, not a claim that v2 already performed compiled parity.

Accepted finite_only rows require ok:true, empty message and exactly seven finite real non-Boolean values. **Do not compare to fake zeros, NaNs or a giant numerical tolerance.** Their native/Wasm parity is separately `abs(n-w)/max(1,abs(n),abs(w))<=1e-10` per component; that uses both observed backend values only and provides no independent source-accuracy claim. Rejected support and historical invalid rows require exact ok:false, nonempty material-domain failure message, correct finite input echoes and values:null. Distinguish a recognized domain rejection from parser/type/arity exceptions.

Every response binds model ID, actual catalogue hash, full parameter/state/increment echoes and exact shapes. Descriptor must match the complete candidate document and **parameter insertion order**, rather than relying on sorted-object equality. Strict JSON rejects duplicate keys, NaN/Infinity and bool-as-number aliases. Retain opaque responses before interpretation, raw stderr/termination/exception states and every failed result. Every recovery must use exactly the baseline args and reproduce the complete baseline response in the same native stream process or persistent Wasm module. This is pure instantaneous call contamination recovery, **not** finite-update rollback or history-transaction evidence.

No finite integration, tangent/AD, positive-stress theorem, physical preparation or experiment claim follows from passing this matrix. Do not revise gates after compiled observation; any failure remains retained negative evidence with a separately identified follow-up if needed.

## Generic v2 transport gap

Inspected `tools/research_rate_observations_v2.py`, `tools/collect_research_rates_wasm_v2.mjs` and `tools/research_rate_parity_v2.py`. V2 correctly accepts explicit v0.3 strain-path profiles and enforces descriptor parameter order/strict duplicates; it does **not** represent accepted finite-only support.

`checked_protocol` unconditionally requires values/absolute_budgets/parity_budgets on every expected ok:true row. `audit` unconditionally computes reference errors, and `parity` reads frozen per-component budgets for every successful row. The Node collector imports that validator. Consequently collection as well as audit cannot honestly use the ten accepted support-only rows. `transport-v2-gap-witness.json` is a minimal valid-model/single-finite-row witness in the current v2 protocol envelope: source-only `checked_protocol` rejects specifically with `KeyError('values')` after profile/model/finite-CSV checks. No process or Wasm module is launched by this witness.

Smallest requested capability: a separately versioned **generic tagged expectation contract**, with accuracy requiring expected vectors plus source/parity budgets, finite_only forbidding source values/budgets and requiring only finite shape plus separately declared backend parity, and reject requiring status/echo/null output and material-vs-parser semantics. Keep exact descriptor/layout/source/build/raw bindings and persistent recovery. Freeze the new validator/collector/auditor/parity closure before compiled execution; preserve the existing v2 tools and old study receipts. A distinctly frozen honest collection/assessment layer could also be reviewed by the coordinator, but must not convert finite support into fake numerical accuracy. This worker edits none of those shared tools.

## Reproduction and evidence status

```sh
python3 -B docs/ingestion/hypoplastic-clay-2005/compiled-plan-v3/corpus.py --check
python3 -B docs/ingestion/hypoplastic-clay-2005/compiled-plan-v3/check.py --root /Users/bmar5496/code/constitutive-atlas
```

`checks.json` records v0.3 schema/contract validation, exact unchanged mathematical fields, five byte-identical source-data copies,109unique literal rows with correct arities/tag counts/recovery pairing, exact corpus regeneration and the actual v2 finite-only gap. No original source rates/support classifications are recomputed. The initial checker assertion looked for uppercase PLUS in a mixed-case correction note and failed; `checker-initial-failure.txt` retains this development issue. Changing that text-only check to case-insensitive matching made it pass; model/corpus/budgets did not change.

Manifest hashes identify the packet, retained v2 source/audit/transport snapshots and source identity. This is **not** a complete frozen compiler/runtime/build closure. Coordinator must independently review the candidate/source mapping, resolve the tagged-transport capability, then freeze exact compiler/schema/headers/driver/generated catalogue/protocol/reference/support/policy/collector/auditor/toolchain/artifact identities before running serial one-target native and Wasm builds. No scientific review status, public-root installation, push or deployment is requested.

Remaining independent gates: final-publisher source equivalence; high-precision near-isotropic/near-singular rate accuracy; full coupled finite-stage paths with source-matched preparation, partitions and transaction failure/recovery; objective frame transport; material AD; calibrated experimental comparisons; human scientific admission. Historical source errors, failed guard witnesses and all old packets remain untouched.
