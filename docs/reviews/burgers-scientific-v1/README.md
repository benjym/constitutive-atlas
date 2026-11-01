# Burgers scientific review v1

**Verdict: approve within the stated continuous dry, infinitesimal, fixed-frame zero-spin scope.** The exact reviewed transcription is faithful to the pinned Itasca 9.0.184 tensor partitions, thermodynamically admissible for positive finite constants, and supported by credible independent analytical references and the saved numerical qualification. No finding below blocks those bounded claims. This is a separate-agent scientific judgment by `burgers_scientific_review`, task **REV-burgers-scientific-v1**, 1 November 2026; it is an automated review, not a human signature or an admission/status change.

The installed definition's SHA-256 is `1452a27d5d3b50989ca66df5beb7f08e22434596800133983339466d3571933c`. This review does not extend to the vendor centered update, Burgers contacts, plasticity, finite rotations, coupled pore pressure or a calibrated material. Experimental predictive accuracy is **unassessed**. Scientific admission remains a coordinator/maintainer decision under the research charter; nothing in this directory promotes the definition.

## Findings, in severity order

1. **Low: relaxation refinement gate does not separately enforce Kelvin improvement.** [study.py lines 132–133](../../ingestion/burgers-itasca900/integration-v1/study.py:132) takes one unscaled maximum over Pa stress and dimensionless Kelvin strain. The stress components dominate; a worse Kelvin error could pass. [acceptance.json](../../ingestion/burgers-itasca900/integration-v1/acceptance.json) and the integration narrative describe stress/history improvement. The actual saved evidence **does** improve in both channels, independently recomputed here: endpoint maximum stress error decreases `4.236536867159884 -> 0.4524055079527898 Pa`; Kelvin error decreases `1.0146007761255987e-6 -> 1.0990417878662014e-7`, identically for both backends. This is a missing enforced gate, not a failed result. Smallest correction: under a new assessor identity, assert each channel separately and add a Kelvin-only corruption witness. Preserve the original frozen files.

2. **Low: installed descriptive metadata is stale.** [model description, line 8](../../../models/research/burgers/burgers-itasca900-dry-zero-spin-ode.json:8) still says “Packet-only” and “No full-path, compiled” after a separate integration delivered precisely those software capabilities. Its draft status and absent experimental/admission claims remain accurate. The later guide and integration receipt correctly distinguish the checkpoints. Smallest correction: separately archive/revise the installed metadata and update its bindings; do not silently alter the original pinned definition or this review's exact-byte target.

3. **Optional qualification extension: returned rates and broader control classes.** [study.py lines 99–110](../../ingestion/burgers-itasca900/integration-v1/study.py:99) checks state, observed stress and accumulated strain against analytic references. `strain_rate` is compared between backends, not against the analytic instantaneous rate; backward-Euler returned endpoint rates include a step-averaging error. Segment-entry stress-controlled rates are explicitly null in the transport, appropriately avoiding an unsupported instantaneous-rate claim. The mixed reference covers prescribed normal strain with prescribed shear stress; no split stress/strain control among normal directions, target-control case, arbitrary rate callback, long-time asymptote or parameter-domain stiffness qualification is established. Smallest extension when needed: freeze a distinct rate/control qualification with separate rate units/budgets and exact boundary-side semantics. No additional execution is needed to support the existing bounded state/strain claims.

There are **no critical, high or medium findings**, no missing-source blocker for the selected subsystem, and no required change to the reviewed constitutive equations.

## Source and transcription judgment

The original private HTML files were readable and their exact hashes match all three [source receipts](../../ingestion/burgers-itasca900/source-receipts.json). Titles, embedded version `9.0.184` and update date 11 December 2025 were inspected. Raw copyrighted HTML remains private. The review uses those bytes, not search snippets or a newer web rendering:

