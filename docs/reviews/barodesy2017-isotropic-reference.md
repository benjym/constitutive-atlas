# Barodesy2017 isotropic finite-path reference and study design

This staged packet supplies an independent stdlib-only scalar reference, ten Python test groups and retained reference data for the selected **body** zero-spin law. It does not run or validate a finite native/Wasm update. Source/model admission, experiments, general nonisotropic paths, finite spin, zero-step tangents and K=0 remain separate gates. Existing model/candidate status is unchanged.

Source selection: Medicus–Fellin, *An improved version of barodesy for clay*, Acta Geotechnica12,365–376(2017), DOI[10.1007/s11440-016-0458-4](https://doi.org/10.1007/s11440-016-0458-4). Publisher PDF SHA256 bd049a3fd874c9e4945e1c77f5af5b84ac14c26a08cee1b953428b4312e6af15. Locators and signs follow the existing implementation checklist: bodyEqs1–10 pp366–367, Table1p367, Table2p368 and incompressible-grain footnote13p374. The packet uses that previously inspected dossier; it does not claim a new PDF inspection or redistribute any PDF. BodyEq8 uses **2p** in critical density; the NCL initialization uses **p**. Appendix41's6p and the finite-spin printing issue remain unresolved source differences.

## Derivation and scope

Let compression-positive stress be pI, loading de=I dv/3 and v=int tr(de), with zero spin and incompressible grains. Write q=1+e, lambda=lambda_star, kappa=kappa_star, t=lambda*c5, K=c3/sqrt(3), B=2^t and z=[q/(exp(N)*(2p/1000)^(-lambda))]^c5. Stress and pressure use Pa; fixed reference pressure is1000Pa. The four soil parameters are explicit and the angle is radians, converted from Table2 degrees once to binary64.

The exact hydrostatic continuation is P=I/sqrt(3). Adding body f and g cancels c6. For signed volumetric coordinate v the scalar body law becomes:

- Compression dv>0: d(logp)/dv=1/lambda+K*(z-B).
- Expansion dv<0: d(logp)/dv=1/kappa-K*(B+z-2).
- In either branch: dq/dv=-q.

The expansion formula follows delta=+sqrt(3), Lambda=kappa. At NCL z=B its slope is1/kappa-2K(B-1), generally different from1/kappa and1/lambda. It is therefore incorrect to extend the compression NCL curve through reversal.

NCL is q=exp(N)*(p/1000)^(-lambda), so z=B, not1. Its derivative satisfies d(logq)+lambda*d(logp)=-dv+dv=0. Thus isotropic compression with mathematically exact NCL initial data stays on the body NCL:

p(v)=p0*exp(v/lambda), q(v)=q0*exp(-v).

No NCL reset is performed during evaluation. Initialization e0=exp(N)*(p0/1000)^(-lambda)-1 is chosen only for these benchmark inputs.

## Binary64 initialization and an independent correction

A stored binary64 e0 generally has a small nonzero log-NCL residual. The ideal exponential curve preserves that initial residual mathematically, but the exact body law slowly evolves it. `exact[].state` retains the requested ideal exponential benchmark, rather than silently forcing the input onto an exact manifold.

To quantify that distinction, the packet derives a separate compression-only closed form for arbitrary supported initial density. With x=(p/p0)^(-t), the compression ODE gives

x'=(-c5+tKB)x-tKz0*exp(-c5v).

Solving this linear scalar equation gives

p(v)=p0*exp(v/lambda)*[1+(1-z0/B)*expm1(tKBv)]^(-1/t).

It reduces to NCL when z0=B. `exact[].rounded_initial_exact` evaluates this formula using Decimal80/100/120 coefficients from the actual binary64 parameters and initial values, including an independent Decimal sine. It is a scalar body-law solution, not a general tensor update. The actual production algebra rounds elementary operations separately; no rigorous global rounding bound is claimed.

The maximum rounded-initial pressure correction in the retained nine paths is2.3283064365386963e-10Pa. Eighty/120-digit outputs agree after binary64 rounding in the focused tests. Every path retains its input and output log-NCL residual, ideal state and corrected state. Proposed numerical reference floors are1e-7Pa stress and1e-14 void ratio; these are conservative empirical comparison allowances, not certified error bounds. Prefer the corrected target for an actual-rounded-initial comparison; if the ideal target is used, explicitly retain the measured correction within the reference allowance.

## Reference data contract

`tools/barodesy2017_isotropic_reference.py` imports no Atlas modules, source evaluator or solver. `study()` is deterministic in the local stdlib environment. Its literal dependency receipts bind the current research model, source checklist and independent Cartesian rate oracle; tests check these against current files. The script SHA and source PDF SHA are also retained.

The top-level contract is barodesy2017-isotropic-reference-v1, symmetric_mandel, compression_positive, zero_spin. The state is sigma_xx,yy,zz,xy_Mandel,yz_Mandel,xz_Mandel,e. Parameters are ordered phi_c,N,lambda_star,kappa_star,sigma_star; sigma_star is fixed1000Pa, not a fifth soil calibration input.

Each case contains `input={id,soil,p0,initial:[7],parameters:[5],increments:[[6]x3],volumetric_knots:[4]}`, canonical input SHA and `exact=[{segment,v,state:[7],rounded_initial_exact:[7],ncl_residual,rounding_correction_stress}]` including segment0. Increment diagonals are the actual binary64 delta-v/3 values. Reference coordinates are formed from the sum of those actual components; they need not equal their decimal labels bit-for-bit.

The nine cases are London/Dresden/Weald at25,100,400kPa, with nominal v knots0,.005,.015,.03. The smallest final void ratio is0.4395410495685315. Exact pressures remain positive; hydrostatic stresses have normalized Sylvester minor1/3 and determinant1/(3sqrt(3)), far inside the declared64-epsilon research margin. The exact hydrostatic loading branch skips the general matrix exponential; this is not finite-path evidence for nonisotropic matrix directions.

## Predeclared common-engine experiment

Use each case with the existing full seven-state research model and schema-generated midpoint solver, explicit initial/parameter vectors, all six strain controls fixed. The matrix is residual/rate tolerances1e-4,1e-6,1e-8 with one caller update per segment, plus caller partitions7 at loose and tight tolerances:45trajectories and459actual calls. Caller partitioning must chain actual returned state and use a final residual subincrement, not repeatedly restart from the original state. Preserve original endpoints.

Before running, proposed global endpoint bounds are max stress component error/p0 and absolute e error <=5e-3,3e-4,2e-5 respectively, plus the declared reference numerical floors. These bounds are independent of local solver settings; passing them is not an error certificate. Also retain isotropy/shear error and exact volume closure at **every** returned caller point, not only original endpoints. Tightening should reduce stress/e maximum endpoint errors beyond their numerical floors, and loose-vs-tight caller-partition discrepancies should shrink. Report measured orders; do not infer a universal order from three tolerances or equate a local tolerance to a global bound. Predeclare the exact shrink criteria in the runner before native results arrive.

The runner should independently bind model/source/reference/generator hashes and fresh exact reference replay; enforce exact45trajectory completeness; finite typed vectors and integer counters; request/response echoes, settings, catalogue identity, true caller chaining and original segment targets. Validate every returned state's positive pressure, e>=0 and selected support, not just endpoints. Retain failed-budget/domain/zero controls and recovery separately; this reference module itself does not implement such native protocol checks.

## Off-NCL and reversal scalar diagnostics

Six extra diagnostics (two per soil at100kPa) retain scalar log-pressure RK4 grids16/32/64 per segment. The exact volume relation is used at every RK stage, with finite p>0/e>=0 checks and minimum stage margins retained. Off-NCL compression starts q0 reduced by10%; its grids are checked against the separate arbitrary-density analytic compression solution. Reversal starts on rounded NCL and follows .01,-.002,.005 signed volumetric increments. It is not compared to a false exact NCL reversal curve.

Observed off-NCL pressure refinement ratios are16.05–16.17. Reversal differences are already small and rounding sensitive: observed ratios2.0–12.53. These are observed grid differences, not rigorous uncertainty bounds or evidence that every reversal has fourth-order asymptotics. No Richardson extrapolation is used to manufacture a certified solution. Reversal native integration is a later packet, not part of the proposed nine compression-only native matrix.

## Verification and reproduction

Ten Python groups pass: source NCL/critical-density distinction; actual typed and independent Cartesian full7 rates for both hydrostatic signs/zero, plus off-NCL rates; ideal and corrected composition; Decimal refinement; finite-difference verification of corrected scalar derivative; scalarRK4 comparison/refinement; reversal distinctions; input/domain rejections; retained reference replay and source pins. Supplied dictionaries and model state are not mutated. No native/compiler subprocess or author code is executed.

After installation, from the repo:

```sh
python3 -B -m tools.barodesy2017_isotropic_reference --output /private/tmp/barodesy-isotropic-reference.json
python3 -B -m unittest discover -s tests -p test_barodesy2017_isotropic_reference.py -v
```

For staging, set PYTHONPATH to staged-root:repo and point discovery to staged-root/tests. The machine manifest whitelists only original project code, docs and generated reference evidence; there is no copyrighted source redistribution. Native/Wasm finite-update comparison, experimental calibration, independent human scientific review and public admission remain open.
