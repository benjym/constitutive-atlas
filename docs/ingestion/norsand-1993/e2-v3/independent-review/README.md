# Independent path-contract review

Reviewer `/root/norsand_path_review`, task `REVIEW-norsand-path-contract-v1`,
2026-11-01. This agent did not author the proposed profile or reduced production
equations. Scope is E2 contract/prospective assessment; this is not E5 model
approval, runtime qualification or website delivery.

The reviewer read `../CONTRACT.md`, the accepted `supplied-original-v2` source
report and its independent review, and the current agent-review policy. The
original source transcription has a prior independent all-13-page visual review;
this review relies on that accepted transcription for the printed laws and does
not claim a new visual inspection of the private PDF.

## Local mathematics

Differentiation of original Eq7 gives
`eta_s = M Y (pi_s/pi - p_s/p)`, with `Y=(p/pi)^(N/(1-N))` and the
exact `N=0` value `Y=1`. Differentiating `p=C/(1-K eta)` gives
`p_s/p=C_s/C+(K_s eta+K eta_s)/(1-K eta)`. Substitution of Eq12 gives
exactly the proposed eta ODE, including the sign of the `K_s` term and its
denominator. The `K=1/3` constant-cell specialization agrees with the accepted
source reduction; `K=0` gives mean-pressure control. There is no extra independent
image-pressure initial degree of freedom on this active surface.

The independent script [check_control_algebra.py](check_control_algebra.py)
reconstructs eta by a scalar root of original yield plus mixed control after
perturbing pi by the original Eq12 tangent. It imports no Atlas implementation.
Its predeclared central-difference tolerance is 2e-6; all 54 checks pass with
maximum normalized error 1.249e-9. [Results](algebra-results.json) cover exact
`N=0`, `.2`, `.39`, fixed and varying controls, and `K=0,.2,1/3`.
These are local equation checks, not finite-trajectory or backend evidence.

Current-image Eq11 with Eq12 and the explicit incompressible-grain/current-volume
choice `e_s=-(1+e)D` agree with the accepted source scope. The finite-volume choice
must remain labelled Atlas kinematics. Accumulated principal strain increments
must not be advertised as exact finite principal stretch strains. General control
paths beyond conventional cell/mean pressure remain mathematical controls, not
new source validation or an unloading/elastic branch.

## Prospective contract findings

No blocking local mathematical finding was identified. The state/coordinate
offset must be explicit: `eq(s)=eq0+(s-s0)`, with both coordinate and state retained
on restart, or literal `eq=s` must be enforced. The coordinator has selected the
offset interpretation; this avoids silently changing user history.

The generic proposal appropriately requires every declared input, closed control
names, finite value/derivative inputs, positive representable progress, exact
zero-progress identity only with constant controls, and whole-parent rollback.
It supplies scalar controls rather than ignoring components of an imposed strain
tensor. Its restrictions exclude the source's missing interior/unloading/cyclic
laws. Full initial and stage checks must actually execute, including output
stress and diagnostic checks, unused inputs, all accepted substeps, and the full
parent context on a late failure.

**Decision pending exact implementation and frozen reference review.** A prose
proposal and these checks cannot establish that the generic evaluator exists,
that its schema accepts only the declared profile, or that numerical acceptance
policies and references are complete. No acceptance of unseen code or future
results is implied. Exact hashes and a final bounded decision will follow review
of the staged implementation and prospective freeze.

## Frozen v1 static implementation assessment

The reviewer inspected all nine files bound by `../prospective-freeze-v1.json`;
all nine hashes matched on inspection. The generic Python runtime reconstructs
and checks stages, applies Richardson factor 3 to full versus two-half midpoint,
accepts the two-half state, retains start controls in a context and compares them
exactly on the next advance. Its local working arrays and copied return context
provide the intended parent transaction design. The DSL's `evaluate` validates
each executed expression result, including derived values and observables. The
candidate's equations, stress embedding and exact N=0 branches agree with the
accepted active source reduction. No production trajectories or compiled
artifacts were executed by this reviewer.

**Blocking static finding V1-01:** the new C++ generator introduces unreserved
identifiers `inputs`, `rates`, `observables`, `scales`, `initial`, `model`, `rr`,
`oo`, `ss` and loop identifier `x`. The staged validator accepts these identifiers
for equation inputs, state, parameters or derived expressions. An equation input
named `inputs` generates `const T inputs=inputs[j];` in a function whose parameter
is already named `inputs`; a state named `rr` collides with the generator's result
vector. Thus the proposed generic accepted input language is not safely compilable.
Reserve every generated identifier or implement a collision-proof symbol mapping,
then bind and review revised bytes. This finding is static and does not imply
that this particular NorSand candidate uses the colliding names.