| Primary source | Governing locators checked | Judgment |
| --- | --- | --- |
| [Burgers](https://docs.itascasoftware.com/itasca900/common/models/burgers/doc/modelburgers.html) | Eqs. (1)–(13), Kelvin initialization function, properties/notes | Kelvin/Maxwell series identity, scalar centered elimination and preparation agree. |
| [Burgers–Mohr](https://docs.itascasoftware.com/itasca900/common/models/cvisc/doc/modelcvisc.html) | Eqs. (1)–(10), note after (12), (15)–(27) | Setting plastic rates to zero gives the exact continuous tensor subsystem and the separately recorded centered algorithm. |
| [Maxwell](https://docs.itascasoftware.com/itasca900/common/models/viscous/doc/modelviscous.html) | Eqs. (1)–(6), properties/notes | Confirms the deviatoric factor, purely elastic volume and dynamic-viscosity meaning. |

The Burgers page's bar over the stress in differential Eq. (5) and the Maxwell page's repeated `ij` instead of the scalar `kk` trace are already disclosed in the original packet. The unambiguous Burgers–Mohr tensor definitions/continuous Eqs. (5)–(7), (10) resolve the selected law without guessing a new variant. The initialization function independently supplies `k = dev(sigma)/(2 Gk)`. The source does not establish this restriction's finite-rotation or coupled stress semantics. The restriction to dry total stress, where total and effective coincide, is appropriately declared as an Atlas scope choice.

Writing `S=dev(sigma)`, `p=tr(sigma)/3`, `D=epsilon_dot`, the source gives

```
k_dot = (S - 2 Gk k)/(2 etaK)
D_dev = k_dot + S_dot/(2 Gm) + S/(2 etaM)
p_dot = K tr(D).
```

Thus the installed stress equation is exactly `K tr(D) I + 2 Gm (dev(D)-k_dot-S/(2 etaM))`. Its `dev(ek)` handles roundoff in a redundant six-component representation of five Kelvin degrees of freedom; it is an explicit numerical choice, not a volumetric creep mode. Moduli have Pa units, viscosities Pa s, Kelvin strain is dimensionless, and both derivatives have the required per-second units. The installed v0.3 contract correctly declares ODE/physical time, required stage rate/time and advance clock/duration, persistent stress/history, and observable Cauchy total stress.

Negating stress, strain and Kelvin strain together preserves every linear relation and preserves work. Source Cartesian tensor shear obeys `S_xy=2 G e_xy`; Mandel multiplies both shear stress and tensor strain by `sqrt(2)`. Consequently the Euclidean Mandel product equals Cartesian `A:B`, with twice the Cartesian off-diagonal products. No engineering-shear factor is missing, and the declared `xy,yz,xz` ordering matches the contract. Sign conversion does not authorize reuse of the excluded plastic yield criteria.

## State, preparation and thermodynamics

Stress and Kelvin strain are sufficient to predict subsequent stress for a supplied rate history. The absolute Maxwell dashpot strain and a stress-free total-strain reference are not determined by these fields; accumulated strain is separately initialized/bookkept by the schedule. Starting accumulated strain at zero with preloaded stress is a legitimate incremental reference, not a claim that total strain relative to a natural state is zero.

`k=S/(2 Gk)` makes only `k_dot` zero initially. With nonzero `S`, Maxwell flow persists; under a strain hold the subsequent stress changes. Arbitrary deviatoric `k` represents another prepared history and need not equal this recipe. Restart must preserve all twelve stored components plus schedule strain, clock and rate provenance. An accepted nonzero trace within `1e-12` remains a constant, unused storage artifact because the evolution is deviatoric. It is neither an inferred isotropic Kelvin branch nor an automatic state projection. This absolute tolerance is a disclosed implementation convention; relative robustness for extremely large history values is not established.

For trace-free physical Kelvin strain the energy and dissipation are

```
U = p^2/(2 K) + (S:S)/(4 Gm) + Gk (k:k)
sigma:D - U_dot = (S:S)/(2 etaM) + 2 etaK (k_dot:k_dot) >= 0.
```

This follows by differentiating the elastic bulk and Maxwell spring energies, substituting the strain partition, then using `S-2 Gk k=2 etaK k_dot`. The original review script checks it in exact rational Cartesian arithmetic for 100 independently generated tensors/positive parameter sets. The full stored `k` would add only a constant trace-energy offset. Positive constants ensure a positive physical stored energy and nonnegative dissipation; no dissipation from hydrostatic creep is introduced. This mathematical property is not evidence that a particular material follows the law.

## Stability, limits and algorithms

For each deviatoric component the source block has characteristic polynomial `lambda^2 + T lambda + P`, where

```
T = Gm/etaK + Gm/etaM + Gk/etaK > 0
P = Gm Gk/(etaM etaK) > 0
T^2-4P = (Gm/etaK+Gm/etaM-Gk/etaK)^2 + 4 Gm Gk/etaK^2 > 0.
```

Both decay rates are real and strictly negative. At the illustration parameters they are `-2 +/- sqrt(3)` per second: timescales about `0.268` and `3.732 s`. At short times, finite-rate Kelvin/dashpot strains cannot jump and the instantaneous shear modulus is `Gm`. Under fixed total strain the deviatoric stress/history ultimately decay to zero while pressure remains constant. Under constant deviatoric strain rate, the steady flowing values are `S=2 etaM D_dev` and `k=etaM D_dev/Gk`. Under a constant stress, Kelvin tends to `S/(2 Gk)` and Maxwell strain grows linearly. Infinite `etaM` gives a zero decay rate and retained elastic response, outside the strictly finite admitted domain. Vanishing `etaK` requires an algebraic constraint and a singular-limit treatment; it cannot be passed as zero to this ODE. Infinite `etaK` freezes Kelvin history. None of these mathematical limits is certified as an executable option by the present parameter declaration.

The direct algorithm is explicit midpoint with step doubling, accepting the two-half-step state without extrapolation; the schedule solves backward Euler with step doubling. Reading `time.hpp` and `schedule.hpp` confirms these descriptions and immutable incoming-state commit/rollback structure. For a negative eigenvalue, midpoint's scalar amplification `1+z+z^2/2` is stable only for `-2<=z<=0`; backward Euler's `1/(1-z)` damps arbitrarily stiff negative modes but accuracy and nonlinear convergence still need qualification. A positive/finitely evaluable model parameter set is not a guarantee that step limits/budgets can resolve it. The current broad numeric bounds span enormous stiffness ratios and do not assert material validity. The source centered update has amplification `(1+z/2)/(1-z/2)`, is distinct from both algorithms and is not L-stable. No vendor-step parity is implied by the current tests.

## Independent reference and numerical-evidence judgment

[independent_check.py](independent_check.py) is original to this review. It imports only Python standard-library modules and does not import the existing reference generator, Atlas equations/interpreter or a numerical integration backend. It nondimensionalizes stress as `x=S/(2 Gm)` and advances the affine system for `[x,k,epsilon,1]` using a 110-digit Taylor matrix exponential with scaling/squaring. Prescribed stress directly sets `x_dot`, and the Kelvin plus Maxwell partitions give `epsilon_dot`; pressure is treated separately. This avoids the existing reference's eigenvalue decomposition and stationary-state shift, providing a distinct calculation with the same explicitly inspected source law.

All **1,584 state/strain scalars at 88 saved schedule points** agree with the frozen 160-digit closed forms within `1e-70*max(1,abs(reference))`; the maximum scaled difference is `2.224e-102`. The gate and truncation threshold were set in this new script before its first execution. The restricted mixed-control decoupling assumptions are valid for the actual requests, including all three shear directions. The original 90/160-digit agreement alone would check arithmetic convergence rather than independence; the source derivation and this separate matrix representation provide the additional argument.

The saved-only integration verifier reconstructs the calls, checks frozen identities, replays references and reassesses both backends: **44 calls and 88 analytical schedule points per backend pass**. Six fine paths are within the frozen `20 Pa` stress and `2e-6` history/accumulated-strain absolute budgets; actual maxima are `4.32515 Pa` and `5.40541e-7`. Direct midpoint endpoints meet `0.01 Pa`/`1e-9` history budgets. These are meaningful engineering-unit numerical-error tolerances for the selected uncalibrated illustration; they have no experimental uncertainty interpretation, are not a global solver guarantee and cannot be extrapolated to all parameters. The coarse companions use separate diagnostic budgets and do not qualify as fine paths.

The source state/reference comparison is independent of backend parity. The **6,168 native/Wasm physical-scalar comparisons** show agreement of shared software paths, with maximum stress difference `1.4552e-11 Pa` and strain/rate difference `8.674e-19`; they cannot independently establish the equations. State/observable duplication likewise checks plumbing. Restart endpoints satisfy the same source references; triangle inequality supplies the stated twice-budget restarted/uninterrupted bound where both endpoints use that reference, without demanding bit identity across partitions. Invalid-duration/history/viscosity and untimed calls are rejected, and rejected ODE work returns the original state/time. The saved schedule rollback witness retains the last committed sample rather than partially committing an interval. Persistent-instance recovery is supported for Wasm; native calls are separate processes. These are appropriately bounded transaction claims, not a proof for every possible failure point.

The frozen archive, references, policies, raw calls and toolchain receipt are coherent with the stated prospective protocol. Hashes and the retained failed Wasm link support the audit trail; this review cannot independently observe historical wall-clock ordering from a self-authored receipt. No tolerance change or discarded constitutive failure was found. The initial dimensional-validation/preparation failures and first unwritable-cache Wasm link failure remain intact. This reviewer made **zero compiled/vendor calls and no builds, fits or new execution campaign**.

## Reproduction and handoff

```sh
python3 -B docs/reviews/burgers-scientific-v1/verify.py
python3 -B docs/reviews/burgers-scientific-v1/independent_check.py
python3 -B docs/ingestion/burgers-itasca900/integration-v1/verify.py
python3 -B docs/ingestion/burgers-itasca900/verify.py
python3 -B -m unittest tests.test_burgers -v
```

The new [results](independent-results.json), [integration replay](integration-replay.json), [ingestion replay](ingestion-replay.json), and [four-test log](regression-replay.txt) preserve the observed passing checks. [Reviewed inputs](reviewed-inputs.json) distinguish direct content review from archive/integrity-only coverage and record private-source identities without redistributing them. [Source audit](source-audit.json) records source identity/hash and archive-entry checks. [Retained failures](retained-failures.json) records a path lookup error and an overly literal HTML-whitespace assertion corrected during audit preparation; there was no scientific-check failure. [Manifest](manifest.json) pins this deliverable. Private HTML is optional for portable verification; use `--private-sources` to require its original bytes. Context-only input drift is reported without invalidating this historical review; scientific-input drift fails verification.

All new files are under `docs/reviews/burgers-scientific-v1/`. No board, model, compiler/schema, admission record, original evidence or unrelated work was edited. The smallest next action is for the coordinator to record this bounded automated review and separately scope the two low-severity documentation/assessor corrections if desired. Physical-material validation and any formal admission decision require their own explicit evidence and authority; neither is silently substituted for this completed scientific review.
