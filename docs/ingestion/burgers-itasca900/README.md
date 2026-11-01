# Burgers continuum, Itasca 9.0.184 — ingestion packet

Task ID: ING-burgers-itasca900. Owner/date: coordinating parent, 1 November 2026.
Scope: first source ingestion of the five-constant, positive-finite-parameter continuum Burgers viscoelastic law; explicit dry, infinitesimal, zero-spin continuous-law specialization. The source's finite-step algorithm is recorded separately. No root model, public catalogue entry or scientific admission is installed.

## Identity and sources

The target is Itasca's [`burgers` continuum model](https://docs.itascasoftware.com/itasca900/common/models/burgers/doc/modelburgers.html), not the PFC contact Burger's model, a generic historical attribution, or the plastic Burgers-Mohr formulation. Corporate author: Itasca; publication: *Itasca Software 9.0 documentation*, downloaded build **9.0.184**, updated **11 December 2025**, copyright 2024. No DOI is assigned by these manual pages. The original Burgers publication and the Jaeger (1969) book cited by the Maxwell page were not acquired.

Three readable primary HTML sources were acquired and inspected: Burgers Eqs. (1)–(13), initialization function/properties/notes; [Maxwell](https://docs.itascasoftware.com/itasca900/common/models/viscous/doc/modelviscous.html) Eqs. (1)–(6); and [Burgers-Mohr](https://docs.itascasoftware.com/itasca900/common/models/cvisc/doc/modelcvisc.html) Eqs. (1)–(10), (15)–(27), with its plastic contributions explicitly set to zero solely to expose the tensor viscoelastic subsystem. The latter page identifies that subsystem as Burgers; its plasticity, strength parameters, failure branches and default-property sentinels are not imported. Mathematical HTML and surrounding prose were inspected; Figure 1's separate image was not acquired or viewed. No vendor code or binaries were executed, including the displayed FISH initialization example.

[Source receipts](source-receipts.json) record exact URLs, private paths, byte counts, SHA-256, UTC access timestamps and equation/section locators. Downloaded hashes are:

| Source | SHA-256 |
| --- | --- |
| Burgers | `ce6d4f9642132f05ca08e7dc3cb62fff34789c07a8558322cc55cdd3325354a2` |
| Maxwell | `5abf3802b947ef8dbf75a4ce494f688398343905ec7d51da4318ed6d3ab8b031` |
| Burgers-Mohr | `111e424d178c539bf292bc072b875b2d4f3ad52f2d01b9955ed6fcdb96a83ba5` |

Downloads and existing source/ingestion inventories were checked first; no Burgers source/packet was identified. Synthetic Maxwell/Kelvin engine fixtures already exist in `tests/fixtures/time/`; they are not a source-linked Burgers model. The first hostname returned HTTP 403 during byte acquisition; the official alternate hostname succeeded. The web-reader/search-visible first hostname showed **9.0.182 / 12 November 2025**. This packet binds the downloaded **9.0.184** bytes and does not assert cross-host byte or implementation equivalence. Raw HTML remains private under `/private/tmp/atlas-burgers-itasca900-sources/`; redistribution permission is not established. The receipt hashes remain usable if temporary sources are later removed.

## Existing work and gaps

This adds a new continuum viscoelastic family packet. No existing model record is migrated. [The draft](continuous-draft-v03.json) lives only in this ingestion directory. It is structurally/semantically valid for the current common ODE evaluator, not a qualified executable release. Prior synthetic time fixtures demonstrate general infrastructure; their results are not transferred to this identity.

The inspected manual provides a closed continuous tensor law and a centered finite-step construction. It does not establish full host rotation/history transport, coupled total/effective stress scope, a specimen calibration or scientific validation. The selected dry scope has no pore pressure, so total and effective stresses coincide; `scope: total` is an explicit Atlas restriction. It is not inferred as a general vendor stress convention. Likewise zero spin/small strain restrict this packet rather than certify the full FLAC3D/3DEC host.

## Equations and schema crosswalk

Target: [schema v0.3](../../../schemas/model-v0.3.schema.json) and [formulation contract](../../FORMULATION_CONTRACT.md). [Crosswalk](crosswalk-v03.json) preserves the complete explicit `formulation` and initialization declaration. No top-level `integration` field is used.

Let compression-positive Cauchy stress be `sigma`, `p = tr(sigma)/3`, `S = dev(sigma)`, strain rate `D`, and Kelvin deviatoric strain `k`. The strain split and series law give

```
D_dev = k_dot + eM_dot
S = 2 etaK k_dot + 2 GK k
eM_dot = S_dot/(2 GM) + S/(2 etaM)
p_dot = K tr(D)
```

These follow Burgers-Mohr Eqs. (5)–(7), (10) with plastic rates zero, consistent with Burgers Eqs. (1)–(7), its Kelvin initialization function, and Maxwell Eqs. (4)–(6). Eliminating `eM_dot` gives the packet ODE:

```
k_dot = (S - 2 GK k)/(2 etaK)
sigma_dot = K tr(D) I + 2 GM [dev(D) - k_dot - S/(2 etaM)]
```

The draft evaluates `dev(k)` to avoid introducing physical volumetric Kelvin strain from storage roundoff. Its explicit absolute trace tolerance `1e-12` is an Atlas numerical choice; accepted trace error remains constant and is not an additional physical mode. No projection of caller initialization is performed. A six-component Kelvin field stores five physical degrees of freedom. Stress plus Kelvin strain closes future stress prediction; absolute accumulated Maxwell/dashpot strain is not reconstructed without additional bookkeeping.

| Source locator | Quantity | v0.3 representation / units | Status |
| --- | --- | --- | --- |
| Burgers properties; tensor Eqs. (6), (7), (10) | `K`, `GM`, `GK` | parameters `Kmod`, `Gm`, `Gk`; Pa | Strictly positive and finite in this scope |
| Same equations and dimensional balance | `etaM`, `etaK` | `etam`, `etak`; Pa s, SI `[1,-1,-1,0]` | Dynamic viscosities, not time constants |
| Tensor Eqs. (1)–(4) | `sigma`, `k` | two persistent symmetric spatial tensors; Pa and dimensionless | 12 scalar slots; trace-free Kelvin constraint |
| Differential equations | physical time | `physical_time` / `ode`; stage `time` (s), `strain_rate` (1/s) | A hold needs positive elapsed time even with zero strain increment |
| Source Cartesian `ij` shears | tensor representation | Mandel `[xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz]` | Shear strain is tensor shear, not engineering shear |
| Burgers-Mohr note after Eq. (12) | source compression negative | flip stress, strain and Kelvin-strain signs together | Linear relations unchanged; no principal ordering needed |
| Restricted Atlas scope | frame/kinematics | `small_strain_3d`, `fixed_spatial`, `objective_rate: none` | Full objective transport unspecified in inspected model pages |
| Dry specialization | output | observable `stress = sigma`; Cauchy, total | No pore-pressure input or coupled stress claim |
| Burgers initialization function | compatible Kelvin preparation | optional `k = dev(sigma)/(2 GK)` | Explicit recipe, not automatically enforced |

All five material constants and both persistent fields must be supplied explicitly to initialization, with initial stage time and strain rate. Illustrative values in the draft are not source calibration or physical defaults. Broad finite parameter bounds `1e-12` to `1e30` are declaration bounds, not a material applicability range or assurance of stable/finitely representable rates for every combination. Checks reject nonfinite evaluations. Restart requires all stress and Kelvin components plus clock/loading provenance. There is no void-ratio, density or hardening state in this law.

For positive finite parameters there is no yield surface, tensile cut-off, plastic branch or reversal reset. Zero/infinite viscosities, disabled branches, changing parameters, temperature dependence and failure must be separately specified. In particular, Burgers-Mohr's zero-stored infinite-viscosity convention is not a physically zero viscosity and is not assumed to be the pure Burgers default.

### Recorded centered source algorithm

For one step `h`, old/new values `o/n`, and `de = dev(delta_epsilon)`:

```
A = 1 + GK h/(2 etaK); B = 1 - GK h/(2 etaK)
a = 1/(2 GM) + h/4 [1/etaM + 1/(A etaK)]
b = 1/(2 GM) - h/4 [1/etaM + 1/(A etaK)]
S_n = [de + b S_o - (B/A - 1) k_o]/a
k_n = [B k_o + h (S_n + S_o)/(4 etaK)]/A
p_n = p_o + K tr(delta_epsilon)
```

Burgers-Mohr Eqs. (21)–(27) supply this viscoelastic tensor update. The Burgers page Eqs. (8)–(13) gives the corresponding scalar force/displacement elimination. The source uses a mean-force symbol in its differential Eq. (5); the tensor differential law and endpoint-average Eq. (6) distinguish continuous stage stress from the finite-step mean. Maxwell's unnumbered deviator definitions repeat `ij` where a scalar trace is intended; the unambiguous `kk` definitions in Burgers-Mohr Eqs. (1)–(4) are used. These printing details are retained, not silently promoted into a new constitutive variant.

For fixed `h`, its strain-to-stress tangent is `K I⊗I + (1/a) Pdev`; the Kelvin tangent is `h/(4 etaK A a) Pdev`. As `h -> 0`, `1/a -> 2 GM`. This update is centered, not the exact exponential solution. It depends on duration as well as mechanical increment. It must not be placed in the dimensionless `strain_path` residual profile. Exact replication would require the physical-time residual/discrete-update capability noted as BUR-CAP-01.

## Temporal integration and transactions

The continuous ODE requires actual seconds and a stage-consistent strain-rate history. `start_time` and strictly positive `duration` are required for advance calls; `time` and six Mandel `strain_rate` components are equation-stage inputs. Piecewise loading discontinuities require separate advances. An instantaneous stress/strain jump is an explicitly prepared new state/event, not an infinite rate silently sent to the ODE. There is no explicit age dependence for constant parameters.

A zero-strain-rate hold generally relaxes deviatoric stress and changes Kelvin history. A constant-stress hold generally creeps through the Maxwell dashpot and adjusts Kelvin strain. Hydrostatic stress does not drive creep. Setting `k = S/(2 GK)` cancels the instantaneous Kelvin rate only; it does not cancel Maxwell flow. At `S = k = 0`, zero strain rate is stationary even at nonzero hydrostatic stress. Duration zero is outside the ODE advance contract; the source discrete formulas have an elastic `h=0` mechanical-update limit, which is a different operation.

Evaluate both derivatives at the same current integration stage, without lagging Kelvin history. Source centered updates instead use coupled endpoint means and immutable old values. No parameter/history reset or hold shortcut is authorized. Trial updates start from the same committed stress, Kelvin history and clock; successful steps commit together. Failed caller updates must restore the complete incoming state and time even after partial substeps. These are proposed Atlas transaction requirements; vendor rollback/restart API behavior is unspecified in the inspected source.

The local continuous state block per deviatoric component is

```
[ S_dot ] = [ -GM(1/etaK+1/etaM)   2 GM GK/etaK ] [ S ] + [2 GM D_dev]
[ k_dot ]   [  1/(2 etaK)         -GK/etaK      ] [ k ]   [0         ]
```

Its trace is negative and determinant `GM GK/(etaM etaK)` positive. The two relaxation rates are real and negative for positive constants. Relaxation/retardation times can make explicit integration stiff; a timestep must be chosen/qualified against analytical solutions, rather than claiming a universal step bound. The instantaneous fixed-state rate tangent is `K I⊗I + 2 GM Pdev`; it is not the finite accepted-step tangent. Full finite-step tangents, solver convergence, event handling and native/Wasm equivalence are not checked here. No model-specific kernel is proposed.

## Independent checks

The acceptance criteria were saved in [acceptance.json](acceptance.json) before the numerical checker ran. Reproduce:

```sh
python3 -B docs/ingestion/burgers-itasca900/check_packet.py
python3 -B docs/ingestion/burgers-itasca900/check_packet.py --private-sources
python3 -B docs/ingestion/burgers-itasca900/verify.py
```

[Saved results](check-results.json): **nine groups / 518 cases** with private-source verification; the portable run omits three private-source cases. Exact rational calculations verify 200 centered tensor updates directly in the original Kelvin and Maxwell partitions and 200 continuous energy identities. With tensor inner products (off-diagonal terms weighted twice),

```
U = p²/(2K) + (S:S)/(4 GM) + GK (k:k)
sigma:D - U_dot = (S:S)/(2 etaM) + 2 etaK (k_dot:k_dot) >= 0
```

Four 80-digit constant-stress creep cases include the initial elastic jump. Four two-exponential relaxation cases satisfy the source differential partitions to `1e-65`; example rates are `-2 +/- sqrt(3)` per second. Three volumetric checks, explicit initialization/rejection and a compatible-preparation/nonstationary-hold witness are also retained. One hundred interpreter evaluations are checked against independent Cartesian source-partition residuals (including all shear directions); maximum normalized discrepancy `3.8817528884888104e-16`, below the prospective `1e-12` budget. This last comparison checks the draft transcription; the exact partition and analytical checks are separate evidence.

[Retained failures](retained-failures.json) records the first draft's dimensionally invalid comparisons against literal zero. The correction uses `x > 0*x` without changing physical bounds; the same structural validation now passes. No failed constitutive trajectory was discarded. There were **zero compiled/vendor calls and zero finite-path integrations**. These checks do not establish complete host implementation fidelity, experimental applicability or independent scientific review.

## Handoff

Owned files are this README, claim/source receipts, explicit v0.3 continuous draft/crosswalk, acceptance policy, source-partition checker/results, retained failure ledger, manifest and verifier. [Manifest](manifest.json) pins exact packet and shared-contract/checker dependency bytes. No historical evidence, root models, compiler, schema, CMake, website, catalogue or paper file was changed. Only the live board and this directory belong to this task.

**Source completeness:** closed for the inspected manual's positive-finite, dry, infinitesimal zero-spin continuous viscoelastic subsystem; full vendor-host objectivity/coupling/default semantics and original historical publication remain unverified. **Executable status:** packet-only ODE draft passes common Python structural/semantic/evaluation checks; no installed/qualified native, Wasm or browser model. **Numerical verification:** bounded algebra, analytical residuals and rate checks only; no integrated trajectories. **Scientific admission:** pending/unassigned; no experimental validation.

Smallest next action: independently review the selected continuous-law scope and freeze a named creep/relaxation finite-path reference and transaction acceptance policy before common timed-engine execution. Exact vendor-step reproduction is a separate generic capability task, dependent on an explicit physical-time residual/discrete-update contract. No source acquisition blocker prevents this bounded packet; broader host gaps do not authorize guessed conventions.
