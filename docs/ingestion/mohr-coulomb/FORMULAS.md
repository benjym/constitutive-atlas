# Source-located complete H=0 branch specialization

All notation here initially follows the exact pinned preprint's tension-positive convention. PDF and printed page numbers coincide. These equations are algebraic specializations/notations of source Eqs3.1-3.6 and4.8-4.29, not an extension of its parameter domain. Define s=sin(phi), d=sin(psi), h=2*c*cos(phi), K=E/[3(1-2nu)], G=E/[2(1+nu)], L=K-2G/3. Use positive K,G,c and 0<phi,psi<pi/2.

## Constitutive definition

Source p7 Eqs3.1-3.5:

- sigma=C:(eps-eps_p), with C:X=2G*X+L*tr(X)*I.
- F(sigma)=(1+s)*tau_max-(1-s)*tau_min-h <=0.
- g(sigma)=(1+d)*tau_max-(1-d)*tau_min.
- eps_p_dot belongs to lambda_dot*partial(g)(sigma), lambda_dot>=0 and lambda_dot*F=0.
- H=0 makes cohesion constant. The source's auxiliary epsbar_p_dot=2*cos(phi)*lambda_dot does not affect stress and can be retained only as a named diagnostic.

At a smooth face the ordered source flow eigenvalues are (1+d,0,-1+d). At an edge/apex use the full subdifferential, not an arbitrary single face. Source p8 Eq4.5 and p9 Eq4.8 characterize a common coaxial eigenbasis and flow values v_i by

`1+d >= v1 >= v2 >= v3 >= -1+d`, `v1+v2+v3=2d`,
`(v1-1-d)*(r1-r2)=0`, `(v3+1-d)*(r2-r3)=0`.

Here r1>=r2>=r3 are returned source principal stresses. The finite update (p7 Eq3.6) is `sigma=sigma_trial-gamma*C:v`, gamma>=0, F<=0, gamma*F=0. For constant C, sigma_trial=sigma_n+C:de. When Ftrial<=0 choose gamma=0 and return the unchanged trial tensor (p8 Eqs4.1-4.2).

## Plastic branch coefficients and intervals

Let t1>=t2>=t3 be trial principal stresses in source signs. Define (p10 Eq4.13, p10 Eq4.18, p11 Eq4.23)

`g_sl=(t1-t2)/[2G(1+d)]`, `g_sr=(t2-t3)/[2G(1-d)]`,
`g_la=(t1+t2-2t3)/[2G(3-d)]`, `g_ra=(2t1-t2-t3)/[2G(3+d)]`.

Set A=2*L*d. All branch denominators below are positive in the selected source domain, including when L is negative (their equivalent forms use positive K,G). The piecewise scalar q functions decrease continuously; source Lemma4.2 and Theorem4.2 pp12-13 establish the unique admissible return. For H=0, each branch q is affine and its unique root is the explicit gamma below; only the branch whose root satisfies its interval is admissible.

| Return | gamma numerator | gamma denominator | Exact admissible interval |
| --- | --- | --- | --- |
| Smooth face | (1+s)t1-(1-s)t3-h | 2*A*s+4G(1+d*s) | 0<gamma<min(g_sl,g_sr) |
| Source left edge | (1+s)(t1+t2)/2-(1-s)t3-h | 2*A*s+G(1+d)(1+s)+2G(1-d)(1-s) | gamma>0 and g_sl<=gamma<g_la |
| Source right edge | (1+s)t1-(1-s)(t2+t3)/2-h | 2*A*s+2G(1+d)(1+s)+G(1-d)(1-s) | gamma>0 and g_sr<=gamma<g_ra |
| Apex | (2/3)*s*(t1+t2+t3)-h | 4K*d*s | gamma>0 and gamma>=max(g_la,g_ra) |

Source locations: face Eqs4.9-4.13 pp9-10; left Eqs4.14-4.18 p10; right Eqs4.19-4.23 pp10-11; apex Eqs4.24-4.27 p11. Equality at the face upper limit belongs to the appropriate edge; equality at the edge upper limit belongs to the apex. Degenerate empty edge intervals do not generate a branch. The source's affine q/branch conditions suffice without guessing faces until one happens to pass.

Returned principal stresses:

- Face: `(t1-gamma*(A+2G(1+d)), t2-gamma*A, t3-gamma*(A-2G(1-d)))`.
- Left: `r1=r2=(t1+t2)/2-gamma*(A+G(1+d))`, `r3=t3-gamma*(A-2G(1-d))`.
- Right: `r1=t1-gamma*(A+2G(1+d))`, `r2=r3=(t2+t3)/2-gamma*(A-G(1-d))`.
- Apex: `r1=r2=r3=(t1+t2+t3)/3-2K*d*gamma=c*cot(phi)`.

As a denominator check, the smooth denominator equals `4K*d*s+4G*(1+d*s/3)>0`. Left/right denominators also equal their positive-G parts plus4Kds, after combining the -8Gds/3 contribution; for example the left G factor is `3-s-d+d*s/3`, positive for s,d in(0,1). The right factor is `3+s+d+d*s/3`. Apex denominator is strictly positive only with the selected strictly positive d,s; do not use it at zero dilation/friction.

Reconstruct in trial eigenspaces (Lemma4.1 p9). Face uses sum(r_i*P_i). Left uses `r1*(I-P3)+r3*P3`; right uses `r1*P1+r3*(I-P1)`; apex is `r1*I`. Source pp14-15 Eqs5.4-5.11 supply matching grouped-projector tangent forms. No individual projector inside a repeated eigenspace is physically unique; the grouped expression is.

## Compression-positive Atlas conversion

Let S=-sigma_source and Eps=-eps_source. If Atlas descending compression principal values are S1>=S2>=S3, then source ordered eigenvalues are tau1=-S3,tau2=-S2,tau3=-S1. Therefore

`F_Atlas(S)=(1-s)*S1-(1+s)*S3-h`,
`g_Atlas(S)=(1-d)*S1-(1+d)*S3`.

For a given stored Atlas trial tensor, a safe derivation evaluates the source formulas on `-S_trial`, reconstructs its returned source tensor and negates the result. Alternatively derive ascending/descending source scalars from Atlas extrema with the explicit reversal above. Merely negating eigenvalues without reversing order is wrong. The source left edge (tau1=tau2) corresponds to the repeated **lower** compression pair S2=S3; the source right edge corresponds to repeated **upper** compression pair S1=S2. Labels must retain their coordinate identity in diagnostics.

On the smooth Atlas face the flow in descending compression principal coordinates is `(1-d,0,-1-d)`; its trace is -2d, so plastic dilation is negative compression-positive volumetric strain. The source tensile apex maps to S=-c*cot(phi)*I, not a positive compressive cap. Add no extra tension cutoff or pressure positivity gate.

## Tangent boundaries

Source Section5 pp14-16 separates the open elastic/face/edge/apex regions and discusses generalized derivatives on their boundaries. For H=0, Eq5.11 gives zero stress tangent in the interior apex region. For a distinct-spectrum smooth face restricted to fixed principal directions, differentiate the affine return: `dr/dt = Identity - (C:v) outer (1+s,0,-1+s)/D_face`. This principal-direction formula omits rotation of trial eigenspaces; full tensor tangents require projector derivatives. Repeated trial pairs on a grouped edge are legitimate inputs, while arbitrary eigenvector derivatives there are not unique. No generic semismooth AD policy is selected by this packet.
