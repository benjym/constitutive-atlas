# Independent source interior-Lode reference v1

NUM-md1997-interior-lode-v1 owns this new directory. The original parent reference files and manifest are unchanged. Policy was frozen before the first source reference execution; no compiled results were observed or artifacts executed by this worker.

## Derivation from original equations

Original Eq16 uses the translated ratio rbar=r-alpha. Set a fixed trace-free unit tensor n with three distinct eigenvalues; alpha=beta*n and r=x*n. Then yield Eq9 requires x-beta=S*m with S=sqrt(2/3). Since this difference is positive, rbar has the same fixed direction n. For n:n=1, Eq16 reduces to cos(3theta)=sqrt(6)*tr(n^3). This expression is explicitly evaluated from the rotated matrix, independently of the angle used to construct it.

Source Eq17 gives g=2c/[(1+c)-(1-c)*cos(3theta)]. Define three distinct source g values using c=Me/Mc=1, cb=kbe/kbc=2/3.975, cd=kde/kdc=.07/4.2. Original Eqs18,20,21 then imply scalar image projections beta_b=S*(g_M*Mc+g_kb*kbc*positive_part(-psi)-m), beta_d=S*(g_M*Mc+g_kd*kdc*psi-m), with psi=e0-ec(p). The first source b_ref choice is 2*S*(Mc+kbc*positive_part(-psi)-m), not a direction-dependent substitution. Thus b:n=beta_b-beta, h=h0*abs(beta_b-beta)/(b_ref-abs(beta_b-beta)), D=A*(beta_d-beta), with the source zero-dilation override when psi>0 and D<0.

Impose total strain epsilon=t*n. Its trace is zero, so the source small-strain void ratio relation gives e'=0. Eq24 gives beta'=L*h*(beta_b-beta), and Eq13 gives p'=-K*D*L and deviatoric stress amplitude derivative (p*x)'=2G*(1-L). Differentiated consistency gives x'=beta'. Combining the two amplitude derivatives produces

`L = 2G / [p*h*(beta_b-beta) + 2G - K*D*x]`.

This reduction was re-derived from the source stress-rate and consistency equations; it was not copied from the production candidate or evaluated through Atlas. The implementation integrates p, beta, and x separately. It computes x' from the independent stress-amplitude equation and checks yield drift, providing an internal consistency check against the beta equation. Full tensors are reconstructed using the integrated x: sigma=pI+p*x*n and alpha=beta*n.

Eigenvalues are S*cos(theta+2k*pi/3), k=0,1,2. Rotating with Q=Rz(.37)*Ry(.51)*Rx(.23) yields a genuinely three-dimensional Mandel direction with all six components nonzero. Every case retains Q, eigenvalues, n, angle, independently recovered cos3theta and all three g factors. These are interior angular checks, not axisymmetric endpoint tests or mere covariance comparisons.

## Execution and result

Run `python3 docs/ingestion/manzari-dafalias-1997/delivery-v1/reference-v1/interior-lode-v1/reference.py` from repository root. It uses standard Python only. All six dense/loose and interior-angle cases pass the prospective refinement and source-consistency gates. Maximum coarse/fine full stress difference is 0.000018947 Pa. Each case contains six full strain/stress/backstress/void-ratio checkpoints from t=0 through .01. `requests.json` is a downstream target description, not a claimed Atlas request-schema file. Pressure is computed in kPa and serialized in Pa.

This strengthens the earlier axisymmetric source oracle with interior Lode dependence and shear-bearing full tensor states. It does not independently qualify arbitrary changing Lode directions, noncoaxial plastic histories, full plastic reversals or measured experimental data. Native/Wasm comparison and independent scientific review remain parent tasks.
