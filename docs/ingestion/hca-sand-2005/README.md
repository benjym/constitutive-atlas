# hca-sand-2005 — ingestion packet

Task ID: ING-hca-sand-2005
Owner / date: review_igs97 / 2026-10-31
Scope: full-nine-component versus symmetric-six-component polarization, recording/filter source reconciliation, state/schema/integration requirements and distinguishing algebra fixtures. Completed sampled-amplitude and scalar-history diagnostics are not repeated.

The inspected manuscript cannot support a single silently normalized six-component-space implementation. Its full-space isotropic initializer has a different norm and subsequent memory evolution from its symmetric restriction; its stated spherical-average explanation gives a third expression. The recording equation and drawing select different states. A further conventional-operator-action witness makes the printed rotation sign disagree with the stated angle decay. These are explicit source decisions, not corrections made by this packet. A conditional **22-scalar** polarization representation preserves the literal full-space initializer without storing all 81 fourth-order components; it does not choose the source variant or settle its sign.

## Identity and sources

Niemunis, A., Wichtmann, T. and Triantafyllidis, Th. (2005), *A high-cycle accumulation model for sand*, Computers and Geotechnics 32(4),245–263. [DOI](https://doi.org/10.1016/j.compgeo.2005.03.002); [author-hosted manuscript](https://www.torsten-wichtmann.de/paper/journal/2005-CG-a-high-cycle-model.pdf).

The existing private author-manuscript copy, `paper/results/sources/niemunis-2005-hca.pdf`, is 2,545,347 bytes with SHA256 `ecf856384f0c77d5440a2aeb28c96420e609ed7cefffab9f19a0b8e141a796ce`. Title/authors and relevant equations were visually inspected using the PDF skill on 2026-10-31: PDF pp1,3,9,10,11,12,13,14. Locators below are **manuscript PDF pages**, not journal pagination. The source was already pinned and locally available; this review did not acquire a journal version or assert a fresh web download. Publisher/manuscript equivalence and author implementation access remain unresolved. The [receipt](source-audit.json) records exact scope. No source PDF, extracted source text, page render, or author software is in this packet.

## Existing work and gaps

- [Prior contract](../../reviews/hca-2005-contract.md) already identified the identity/filter issues and outlines the full three-mode algorithm.
- [Completed arithmetic diagnostics](../../HCA_DIAGNOSTICS.md), [code](../../../tools/hca_diagnostics.py) and [retained evidence](../../../catalogue/investigations/hca-diagnostics-v1/evidence.json) cover finite sampled-loop amplitude and fixed-amplitude scalar history. This packet leaves them unchanged.
- Local supplemental context `paper/study/source_formulations/hca-sand-2005.json` is a partial audit in the unrelated untracked paper tree. It is not a delivered dependency of this packet; its status and independent parameter count are unchanged.

This packet adds an exact source-decision table, a representation-preserving conditional reduction, a rotation-sign witness, recording-filter decisions at distinguishing angles, and an explicit state/integration ledger. All unresolved decisions remain visible.

## Equations and schema crosswalk

| Source locator | Equation / quantity | Schema representation / units | Status / ambiguity |
| --- | --- | --- | --- |
|pp9–10,Eqs21–23|`A=sum R_i r_i⊗r_i`, `Ahat=A/||A||`, `epsilon_ampl=||A||`|Symmetric PSD operator on symmetric strain;6×6,21packed scalars; strain dimensionless|Existing finite-sample extractor. Physical6D strain and fourth-order-operator coordinates are different spaces.|
|p10,Section3.2|`cos(alpha)=Ahat::pi`, both tensors unit|Fourth-order Frobenius contraction with declared full/reduced metric|Do not renormalize a restricted state silently.|
|p10,Eq24|`dalpha/dN=-Cpi2*alpha*epsilon_ampl²`|Cycle-count ODE, not physical-time rate|`Cpi2>0`; exact exponential angle decay only for frozen amplitude/direction.|
|p10,Eqs25–26|`pi_new=R::pi`, normalized `mu=Ahat+pi`, `nu=Ahat-pi`|Rotation in fourth-order-tensor component space, not physical frame rotation|Conventional left-action sign witness below; source choice unresolved. `J` here is eighth-order identity, distinct from Eq29's fourth-order `J`.|
|p11,Eq27|`fpi=1+Cpi1*(1-cos(alpha))`|Scalar dimensionless multiplier; no new state|At Cpi1=4, orthogonal polarizations give5, consistent with accompanying prose; Table1's typical-response range is not a universal bound.|
|p11,Eq28|Known-preloading `pi=r⊗r`|Unit symmetric fourth-order rank-one history;21packed entries with zero skew-sector scalar|`r` must be supplied/prepared as a unit second-order strain direction; no sign preference.|
|p11,Eq29 and p14 Appendix A|Literal `pi_iso=J/3`, `J_ijkl=delta_ik delta_jl`|Unit identity on all9 second-order Cartesian components|Retains antisymmetric-sector norm. Contradicts unit6D restriction and the unnormalized stated six-sphere average.|
|p12,Eq36|`cos(beta)>0.9` and`||epsilon_R||>1e-5`|Named recorder policy with anchor/current-increment inputs|For 0≤beta≤pi this selects beta<25.8419degrees.|
|p13,Fig22|`beta>10degrees` and same norm threshold|Separate named recorder policy|Different from Eq36; neither replaces the other here.|
|p12,Section4|First state plus qualifying states retained; all trial states refer to increment start|Driver-owned ordered record buffer plus companion state|Record/anchor changes must commit atomically; endpoint retention and zero-current-increment cases are unspecified.|
|p3,Fig3/steps2–4|Resolve at least two initial cycles; record second regular cycle; freeze amplitude until control cycle|Explicit cycle-resolution/recording/accumulation phase object|Do not regenerate amplitude at every internal HCA substep or erase history when changing modes.|
|pp3,12|Stress rate per N; companion resolves cycles; original FE trials start from parent|Rate-law host plus separate companion state/phase; unitsPa and dimensionless histories|Full stiffness, monotonic flow, density evolution, cycle-count handoff and physical-frame rules remain outside this bounded reconciliation.|

The machine-readable [ledger](schema-integration-ledger.json) gives units, branches, trial ownership and capacity alternatives. It is a source-backed design inventory, **not** an accepted schema or executable model.

### Full-space versus symmetric restriction

Let `S` be the symmetric-tensor projector and `K=J-S` its skew-tensor complement. In an orthonormal Cartesian basis, `rank(S)=6`, `rank(K)=3`, and `S::K=0`. A symmetric strain amplitude satisfies `Ahat=S Ahat S`; the physically unused skew sector is zero.

Four distinct initializer interpretations must remain separate:

| Interpretation | Full Frobenius norm | Contraction with rank-one symmetric Ahat |
| --- | ---: | ---: |
|Literal `J9/3`|1|1/3|
|Restricted `S/3`|sqrt6/3|1/3|
|Renormalized symmetric `S/sqrt6`|1|1/sqrt6|
|Average of `r⊗r` over unit symmetric directions `S/6`|1/sqrt6|1/6|

The last result follows from rotational invariance and trace: the 6D second moment is proportional to identity, its trace is 1, so each diagonal entry is1/6. An exact second-moment ±basis quadrature tests it. Normalizing that mean would yield `S/sqrt6`; it does not yield `J9/3`. Source p11 explicitly discusses nine eigenvalue slots, a six-dimensional sphere and a 6D figure; those references cannot all be made identical by dropping three components.

Initial equality of `Ahat::pi` for literal and restricted states is insufficient: the restricted state is not unit, so its arccos is not the source's unit-vector angle and future rotation differs. For a uniform symmetric Ahat=S/sqrt6, literal`J9/3` gives cos(alpha)=sqrt6/3 and fpi≈1.7340 at Cpi1=4; the renormalized 6D initializer gives cos(alpha)=1 and fpi=1. These observables distinguish the formulations.

### Conditional 22-component full-space representation

For only the source initializers Eq28 or literal Eq29 and symmetric supplied amplitudes, a span-based update preserves

`pi = S B S + c*K`, with symmetric 6×6 B and skew-sector scalar c.

Any update`pi_new=u*pi+v*Ahat` carries`B_new=u*B+v*Ahat6`, `c_new=u*c`. Thus 21 packed B entries plus one scalar c suffice; its norm is`||B||F²+3c²`. Literal Eq29 starts`B=I6/3,c=1/3`; Eq28 starts`B=r6⊗r6,c=0`. Store offdiagonal B entries with sqrt2 packing and optionally `w=sqrt3*c`: then the 22-coordinate norm is an ordinary Euclidean norm, and the amplitude's22nd coordinate is zero.

The unambiguous angle-law consequence under frozen Ahat/epsilon_ampl is`alpha_new=alpha_old*exp(-h)`, `h=Cpi2*epsilon_ampl²*DeltaN`, and

`pi_new = sin(alpha_new)/sin(alpha_old)*pi_old + sin(alpha_old-alpha_new)/sin(alpha_old)*Ahat`.

This is derived from Eq24 plus unit-vector geometry, **not** certified equivalent to the unresolved printed Eq26 sign. The fixtures compare a full Cartesian 9×9 operator with this 22-coordinate reduction through three noncommuting polarization changes. Errors are≤2.5e-16 and full/reduced norms agree. They also show that general anisotropic skew history or symmetric/skew cross-memory is **not** representable by 22 coordinates. A general self-adjoint 9×9 pi needs 45 entries; an unrestricted fourth-order tensor has 81. These are storage counts, not independent material-parameter counts.

### Additional rotation-action ambiguity

Using conventional left outer-product action in Eq26, choose orthogonal unit rank-one pi and Ahat. Then`mu=(Ahat+pi)/sqrt2`, `nu=(Ahat-pi)/sqrt2`, and the printed operator gives

`R::pi=cos(deltaalpha)*pi+sin(deltaalpha)*Ahat`.

With the printed`deltaalpha=dot(alpha)*DeltaN=-0.1`, its Ahat projection is`-sin(.1)≈-.0998334` and the angle grows from pi/2 to pi/2+.1, violating both the stated nonnegative projection and Eq24's decreasing angle. The norm remains1, so norm-only tests miss this. Reversing operator action/contraction, the sine sign, the definition of nu, or interpreting deltaalpha as the positive rotation magnitude can change this conclusion, but the packet selects none. Source-code/publisher clarification is needed. This is an exact conditional algebra witness, not a claimed author-intent correction.

## Temporal integration and transactions

Accumulation evolves in continuous cycle count N with positive DeltaN, not physical seconds. Recording has a separate ordered phase or measured time coordinate for the companion model. Frequency must not silently introduce physical-time material behavior. Internal polarization-space rotation is distinct from physical frame transport.

For constant Ahat and amplitude, the angle-law update above is exact in real arithmetic. A block-boundary amplitude change changes the angle but retains pi; no reset to Ahat or isotropic pi is justified. Coupling fpi to evolving stress, density and other factors requires a complete stage-consistent block policy. Trials read immutable parent stress, e, gA, pi, amplitude identity, companion state and phase. Cutbacks, mixed-control trials and Newton iterations must not commit partial histories or recorder anchors. Success commits full state, count, phase, buffer and refresh decision atomically; failure retains the parent and evidence. Source p12 supports beginning-of-increment ownership; exact cross-mode history and counter transfer remain unspecified.

At alpha=0 the angle-law limit leaves pi unchanged, while Eq26's normalized nu is undefined. A matched-direction branch is necessary. At zero amplitude, Ahat is undefined. The bounded angle-law tendency tends to zero with amplitude squared for any retained unit direction, but a complete zero-amplitude branch must be declared separately: monotonic loading may still advance stress/plasticity. A block with D=0 can accumulate or relax when amplitude is nonzero. DeltaN=0 is an identity for this analytic diagnostic, not a positive-length accumulation block.

Recording must preserve all original samples. A derived filtered view must name Eq36, Fig22, or another explicit project rule, and retain selected indices, anchors, rejection reasons and version. Epsilon_R is measured from the last recorded strain; Deltaepsilon is the current strain increment. Zero R fails the strict radius test. A zero current increment with nonzero R makes the printed angle undefined. Exact thresholds and floating-point decisions need explicit policies; no clipping or near-threshold merging is used here. The source does not settle trial-endpoint selection, mandatory final-sample retention, duplicate samples or anchor rollback. Keeping every sample is the existing diagnostic policy, not source-filter equivalence.

## Independent checks

[fixtures.py](fixtures.py), [test_fixtures.py](test_fixtures.py) and [fixtures.json](fixtures.json) contain original stdlib-only algebra. Ten Python groups pass. They verify Cartesian symmetric/skew metrics, four initialization interpretations, the spherical second moment, three conditional full 9D/22 updates and histories outside the reduction. They distinguish the printed Eq26 action from Eq24, and Eq36 from Fig22 at 0, 15, 30 degrees. The strict radius boundary 1e-5 rejects; an undefined zero current increment returns null rather than an invented angle. These are decision witnesses, not another filter or amplitude extractor.

```
python3 -B -m unittest discover -s docs/ingestion/hca-sand-2005 -p test_fixtures.py -v
python3 -B docs/ingestion/hca-sand-2005/fixtures.py --output /private/tmp/hca-reconciliation-fresh.json
```

Arithmetic checks use moderate finite values. They are not a general numerical kernel, near-endpoint AD implementation or full-domain proof. No author code, companion, shared interpreter, native or Wasm solver was executed. Copyrighted sources and renders remain private.

## Handoff

Owned files: README.md, source-audit.json, schema-integration-ledger.json, fixtures.py, test_fixtures.py, fixtures.json and manifest.json. Only the coordinator updates the live board or shared code/status.

The next source action is to compare exact journal Eqs26,29,36 and Fig22, then acquire a matching dated author implementation for static inspection if accessible, with license/hash/version retained. Apply the initializer, rotation-sign and filter witnesses to that source. This may identify a literal full-space, corrected angle-law or six-dimensional variant; it cannot make those variants identical. No author binaries should be executed.

After an explicit source decision, the next bounded capability study is a supplied-amplitude polarization-only fragment, using 22-component packing only if its initialization class is selected. Freeze stress/density/scalar history and compare full 9D/22 analytic angle decay and piecewise amplitude changes before full coupling. Current DSL supports sin/cos but not acos; guarded angle initialization or a scalar angle-factor capability may be needed. This does not justify a handwritten model kernel or a 6561-entry eighth-order array. Recorder buffers, phase/count transactions and companion handoff are separate generic requirements.

Source completeness: this bounded reconciliation is complete with explicit unresolved choices; full HCA equation/version closure remains open. Executable support: none added. Numerical verification: ten isolated algebra tests, not full constitutive trajectories. Scientific admission: unchanged/not admitted. Experimental validation: none.
