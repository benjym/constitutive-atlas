# Clay2013 isotropic trajectory: independent closed form

This packet independently solves the isotropic ODE supplied in the task; it does not import the model DSL or numerical solver and makes no model admission or experimental validation claim. `tools/reference_clay2013_isotropic.py` implements the closed form in90-digit Decimal; `tests/test_clay2013_isotropic_reference.py` checks the closed form. `catalogue/investigations/clay2013-integration-v1/isotropic-reference.json` retains nine arbitrary-density loading/unloading/reversal paths, exact decimal input strings, full p/e/pe/r endpoints and oracle/generator SHA256. Float inputs preserve their exact binary64 identity; string inputs preserve decimal identity.

Write L=lambda_star, K=kappa_star, C=1/K−1/L>0, x=integral(v), s=integral(abs(v)), eta=sign(v), and r=(p/pe)^2. Given

    p'/p = 1/2[(1/L+1/K)v+(1/L−1/K)r abs(v)]
    (ln(1+e))' = −v,
    (ln pe)' = v/L,

we obtain `dr/ds=C*r*(eta−r)`. With y=1/r this is linear: `dy/ds=C*(1−eta*y)`. On a segment of constant sign:

    compression: y=y0*exp(−C*s)+(1−exp(−C*s))
    unloading:   y=y0*exp(C*s)+(exp(C*s)−1)
    1+e=(1+e0)*exp(−x)
    pe=pe0*exp(x/L)
    p=pe/sqrt(y).

Every p0>0 and e0>=0 is mathematically admitted for this scalar calculation, with L>K>0 and finite N. pe0 is recalculated from1000*exp((N−ln(1+e0))/L), not independently supplied. Compression stays inside e>=0 only for x<=ln(1+e0). y remains positive for finite same-sign segments and positive y0; no finite pressure blow-up occurs in that scope. Compression drives r toward1; unloading drives r toward0. At r0=1, compression obeys p=pe exactly, hence ln(p/p0)=x/L. Unloading from r0=1 is not the reverse path: a closed strain loop restores e but generally not p. v=0 gives unchanged state. Piecewise reversal requires composing segments, not replacing x by accumulated absolute strain. Segment timing is immaterial for this rate-independent model.

The exponential differences use a cancellation-resistant expm1 series. The implementation intentionally retains a finite Decimal precision/domain, not an all-real oracle; extremely disproportionate scales may need higher precision. The derivative test evaluates the supplied scalar equation independently of the closed-form update, for both signs and densities far above/below the density surface. Semigroup tests use37 partitions and do not compare two numerical ODE solvers.

# Proposed common-engine acceptance tests

1. Construct exactly isotropic Cartesian/Mandel stress `[p,p,p,0,0,0]` and a fixed sign increment `[dx/3,dx/3,dx/3,0,0,0]`; with binary64 dx/3, use the actual trace sum as oracle x. Extract p as mean of output normal stresses; test all three equal, shear zero and void ratio as well as p. Cover p0=10,10000,1000000 Pa at e0=.8, L=.12,K=.025,N=1.1. These span strongly different initial r, not only r=1.
2. Use the nine retained paths as endpoint references. Compare actual binary64 initial p/e/parameters with Decimal.from_float oracle inputs; oracle pe must use those same inputs and fixed1000Pa. For reversal, call solver separately at every sign change; include entry/exit records and cumulative signed volumetric strain. Compare p/e separately with declared stress/e scales, not only max norm; also report r and exact mass relation residual `ln((1+e)/(1+e0))+x`.
3. Refinement: at least three strictly tighter rate tolerances on identical caller increments; record settings, accepted fractions, substeps/rejections, final errors and full input/model hashes. Require demonstrable asymptotic improvement in both p and e outside roundoff; do not require every arbitrary tolerance pair to improve strictly, since adaptive partitions may coincide. A stronger deterministic check uses fixed caller partitions1,2,4,8,16 at tight enough solver settings to expose convergence and checks pressure/void-ratio order against the closed form.
4. Caller partition: for compression, unloading and reversal separately compare1,7,37 equal subdivisions within each sign segment against the same closed-form state. Exact partition equality is not expected from a numerical solver. Require the discrepancy to shrink under solver tolerance refinement. Each caller subdivision must preserve precisely the intended total actual binary64 strain (put any residual in last increment).
5. Density-surface compression r0=1, formed with actual initial pe, checks the simple exponential p/pe invariant, while arbitrary density cases distinguish omission/mis-sign of nonlinear coupling. Zero increment must preserve all7 fields and return success without fabricated strain. A roundtrip compression/unloading case must restore e within tolerance but must NOT be asserted to restore p.
6. Domain rollback: from e0=.1 request compression dx=.2 (larger than ln1.1), so no admissible endpoint exists. Expect `ok=false`, returned state exactly equal to input7 fields, unchanged caller-owned input/parameter buffers, informative failure. Common-engine diagnostics may retain attempted accepted substeps/rejections; do not assert those counters are rolled back. Follow the failed call with a small legal increment and compare with the same call from an untouched initial copy, detecting hidden partial-state contamination.
7. Budget rollback: choose a legal, nonlinear arbitrary-density increment that demonstrably needs more than the allowed substep budget; first establish success under sufficient budget, then a deliberately tiny max_substeps/max_depth must fail and return original state exactly. Distinguish invalid settings from an actual partial-recursion failure. A failed attempted intermediate positive half followed by failing second half is the most useful rollback case. Diagnostics can prove partial progress was attempted but never retained in returned state.
8. Initial-domain rejects: p<=0, e<0, invalid L/K ordering and nonfinite fields must fail deterministically before integration and preserve inputs. Avoid assuming every positive stress magnitude is numerically representable throughout all source expressions. Include a nonisotropic companion separately; the isotropic oracle cannot validate deviatoric flow, objectivity, Lode dependence or full7-dimensional integration.

Repository solver locator reviewed read-only: cpp/include/atlas/solver.hpp lines50–106, midpoint/advance_recursive/integrate. It returns original state on failure while diagnostics count attempted work, so rollback assertions above follow the existing observable contract. No builds/native execution or repo edits were performed for this packet.
