# Independent generated spectral context assessor, v1

Task: AUDIT-spectral-generated-context-assessor-v1. This prospective packet implements a standard-library-only assessor for the staged generated-context study. It imports neither Atlas nor author code, runs no candidate numerical implementation and makes no scientific-admission claim. The included ideal rows are synthetic rounded independent references, **not compiled observations**.

## Run

```sh
python3 -B check_sources.py /path/to/spectral-generated-context-v1 /private/tmp/new-source-review
python3 -B check_assessor.py /path/to/spectral-generated-context-v1 /private/tmp/new-synthetic-checks
python3 -B assess.py /path/to/spectral-generated-context-v1 /path/to/backend/run.stdout
```

The second command accepts an ordered JSON array or NDJSON output and exits nonzero on assessment failure. The first command constructs ideal rows from the frozen independent p360 references, then rejects each corrupted full output frame. Its output directory should be fresh to retain preceding results. `checks/` retains the first 28-probe run; `checks-final/` adds an explicit Mandel shear-direction corruption. Neither run invokes a compiler or a compiled artifact.

## Exact acceptance

Require all 1,589 rows in request order, unique matching identity by position, exact integer slot, exact kind, strict Boolean expected status and true input-unchanged witness. Success outputs have the exact requested arity; every number is finite, each Jet has exactly 38 finite derivatives. All successful spectral requests must use precisely the reference tensor and 38 original stored-Mandel seeds, including rounding. The first 1,136 emitted-expression requests retain the primitive requests' values, seeds, operation, kind and expected status.

Use the existing primitive bounds without modification: eigenvalue/sum primal `512 eps ||A|| + 2 minsub`, projector primal `2048 eps ||A||/gap + 2 minsub`, scalar directional `2048 eps ||H|| (1+||A||/gap) + 2 minsub`, projector directional `8192 eps (||H||/gap) (1+||A||/gap) + 2 minsub`. Norms use stored Mandel components and Decimal arithmetic at 500 digits; Cartesian projector references are converted with mathematical sqrt(2). Exactly representable diagonal eigenvalue queries require exact binary64 equality; value-only Jet transport derivatives are exactly zero in all 38 columns. Constant/identity context outputs and their derivatives require exact equality; no new composite-error allowance is introduced.

Expected failed calls must report false and preserve inputs. Their scratch outputs are not constrained numerically. This intentionally makes no scratch-output transaction claim. Accepted solver state is checked even on expected failure.

History: success full state is `[18] + projector6`, generation8, epoch3, events `[0,1]`, failed−1, executed2. Failure full state remains `[17,11,12,13,0,0,0]`, generation7, epoch3, no events, failed1, executed2. Numeric types and integer metadata are checked independently.

Solver: expected failed accepted state is `[7,2,-3,0,0,0,.7,0]`; success changes only memory to1. Both calls require the tentative-reset witness, successful recovery and recovery/fresh agreement. Independently require **both complete recovery and fresh states** to equal `[7,2,-3,0,0,0,.7,1]`, even if all flags are true. Failure requires rejected≥1 and the `integration failed` prefix; success requires rejected0 and an empty message.

## Source review and resolved finding

Reviewed actual `driver.cpp`, generated `contexts.hpp`, generated model/history source, 23 model fixtures, history input, slots/policy/wire and the frozen solver/settings. Source hashes are in `source-pins.json`; these are observations of specific immutable bytes, not a claim that later parent changes were reviewed.

**R1 — recovery observability, fixed before compilation.** Initial driver metadata only exposed recovery/fresh equality and Boolean success. Two equally stale states could satisfy those flags. Parent accepted the finding and added full `recovery_state` and `fresh_state` vectors (current driver line34); the assessor now checks both independently. The synthetic stale-equal-state corruption leaves all flags true and is rejected. The original interface/finding is recorded here; no compiled failure occurred.

Actual scalar residual adapters negate the emitted `-lambda` component back to lambda; no operation-chain budget is needed for sign reversal. Actual physical-time observable adapters return the scalar/projector directly. The first three isolated emitted-expression adapters exercise value-only primitive transport; they do not prove those functions are legal numeric model sinks. Separate static qualifier tests and actual domain/lazy predicates cover legal and rejected consumers.

Control review: lazy unselected hydrostatic branches must succeed with constant I; selected hydrostatic projector branches fail; a repeated complementary pair with isolated selected extreme succeeds. Sticky invalid ordinary spectral predicates must retain failure even when their fallback Boolean selects a valid arm; eager zero masking and eagerly declared derived expressions also fail. Ordinary spectral domain/initial checks reject selected repeats, while value-only domain checks can accept them. Check-only skips equations; inactive reset returns exact input value/seeds; selected invalid reset fails and valid reset returns projector. State/observable scale calls are double-only and test failure then recovery. The failed solver trial makes trialA=3I only after tentative memory reset; frozen solver source retains original accepted state on failure. max_depth0 ensures a rejection cannot silently recover through subdivision; other frozen settings match policy (45 iterations, 2e−10 residual, 1e−6 rate, 20,000 substeps, 11 backtracks).

No additional blocking source issue was found in that bounded review. This does not establish compiled emission, backend accuracy, full constitutive tangent/branch semantics or Mohr–Coulomb admission. Parent must freeze the whole prospective source closure and run native then Wasm serially.

## Evidence limits

Input immutability is a driver witness, supported by source comparison of exact input bits; the assessor cannot reconstruct hidden process memory from output alone. Solver reset preparation is witnessed by a separate explicit prepare call, with the actual integrator's prepare-then-trial ordering also inspected in frozen source. Recovery uses the stateless integration API with original parent inputs; this is not a persistent solver-object test. Every request carries all 38 seeds, but history/scales/solver APIs are double-only; arbitrary 38-column accuracy is asserted for the emitted-expression, residual, observable and applicable reset/control Jet contexts.

Expected failure diagnostic classes are intentionally not invented: the direct wrapper exposes a Boolean. Source-generation failures were retained by the parent study. The initial request crosswalk assumed every original invalid-input request had case metadata; 88 intentionally invalid requests omit it. The corrected check compares all present original fields and always compares values/seeds/status. Its failure is retained in checks/source-review-initial-error.txt. The assessor's initial Python syntax typo was corrected before any numeric run; no candidate numerical result motivated a change to references, expectations or bounds.
