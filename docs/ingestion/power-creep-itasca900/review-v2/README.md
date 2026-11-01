# Independent power-creep checklist review v2

Task SCI-power-creep-checklist-v2; reviewer run `/root/review_power_creep`;
transcription/execution author run `/root`. This is the same separate reviewer
that actually performed review-v1, now completing all nine policy items. It is
not fresh-context review and is not a second implementation-author judgment.
Date: 2026-11-01. Exact model SHA-256:
`67f3fabd6aecfda19b977bf3baeae2dce45f9081fa81a4436a750a41825a4bef`.

## Findings and decision

**Accepted for the bounded material-point scope below; no unresolved blocking
constitutive finding.** The two prior low findings remain disclosed: literal
fresh-copy reference instructions fail, and verification-v1's clock/restart
comparisons assess stress response rather than endpoint-clock advancement. The
additive review-v1 reproduction command fixes the first without rewriting old
evidence; execution-v1 separately checks endpoint times. Neither prevents this
bounded approval. No experimental validation is inferred.

Full delivery is incomplete: this decision is E5 evidence, not completion of
E6–E8. The current browser has neither an import/reset workflow nor a recorded
complete invalid-input/recovery/latest-request campaign. The two observed default
experiments, prior JSON export/native replay, and package analytical checks do
not establish that broader browser lifecycle. No deployment is verified here.

Scope: exact both-active, dry u=0, small-strain, fixed-spatial, zero-spin,
compression-positive Mandel stress ODE. Approval covers the literal synthetic
parameters, states, protocols and strict settings in execution-v1/refinement-v2,
the noninteger finite history in verification-v1, and the two default 10-second
browser experiments only to their saved observation/package coverage. Native
CLI evaluation/direct advance and common Wasm material interfaces and named
timed schedules are qualified; full parameter ranges, general FE tangents,
threshold events, material calibration and full browser lifecycle are excluded.

## source_provenance

Read the actual retained readable vendor equations and conventions, not only
the dossier: Itasca 9.0.182 Power Model Eqs1–7, property list, Both Components
Active option, Sign Conventions and Notations. The persistent URLs and locators
are in source-receipts.json. Private extracted-text JSON hash
`26bc9996d276f76dc16d9bdd9a3ec93d97cddd75701166ce1909be64912537a6`
matches both original receipt and durable ignored `.local/sources/` copy.
This is not origin HTML, the source book, or vendor implementation bytes.
The inaccessible origin HTML and uninspected Norton1929 book remain explicit
source limitations; neither supplies an equation assumed by this identity.

## equation_fidelity

Every implemented expression was compared with source Eqs2–6: s=dev(sigma),
q=sqrt(3s:s/2), Dc=3f*s/(2q), elastic volume and the sum of both powers.
b_i=A_i*p_ref^n_i yields the implemented decay
3G/p_ref times sum(b_i*(q/p_ref)^(n_i-1)); multiplying by s gives exactly
the source-derived continuous deviatoric relaxation. Both-active means no
finite threshold; the full gated law has a distinct unresolved identity.
Use of Eq2 projection instead of the inconsistent printed Eq7, the continuous
ODE interpretation and q=0 vector extension for n>=1 are labelled choices.
The time_scale parameter affects only observable scaling. No hidden hardening,
strain memory, domain branch or vendor discretization has been added.

## conventions_dimensions

All stress and strain-rate components reverse sign together from source
tension/extension positive to Atlas compression positive, including shear.
Mandel order [xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz] preserves Cartesian
double contractions. K,G,p_ref are Pa; b_i are 1/s; exponents dimensionless;
state rate is Pa/s. Physical seconds, small strain, fixed spatial frame and
no objective rotation are explicit. Effective Cauchy scope is justified only
in the declared dry uncoupled zero-pore-pressure host. Current model validation
passes; no total/effective conversion or finite-spin equivalence is inferred.

## initialization_domain

The complete material state is six persistent stresses with explicit-state,
examples-only initialization. Timed schedules additionally carry strain,
rate and clock as protocol state. The numerical example is not prepared salt
equilibrium: deviatoric stress creeps during a strain hold. Positive elastic
moduli/scales, nonnegative coefficients and n>=1 are project restrictions;
the declared machine parameter envelope is not a qualified material range.
Saved tests include hydrostatic/zero states, shear, sign reversal, noninteger
powers, elastic b_i=0, missing-state and sublinear-exponent rejection.

