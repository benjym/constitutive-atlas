# Independent Barodesy 2017 body-law review

Reviewer `/root/barodesy2017_agent_review`, 1 November 2026; separate assigned run. Starting repository commit `365661fb9a65b11655fedbab393e1d9341926522`. The coordinator `/root` authored the current reconciliation and analytical example; historical transcription/run author identities are unknown. This run authored neither the model nor the original numerical studies. It read the actual original PDF and reports, wrote independent source algebra and a Decimal dense-matrix exponential, and reran saved-only audits. It made no build, native/Wasm material call, experiment, author-code execution, deployment or shared-file edit.

**Accepted for the exact named complete body formulation and bounded material-point evidence below.** This is checklist-v1 acceptance of model SHA256 `0bf4fd2789274f1271b438ffea57168866f7ebea55cfcf8ef786532903ab3477`. It is not a current engine/package/live website attestation. Original draft descriptions, unsigned source review and closure sheet remain historical and unchanged. No human signature is required by the current agent-review policy.

## source_provenance

Primary source: Medicus and Fellin, *An improved version of barodesy for clay*, Acta Geotechnica 12, 365–376 (2017), [DOI](https://doi.org/10.1007/s11440-016-0458-4). The actual publisher PDF was independently hashed as `bd049a3fd874c9e4945e1c77f5af5b84ac14c26a08cee1b953428b4312e6af15` (1492680 bytes, 12 pages). This reviewer newly rendered and visually read printed 366, 367, 368, 369, 374 and 375: notation, Eqs1–10, Tables1/2, Eq11, embedded extension ratio, Appendix2 and Appendix3. PDF/text/renders stay private. The coordinator's durable retention receipt identifies the same original bytes.

The body Eq8 on p367 and Appendix2 Eq32 on p374 use `2p/sigma_star`. With source `p=-tr(T)/3` on p366, Appendix3 Eq41 on p375 instead uses `-2tr(T)/sigma_star=6p/sigma_star`. The appendix gives no compensating redefinition of N, p or sigma_star. Body selection is defensible and precisely named; this review does not pronounce an externally established erratum. Source p366 prints identical WT products in the spin conversion. Restricting W=0 avoids selecting an unstated repair. No exact 2018 author-UMAT source archive was obtained or executed; equivalence to it is excluded, as are 2012 clay, sand, ISA and later IGS extensions.

## equation_fidelity

The following complete source-to-model comparison was made against the actual source pages, not inferred from a hash manifest.

| Source | Exact reviewed mapping |
| --- | --- |
| Eqs1–2 p366, c4=1 in Table1 | `sigma_rhs=c3*norm(E)*(f*norm(sigma)*P+g*sigma)` after T=-sigma, D=-E; no extra minus sign |
| Eq3 and footnote5 p366 | `P=expm(-a*U)/norm(expm(-a*U))`, U=E/norm(E), a true matrix exponential |
| Eqs4–5 p367 | delta=-tr(U), q=norm(dev(U)); sqrt(3/2)*q equals source denominator sqrt((3-delta²)/2) for normalized U; m=-sqrt(3/2)*delta/q |
| Eq5 | x=c1(m-c2)²; K=x/(1+x); model stable log1p forms equal logK for x>0 |
| Eqs6–7 | f=c6 beta delta-1/2; g=(1-c6) beta delta+((1+e)/(1+ec))^c5-1/2 |
| Eq8 | 1+ec=exp(N)*(2p/sigma_star)^(-lambda_star), explicitly body selection |
| Eqs9–10 | beta=-1/(c3 Lambda)+(2^(c5 lambda_star)-1)/sqrt3; Lambda interpolates lambda_star at compressive hydro and kappa_star at expansive hydro |
| Table1 p367 / Sec4.3 p369 | All c1,c2,c3,c5,c6 match; c4=1 absorbed. The source choice p_extension/pe=1/1000 produces `(1/500)^t`, not a fifth soil input |
| Footnote13 p374 | e_rhs=-(1+e)tr(E), incompressible grains |

Four independent inputs are phi_c, N, lambda_star and kappa_star; sigma_star=1000Pa is singleton-fixed. No law component or history variable needed for this explicitly named base formulation is missing. Derived fields are computed quantities, not additional states. All three complete Table2 calibrations have c3<0; adding a positive-c3 guard would be wrong. San Francisco Bay Mud has incomplete Table2 input and is not silently completed.

Independent reviewer checks distinguish the body/appendix readings on all three Table2 soils: body NCL gives dlog(p)/dv=1/lambda_star; substituting 6p does not. The independently written dense Decimal Taylor exponential, with scaling/squaring at 80 decimal digits, supports source-shaped Cartesian directions and compares all111 saved native and Wasm primal cases per backend. Maximum normalized mismatch is 2.2538006305693828e-15. This reviewer budget of 2e-12 is an additional check, not a replacement for the original stricter 2e-13 study gate, which also replays successfully.

## conventions_dimensions

Source effective Cauchy T and stretching D are compression negative. Atlas sigma=-T, E=-D are compression positive; six Mandel components are xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz. Frobenius norms match Cartesian matrices, and the determinant expression correctly converts Mandel shears. Scalar phi is supplied in radians; N/lambda/kappa and all coefficients are dimensionless. Stress is in Pa and every density/log/power pressure argument divides by the 1000Pa scale. The fixed-spatial infinitesimal strain-path formulation has no physical-time relaxation or rate dependence. Ordered loading history is caller-owned. Fixed orthogonal-coordinate covariance is useful evidence, but establishes no finite-spin objectivity. Small-strain zero-spin effective-stress material points are the accepted host interpretation.

## initialization_domain

Both persistent fields sigma and e must be supplied. There are seven physical scalar components, no temporary multiplier, hidden fabric, OCR reset or preparation memory. `initialize_state` validates finite complete named parameters/state and declared domain using zero loading; it preserves supplied values rather than inferring equilibrium or preparation. Default sigma=100kPa I and e=.8 remain software examples and are not promoted into source-matched specimen data.

The separately pinned `ncl-example-v1/example.json` is accepted as an **analytical assignment only**: Table2 London `(22.6deg,1.375,.11,.016)`, sigma_star1000Pa, project-chosen p0=100000Pa and Eq11 p368 give e0=1.3831693930553504. Independently evaluating at 90 decimal digits and passing the full state through the actual Python initialization validator confirms its value and preservation. The coordinator's original checker also reruns byte-exactly, including missing e, zero stress and e=-1 rejection without mutation. It is neither a consolidation trajectory nor measured preparation; saturation, drainage, pore pressure, duration and experimental applicability remain unassigned. B17-05 does not require fabricating these for a mathematical example.

Model restrictions e>=0, p>0, positive compressive diagonal stress, normalized leading minor and determinant greater than 64 binary64 epsilons, and abs(a)<=64 are declared software support restrictions. They are not the paper's full domain or a certified invariant SPD classifier. Ill-conditioned SPD states may reject, and boundary classification need not be rotation invariant. Parameter intervals alone do not certify every denominator/conditioning throughout that box; acceptance covers named Table2 calibrations and frozen requests, not all conceivable bounded inputs.

## integration_transactions

This is a strain-path rate law, not an endpoint plastic return map or physical-time rheology. The common explicit-midpoint/step-doubling finite-update algorithm supplies numerical discretization; the source does not prescribe it. At zero E the homogeneous finite-direction rate admits zero continuation, while a unique full loading Fréchet derivative is not established. Exact hydrostatic signs use delta=minus sign(trace(E))*sqrt3 and P=I/sqrt3. For q→0, m grows as1/q, logK tends as q² and a tends to0; the normalized exponential tends to that isotropic direction. These are explicit project continuations. No epsilon neighborhood is flattened. Near-hydro arithmetic and tiny norm/deviatoric underflow can reject. x=0/K=0 singularity and out-of-range exponentials reject rather than clip/project the source law.

The actual wider saved reports contain two committed-prefix updates, followed by a control. Their budget-three failure retains two accepted substeps covering .0078125, yet returns exactly the committed parent; recovery equals the original control. The saved domain failure also returns that parent despite20000 accepted diagnostic substeps, and then recovers identically. This is important negative evidence, not a successful trajectory. Zero loading preserves the parent. Isotropic saved failure similarly retains .015625 partial diagnostic coverage and rolls back; its invalid initial-state rejection has no accepted progress. This reviewer independently checked both backends' saved state/control identities. Native finite-path calls are separate CLI processes; Wasm uses one persistent module. No serialization/restart, host strain/history-state or persistent native solver process qualification is inferred.

## independent_numerical_evidence

`check_review.py` independently checks15 source/DSL cases (zero, both hydro signs, oedometric and noncoaxial loading for each complete Table2 soil), NCL distinguishing algebra, Jaky target ratio K=1-sin(phi), invalid initialization immutability, all111 saved primal responses per backend, the research/current mathematical bridge and saved rollback controls. Its matrix reference imports no production exponential, DSL or original rate oracle. Production Python interpretation is only an object under test.

Fifteen additional actual saved-only audit tests pass, including:

- Original rate reference regeneration/refinement, 111+3 support cases and16 rejection/recovery pairs per backend; 21 regular7x13 material Jacobians and20 pairs per backend.
- Exact nonzero hydrostatic36 Jacobians and48 rejection/recovery pairs per backend, independent100/160digit analytic references and133 raw-call transport audits per backend. This is a separate already-completed study, not future work.
- Exact candidate previewv1/v2 source/journal/descriptor/control/volume/parity reassessment, browser-default101points per backend and corruption checks. Frozen compiler regeneration only; no C++ compilation.
- Original archived finite assertions:28 isotropic and20 wider groups. These re-evaluate the retained scalar/caller references and original tests inside the exact source replay; they do not execute model binaries. The replay retains unrelated original clay failure as failed rather than relabeling it.

Historical isotropic coverage is45 trajectories/459 updates per backend; wider coverage48/576 with off-NCL compression, reversal and rotated nonproportional paths. Scalar analytical references and empirical tensor RK4 final-pair uncertainty have different strength; neither establishes arbitrary-domain error control. Successful backend parity alone is never the independent reference.

## backend_delivery

The exact current v0.3 model bytes are directly present in frozen previewv1 andv2. Each has13 requests/backend,330 caller points/backend across five monotonic/cyclic lab protocols, zero identity and invalid/missing-state rejection. The separately retained default request has101points/backend and explicitly reports rendered-browser QA=false. This review independently recomputed all three assessments from their raw journals and freeze manifests. These prove their historical artifacts/interfaces, not a present release build or live browser.

Historical research definition `16e0ef4de35ea1b47c4dc9122f01a264c56993d6851ba2387e974c0ff5f0af4f` has exactly equal parameters, derived expressions, domain, equations and physical state layout/examples. v0.3 adds explicit semantic/formulation/initialization metadata. That bridge supports mathematical applicability of the earlier rate/path results, not binary/source attestation of a new current executable. Current engine changes, full package/browser integration and deployment require separate qualification.

Regular and exact nonzero hydrostatic evidence concerns **instantaneous** rate Jacobians at fixed parameters. It is not a complete-update FE algorithmic tangent. Zero/near-hydro AD, second derivatives, finite rotation and implicit FE coupling are excluded. The explicit material-point claim therefore does not require an untested FE tangent.

## applicability_claims

Accepted scope is the complete named Medicus-Fellin2017 **body Eqs1–10**, body2p, incompressible grains, zero spin, fixed-spatial infinitesimal Mandel effective stress/e formulation, restricted to the retained Table2/frozen software matrices and analytical initial-state assignment. It is neither the complete unqualified paper/UMAT family nor an experimentally validated clay predictor. No general parameter-box guarantee, arbitrary-stress boundary preservation, tensile/stress-free branch, near-singularity accuracy, physical preparation, pore-pressure material law, finite rotation, global tangent or current release claim is made. These exclusions are material parts of acceptance, not deferred in-scope blockers.

## reproducibility_rights

The actual failed live-root original closure preflight is retained. Its unchanged historical pins refer to three since-changed shared documents; the coordinator repaired only missing archive redirects. `reconstruct_preflight.py` restores each original pin into a temporary tree, verifies all34 original input hashes and runs the unchanged historical preflight. Its passing result still says review=pending and scientific_admission=false; it is not rewritten as this new review. Exact current model and original numerical evidence remain unchanged.

Raw publisher PDF, extracted text and renders stay private; public output comprises source links, hash receipts, independently written checks and assessment. No author code, experimental dataset or source artwork is redistributed by this packet. Original run artifacts are evidence receipts, not current executable availability or a reproducible-build claim. Historical author run identities remain unknown rather than invented.

Reproduce from the repository root:

```sh
python3 -B docs/reviews/barodesy2017-agent-v1/check_review.py --private-source .local/private-sources/barodesy-clay-2017/medicus-fellin-2017-publisher.pdf --output /private/tmp/barodesy2017-review-check.json
python3 -B docs/reviews/barodesy2017-agent-v1/reconstruct_preflight.py --output /private/tmp/barodesy2017-original-preflight.json
python3 -B -m unittest tests.test_barodesy2017_evidence tests.test_barodesy2017_hydro_evidence tests.test_barodesy_preview_evidence tests.test_barodesy2017_wider_evidence tests.test_barodesy2017_integration_evidence
python3 -B -m atlas.agent_review docs/reviews/barodesy2017-agent-v1/agent-review.json --for-approval
```

The JSON review and separate B17 decisions are this actual reviewer's decision. No original unsigned sheet, pending review, source policy, tolerance, model or failing historical study is changed. Coordinator integration and current release/browser qualification remain the smallest next steps.
