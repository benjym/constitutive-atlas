# Maxwell SCI-maxwell-agent-v1 — AI technical review

Reviewer: fresh-context `maxwell_scientific_review` AI agent, 1 November 2026.
No prior involvement in this model's ingestion, implementation or reference
generation. Independence consists of a separate original-source reading and
new algebra/saved-data checks within the same repository and agent system. This
is **AI technical review**, not human scientific signoff, canonical signature,
model admission, experimental validation or release qualification.

The exact reviewed model is
`models/research/maxwell/maxwell-itasca900-zero-spin-ode.json`, SHA-256
`dc378ac0eb6956f7d0028b1fa5927d2906bf05e14ab45b116bc447c25e6b885f`.
It remains a research draft. I support the bounded source transcription and
saved numerical evidence for its dry, fixed-frame, zero-spin, small-strain
continuous-law specialization at the frozen cases/settings. I found no blocking
coefficient, sign, shear-map or analytical-reference error in that claim.

## Findings, ordered by severity

1. **Medium — continuous dissipation is not unconditional numerical
   dissipativity (MW-10).** With zero strain rate, positive parameters and pure
   deviatoric initial stress, the direct midpoint stability polynomial is
   `R(x)=1-x+x²/2`. For the legal setting `rtol=0.5` and `h/tau=6`, the full-step
   multiplier is 13 and the two-half-step multiplier is 25/4. The normalized
   full/two-half error is at most 18/25, so the inspected algorithm accepts while
   elastic energy increases by 625/16. Positive absolute tolerance only lowers
   that estimator. This is an algebraic counterexample from `time.hpp`, **not a
   compiled observation**. It does not contradict the tight frozen tests, which
   pass. Do not infer a structure-preserving or unconditional energy guarantee
   from the continuous identity or local-error acceptance. No change is required
   for the current bounded claim; any such stronger claim needs a distinct
   prospective energy-policy study.

2. **Medium — declared parameter domain exceeds computational qualification
   (MW-12).** The positive bounds permit `tau=eta/G=1e-42 s`, whereas the direct
   method has a `1e-12 s` minimum half step in these settings. A nontrivial
   relaxation on that scale cannot be resolved with the qualified configuration.
   The suite varies viscosity to obtain tau 0.2, 2 and 20 s, with fixed K and G;
   it does not establish arbitrary stiffness ratios, scales, stress amplitudes,
   very long histories or arbitrary tolerances. Existing packet/example
   disclosures state this restriction correctly. Retain it in any consumer.

3. **Low — original-source durability remains open (MW-14).** All four original
   private HTML files are currently readable and hash-correct, but they reside in
   temporary storage. The 92-member checked-in source closure preserves executable
   inputs, not the copyrighted manual pages. Retain those exact source bytes in
   durable private storage, respecting rights; a URL plus hash cannot recover
   deleted bytes. Jaeger's book, linked figures, called example `parameter` file
   and full vendor host/rotation semantics were not examined. They are not needed
   to decide this explicitly selected manual specialization, but wider lineage,
   vendor reproduction and host claims remain unresolved.

4. **Low — transaction coverage is bounded (MW-09).** The direct late failure
   demonstrably follows nonzero accepted internal work and restores stress/time.
   The schedule budget failure retains its initial left point and valid entry
   transition at t=0; it does not exercise failure after a nonzero-time committed
   regular sample. The code retains the last committed sample, but this particular
   source-specific saved test does not independently demonstrate that later
   scenario. Restarts do use actual complete regular endpoints. No general
   transaction qualification beyond these cases follows.

5. **Informational — original parity-v1 is still a failure (MW-13).** Read-only
   replay reproduces `.initial_strain_rate[2]` exact-comparison rejection. V2 adds
   physical initial fields to their existing stress/strain/rate budgets, rather
   than increasing those budgets. I accept the bounded v2 physical comparison;
   the original failure and assessor remain distinct and unchanged. Recorded
   freeze chronology is supplied provenance, not an independently timestamped
   proof that no earlier observations existed.

## Source and formulation decisions

I read the four original pinned HTML files, including original equations and
adjacent text, rather than relying only on packet summaries. They identify
Itasca 9.0.182 and the 12 November 2025 update. The main manual's Eq4 explicitly
uses `G h/(2 eta)` in its coefficients with `2G` multiplying deviatoric strain.
Rearranging gives

`(s_new-s_old)/h = 2G dev(Delta epsilon)/h - (G/(2 eta))(s_new+s_old)`.

Consequently the continuous limit is
`sigma_dot = K tr(D) I + 2G dev(D) - (G/eta) dev(sigma)` and
`tau=eta/G`. Substituting `k=2G` into the scalar damping coefficient would change
the tensor law; it is rejected. The original oedometer exponent
`b=KG/[eta(K+4G/3)]` independently corroborates the selected factor.