## integration_transactions

Inspected frozen time.hpp and schedule.hpp: direct advances initialize output
with incoming state/time and commit a trial only on full success. Saved budget
failure after two accepted substeps returns all six original stresses and time7;
same-instance Wasm recovery succeeds to time12. Native calls are separate
processes and do not establish persistent-process recovery. Schedules solve
BE state balance and mixed controls together using Jet Jacobians and step
doubling; they retain the last committed sample on failure, not whole-run
rollback. Control discontinuities are segment boundaries, not material events.
Holds, reversal and state restart are checked in saved studies. The exact
midpoint restart reproduces the same partition; arbitrary adaptive checkpoint
recovery and browser transaction lifecycle remain unqualified.

## independent_numerical_evidence

Reapplied saved frozen assessors: original22/27 failure is retained; tighter
settings v2 passes27/27 native and27/27 Wasm/parity without relaxed budgets.
References use Cartesian source creep, analytical linear/cubic/mixed relaxation,
affine loading and exact stress-hold strain. Recomputed RK4 reference exactly;
the step-refinement diagnostic is not a rigorous bound. Prior reviewer checked
100 independent invariant/energy identities. New bounded reviewer checks compare
the analytical radial-law Jacobian with centered source-RHS differences for
n=1,1.5,2.2,3 (maximum error below7.46e-12/s).

For a mechanism R=-c(q)s, J=-c*Pdev-c*(n-1)*3s⊗s/(2q²).
At q=0 its derivative is -3G*b/p_ref*Pdev for n=1 and zero for n>1.
Inspected lazy generated selects and frozen Jet power rules: their selected
origin branches give these derivatives without evaluating singular unselected
powers. This is analytical/code inspection plus source finite differences, not
a compiled Jet/finite-difference campaign. Saved Newton loading from the origin
corroborates relevant execution. The von-Mises observable is a norm and lacks a
unique gradient at zero; runtime's chosen zero derivative is not an approved
physical norm gradient or consistent FE tangent. Energy identity
psi_dot=sigma:D-q*f supports the bounded endpoint-hold check; it is derived
from source equations, not explicitly printed in the manual.

## backend_delivery

Inspected saved native/Wasm requests, statuses, full physical-state comparisons,
catalogue identity, partial-work rollback and recovery. Exact binaries are bound
by execution manifest and checked; no new builds or compiled calls were made.
Browser/package evidence supports the two default creep/relaxation experiments
and the earlier22-point export/native replay only. Inspected current HTML and
package assessor: honest physical-time controls and relative asset URLs are
present. This is not approval of import/reset, invalid UI recovery, changed
parameters across their entire envelope, latest-request handling, ordinary
strain-path routing, hosted deployment or every E7 requirement.

## applicability_claims

The dossier and exact model disclose illustrative coefficients, unsupported
threshold switching, n<1, pore pressure, finite spin, vendor finite-step
equivalence and experimental prediction. Approved scope is the named bounded
synthetic material-point evidence, not every machine-admissible parameter/state.
An accepted agent checklist suffices under current policy; no human signature
is required. Old absence-of-admission statements remain historical, and existing
explicit user acceptance is preserved independently of this new record.

## reproducibility_rights

Public receipts identify private copyrighted extracted source; no raw vendor
text, vendor code or measurement arrays are added by this review. Durable source
copy is ignored and hash checked; redistribution permission is not asserted.
Exact model, source receipts, frozen common runtime/generated closure, tests,
saved failures and reports are bound by hashed artifacts in the new catalogue
record. Source commit describes repository context; exact file hashes bind the
reviewed working-tree artifacts. Corrected read-only replay is in review-v1.
Run `python3 -B docs/ingestion/power-creep-itasca900/review-v2/check_review.py`
from this repository; it checks retained data only and prints results. Private
qualified binaries are read for hashes, never executed. Their eventual absence
from temporary storage is a reproduction prerequisite, not silent replacement.

## Work and retained diagnostic failure

The reviewer authored check_review.py and results.json. It verifies458 manifest/
artifact hashes (a different explicit set from review-v1's462 checks), source
retention, current validation, saved gates, reference and source Jacobian.
First invocation failed before checks because the script path did not place the
repository on sys.path (`ModuleNotFoundError: No module named atlas`); inserting
the repository root corrected this review harness only. No production/model/
reference changes occurred. The initial results output was empty; failure is
retained here. No compiled execution, shared edits, commit or promotion occurred.
