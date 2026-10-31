# Mašín 2014 anisotropic clay: source dossier

Research source packet only; no model admission, complete kernel, scientific validation, or author-code equivalence is claimed. All page numbers below are **one-based PDF manuscript pages**, not final journal pages.

## Exact identity and acquisition

David Mašín, *Clay hypoplasticity model including stiffness anisotropy*, Géotechnique 64(3),232–238,2014, [DOI10.1680/geot.13.P.065](https://doi.org/10.1680/geot.13.P.065). The publisher records acceptance28November2013 and issue1March2014. This is distinct from the 2013 explicit-ASBS host DOI10.1007/s11440-012-0199-y and the Mašín–Rott anisotropic-elasticity review DOI10.1007/s11440-013-0271-2.

Acquired31October2026 from the [author's Charles University site](https://web.natur.cuni.cz/uhigug/masin/download/Masin_Geot14-pp.pdf):1095956bytes,16pages,SHA256`2eb8598297e3ac9cf245161f56674d6cef622b35fc612adc89dc129568b55202`. The title page identifies a submitted Technical Note dated26November2013. It is an **author manuscript**, not verified final publisher text. [Author bibliography](https://web.natur.cuni.cz/uhigug/masin/bib/DMbib.htm) warns that preprints can differ from final publications. Current publisher article and PDF links redirect to an access-restricted abstract; no account/purchase was used. The discovered final-PDF route is https://www.emerald.com/jgeot/article-pdf/64/3/232/2529090/geot_13_p_065.pdf . Filename search in Downloads for clay/masin/065/anisotrop/geot found no matching PDF; generic filenames were not exhaustively identified.

Visually inspected complete manuscript pages2–6,9–11,13. Private PDF, extracted text and renders must remain excluded from repository/public packet.

## Host and scope

The 2013 explicit-ASBS host supplies density/asymptotic direction machinery. Eqs2–15 replace its linear tensor and barotropy factor; AppendixA also changes the pyknotropy exponent. Setting all anisotropy ratios to1 restores the scaled isotropic **linear action**, but does not automatically restore the entire2013 model: p3footnote2 and p10 explicitly distinguish alpha_f=2 from the proposed Eq49.

Separate identities are required for (a) anisotropic base law Eqs2–15,34–50 and (b) the same law coupled to this manuscript's AppendixB IGS Eqs51–57. Do not use arbitrary ISA/GIS/IGS variants interchangeably. The base is rate independent, three-dimensional symmetric stress plus void ratio. No strength-fabric evolution is specified. Very-small-strain predictions require the AppendixB overlay (p3,Eqs16–19).

## Typed quantities and storage

| Quantity | Shape/unit | Role/source |
|---|---|---|
| effective stress | full symmetric6,Pa | retained physical state; Eq1/34 |
| e | scalar,1 | retained physical state; p10; inherited mass balance, not explicitly restated here |
| n | unit vector3,1 | material-plane normal, p2 Eq3; not a principal-stress direction |
| P=n⊗n | symmetric6,1 | derived immutable orientation/projector; no independent evolving fabric law established |
| phi_c,lambda*,kappa*,N,nu_pp | scalars,1 (angle in radians in implementation) | five base constants, p10; nu_pp replaces isotropic nu |
| alpha_G,alpha_E,alpha_nu | scalars,1 | independent anisotropy ratios Eqs9–11; respectively Gpp/Gtp,Ep/Et,nu_pp/nu_tp |
| a1…a5,Am,fs,fd,pe,dA,d | derived typed scalars/tensors | no additional retained history; Eqs4–8,14–15,34–50 |
| a,alpha_f | scalars,1 | source suggests a=.3; alpha_f from49–50 or explicitly selected optional calibrated parameter, p10; alternatives must have separate identities |
| delta | full symmetric6,strain dimensionless | additional physical memory only for AppendixB, Eqs53–55; no deviatoric projection |
| R,beta_r,chi,m_rat,Ag,ng | scalars,1 | AppendixB independent inputs. R appears Eq53/Table1 although the p11 parameter-list sentence omits it |
| rho,delta_hat,mR,mT | derived scalar/symmetric | rho=norm(delta)/R; mR state-dependent Eq56, mT=m_rat*mR Eq57; do not store them as independent history |

Base retained scalarized state is7; IGS adds6 for13. Orientation needs explicit preparation metadata, not a speculative evolving state. Fixed global n or P is defensible only with an explicitly named zero-spin/fixed-material-plane research scope. Finite-rotation transport of n/P is not specified by an evolution equation in the inspected paper; Jaumann stress/delta notation alone does not settle it.

## Exact contraction and sign mapping

For a symmetric D and P=n⊗n, Eqs2–3 imply the derived action

`L:D = a1*D + a2*I*tr(D) + a3*(P*tr(D)+I*(P:D)) + a4*(P D+D P) + a5*P*(P:D)`.

The factor1/2 multiplying a1 in Eq2 compensates the four-term product definition in Eq3; dropping it doubles that term. The independent test implements the original four-index definition and a separate matrix action. In-plane/transverse pure shear responses have ratio alpha_G. P is unchanged by n→-n; rotating BOTH P and D rotates the action.

For Atlas compression-positive stress Sigma and strain rate E, source stress T=-Sigma and D=-E. At zero spin negate the source stress RHS to obtain Sigma RHS. If AppendixB used, store H=-delta, preserving the loading scalar delta_hat:D=H_hat:E, and negate the source delta objective rate. Inherited incompressible-grain closure is edot=-(1+e)tr(E). This closure is a host dependency, not a newly printed2014 equation.

No generic fourth-order DSL primitive is mathematically required for this action. Existing `tensor_square` permits the symmetric mixed product by polarization: `(P+D)^2-P^2-D^2=PD+DP` when dimensions match; here P dimensionless and D has strain-rate dimension, so **do not use that literal dimensionally invalid sum** in a rate-dimensional schema. Instead construct a dimensionless normalized direction and restore rate magnitude, or expand fixed-axis components with explicit units. Production implementation needs a typed, independently checked action strategy. Scalar-only parameter schema currently cannot directly encode a symmetric orientation parameter; a validated preparation projector or explicit scalar axis-component parameters is a design choice. Verify rank-one,unit trace,idempotence; never silently normalize an invalid projector.

## Important unresolved printed normalization conflict

On p4 Eq17, `Gtp0 = mR * [9p/(2Am)] * (1/lambda*+1/kappa*) * [alpha_E/(2alpha_G)] * B`, with `B=1-nu_pp-2alpha_E*nu_pp^2/alpha_nu^2`. Eq18 defines `Gtarget=pr*Ag*(p/pr)^ng`.

Printed Eq19, repeated Eq56 on p11, gives `mR = Gtarget * [4Am*alpha_G/(2p*alpha_E)] * [lambda*kappa*/(lambda*+kappa*)] / B`.

Substituting the printed expressions gives **Gtp0=4.5*Gtarget**. Algebraic inversion of17 would instead put9p in19's denominator, but this packet selects no correction. The retained scalar diagnostic records this discrepancy, and its passing regression asserts the conflict, not equation consistency. Exact publisher comparison/corrigendum or source-author resolution is required before a source-faithful AppendixB implementation can choose a normalization.

## Initialization, boundaries and integration gates

Supply initial full stress,e,orientation and,when used,delta explicitly. Eq54 defines delta_hat=0 at delta=0; Eq52 uses the nonpositive branch at zero loading scalar; Eq55 then gives delta_rate=D. No automatic delta=0 preparation is established for the London Clay consolidation history. No reset/reversal event writes or numerical old/new lag are printed: branch changes are instantaneous rate evaluations. Do not introduce caller-increment resets.

Require positive p/pr,1+e,lambda*,kappa*,R; finite coefficients and nonzero denominators alpha_G,alpha_nu,Am; physically admissible stiffness should be checked independently of mere denominator nonzero. Eq49 needs a positive logarithm argument (suggested lambda*>kappa*>0 and positive friction angle do not remove every numerical restriction). AppendixA inherits stress-invariant,hydrostatic-Lode and d-normalization branch issues of2013; do not clip them silently. Norm(delta)<=R is an intended memory surface, but finite-step overshoot/integration control must be explicit; source does not supply a complete integration algorithm or tolerance/subdivision policy.

The LondonClay example has e=.69 (p5),IC p323kPa and AC printed `p=323kPa and p=-166kPa` (p6). The second p label is internally ambiguous; do not silently relabel it q. Tables1–2p13 give the selected calibration, not universal defaults. Eqs30–31 p5 use alpha_E=alpha_G^(1/.8),alpha_nu=alpha_G for the reported empirical reduction; full independent calibration is another variant. Complete HCA schedules,consolidation/IGS memory and digitizable experimental arrays require Nishimura/Gasparre sources before replay can be claimed.

## Bounded next steps

1. Resolve Eq17/19/56 normalization and final/manuscript differences before coupling IGS.
2. Independently review Eqs4–8,14,49 signs/powers and instantiate a base-law-only typed fragment with explicit orientation and exponent choice; compare to the matrix witness.
3. Verify hydrostatic/zero-rate/Lode continuations separately; add inherited e closure and full rollback only when the rate fragment is settled.
4. For AppendixB select explicit R,Ag,ng,m_rat,beta_r,chi and preparation memory; test zero-memory/loading/reversal/covariance and pressure scaling. No author implementation reuse/license/version pairing is established by the statement that code is freely available.

The six pure Python test groups are source algebra diagnostics only: tensor contraction,rotation/sign of plane normal,shear ratio,isotropic fsL limit,changed density exponent, and retained printed mR discrepancy/pressure homogeneity. They are not experimental validation or integration evidence.
