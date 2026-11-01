# Barodesy clay 2017: bounded production-admission closure

Prepared 1 November 2026 for ADMIT-barodesy2017-closure-v1. This is a decision packet, not a signed review or status promotion. The executable remains **draft**. The source, numerical studies and pending review already exist; another broad numerical campaign is not the next action.

## Exact candidate and proposed claim

Candidate: `models/barodesy-clay-2017.json`, SHA-256 `0bf4fd2789274f1271b438ffea57168866f7ebea55cfcf8ef786532903ab3477`. The pending [source review](../../../../catalogue/reviews/barodesy-clay-2017-source-v1.json) already binds these exact bytes. The linked `pins.json` records this packet's inputs; `preflight.py` verifies them without executing compiled artifacts or updating evidence.

Proposed first claim, **subject to independent agreement**: a source-linked, numerically supported material-point implementation of the Medicus–Fellin 2017 body Eqs 1–10, with body `2p` critical density, incompressible grains and zero spin; small-strain, fixed-spatial, compression-positive effective Cauchy stress in six Mandel components, plus void ratio. It advances dimensionless strain-path rates from explicit stress/e and resolved parameters. It has no physical-time relaxation or hidden preparation memory. The numerical support is the declared conservative positive-definite stress interior and bounded matrix exponential, within specifically tested parameter/path sets.

The first claim excludes general finite rotation, complete author-UMAT equivalence, the alternative Appendix `6p` law, arbitrary parameter/domain accuracy, a universally valid complete-update tangent, and experimental prediction. Review may accept this restricted identity without declaring an erratum. If that scope is rejected, retain the draft; do not silently repair the source or enlarge the claim.

## Source choices requiring a decision

