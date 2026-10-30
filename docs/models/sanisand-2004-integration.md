# SANISAND reference integration: dispatch and failure semantics

This is source inspection of the [pinned OpenSees implementation](https://github.com/OpenSees/OpenSees/blob/8a0273db3e2f5a14c05924a179c1e439500c852c/SRC/material/nD/UWmaterials/ManzariDafalias.cpp), revision `8a0273db3e2f5a14c05924a179c1e439500c852c`. It advances SAN-01/03/06 without executing the complete material or selecting Atlas's canonical equations. The [machine-readable contract](../../catalogue/source-audits/sanisand-2004-integration.json) pins raw file hashes, function ranges and normalized function hashes, nine findings and ten pending runtime cases. No case is marked passed from inspection.

Original-paper extraction remains open. The ASCE reader returned 403 on 2026-10-31; the [NTUA university record](https://dspace.lib.ntua.gr/xmlui/handle/123456789/16222?show=full) supplies bibliographic metadata but no inspected full text. The numerical implementation below is not a substitute for the article. Read alongside the [initialization contract](sanisand-2004-initialization.md) and [tensor/unit conventions](sanisand-2004-conventions.md).

## Record actual routing

The C++ macros and active switch statements override misleading historical header comments. Stage zero still selects the elastic preparation branch independently of the scheme number. For elastoplastic stages:

| Code | Dispatch | Effective kernel |
| --- | --- | --- |
| 0 | Work-increment wrapper | Modified Euler |
| 1 | Direct explicit driver | Modified Euler |
| 2 | Implicit driver | Backward Euler with recursion/explicit fallback |
| 3 | Direct explicit driver | RK4, without active adaptive rejection |
| 4 | Work-increment wrapper | Forward Euler |
| 5 | Direct explicit driver | Forward Euler |
| 6 | Work-increment wrapper | RK4 |
| 7 | Maximum-strain wrapper, labelled MFE | Forward Euler |
| 8 | Maximum-strain wrapper, labelled RK | Forward Euler |
| 9 | Maximum-strain wrapper, labelled FE | Forward Euler |
| 45 | Direct explicit driver | RK45 |

In `MaxStrainInc`, only the FE case and a default selecting FE exist. Codes 7 and 8 therefore do not select their named algorithms. The explicit driver's unknown-code default selects Modified Euler; a future reference driver should require a known numeric code rather than silently accept that fallback.

## Wrapper subdivisions do not equal committed public steps

The strain wrapper uses the largest absolute component of internal engineering strain, with threshold `1e-5`. Above the threshold, its count is `floor(max_abs_component/threshold)+1`, including an extra subdivision at exact multiples. A Mandel shear component must be converted before assessing this threshold.

Between inner calls it advances stress, total strain, alpha and fabric, while retaining the original elastic strain and reversal anchor. Its local scalar outputs are not copied back in the subdivided branch; the final tangent reconstruction uses outer scalar arguments. Record complete state/tangent packets before assuming equivalence to repeated public increments.

The work wrapper first performs a full trial call and checks a signed stress-increment/strain-increment contraction against numeric `1e-4`. If exceeded, exactly two kernel calls replace tensor outputs. There is no recursive check enforcing that work limit after replacement. The same elastic-strain transfer omission occurs, and local scalar outputs are not copied back. Thus the work threshold is not an absolute, unit-invariant adaptive energy guarantee.

## Stage density uses a shifted strain argument

Modified Euler, RK4 and RK45 use the endpoint plus `T` times the full increment as the strain argument for void ratio. Standard interpolation would use the current strain plus `T` times that increment. At `T=0`, these routines already evaluate density at the caller endpoint; later stage inputs extend beyond it. This is a source fact to reconcile, not an instruction to adopt that convention in Atlas.

For example, with initial void ratio 0.8, current volumetric strain 0.01, endpoint 0.02 and `T=0.5`, the implementation argument is 0.025 and its density expression gives 0.755. Interpolation inside the caller interval would use 0.015 and give 0.773. These are algebraic predictions, not executed stress responses. Commit-time correction to the final void ratio cannot reverse density effects already accumulated in stress and history.

## A tolerance and a return code are insufficient evidence

Modified Euler fixes its local error tolerance at `1e-4` and minimum path fraction at `1e-6`; it does not use supplied `TolR` for that estimator. RK45 uses supplied `TolR` and a minimum fraction of `1e-3`. Error normalization changes at numeric stress norm 0.5, introducing another pressure-unit dependency. RK45 also estimates alpha error. Neither estimator measures fabric error. Record every history component under refinement.

At the minimum fraction, excessive error can still advance stress/elastic strain, limit the stress ratio and reconstruct alpha while leaving fabric unadvanced in that branch. Negative-pressure candidates at the minimum fraction can return before finishing the requested interval. Ordinary Modified Euler acceptance calls stress correction; RK45's corresponding call is commented out. These differences need runtime characterization.

The implicit path uses 19 residual components, a 30-iteration Newton loop and a threshold `(initial residual norm+1)*TolR`. Its residual includes dimensionless elastic-strain, alpha and fabric blocks together with an unscaled stress-valued yield function. A nominal relative tolerance is therefore not proof of unit-invariant residual control. The declared line-search variables do not imply an active line search in this Newton loop.

Scheme 2 is not pure Backward Euler: low trial pressure routes to explicit integration; other failures can recursively halve the interval or fall back explicitly. Depth is limited to 10. An explicit fallback is assigned success status. The recursive path also retains the original elastic strain for the second half; it copies the second-half multiplier and later uses it to reconstruct elastic strain over the whole caller increment. Capture these outputs separately before drawing conclusions from stress agreement alone.

The public 3D `setTrialStrain` returns zero after calling a void integration method. That method discards the implicit routine's status. A zero public return code cannot certify convergence, admissibility, tolerances, full-interval completion or rollback.

## Requirements for the eventual reference comparison

Capture requested and effective schemes, pressure units, explicit/implicit tolerances, internal stage fraction and density, accepted/rejected steps, fallback branch, recursion depth, correction/projection use, full state and tangent packets, and completed strain fraction. Keep fresh-process preparation and trial/commit observations from the initialization contract. Any diagnostic instrumentation must be separately hashed and distinguished from the unmodified reference.

The ten pending cases cover routing, strain thresholds, inner state transfer, stage density, tolerance refinement, Pa/kPa equivalence, excessive-error minimum steps, pressure early returns, implicit fallback and recursive history bookkeeping. The existing 87 selected-function comparisons do not exercise these integration paths and remain a separate evidence claim. No compiler, external material driver or native/Wasm run was used for this audit.
