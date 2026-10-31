# Clay2005 source-plus / conservative SPD interior — rate study v2

Task SRC-clay2005-rate-v2; owner review_igs97,2026-10-31. This is a **separate non-admitted zero-spin instantaneous research draft**. It preserves all [v1](../rate-study-v1/README.md) and [audit](../rate-review-v1/README.md) bytes. Nothing is added to the shared catalogue, compiler, solver build or website.

## Corrected source identity and unchanged rate

[Mašín2005](https://doi.org/10.1002/nag.416), accepted manuscript SHA256 `8650dd58a4b5725dc0176ab9cf3a034ed211847b840524254876c2652bdf9ff3`, AppendixC Eqs73–85 and p10 Eqs38–41. The printed Eq38 bracket is **plus**, consistent with Eq40/AppendixC; the old alleged conflict was an Atlas source-reading error. [SOURCE_CORRECTION.md](SOURCE_CORRECTION.md) carries the additive correction without rewriting historical evidence. Final-publisher equivalence remains unverified.

The compression-positive stress6/e rate and independent81component Cartesian action oracle are unchanged from the source-consistent v1 algebra:

`Sigma° = fs*(L:E + fd*Y*(L:m_unit)*norm(E))`, `e_dot=-(1+e)*trace(E)`.

Source m remains the negative spherical flow direction, H=Sigma/trace(Sigma), and `L:X=3*(c1*X+c2*a*a*H*(H:X))`. The source has five physical parameters phi_c,lambda_star,kappa_star,N,r; reference pressure, solver scale and fixed arithmetic metadata are not extra material constants. No new parameter or state was introduced. The schema still uses seven states and the same nine ordered parameter slots asv1: p_ref,p_scale,phi_c,lambda_star,kappa_star,N,r,lode_allowance,j2_floor. Mandel order is xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz. The model has a distinct ID `hypoplastic-clay-2005-appc-plus-spd-interior-v2-research`.

All41historical input/parameter/diagnostic/seven-rate records are bit-identical between old and new independent references; all10historical invalid input records are retained **byte-identically**. The new metadata and guard do not alter the rate expressions. Tests explicitly verify these facts against pinned old files.

## Separate conservative numerical stress support

V1 used the scale-free identity `detH=1/27-j2/6+j3/3` both in the rate and as a positivity guard. Cancellation could admit zero/negative eigenvalues, e.g. Sigma=diag(1,1,-1e-20)Pa. V2 retains this algebraic identity in the **rate** but adds independent numerical-domain checks before accepting a result.

The draft forms A=Sigma/p_ref and U=A/norm(A) in orthonormal Mandel coordinates. With U components x,y,z,u,v,w:

```
minor2 = x*y - u*u/2
D = x*y*z - (x*v*v + y*w*w + z*u*u)/2 + u*v*w/sqrt(2)
```

Require finite nonzero norm, x>0,y>0,z>0, minor2>m and D>m, with **m=64*epsilon=1.4210854715202004e-14**, epsilon=2^-52. In exact arithmetic, positive leading principal minors give positive definiteness by Sylvester's criterion; the extra diagonal checks are conservative. The normalization makes the margin dimensionless. p_ref is a fixed1kPa unit convention, not a fitted density parameter or new stress scale; using it before normalization does not change the real-arithmetic unit tensor.

The independent Cartesian oracle adds a separate max-scaled Cartesian Frobenius normalization and cofactor determinant check; it does not use Hdev or the DSL determinant rewrite for this support decision. The original direct Cartesian source-rate route and explicit fourth-order tensor action remain independent of the DSL.

The margin is a deliberately conservative **numerical interior**, not an all-SPD classifier or global floating-point theorem. It intentionally rejects some strictly SPD ill-conditioned inputs. Its rationale is independent of the failed v1 invariant expression: normalized components have magnitude at most1, so short polynomial evaluation has small **absolute** roundoff even near determinant cancellation, while relative determinant error is unbounded there. Binary64 epsilon is twice unit roundoff;64epsilon is128u, well above the few-operation roundoff scales. The usual product/sum error framework and its assumptions are described by [Higham's primary floating-point overview](https://nhigham.com/wp-content/uploads/2021/04/high21m.pdf). That reference does not prescribe this model's margin.

An operation-count sanity estimate uses terms of total coefficient magnitude at most1+3/2+1/sqrt2, several product/add rounding errors and normalization error; this motivates a margin of many tens ofu instead of testing D>0. It is **not a completed proof** covering all subnormal, overflow, library and expression-order possibilities. Finite intermediate checks and the unchanged arithmetic caps still reject nonrepresentable evaluations. A formal interval/certified-PD primitive would require a separate shared capability and review; none is added here.

This policy was declared before compiled observations. Independent80/120digit Decimal Cartesian diagnostics evaluate the **actual retained binary64 Mandel inputs** using Decimal sqrt2, not the intended pre-rounding spectrum. For the29retained support witnesses, maximum absolute determinant discrepancy from the DSL guard is4.124e-17, below m/100. This is empirical evidence for these cases, not a global bound or admission theorem.

## Separate accuracy and support corpora

[reference.json](reference.json) retains the original41all-seven-rate comparisons under the unchanged v1 input-scaled policy: stress component error<=1e-10Pa+2e-12*S; void error<=1e-15+2e-13*V. S=max(1Pa,norm(Sigma0))*norm(E); V=max(1,(1+e0)*norm(E)). Nonisotropic comparison cases have j2>=1e-8; exact spheres use correct analytic limits. High-precision near-isotropic accuracy remains unresolved, as does near-singular rate accuracy of the determinant route. These fixed budgets were not tuned after compiled observations; none occurred.

[invalid-cases.json](invalid-cases.json) preserves the old10finite invalid inputs. [support-inputs.json](support-inputs.json) adds29**support-only** requests: tinypositive/zero/negative diagonal eigenvalues, actual positive/negative subnormals, points well inside/outside the declared margin, scale factors1e-50/1/1e50, dense oblique companions and shear rank-loss adversaries. Rounded rotated tensors are not asserted to retain exact intended eigenvalues; [support-reference.json](support-reference.json) reports actual-input Decimal minors, determinant and SPD/support classification separately.

Both model and Cartesian oracle must reject every excluded support witness. Accepted support witnesses must return finite7rates, but they are **not source-rate accuracy certifications**. In particular, admitting diag(1,1,1e-10) into the numerical domain does not establish useful rate accuracy near that boundary. Rotated intended tinypositive/negative states can round to the same matrix; the margin rejects that shell without a sign correction. No eigenvalue, pressure, density, Lode or Y clipping is introduced.

The exact-sphere branch, double-deviator Hdev projection, independent component residual, nonzero-j2 floor1e-100 and raw-Lode64ulp allowance remain unchanged. They test evaluation support, not full physical SBS admissibility. No spin, IGS, structure, plastic strain or hidden reset is added.

## Replay and source-only evidence

From this directory in the installed repo:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 check_study.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_rate test_v2
```

Staging requires `--repo /path/to/constitutive-atlas` for the checker; set `PYTHONPATH` and `ATLAS_REPO` to that checkout for unittest. `reference.py` and `support.py` need only stdlib Python; full Atlas checks use the existing interpreter. Fresh references include complete strict JSON/type representation checks, preventing Boolean/numeric alias forgeries. Use a **fresh** optional `--output` path to retain a new checker report. The delivered [checks.json](checks.json) is the source-only v2 report.

Result:18Python groups pass,41historical rate comparisons pass,10historical invalids reject,29support statuses match both implementations and the two Decimal precision grids. Header generation with the common compiler is tested in a temporary directory; this is not compilation. Pure evaluation immutability tests are not finite-update rollback tests. The manifest pins new files, historical dependencies and observed common runtime bytes. No private sources/renders, author code, bytecode, utility assembly scripts or compiled artifacts are delivered.

## Frozen next step and remaining gates

After independent review, a separately authorized coordinator can freeze an isolated generated catalogue with this exact model, bind source/runtime/generated/artifact hashes, then build/run one serial native instantaneous target and one Wasm target. Preserve the **three distinct** groups:41accuracy requests,10historical numeric-invalid requests,29support-status requests. Keep normal-domain failures distinct from parser/type/arity errors. Each negative must have same-process/instance known-parent recovery, raw bytes persisted before parsing, strict finite input/output/status/descriptor checks and both raw companions for parity. Do not coerce named/type-invalid JSON into numeric CSV and count it as compiled coverage.

The support-only rows must not be assessed under the historical rate-accuracy policy or used to claim newly verified near-singular rates. No compiled collector, material AD, finite path, objective rotation, initialization repair, experimental calibration or scientific/public admission is supplied. Independent high-precision near-isotropic/near-singular rate work, a full all-stage coupled finite-path reference and explicit transactions remain separate milestones.
