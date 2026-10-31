# Independent reduced axisymmetric law

Use Atlas compression-positive axial stress a and equal radial stresses r; q=a−r, p=(a+2r)/3. E,nu,c,phi,psi are decoded from exact stored binary64. K=E/[3(1−2nu)], G=E/[2(1+nu)], L=K−2G/3, s=sin(phi), d=sin(psi), h=2c cos(phi). High-precision trigonometry uses convergent sine/cosine series; no candidate coefficients are used.

Primary source: Sysala and Cermak, arXiv1508.07435v3, exact PDF SHA bf35ee09d500b8e21aabdddbdfac363c5f68368f150890c60343bc62447c83ca; pp7–13 Eqs3.1–3.6 and4.8–4.29, H=0. Readable transcription is repository docs/ingestion/mohr-coulomb/FORMULAS.md. [Primary preprint](https://arxiv.org/abs/1508.07435v3). This reduction implements its finite return, not a differential integration approximation.

For axial/radial strain increments x,y, elastic stress increments are

`da=(L+2G)x+2Ly`, `dr=Lx+(2L+2G)y`.

Compression q>=0 yields F=(1−s)a−(1+s)r−h; extension q<=0 yields F=(1−s)r−(1+s)a−h. Compression plastic flow per unit multiplier is `(u,v)=(1−d,−(1+d)/2)`; extension is `(−1−d,(1−d)/2)`. Its trace u+2v=−2d, so plastic volume is negative under positive multiplier. These are the grouped edge subgradients of the full3D law, with the radial degeneracy preserved.

For prescribed x,y, form elastic trial (at,rt). If trial is admissible return it elastically. Otherwise choose compression/extension from trial q, solve the single affine yield equation gamma=Ftrial/[n·C:(u,v)], and subtract gamma*C:(u,v). The denominator is positive by the source strict domain. Check returned order; if the root passes the hydrostatic junction return apex a=r=−c cot(phi). Apex multiplier is `(papex−ptrial)/(2Kd)`. For a nonhydro trial reaching apex, recover u,v from `(trial−apex)/gamma=C:(u,v)`; do not assume its subgradient is isotropic. Trace/bounds/complementarity determine the admissible apex subgradient.

Protocol0: x=stored caller increment, y=0.

Protocol1: r fixed at the initial100kPa. The two axial plateaux are

`ahi=[(1+s)r+h]/(1−s)`, `alo=[(1−s)r−h]/(1+s)`.

For prescribed x, set a_new=clamp(a_old+E*x,alo,ahi). Elastic axial strain is xe=(a_new−a_old)/E and plastic axial strain xp=x−xe. Radial strain is `−nu*xe−(1+d)/(2(1−d))*xp` in compression, or `−nu*xe−(1−d)/(2(1+d))*xp` in extension. Multipliers are xp/(1−d) or xp/(−1−d). This handles reversals and complete crossing from one plateau to the other in one increment, with no outer Newton or copied spectral return.

Protocol2: x=caller increment, y=−x/2. Elastic mean stress stays constant; q_trial=q_old+3Gx. Plastic mean stress increases by2Kd*gamma. It is not an elastic/constant-mean-stress model after yield.

Protocol3: caller increment is prescribed deviatoric stress change dq under zero strain volume. Set q_new=q_old+dq. At p_old test source yield; if admissible keep p_new=p_old, x=dq/(3G). Otherwise compression gives

`p_new=[(1−s/3)q_new−h]/(2s)`, `gamma=(p_new−p_old)/(2Kd)`, `x=[dq+G(3−d)gamma]/(3G)`.

Extension gives

`p_new=[−(1+s/3)q_new−h]/(2s)`, `x=[dq−G(3+d)gamma]/(3G)`.

In both cases y=−x/2 and recover a=p+2q/3,r=p−q/3. This algebraically inverts the monotone finite axisymmetric constitutive map, not the host's finite-difference Newton controller.

Protocol4: x=y=caller increment. From an isotropic stress state q remains0; elastic p changes by3Kx. Large expansion can reach the tensile apex and is then plastic; an arbitrary cyclic isotropic path must not be presumed elastic.

For every endpoint check elastic trial minus gamma times elastic flow, source yield/nonnegative multiplier/complementarity, flow trace/subgradient bounds, returned compression/extension ordering, and protocol constraints. Pore-pressure display for protocols2/3 is initial radial stress minus current radial effective stress; it is an algebraic host diagnostic, not a separately evolved state.

Only the actual binary64 caller delta is consumed. A high-precision subtraction of stored targets differs from the stored rounded caller subtraction; the input must preserve both. Source references do not reproduce libm sine as a hidden substitute for the real caller sequence. No backend acceptance tolerance is set by this reference precision check.