The existing [source inventory](../../../reviews/barodesy-clay-2017-source-packet.md) and [technical cross-review](../../../reviews/barodesy2017-independent-review.md) document the publisher PDF: Medicus and Fellin, *An improved version of barodesy for clay*, Acta Geotechnica 12, 365–376 (2017), DOI [10.1007/s11440-016-0458-4](https://doi.org/10.1007/s11440-016-0458-4), PDF SHA-256 `bd049a3fd874c9e4945e1c77f5af5b84ac14c26a08cee1b953428b4312e6af15`, acquired 31 October 2026. This packet relies on those retained inspections; it makes no new PDF inspection or author contact claim. Raw source is not copied here.

| Decision | Existing evidence | Proposed disposition, unsigned |
|---|---|---|
| Body critical density versus appendix | Body Eq 8 p367 and Appendix 2 Eq32 p374 use `2p/sigma_star`; Appendix 3 Eq41 p375 implies `6p/sigma_star` using p=-tr(T)/3. The NCL scalar reduction distinguishes the readings. | Accept the explicitly named body selection only; keep discrepancy visible, without claiming confirmed erratum. |
| Objective-rate typography | Section 2 p366 repeats WT products in the printed conversion. Fixed-basis covariance does not establish finite-spin objectivity. | Accept W=0 scope. Any finite-spin profile requires separately sourced convention and implementation evidence. |
| Zero/hydrostatic loading | Raw source direction normalization is undefined at zero; isotropic normalized exponential has a limit. Existing code selects exact branches without flattening a neighborhood. | Review exact-zero continuation, both hydrostatic signs and near-hydrostatic failure/support boundaries as explicit numerical choices. |
| Numerical interior | Current normalized leading minor/determinant floor is 64 binary64 epsilons; abs(a)<=64 bounds exponential support. Ill-conditioned SPD states may reject. | Approve only as software support restrictions; neither a complete paper domain nor a rotation-invariant boundary classifier is claimed. |
| Author implementation | Exact base 2018 archive/version/license was not acquired in the retained source audit; later IGS/ISA/sand variants differ. | Exclude author-code equivalence. New ordinary-access source acquisition is conditional, not a reason to repeat completed rate/path work. |

## What the existing evidence actually covers

| Evidence | Identity and useful coverage | Admission limitation |
|---|---|---|
| `barodesy2017-preview-v1` and `preview-v2` | Both frozen manifests pin the exact current candidate. Each passes 13 requests/backend, 330 caller points/backend, five lab protocols monotonic/cyclic, independent void/control checks, zero-state identity and invalid/missing-state rejection. v2 also checks the combined catalogue/parameter order. | Small bounded software matrix; not independent full stress-trajectory validation or physical preparation. |
| `preview-v2/browser-default-v1` | Current candidate; 101 caller points/backend for the supplied 1% drained default. Retained assessment passes. | Engine request verification; its report explicitly says rendered-browser QA false. Separate integration documentation contains browser QA. |
| `barodesy2017-runtime-v1`, rates and material AD | Historical research definition SHA `16e0ef4de35ea1b47c4dc9122f01a264c56993d6851ba2387e974c0ff5f0af4f`. Independent instantaneous rate, regular 7x13 derivative, covariance/scaling and rejection/recovery evidence. | Derivative evidence is instantaneous, not an integrated algorithmic tangent; archived runtime/build identity remains historical. |
| `barodesy2017-hydro-ad-v1` | Historical research definition; 36 exact-hydro Jacobians and 48 invalid/recovery pairs/backend already assessed. | Exact nonzero hydro only; near-hydro, zero, second derivatives and integrated tangent explicitly false. Do not list this completed study as future work. |
| `barodesy2017-integration-v1` | Historical research definition; 45 isotropic trajectories/459 chained updates/backend with independent scalar references. | Specified pressures, soils, partitions and tolerances only. |
| `barodesy2017-wider-integration-v1` | Historical research definition; 48 trajectories/576 updates/backend, off-NCL compression, reversal and rotated nonproportional paths; independent caller references, partial-progress failure/rollback/recovery. | Scalar analytic references and tensor RK4 convergence have different uncertainty strength. Full domain preservation and experimental validation are unproved. |

The current and research **parameters, derived expressions, domain and equations compare exactly equal**. State names/shapes/units/scales/examples also match; v0.3 adds explicit state semantics, formulation inputs and initialization policy. This provides a transparent mathematical relationship, not a source-to-current-binary attestation. `preflight.py` reports it separately from direct current-preview manifest bindings. Any new definition or engine change needs a new applicability judgment; do not rewrite archived results or label them current artifact verification.

The [wider results](../../../reviews/barodesy2017-wider-integration-results.md) and [research dossier](../../../models/barodesy2017-research-rates.md) contain historical next-action prose superseded by later studies. Their original bytes are retained. Use the evidence matrix above for this decision; review the actual manifests and failures before signing.

## Physical preparation: the remaining usable-example gap

All seven persistent components must be supplied explicitly. Passing `initialize_state` establishes declared domain checks; it does not establish specimen preparation or equilibrium. Table 2 London/Dresden/Weald parameters are source examples. Current sigma=100 kPa I and e=0.8 are software examples, not a source-matched test. No fabric/backstress or hidden OCR can be invented because the base law retains only stress and e.

A preparation deliverable must select one material and one intended protocol and record: exact publication/test identity, four soil parameters and degree/radian convention, fixed sigma_star=1000 Pa, effective stress and density/void-ratio provenance, saturation/drainage and pore-pressure interpretation, consolidation path and endpoint, conversion to Mandel/Pa/compression-positive values, and uncertainties or absent metadata. A numerical preparation path must retain loading order, full endpoint sigma/e and transactional failure behavior rather than resetting to NCL. NCL e=exp(N)*(p/sigma_star)^(-lambda_star)-1 is a source analytical reference, not a universal reset or measured preparation substitute; overconsolidated states remain allowed within support.

If published measurements/preparation cannot be sourced, a clearly labeled analytical NCL software recipe can close a reproducible mathematical example only. It must leave material applicability and experimental validation undetermined. No experiment, e0 or source parameter is fabricated here.

## Ordered closure work and stop rules

1. **Source/scope decision:** an agreed independent reviewer completes decisions B17-01–04 in `review-sheet.json`, checks equation-by-equation locators, sign/units and constants against the pinned source, and approves or rejects the restricted candidate identity. Existing AI technical reports are supporting work, not an independent scientific signature. No reviewer is assigned by this packet.
2. **Preparation implementation:** after scope agreement, implement one separately versioned source-backed recipe/example plus evidence receipt as described above. Freeze expected state and loading metadata before engine observation. Keep analytical and measured preparation claims distinct. If metadata is absent, record that bounded gap rather than calibrate around it.
3. **Evidence applicability review:** verify direct current-preview pins and the research/current mathematical bridge; review retained raw transports, references, original failures and uncertainty. Decide whether the exact intended use needs a small targeted new check. Reuse completed campaigns; a new check requires a distinct prospective identity, input corpus and accuracy/rollback gates before observations. Changed engine bytes need their own release integration gate.
4. **Host/tangent scope:** the material-point preview can explicitly exclude a complete-update tangent. If production means implicit FE coupling, freeze and independently verify the required complete-update derivative and its zero/near-hydro/boundary policy first. Do not infer it from rate AD or native/Wasm parity. General-spin hosts remain unsupported.
5. **Release decision:** independent equation/numerical review signs exact definition and allowed scopes; coordinator binds source commit, toolchains, catalogue/binaries, tested recipe/protocols and packaged-site evidence in a new release snapshot. Only then update admission/review records through normal integration. A software deployment and scientific admission remain separate actions.

The smallest next implementation action is the scoped preparation/example record, once the reviewer agrees its intended claim. The immediate decision work is to obtain agreement on the four source/numerical restrictions; more finite-path runs will not resolve those judgments. No gate or tolerance is relaxed to obtain admission.

## Local reproducible preflight

Run from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B docs/ingestion/barodesy-clay-2017/production-closure-v1/preflight.py
```

`verification.json` retains the observed outcome. This hashes this packet's pinned public inputs, checks pending current review identity, exact preview bindings, algebra/state-layout equivalence and absence of any signed decision. It does not execute a solver, regenerate historical numerical reports, inspect private source files, assess equations scientifically or establish hosted status. Every review decision remains unsigned.
