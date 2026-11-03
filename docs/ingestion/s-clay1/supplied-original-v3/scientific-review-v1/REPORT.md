# S-CLAY1 independent scientific checklist review

Reviewer: actual separate agent `/root/norsand_original_review`, task
`SCI-s-clay1-v3`, 3 November 2026. Author run: `/root`. The reviewer did not
transcribe this candidate, construct the original compliance reference, build
or execute native/Wasm artifacts or perform material solves. Work here consists
of source reading, equation/residual algebra, independent source-reference replay
and saved-artifact checks. Earlier NorSand approvals do not approve S-CLAY1.

Candidate SHA-256:
`2d1518c1aee44d9adec35229adc83b32a9f39d9175f307c8ddfd90cdfbd1caec`.

Decision: accepted for the exact bounded scientific/backend scope below. All nine
checklist-v1 items pass; no unresolved blocking findings. The installed definition
at /private/tmp/atlas-s-clay1-delivery-v3/models/s-clay1.json has the exact candidate
hash. Website/profile integration, actual browser use and live delivery remain E6–E8.

## source_provenance

The exact original is Wheeler, Naatanen, Karstunen and Lojander (2003),
*An anisotropic elastoplastic model for soft clays*, Canadian Geotechnical
Journal40,403–418, DOI10.1139/T02-119. The source receipt binds800632bytes,
SHA1923aff43b80f14970dec624deb8f78b09635f419adbf71d797fa0a1a4169511.
The attachment's2011filename is not publication identity. This reviewer read the
extracted governing/calibration/discussion material and visually inspected p405
and Appendix417–418 equation images, including the A12 bracket. Separate source
reviewer `/root/norsand_source_review` inspected all16pages. This review does
not claim a second all16page visual inspection. Later bonding/destructuration,
creep and finite-rotation extensions are excluded.

## equation_fidelity

Every candidate derived expression/residual was checked against original Eq1,
Eqs2–5/7–9 and A1–A14. ConstantM is a source-permitted complete original choice;
optional shifted-Lode interpolation is not a required omitted equation. The
source's Mandel representation and deviatoric fabric give
F=1.5(s-pA):(s-pA)-(M²-1.5A:A)(pm-p)p. Its gradient has deviator3(s-pA) and
trace2M²p−3s:A−(M²−1.5A:A)pm, as used by the stress residual. Dimensionless
gamma/p_ref multiplies this dimensional gradient; normalizedF is used separately
in Fischer–Burmeister complementarity. Size hardening uses signed plastic volume.
Fabric hardening uses its positive part and a nonnegative equivalent plastic
shear norm, including extension and dilation. Neither absolute volumetric strain
nor signed tensor shear is substituted. The endpoint residual, exponential volume
and size updates are explicitly labelled Atlas finite choices, consistent with
the differential law in the demonstrated refinement limit.

The reviewer replayed55exact source assertions and414candidate algebra assertions.
A further69reviewer source/candidate corner assertions cover positive/zero/negative
plastic volume, beta0,mu0 and zero-shift cases. The first supplemental checker
incorrectly demanded exact floating cancellation at nonzero equal stress/fabric
ratio; this retained checker failure is distinguished from a material failure.
The distinct v2 uses the already selected1e-15 algebra comparison there and
retains exact zero for the exactly hydrostatic case. No frozen material gate changed.

## conventions_dimensions

The implementation explicitly declares v0.3 incremental residual, compression
positive infinitesimal3D strain, fixed spatial axes, no objective rate, effective
Cauchy stress and Mandel shear. Deviatoric fabric is dimensionless and traceless;
the original full fabric has trace3. v is specific volume, not void ratio.
lambda/kappa are v-versus-ln(p) slopes. p_ref is numerical scaling, not an additional
material constant or pressure floor. There is no physical clock or creep term.
Passive tensor covariance is checked; finite-spin transport is not inferred.

## initialization_domain

All14persistent components (six stress, six fabric, v,pm), explicit parameters
and loading history are required. Temporary gamma is reset per solve and is not
accumulated physical strain. Parameter safeguards and lambda>kappa,positive
p/pm,v>1,M²>1.5A:A,traceless fabric and initial F tolerance are explicit; they
are not universal source ranges. The default stress20/12.5/12.5kPa combined
with source v3.46,pm17.6kPa and alpha.42 is an illustrative interior state,
not a recreated CAD2251 specimen. K0 estimates are approximate preparation
recipes, not universal initialization constraints. HeavyOC and calibration claims
remain bounded by the source limitations.

## integration_transactions

The shared standard solver was read; the isolated input manifest was independently
verified. Persistent state starts from the full parent; temporary gamma resets
per internal solve. Trial state becomes output only after whole successful
integration; failure returns the incoming layout. AD/Newton, elastic predictor,
substeps and alternate partition are common engine numerics, not source formulas.
Source p413 instead uses very small stress-controlled compliance steps. The
implicit finite law requires refinement; one large update is not assumed equal
to a subdivision. Zero hold, unloading, source refinement, forced failure,
full-parent preservation, fresh recovery and explicit-state restart are present
in the retained calls. Stateful process rollback beyond this stateless interface,
consistent FE tangents and creep are not claimed.