`build_references.py` independently evolves pi, e and accumulated strains using
Decimal RK4 and solves original Eq7 plus the stress control with Newton at each
stage. It does not import the candidate or its eta-rate. The NC initial-ratio
formula, exact zero-N branch and current-image limit are correct. The nine-case
Latin-square coverage samples every declared density/N/control category; it is
not the full 27-case Cartesian product and must be described accordingly.
The reference RHS should assert its complete supported active domain explicitly,
including nonnegative eta, positive e, B and consistency derivative, rather than
relying on root positivity and the Eq11 power-base check alone. This is a
prospective completeness finding; no observed out-of-domain reference result is
claimed.

The short-path reference policy explicitly excludes full E4/E5 closure. It does
not yet freeze complete long paths, restart/failure requests, actual native/Wasm
advance runtime or toolchain identities. Consequently it is useful prospective
capability evidence, but cannot satisfy the contract's full E2 numerical-freeze
requirement by itself. **V1 decision: mathematical mapping accepted; generic
implementation acceptance pending V1-01 correction; E2 overall remains open.**

## V2 follow-up

All input hashes in both `prospective-freeze-v2.json` and
`full-path-freeze-v2.json` matched at inspection. Path-only `PATH_RESERVED`
corrects the new local-variable collisions identified above without altering
legacy profile declarations. **Residual blocking finding V2-01:** `dot`, `norm`
and `cube_trace` remain valid declaration names while the shared DSL generator
emits these helper calls unqualified. For example a scalar parameter named
`norm` shadows an emitted `norm(tensor)` call. Reserve those unqualified helpers
or qualify their generated calls, then bind revised bytes. No compiler execution
is needed to establish this name-resolution conflict.

The revised independent reference builder checks active eta, B, consistency
derivative, pi and e domains. Its policy now explicitly describes the nine-case
Latin-square selection and increases paths to 0.16 shear progress with
4096/8192-step refinement at 50/75 Decimal digits. The additional history
invariants and restart/rollback/runtime evidence requirements are appropriate.
Construction is accepted prospectively as an independent source-equation
reference; its numerical adequacy remains contingent on actual unchanged-gate
results. No results from this new study are accepted before they exist.

The reference schedule freezes material settings and requested types of runtime
checks, but not yet exact per-check runtime requests or an implemented native/Wasm
advance driver/toolchain. E2 must continue to report those remaining tasks.

## V3 static runtime decision

All twelve hashes in `prospective-freeze-v3.json` matched at inspection. The
union of DSL `FUNCTIONS` with path reservations resolves V2-01. The interpreter
also now rejects nonfinite error weights/differences before acceptance.

The new C++ runtime uses local stage/rate/observable arrays and recursive local
substep results. It assigns the output context and observable buffer only after
whole-advance success. The flat C ABI copies input arrays, validates model/index,
shape/count/pointer-presence/settings checks, invokes the same generated evaluator
and runtime, and writes caller outputs only after success. This is consistent
with the intended rollback and zero-progress contract. Settings and derivative
channel semantics match the Python design. No model-ID branch or handwritten
NorSand kernel appears in the reviewed runtime/generator. Static review does not
establish successful compilation, pointer-buffer capacity supplied by external
callers, native/Wasm parity or transaction behavior under execution.

**V3 scoped decision: accepted for source mapping and static generic implementation
design.** No blocking mathematical or static runtime finding remains. E2 overall
is still open pending exact runtime requests/toolchain freeze and prospective
numerical adequacy checks. E3/E4 and E5 approval are not granted by this decision.

Two follow-through requirements were sent to the coordinator. Generated catalogue
metadata should explicitly retain sorted control order, rather than require a
consumer to infer that convention from Python source. Execution of the synthetic
test must bind the actual staged module bytes: the frozen test imports a mutable
`/private/tmp/atlas-norsand-path-v1` tree, so hashing only its own test script
does not prove which implementation ran. These are evidence/interface delivery
requirements to complete before downstream qualification claims.

The reviewer has not executed material trajectories, native builds, Wasm builds
or compiled candidates in any version of this review.

## V4 metadata and independent reference results

