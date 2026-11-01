# Hypoplastic sand + IGS97 — bounded source-review reconciliation

Task REVIEW-hypoplastic-sand-igs97; coordinator integration, 1 November 2026. **The original overlay source mapping and explicit v0.3 crosswalk are technically checked; scientific admission and REV-05 remain open.** This closes the bounded reconciliation/gap-report assignment, not the model's review gate. No root definition, numerical setting, schema/compiler, native code, model status or historical evidence was changed.

## Identity and source coverage

The executed root identity is the general eight-parameter [von Wolffersdorff 1996 host](https://doi.org/10.1002/%28SICI%291099-1484%28199607%291:3%3C251::AID-CFM13%3E3.0.CO%3B2-3), composed with the continuous [Niemunis & Herle 1997 IGS overlay](https://doi.org/10.1002/%28SICI%291099-1484%28199710%292%3A4%3C279%3A%3AAID-CFM29%3E3.0.CO%3B2-8), restricted to zero spin and with declared Atlas numerical continuations. Root SHA-256 is `83777458ea437a3a7c1360117dbf435f7d763913cda399099ef2966e65a67e86`. It remains schema0.1/draft pending separately owned migration; the new crosswalk targets the current v0.3 contract without rewriting it.

The [original-equation technical audit](original-equation-review-v3/README.md) reads all 21 original PDF pages and visually inspects title/sign pages 1–2 and equation/simulation/appendix pages 7–19. Its source receipts and inspection ledger distinguish full text from visual inspection. It is a second-agent technical reading independent of the prior transcription, not a signed independent scientific-author review. Private PDFs and renders are excluded. The original primary-source access gap is closed; full independent review of the general VW96host and scientific/numerical admission are not implied.

Historical [source review v2](../../../catalogue/reviews/hypoplastic-sand-igs97-source-v2.json), [dossier](../../models/hypoplastic-sand-igs97.md) and [original reconciliation](../../models/hypoplastic-sand-igs97-original.md) are preserved byte-for-byte. The new [review v3](../../../catalogue/reviews/hypoplastic-sand-igs97-source-v3.json) remains pending with an updated gap list. This packet adds evidence rather than retrospectively rewriting earlier reading-coverage or review claims.

## Equation, parameter and state crosswalk

[formulation-crosswalk.json](formulation-crosswalk.json) gives explicit source-linked formulation, persistent state semantics, initialization, every derived quantity, all three rate equations, parameter units, domains and source/project distinctions. The main mapping is:

| Quantity | Primary source | Review result |
| --- | --- | --- |
| History magnitude/direction and branch projection | NH97 Eqs7–8,14–15 | Paired stress/strain/history sign conversion; Mandel contractions preserve tensor products. eta=0 at zero history. |
| Overlay stress and history rates | NH97 Eqs14–15 | Contracted root branches agree for physical0<=rho<=1; both stress branches coincide at zero projection, but a globally smooth tangent is not claimed. |
| Linear/nonlinear host tensors | NH97 Appendix A Eqs23–28 | General VW96composition; compression-positive nonlinear tensor has the converted sign. |
| Density/barotropy | VW96 Eqs43–46; NH97 Eqs29–31 | NH97seven-parameter host is beta=1 only. General beta, root defaults and TMD2published constants are distinct identities. |
| Void-ratio continuity | VW96Eq2 | e_prime=-(1+e)trace(de), with no elapsed-seconds interpretation. |
| Objective stress/history transport | NH97 Appendix A Eq32 and AppendixC | Omitted only under explicit W=0 restriction; original finite-spin sign conflict remains outside executable scope. |

All 14 root parameters are accounted for: eight host material constants, five IGS constants and the project stress scale `p_ref`. NH97 Table I is Hochstetten sand with beta=1; the [TMD2baseline](../../benchmarks/kfs-tmd2-research-range-v1/README.md) uses a different complete published2019parameter set, beta2.5 and mobilized isotropic history. Neither is inferred from root examples.

The v0.3 profile is `strain_path_rate`, small-strain3D, fixed spatial frame, no objective transport, compression-positive Mandel effective Cauchy stress. sigma and h are persistent symmetric spatial tensors; e is a persistent invariant scalar. Declaring passive QhQ^T transformation does not add finite-step spin integration. Explicit initialization requires all of sigma,e,h; illustrative field values are examples only. The root physical history ball is norm(h)<=R, while its actual numerical guard admits norm(h)<1.01R with capped rho and no post-step projection.

## Integration and lifecycle

The continuous law is rate independent. `de` defines a straight dimensionless path increment; the equations return derivatives over its normalized fraction. No physical clock, hold-duration law or automatic history decay is supplied. At zero de, all rates vanish. The paper's resting-history erasure is a preparation/reset event, not an unannounced zero-load update.

Source Section5 advises Euler, reversal-sensitive increment control, overshoot correction and isolated trial history. Atlas uses midpoint subdivision, endpoint-defect checks, a rho cap and a 1% admission band. These are different finite-step methods. Trials start from committed history, successful updates commit persistent state, and failed parent updates roll back. No new tangent, event locator or universal mixed-control uniqueness follows from this review.

Source mR>mT>1 and chi>1 recommendations are stricter than exploratory root bounds. Pressure/density guards, the near-isotropic j2 threshold and the overshoot band are project restrictions/continuations, not a published universal validity domain. In particular this packet does not approve source extrapolation through the entire 1% band.

## Checks and preserved evidence

- The independent agent's 21 exact illustrative algebra checks cover four stiffness limits, history saturation/reversal/zero memory, sign conversion, Mandel contraction and the beta1 factor identity. The parent replay matches its JSON exactly; these checks import no Atlas implementation.
- Nine parent checks validate the complete proposed v0.3 profile in memory against unchanged equations, cover all parameters/derived/state equations, accept the complete TMD2state without projection, and reject missing h or history outside the numerical band. No migration is written. Initial profile-only validation failed because current v0.3 additionally requires explicit state semantics and initialization; that failure is retained and corrected without equation changes.
- The existing576-case Cartesian fourth-order original-paper comparison was rerun in Python only; its JSON equals the preserved report exactly. This confirms current interpreter agreement at the original beta1 specialization, not new independent authorship or native execution.
- Both historical 303-case report artifacts pass checksum verification. The failed v1 retains four failed history paths, while v2 passes 303cases under its analytical-history/endpoint-defect correction. This is saved-report integrity, not a rerun of old binaries or a claim that every current source file matches old receipts. The known broader historical binding failures are not repaired or relabelled here.

Reproduce the bounded checks from the repository root:

```sh
python3 docs/ingestion/hypoplastic-sand-igs97/check_crosswalk.py --repo .
python3 docs/ingestion/hypoplastic-sand-igs97/original-equation-review-v3/check.py
python3 -B tools/verify_igs_original.py /private/tmp/igs-original-rates-replay.json
```

No author code, native helper, solver build, compiled model or Wasm was executed. The last command performs only Python instantaneous-rate evaluation.

## Source qualifications and remaining gates

The full-paper audit confirms Fig16's e0=.695 and isotropic100kPa state through its link to Fig7 and p292. These are not borrowed from later cyclic examples, which independently use e0=.695 and 300 kPa. Schematic recent paths and plotted loops do not supply full preparation/control schedules. Figure21 is explicitly qualitative. The finite-spin update sign conflicts with the objective-rate appendix; AppendixB Eq40 also has a printed algebraic anomaly, and a positive-pressure plot caption needs an explicit sign mapping. None justifies changing the current zero-spin strain-driven equations.

Remaining work is precise: independently sign off the general host and overlay scientific review; assess the source-versus-Atlas numerical policy/domain and the generic hidden-crossing/rollback evidence; obtain a complete original history before claiming its trajectory reproduction, or use a separately source-complete benchmark such as the qualified TMD2case; retain separate cyclic experimental applicability and broader parameter/boundary limitations. The unsupported finite-spin profile must remain unsupported until its source conflict and transport are resolved. A new generic engine feature or new model family is not needed to complete this bounded source task.

Source completeness, executable support, numerical verification and scientific admission remain separate: NH97reading and the crosswalk are complete for this task; the existing draft executes in its declared scope; named numerical evidence is retained; reviewed model admission is still pending.