## independent_numerical_evidence

The independent compliance builder was read and replayed without Atlas imports.
It uses source fp/fq and hardening derivatives to form H and loading consistency,
then includes original elasticity and signed size/rotational laws. RK4 at128,
256,512pressure steps converges to roundoff-scale endpoint differences, with
source-yield and positive-loading/domain checks. This confirms the frozen endpoint
adequacy but does not establish a measured fourth-order slope. The native finite
candidate approaches that independent reference with normalized fullpersistent
errors7.18861e-6,3.59034e-6,1.79418e-6; the finest is below unchanged3e-3 and
below coarsest. Hydrostatic unsplit analytical response and elastic continuum
refinement, general3D shear/mixed paths and simultaneous stress/fabric covariance
are additional frozen checks. Backend parity is not counted as independent law
verification.

The reviewer's saved audit independently checks all169isolated input hashes,
1444native calls,2133successful fullstates and seven101point S-CLAY1curves.
Maximum recomputed F/p_ref² is1.98313e-10. It checks exact forced rollback and
recovery/replay, all50interpreted/native residual comparisons and every retained
reference-error value. Maximum residual parity error is4.55e-17. The original
native checker stopped after925passed assertions/1435calls due its own7parameter
indexing error; v2 changes only those indices and completes716checks/9calls.
Both report identities remain preserved; no scientific gate was weakened.

## backend_delivery

The reviewer audited all1494saved actualWasm responses against their original
native requests: identical outcomes, required shapes and38102finite numerical
comparisons pass2e-8, maximum4.44089e-16. The actual Wasm binary hash matches
its receipt. This covers source-reference and elastic paths, covariance,
rejections/rollback, proposed1%drained/undrained histories, edits, regressions and
50residual cases. No browser or compiled call was performed by this reviewer.
The terminal backend-completion receipt and all14evidence/fiveartifact hashes
were independently checked. Serial native/Wasm work is reported released. The
three-definition qualification catalogue and named CLI/NodeWasm requests are
approved; actual browser/full-catalogue packaging remain separate gates.

## applicability_claims

Intended approval scope is original constantM fulltensor small-strain S-CLAY1,
qualified at the frozen source parameter set, named1%drained/undrained100step
examples, mu10/50,beta0/.9,pm20kPa edits and specified general3D/refinement/
transaction cases. It does not imply accuracy over the broad JSON boxes.
Normally/lightlyOC soft clay, isotropic elastic unloading and associated flow are
source assumptions. Small-strain nonlinearity, realistic cyclic response,
destructuration, bonding, creep, finite rotations and FE/MPM tangents are absent.
Dry-side branches are retained mathematically; dry-side-dominated predictions
are unreliable. Published calibration/experimental curves are not independently
replicated here. The source-backed public-profile draft is consistent within
its stated pending-route scope; actual profile instructions and browser use
remain E6–E8 work.

## reproducibility_rights

All source, candidate, prospective policies, scripts, results, private source hash
and review artifacts are bound in the final record. Copyrighted original/text/
images stay private; this directory contains no copied paper or vendor code.
Reviewer scripts reproduce algebra and inspect saved evidence without compiled
calls. Reproduction uses Python bytecode-disabled calls, with PYTHONPATH=. for
candidate algebra scripts. An initial missing-PYTHONPATH invocation failed before
candidate import; it is a command setup issue, not a constitutive result.
No worktree, build/cache, preview server or temporary PDF rendering was created
by this task. Parent-owned private source, isolated builds and unique evidence
must remain until consumers and preservation checks finish; this reviewer owns
no disposable temporary resource requiring removal.

## Resolved findings and handoff

The initial baseline-fixture gap is closed. The coordinator ran five unchanged
existing tests/test_atlas.py assertions (four elastic analytical paths and MCC
yield/hardening/unloading) in six native calls. This reviewer imported that exact
fixture and replaced only its run function with the saved responses; all five
original tests pass, with the same source and definition hashes. The extra six
saved Wasm responses pass2696comparisons, maximum2.91038e-15. Its inherited generic
scope string is explicitly corrected by the additive BASELINE_SCOPE_ADDENDUM.md;
it did not rerun50residuals or the source matrix. Those1494cases remain separately
retained. No frozen test tolerance changed.

The original checker indexing failure, initial Wasm cache permission failure and
reviewer supplemental floating-cancellation assertion remain retained under their
original identities. The empty branch-results.json redirection was removed after
confirming it held no evidence; its failed checker and failure receipt remain.
No other task-owned resources need cleanup. The coordinator owns E6–E8, approval
registry integration and retention of its build/worktree resources. Review status
does not authorize deployment or imply experimental validation.
