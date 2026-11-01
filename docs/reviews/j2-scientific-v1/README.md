# J2 scientific technical review v1 — blocked

SCI-j2-linear-hardening-v1, independent automated reviewer `j2_scientific_review`, 2026-11-01. This review binds candidate SHA-256 `619ea20bf932247962675e56b785398c7457749aafd28e2bcab94ba0dcc24852`, retained as [candidate-v03.json](../../ingestion/j2-linear-hardening/candidate-v03.json). **Do not scientifically admit this candidate: its residual admits a nonphysical reverse-direction root.** Passing saved native/Wasm calculations select the intended branch but do not close this mathematical defect. No human signature, experimental validation, calibration or approval by a named maintainer is asserted.

## Blocking finding SCI-J2-001

The source's signed scalar consistency equation is `q_trial-3G gamma-sigma_y-H alpha=0`, with `alpha=alpha_n+gamma`. The candidate replaces its signed returned magnitude with the norm of current stress in its Fischer–Burmeister residual. Its stress residual fixes the correction in the trial direction but does not forbid crossing through the deviatoric origin. If `H<3G`, the additional root

`gamma_reverse=(q_trial+sigma_y+H alpha_n)/(3G-H)`

has nonnegative gamma, final yield zero, nonnegative alpha and negative radial factor. It passes every declared solution constraint. This does not satisfy associated flow evaluated at final stress. It can exist even for a strictly elastic trial state. Hence uniqueness/source equivalence fails independently of backend behavior.

The exact small-strain witness uses Pa units, `p_ref=100000`, `K=10000000`, `G=3000000`, `sigma_y=2000`, `H=1000000`, zero committed state, and `de=(.001,-.0005,-.0005,0,0,0)`. Then `q_trial=9000`.

| Root | sigma normals (Pa) | alpha=gamma | sigma:d_epsilon_p (Pa) |
| --- | --- | --- | --- |
| Source physical branch | (1800,-900,-900) | .0007 | 1.89 |
| Additional candidate root | (-2250,1125,1125) | .001375 | -4.640625 |

All eight residual components evaluate **exactly zero** for both states through the candidate interpreter. The reverse root dissipates negative plastic work and its stress direction opposes its plastic increment. [results.json](results.json) retains both. The ingestion README's statement that positive material moduli/radius ensure radial positivity is true of the closed physical return map, but false of this candidate's unconstrained residual solution set. Its algebra checks and compiled reference cases test that physical map, so they cannot discover the additional root.

Smallest corrective action: create a distinct candidate and study identity using the signed trial consistency expression in the complementarity residual, retaining current-stress yield for initial admissibility and diagnostics. With `D=3G+H>0`, this gives the unique `gamma=max(0,(q_trial-sigma_y-H alpha_n)/D)`; positive radius then proves positive radial factor for nonzero plastic trials. At `q_trial=0`, gamma is zero and the safe denominator is inactive physically. This source-only assessment of a proposed fix does not approve any later candidate bytes or executable evidence. Preserve v1 and freeze new acceptance evidence before new backend runs.

## Source and convention findings

Readable private originals were checked against all four [receipts](../../ingestion/j2-linear-hardening/source-receipts.json); no vendor code was executed. The documentation THEORY and pinned `J2Plasticity.cpp` lines 480–591, 665–680 establish elasticity, normalized source yield, linear specialization and the update. `J2ThreeDimensional.cpp` lines 130–174 and 203–220 establish engineering strain shears and physical stress shears. The web omission of the bulk identity and differing wrapper-header saturation expression do not affect the selected specialization; executable base equations resolve these ambiguities. Omission of the vendor's line-550 multiplier shrink is an explicit mathematical variant choice, so bitwise vendor replication is not claimed.

Source `phi=||s||-sqrt(2/3)r(xi)` gives `d epsilon_p=gamma_src s/||s||` and `d xi=sqrt(2/3)gamma_src`. Thus Atlas `alpha=xi`, `gamma=sqrt(2/3)gamma_src`, `q_VM=sqrt(3/2)||s||`; multiplying source consistency by sqrt(3/2) yields `q_trial-3G gamma-r(alpha)=0`. H consequently needs no additional rescaling. These conversions and the physical closed map are correct; SCI-J2-001 concerns the declarative residual representation.