The adjacent printed `ij` subtraction is malformed Einstein notation. A
componentwise interpretation fails even on an isotropic tensor; it cannot be a
deviator. The trace projector is the unique isotropic decomposition consistent
with the named deviator, Eq5 and Eq6. I support the explicit correction as an
interpretation, rather than claiming the literal printed indices are correct.

Negating every tensor component of stress and strain converts the source's
tension/extension convention to compression positive without changing this
linear law. Mandel factors preserve tensor contraction: raw shear work has two
off-diagonal terms and `sqrt(2)` on both packed factors. Engineering shear must
be converted separately. K and G have Pa units; eta has Pa s units. Positive
K,G,eta give a stable dissipative continuous material with no volumetric creep,
yield surface, tension cutoff or resetting branch.

Total stress for a dry uncoupled material point and zero spin are explicit Atlas
specializations; the inspected source does not independently certify a general
vendor total/effective-stress or objective-host equivalence. The model does not
claim either. Its physical-time ODE and source central-difference map are
different numerical identities. At `h=4tau`, source central difference reverses
hold stress by `-1/3`, while the exact continuous multiplier stays positive.
Adaptive direct midpoint and scheduled backward Euler are accurately identified
as Atlas choices.

For this autonomous law, complete initial stress suffices for future stress
prediction under given D. Absolute strain and dissipated-work reconstruction
need their own initial references. No specimen preparation is inferred from
the zero example state. Under the source oedometer preparation, with
`A=K+4G/3`, initial axial strain is `P/A` and radial stress is
`P(1-2G/A)`; starting from zero would solve a different problem. The saved
oedometer specification supplies those values. The actual vendor equilibration
and reset procedure was read but not executed or reproduced.

The independent continuous energy identity is
`sigma:D - psi_dot = s:s/(2eta) >= 0`, with
`psi=p²/(2K)+s:s/(4G)`. A strain hold keeps p fixed and relaxes s; a stress hold
permits `dev(D)=s/(2eta)`. Pure hydrostatic stress has no ongoing creep. Rate
changes require split intervals. Ideal instantaneous strain jumps require an
event treatment beyond a finite-rate ODE call. There is no finite-rotation
objectivity, coupled pore pressure, physical-time discrete-update profile or
public algorithmic tangent supplied by this record.

## Checks and evidence limits

Reproduce from the repository root:

```sh
python3 -B docs/reviews/maxwell-scientific-agent-v1/check_review.py
```

Only this review directory is written. The script performs no builds or
compiled/vendor executions. It reads hashes of private artifacts without
executing them. Source algebra uses independent rational arithmetic for three
material triples, nine trapezoidal residual identities and nine oedometer
derivative substitutions, including preparation and work/dissipation checks.
Trajectory references are recomputed independently; no production evaluator
produces their expected stress/strain.

The original 24-case saved-data assessor also replays read-only on both backends.
Independent checks cover the 24 main plus 14 recovery/restart cases per backend,
two calls each: 76 calls/backend. All checked saved successes remain within their
original budgets. Maximum direct stress error is 0.0238843 Pa; maximum fine
scheduled stress error is 1.375203 Pa. The coarse relaxation diagnostic remains
138.381 Pa against its separately frozen 1000 Pa gate. Fine relaxation improves
to 1.360719 Pa. Independently computed direct reference values differ from the
frozen expected values by at most 9.1e-13 Pa. Exploratory constitutive equilibrium
checks on 106 regular-point observations/backend find held-stress rate residuals
at most 1.46e-11 Pa/s. These are diagnostics, not a retrospective new gate.

The v2 parity replay performs 5,962 comparisons with maximum stress difference
4.657e-10 Pa and strain/rate difference 1.085e-18. All 12 ingestion-manifest,
44 integration-manifest and 92 execution-freeze bindings match; all 92 archived
source members match their freeze; the three supplemental assessor/transaction
pins, four source receipts and five private artifact hashes match. Raw catalogue
identities independently match the exact model serialization. No stale input
or historical repinning was needed. Saved replay and hash checks establish the
retained evidence, not a newly built executable or current-platform run.

[decisions.json](decisions.json) records explicit MW-01–MW-16 judgments, conditions,
exclusions and follow-ups. [inputs.json](inputs.json) identifies material examined;
archive-only/shared dependencies are bound for provenance rather than claimed as
an exhaustive engine audit. [results.json](results.json) and the check stdout/stderr
retain the actual run. [retained-failures.json](retained-failures.json) explains
the retained original failures and this review's initial vacuous endpoint
diagnostic, corrected before the final run. The initial result is preserved as
`attempt-1-results.json`; its zero-count diagnostic is not accepted evidence.

No source access blocker currently prevents this bounded decision. The smallest
next actions are to preserve the exact private originals durably and have the
coordinator integrate this review with its explicit exclusions. Any request for
unconditional energy behavior, larger parameter/loading scope, later schedule
rollback, full vendor equivalence or scientific admission needs its own agreed
decision or prospectively frozen study; this review does not authorize promotion.
