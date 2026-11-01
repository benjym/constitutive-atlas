# First plastic-step failure: independent local root existence

NUM-md1997-native-failure-analysis-v1, bounded numerical diagnosis only. This work read saved native failures and source; it executed no compiled artifact, imported no Atlas evaluator and changed no model or shared code. The actual failed E4 qualification remains a failure.

## Observed failure

The saved native-v3 dense-cos3theta-+0-128 chain starts exactly on yield at p0=160kPa, alpha=0, e=.65, cos3theta=0, using the rotated Mandel direction established in the independent interior-Lode reference. Its first prescribed strain is t*n with t=.01/128=.000078125. The response fails and rolls back, reporting49iterations,15rejections,0acceptedsubsteps. All observed plastic paths fail; hydrostatic and the purely elastic control pass. This pattern alone cannot prove the cause, so an independent local-root study was frozen separately before its execution.

## Source-derived backward-Euler reduction

Keep the fixed unit direction n. At a plastic endpoint let alpha=beta*n, r=x*n. The source yield equation imposes x=beta+S*m, S=sqrt(2/3). Source coefficients beta_b(p),beta_d(p),h(p,beta),D(p,beta) are obtained directly from original Eqs17–21,24,26,27 using cos3theta=0 and fixed e=.65. No candidate residual expression was imported.

Backward Euler applied to the source mean-stress equation, tensor deviatoric stress-amplitude equation and backstress equation gives:

- `p-p0 + gamma*K(p)*D(p,beta) = 0`.
- `p*(beta+S*m)-p0*S*m - 2*G(p)*(t-gamma) = 0`.
- `beta - gamma*h(p,beta)*(beta_b(p)-beta) = 0`.

Eliminate gamma using the third equation, then bracket p in[1,160]kPa for each beta. Finally bracket beta in[0,.1] with opposite-sign deviatoric stress residuals, and bisect. This uses a scalar existence construction instead of production Newton, AD or its elastic predictor. The diagnostic enforces the frozen endpoint domain and residual tolerances.

An admissible local endpoint exists for the full first increment, its half, and its maximum configured dyadic subdivision1/16384. Fullstep root: p=157619.734054626Pa, beta=.0279774424552234, gamma=.0000258594523097737. All normalized residuals are below8e-17; hardening-distance margin is1.56733366>0. At the1/16384subdivision, p=159999.855660523Pa and gamma=1.50421096e-9. Thus lack of an admissible local root does not explain this bounded failure. No uniqueness or global-path existence claim is made.

## Narrow source-code defect

Read-only inspection of isolated source-v2 `cpp/include/atlas/solver.hpp` shows `implicit_step` sets `predictor=true` whenever a model has a plastic multiplier, then replaces the multiplier residual with gamma during that elastic predictor. Its only transition to `predictor=false` is inside the condition `err<residual_tolerance && solution_admissible(model,z,p)`.

The candidate correctly declares final yield feasibility as a solution constraint. At this plastic first step, the converged gamma=0 elastic predictor violates it: its yield_scaled is.04065385005643578, versus the allowed1e-8. At the maximum1/16384subdivision the same predictor violation is2.4813140903565e-6, still above1e-8. Because feasibility gates the transition, the solve cannot enable plastic correction even though its elastic mechanical residual has converged. It instead attempts Newton on an already solved predictor system; zero or roundoff corrections do not provide the required departure. Subdivision within the configured depth cannot fix that transition gate.

The smallest generic capability correction is to permit a converged domain-valid elastic predictor to transition into the full complementarity solve before applying final solution feasibility. Final return/commit must continue to require solution constraints. This is a proposed generic solver correction, not an implementation or approval. The model constraint must not be relaxed to make the elastic predictor look admissible. Parent owns implementation, independent review, serial rebuild and rerunning the unchanged E4 gates.

## Reproduction and retained evidence

Run `python3 docs/ingestion/manzari-dafalias-1997/delivery-v1/native-failure-analysis-v1/root_study.py`. `POLICY.md` was frozen before this diagnostic. `results.json` retains brackets, roots, source domain margins, normalized residuals and predictor violations. `inputs.json` hashes the read-only actual failure/source/model inputs. `manifest.json` binds this new diagnostic only. Earlier source references and native failure reports remain unchanged.