Simultaneously reversing stress, strain and plastic-strain signs preserves elasticity, the centered J2 surface and associated flow; alpha/gamma and nonnegative work remain invariant. Mandel sqrt(2) shears preserve full tensor contraction and elastic work, whereas direct use of engineering shear numbers would not. Isotropy gives fixed-basis covariance, not finite-rotation objectivity. The declared dry total-stress, fixed-frame, infinitesimal-strain, rate-independent scope is bounded appropriately; it supplies no pore-pressure law.

Stress plus alpha suffices for future incremental stress evolution with constant elasticity, because the committed plastic strain tensor can be eliminated from successive elastic trial stresses. It cannot reconstruct accumulated plastic strain or preparation history. Required explicit stress/alpha initialization with nonnegative alpha and yield tolerance is appropriate, but is only an admissibility check. Temporary gamma reset, complete failure rollback, unchanged zero-load holds, caller-split loading corners and BE subdivision dependence are correctly described as host/update semantics. H=0 is included; softening, viscosity, saturation, parameter changes, plane-stress solving, physical time and stress-controlled protocols are outside qualification. The full very broad schema parameter envelope is unqualified.

## Saved numerical evidence and independent checks

The [frozen plan](../../ingestion/j2-linear-hardening/execution-v1/PLAN.md), reference file, complete 89-file execution freeze and source archive were read and checked. Each archived member matches its frozen digest; live replacements after freeze are not used as v1 inputs. The frozen assessor is read from the archive and executed only on saved stdout. No build, backend execution, remote action or vendor execution was performed by this reviewer.

Both saved backends pass all 114 cases / 228 calls each, including nonproportional/reversal history, H=0, signed pressures, origin and yield holds, temporary reset, invalid initialization, forced complete rollback and recovery. Exact repeat outputs are enforced within each backend. Saved native/Wasm parity logs pass. Qualification forbids subdivision, matching the named one-step BE map. Stress/history and tangent budgets were frozen before backend observations; they are small relative to the study's stress scale and do not establish full-range robustness. Invalid-call evidence tests rejection/rollback rather than uniquely classifying every error message; native recovery is a separate process, while Wasm uses one persistent module.

An independently derived projector expression checks all 48 entries of each strict elastic/plastic 8x6 reference tangent, including alpha and gamma rows. With `P=I_sym-I⊗I/3`, `a=1-3G gamma/q_trial`, its plastic stress block is

`C=K I⊗I+2G a P-[9G^2/q_trial^2](1/D-gamma/q_trial) s_trial⊗s_trial`,

and each history row is `3G s_trial/(D q_trial)`. The elastic block is `K I⊗I+2G P`, with zero history rows. The source tangent is consistent after multiplier normalization. No tangent is claimed at yield switching or the norm origin. These checks independently verify the intended branch derivative, not global residual uniqueness. Sixteen deliberate saved-output corruptions covering stress, history, tangent history, success, rollback temporary value, input identity, subdivision and missing case are rejected.

Reproduce from repository root:

```sh
python3 -B docs/reviews/j2-scientific-v1/check_review.py
```

A successful script exit means this review, **including its admission-blocking counterexample**, reproduces. [decisions.json](decisions.json) separates severity and claims; input/output manifests bind exact files. The initial check failed because the coordinator replaced the live model while v1 was being reviewed. That stale-path failure is retained in `retained-failures.json`; the checker was corrected to bind the unchanged historical candidate and archive. A second byte-for-byte replay comparison found the live-drift metadata changing during concurrent v2 work; the checker now ignores live execution paths entirely and binds archived members. No acceptance tolerance was changed.

Scientific admission: blocked for this exact candidate. Numerical software evidence: bounded passing intended-branch cases. Source acquisition/conversion: complete for the stated OpenSees linear specialization, with the residual-equivalence defect above. Human signed independent scientific approval and experimental verification: absent. Coordinator owns final integration and any later corrected review.