The `backend-proposal-v4/atlas/path_compiler.py` delta from v3 adds only explicit
sorted control order to catalogue metadata. This resolves that follow-through
requirement without changing generated equations or runtime numerics. The
`executed-stage-bindings-v3.json` records the actual eight proposal files and
Python executable/version/platform; its listed hashes agree with the reviewed
v3 proposal. The expanded v4 tree retains dependencies for reproducibility;
downstream execution still needs an exact full-tree/request/toolchain manifest.

`references-v2.json` binds the unchanged reviewed source builder and policy.
All nine retained cases meet the frozen gates: maximum 4096/8192 refinement
error 1.93137e-11 versus 2e-8, and maximum 50/75-digit precision error
1.84653e-48 versus 1e-35. This is adequate for the planned 2e-6 candidate
endpoint comparisons.

The reviewer independently checked each retained endpoint with
[check_reference_endpoints.py](check_reference_endpoints.py): original Eq7,
`q=p eta`, `C=p-K q`, accumulated shear progress, and
`(1+e) exp(ev)` invariance. All nine pass; maximum source-algebra normalized
error is 1.626e-50 against the independently predeclared 1e-35 gate, and maximum
kinematic invariant error is 1.039e-15 against 1e-10. Exact results and hashes
are in [reference-endpoint-results.json](reference-endpoint-results.json).
These checks inspect existing independent reference endpoints and do not run the
production candidate. No full transient curve or experimental accuracy is
inferred from endpoint qualification.

**Reference-v2 decision: accepted for the declared nine sampled endpoint
comparisons.** Backend requests should also explicitly exercise nonzero-shear
restart/partition and recovery following a rejection. Interpreter-only restart
checks do not execute those backend paths. The artifact checker should enforce
exact output lengths and finite numeric values before `zip`/`max`, whose current
truncation otherwise weakens its standalone validation. These were reported
prospectively before compiled results; no tolerance change is requested.

## Final scoped V5/V6 handoff

All 117 input hashes in `backend-source-request-freeze-v5.json`, and all 119
in `backend-source-request-freeze-v6.json`, match. The v5 material candidate,
model validation, Python path runtime and C++ path runtime are byte-identical to
the reviewed v3 files. The generator adds the accepted explicit control ordering
and conditional checked-DSL helper headers; CMake enables Emscripten exceptions
for the C ABI's catch-based failure boundary. These changes introduce no new
constitutive formula or integration algorithm.

The reviewer independently recomputed the retained interpreter evidence's
reference-error arithmetic from all endpoint output fields and verified its
source policy/reference/request/script hashes. All nine cases pass the unchanged
2e-6 gate; maximum error is 2.726941911e-7. All nine volume invariants pass the
unchanged 2e-8 gate; maximum error is 2.135017718e-9. The retained report records
45 negative checks, exact zero-progress/recovery checks and zero differences
between full and split/restarted state paths. The reported field errors and
volume invariants reproduce exactly from the retained output numbers. This is
independent checking of actual retained interpreter evidence, not an independent
rerun of the candidate or a substitute for the source reference construction.

The prospective 58-request backend batch contains 40 expected successes and
18 expected rejections. Its nine half paths, nine backend-state chained restarts
and nine cold restarts have consistent predecessor order, state layouts,
coordinate endpoints and retained/start controls. An explicit rejected request
is immediately followed by a recovery success. Native and Wasm runners both
use the preceding backend state for chained restart, check input preservation
and failed-output sentinels, and retain exact request/artifact hashes.
`check_backend_results_v3.py` independently enforces output lengths, finite
numeric values, expected status, failed-output sentinels and unchanged numerical
gates. Its eight reported synthetic checker tests are correctly labelled as
checker evidence only. The static request/checker concerns raised above are
resolved for these frozen bytes.

**Final decision: accepted within the bounded source-mapping, static generic
implementation, independent reference-endpoint adequacy, retained interpreter
evidence and prospective backend-request scope.** There is no unresolved blocking
finding in that scope. The backend batch has not been compiled or executed;
native/Wasm agreement and backend transaction qualification remain unobserved.
E2 overall remains open for the pending exact toolchain/execution receipt and
serial build-slot handoff. E3/E4 backend closure, E5 approval, atlas/browser
integration and live delivery are not granted by this review.

Exact final input and reviewer-output hashes are retained in
[final-review-bindings-v6.json](final-review-bindings-v6.json); independent
artifact arithmetic is in
[interpreter-request-arithmetic-v5.json](interpreter-request-arithmetic-v5.json).
The reviewer executed no model trajectory, native build, Wasm build or compiled
candidate throughout this review.
