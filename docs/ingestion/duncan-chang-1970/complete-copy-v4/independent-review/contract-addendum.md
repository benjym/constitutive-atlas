# Independent finite-contract proposal review

Reviewer: `/root/duncan_complete_review`,2026-11-01. Separate from proposal author. Scope: prospective E2 design and Python-only capability diagnostic; no E5 model approval or compiled qualification.

The residual is the correct inverse of original Eq15: deviatoric stiffness E/(1+nu), volumetric coefficient E/[3(1-2nu)] multiplying trace(de)I. Both residuals have Pa units; numerical residual scaling is a separate solver choice. Endpoint arithmetic principal-stress averages are objective under passive fixed-basis changes; they differ from eigenvalues of the averaged tensor and are a clearly labelled discretization choice. The source does not prescribe this implicit scheme.

Endpoint branch selection, equality policies, committed maximum-D history, averaged-strength postfailure trigger and exposed E_failure are internally interpretable choices. They do not reproduce exact crossing/event locations or guarantee residual-root existence/uniqueness. In particular an endpoint may be beyond strength while its averaged S is below one; partition refinement and the disclosed10psf sensitivity are required. Selection from the zero-increment root is prospective and still needs a concrete solver/recovery implementation. h records accepted endpoint maxima rather than an exact unresolved continuum extremum. This limitation must remain public.

## Capability finding

Read the numerical primitive, DSL typing rules and validator. Independently ran `python3 -B docs/ingestion/duncan-chang-1970/finite-contract-v1/check_capability.py`. Output matches capability-results.json. Direct differentiable extrema reject source-relevant repeated selected extrema at hydrostatic and conventional triaxial states. Value-only extrema produce primal values, but using them directly in the model residual is rejected; the inferred value-only qualifier independently confirms this is not merely an accidental units mismatch. Upper/lower pair sums cover only the complementary isolated eigenvalue cases and fail at triple repeat. The exact one-sided directional witness disproves a classical linear derivative of max eigenvalue at hydrostatic stress.

This supports a generic numerical/derivative-policy dependency, not an impossibility theorem for the existing expression language. Lazy branches with value-only multiplicity predicates and trace/pair sums can produce exact primal extrema at exact ties; averaged cluster derivatives could define a selected/generalized policy. Their near-tie semantics, transition consistency, rotations and solver behavior remain unreviewed. Source does not choose such a policy. Treat the proposed capability task as an explicit generic design/qualification gate, rather than claiming that a handwritten model kernel is required.

## Findings requiring clarification before candidate freeze

1. Initialization bounds alone do not define accepted-update domain. Require positive finite endpoint and averaged confinement/strength, finite positive evaluated E, finite complete parameters (including n), and history invariants; reject invalid states without clipping. Otherwise a cohesive case can admit a tensile endpoint while average confinement remains positive.
2. The external parent transaction must roll back every internally accepted substep if a later substep fails. Distinguish internal committed parent from externally committed caller state.
3. p_ref is an added numerical scaling parameter, not one of the source soil coefficients; give its role explicitly if retained.

Neither the absence of frozen acceptance tolerances nor the absence of an executable nonsmooth policy is concealed: these remain blocking E2-completion items. This review accepts the proposal as a useful bounded design/gap handoff only after the clarifications above, and does not approve a model, backend, atlas/browser release or experiment claim. See the separate exact-byte receipt and any resolution addendum for the final reviewed revision.

## Resolution and final bounded decision

The final reviewed proposal explicitly applies finite parameter/domain checks throughout evaluation, positive endpoint and averaged confinement/strength, finite positive modulus/intermediates, and no clipping. It distinguishes unsolved Newton memory iterates from accepted-state invariants. It also explicitly rolls back all provisional internal commits when the external parent fails, and labels p_ref numerical only. These resolve findings1-3 above at the design level; eventual declarative implementation and solver qualification must demonstrate them.

Accept the final exact-byte document as a bounded prospective design/capability-gap handoff. Do not mark E2 numerical policy complete: a generic nonsmooth formulation/Jacobian policy, exact candidate, independent references and full acceptance freeze remain unresolved blocking gates. No E5 or release decision is supplied. The companion receipt binds the final reviewed proposal, diagnostic/results, retained failure and source supplement; earlier source review remains unchanged.
