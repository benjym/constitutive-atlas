# SANISAND reference initialization and state observations

This document extracts initialization and transaction behavior from the pinned
[OpenSees implementation](https://github.com/OpenSees/OpenSees/blob/8a0273db3e2f5a14c05924a179c1e439500c852c/SRC/material/nD/UWmaterials/ManzariDafalias.cpp).
It supports SAN-01, SAN-03 and SAN-06. It is a source-inspection result;
the scenarios below have **not** been executed through the complete material.
It does not close original-paper extraction or select the canonical Atlas variant.
See the [conventions audit](sanisand-2004-conventions.md) for tensor and pressure
mapping and the [machine-readable contract](../../catalogue/source-audits/sanisand-2004-initialization.json)
for source hashes, locators and pending reference scenarios.

## Construction is distinct from specimen preparation

`initialize()` zeros trial and committed total strain/stress, backstress ratio,
reversal backstress and fabric, and zeros trial elastic strain and plastic
multiplier. It sets `e=e_init`, `p_min=0.0001 P_atm` and
`p_residual=0.01 P_atm`. Initial stiffness is evaluated at an auxiliary isotropic
stress `P_atm I`; that auxiliary stress is **not** the stored initial stress.
Thus a fresh material does not represent a specimen already consolidated to
`P_atm` merely because its initial tangent was evaluated there.

The named full constructors initialize stress correction to enabled. Do not
rely on constructor defaults for integration settings: the factory and
full constructor taking an explicit class tag default to scheme `1`, tangent `0`, analytical Jacobian
`1`, and tolerances `1e-7`; a different constructor signature defaults to scheme
`2`, tangent `2`. At this revision the actual macros define scheme `1` as
Modified Euler and scheme `2` as Backward Euler. The historical header comment
describing the scheme numbers is inconsistent with those macros. A reference
record must include the constructor/factory route and explicit numeric settings.

## Stage selection has shared and mutating behavior

The stage flag `mElastFlag` is static. It is initialized globally to `1`, but the
class-tag null constructor sets it to `0`. A stage change affects other
instances using the same class in that process. The 3D `getCopy()` creates a
null instance before assigning its fields; construction and copy order therefore
need characterization. Use separate reference processes per case and select the
stage explicitly after all required construction/copy operations.

Parameter update `1` uses an integer stage; update `5` uses a double converted
to an integer stage. Stage `0` selects `elastic_integrator`; nonzero stages take
the elastoplastic integration branch. Updates to stage exactly `1` additionally
call `Elastic2Plastic()` immediately; it is not merely a numerical switch.

That transition has two important branches:

1. If either trial or committed mean stress is strictly below `p_min`, both
   stresses are replaced by `p_min I`, and trial/committed backstress ratio are
   zeroed. The function returns immediately. Strain, fabric, reversal memory and
   stiffness are not explicitly rebuilt by this branch.
2. Otherwise it computes `eta=sqrt(1.5)||dev(sigma_trial)||/p_raw`, where
   `p_raw=tr(sigma_trial)/3+p_residual`. If `eta>Mc`, it changes the stored
   parameter to `Mc=1.1 eta`. This uses the trial stress and mutates a nominal
   constitutive parameter. It does not perform the commented-out stress/backstress
   projections shown near that code.

The branch uses strict inequalities. Equality to the pressure floor or to `Mc`
must be tested separately. Repeating stage `1` is another call to this function;
record when it happens and whether any trial state was uncommitted at the time.

The future Atlas transcription must either represent an explicitly identified
variant with these transitions, or declare a preparation domain that avoids
them and verify that it does. Silent mutation of an immutable Atlas parameter
would invalidate the reported parameter set. Do not impose these implementation
corrections on the original 2004 law without reconciling the publication.

## Elastic preparation changes more than stress

With stage `0`, the source uses constant-in-pressure moduli
`G=G0 P_atm (2.97-e_init)^2/(1+e_init)` and
`K=(2/3)(1+nu)/(1-2nu)G`. It advances stress with the elastic increment, adds
the increment to elastic strain, and updates void ratio from total strain.
When the resulting `p_raw>1e-10`, it assigns
`alpha=dev(sigma_next)/p_raw`. Therefore anisotropic elastic preparation normally
creates nonzero backstress ratio, even though no plastic loading was integrated.
An initialized laboratory test must retain that state rather than replace it
with an isotropic `alpha=0` placeholder.

For fresh, one-step isotropic preparation to compression-positive mean stress
`p_target`, let `K0` denote the above stage-zero modulus. The prescribed internal
strain is `epsilon_i=p_target/(3 K0)` for each normal component, with zero
shear. Its expected source void ratio is
`e_prepared=e_init-(1+e_init)p_target/K0`.
The external OpenSees strain has the opposite sign. This is an analytical
reference case derived from the inspected elastic branch, not an executed
consolidation result or a calibrated sand specimen.

The source's finite-strain bookkeeping is the small-strain relation
`e=e_init-(1+e_init)tr(epsilon_total)` in both preparation and commit. For an
incremental transcription of this variant, the corresponding exact update is
`e_next=e_current-(1+e_init)tr(delta_epsilon)`.
Using the evolving `e_current` in the coefficient instead defines another law.
Resetting the laboratory strain origin must retain the preparation offset or
the consistent prepared void ratio. Rebasing `e_init` to the prepared void ratio
also changes this implementation's elastic moduli, so it cannot silently serve
as an interchangeable restart convention.

The `voidRatio` parameter update does not simply set the current state. It
computes `e_init=(e_requested+eps_v)/(1-eps_v)` using current total volumetric
strain. It therefore changes subsequent stiffness too. The denominator is
unguarded in that method; reference inputs must stay away from `eps_v=1` and
record the change. No immediate assignment to `mVoidRatio` is made there.

## Trial, commit, reset and recorder meaning

Before integration, reversal selection reads committed `alpha` and reversal
memory but uses `mCe` to turn the increment into a trial stress direction.
`mCe` is mutable output of trial integration. Repeated outer trial calls can
therefore require checks beyond merely comparing committed tensors. Full
reference execution must characterize this behavior rather than assuming
Atlas's immutable-parent stiffness policy matches it.

`commitState()` promotes stress, total/elastic strain, backstress, fabric,
reversal memory and multiplier, recomputes void ratio from total strain, and
updates scalar `K,G`. That call does not explicitly rebuild `mCe` from those
new scalars. The state and the stored tangent therefore require separate
observations at the trial and committed boundaries.

`revertToLastCommit()` returns success without restoring state at this revision.
`revertToStart()` skips initialization during initial-state analysis; otherwise
it calls `initialize()`. The latter does not explicitly clear committed elastic
strain `mEpsilonE_n` or committed multiplier `mDGamma_n`. Fresh Vector construction
and reuse/reset are different situations. Scalar initialization and these reuse
paths need runtime checks before a reference driver relies on them. A reset also
does not restore mutated material parameters or explicitly reset the static
stage. Prefer fresh-process replay for independent trial branches until those
behaviors are characterized.

The base `getState()` packs 26 values: internal engineering elastic strain at
indices `0..5`, stress-like `alpha` at `6..11`, stress-like fabric at `12..17`,
**committed** reversal memory at `18..23`, void ratio at `24`, and trial multiplier
at `25`. Base `getAlpha_in()` also returns committed memory. The 3D class hides
`getState()` with a method that packs **trial** reversal memory. The base method
is not virtual, and the base `getResponse()` calls it, so a recorder response
and a direct 3D accessor can report different memory before commit.

The state packet mixes conventions: its elastic strains are internal
compression-positive engineering components, whereas the 3D `elasticstrains`
response negates those components for the external convention. Backstress and
fabric have tensor shear. Use the accessor's documented representation, not one
uniform sign/shear conversion for all 26 numbers.

## Reference execution contract and pending cases

Every case must record raw source and binary hashes, toolchain/build settings,
numeric pressure unit, factory/copy route, all supplied and effective parameters,
stage transitions, integration/Jacobian/tangent choices, tolerances, preparation
increments, absolute strain reference, and commit boundaries. Capture stress,
strain, history, void ratio and tangent before and after stage changes and commit.
Use total elapsed time only as a driver coordinate; this reference law is not
being declared physically rate-dependent.

The machine-readable contract defines pending cases for construction versus
preparation, isotropic and anisotropic preparation, pressure-floor boundaries,
critical-ratio parameter mutation, shared stage/copy effects, trial/commit memory,
repeated uncommitted trials, reset/replay, and void-ratio parameter changes.
None is marked passed merely from inspecting the code. Full monotonic,
extension, reversal and cyclic integration comparisons remain SAN-06 work.

Full reference build and material execution remain pending. The existing
87-case selected-function execution record remains historical evidence of its
stated, narrower scope.
