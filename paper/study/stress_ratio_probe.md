# A compression task that distinguishes yield-surface choices

Status: conditional paper-side derivation and proposed experiment design, pending source-equation and independent review. No model is implemented or admitted by this note.

The [SANISAND lineage note](source_notes/sanisand-lineage-2004-2008.json) separates three publications that share a family name but address different mechanisms. Its evidence is publisher abstracts, not complete equation review. The following calculation concerns an explicitly assumed open-cone yield condition; it does not certify any complete published formulation or numerical implementation.

## Assumed yield geometry

Use compression-positive effective stress, with

\[
p=\tfrac13\operatorname{tr}\boldsymbol\sigma>0,\qquad
\boldsymbol s=\boldsymbol\sigma-p\boldsymbol I,\qquad
f=\|\boldsymbol s-p\boldsymbol\alpha\|-c p\leq0,
\]

where the norm is the Cartesian tensor norm, \(c>0\) is fixed, and the deviatoric backstress ratio \(\boldsymbol\alpha\) remains fixed during elastic loading. Assume a conventional loading rule that gives zero plastic multiplier strictly inside this surface and no other active plastic mechanism. Numerical pressure floors, stage changes and explicit state resets are outside this calculation.

For a proportional stress path \(\boldsymbol\sigma(t)=a(t)\boldsymbol\sigma_0\), with \(a(t)>0\),

\[
p(t)=a(t)p_0,\quad \boldsymbol s(t)=a(t)\boldsymbol s_0,\quad
f(t)=a(t)f_0.
\]

Thus a strictly interior initial state remains interior for every finite positive scale factor. Increasing pressure along this path cannot activate this assumed yield mechanism. The result concerns the full tensor stress ratio \(\boldsymbol s/p\); constant scalar \(q/p\) with rotating principal axes does not satisfy that premise. At the yield boundary, tangency and consistency require a separate analysis; the strict-interior proof does not resolve that case.

In particular, isotropic loading with \(\boldsymbol s_0=\boldsymbol0\) and \(\boldsymbol\alpha_0=\boldsymbol0\) has \(f=-cp<0\). It generates no plastic volumetric strain through this mechanism. Elastic compression, changes in void ratio and pressure-dependent stiffness may still occur. A density change during loading alone therefore does not demonstrate plastic compression.

## Observations and controls for a future panel

| Item | Required declaration |
| --- | --- |
| Loading | Isotropic or proportional effective-stress pressure excursion, with fixed principal directions, remaining at positive pressure |
| Initial state | Full stress, void ratio, preparation/history and location relative to the declared yield surface |
| Measurements | Volume/deformation through loading and unloading; stress controls and their uncertainty |
| Comparison | An open-cone variant against a source-reviewed alternative allowing plastic compression on the selected path |
| Outcomes | Loading response, unloading response and residual deformation at matched stress, with numerical refinement |
| Qualifications | Seating, apparatus compliance, grain crushing, drainage, localization and other possible causes of irreversibility |

If all elastic state equations are reversible along this one-dimensional path, unloading to the same pressure recovers the elastic deformation. That is an additional constitutive assumption, not a consequence of cone geometry alone. Residual deformation can help test a plastic-compression hypothesis, but does not uniquely identify a cap mechanism. Review the elastic law and other active mechanisms before drawing that conclusion.

An oedometer task is different: zero lateral strain does not prescribe constant stress ratio. Its evolving lateral stress may activate plasticity even in an open-cone model. The existing KFS oedometer development evidence must therefore not be described as an isotropic-compression discriminator. The ISO series is a possible discovery route; its responses remain unassigned and must not be inspected until the reservation policy and task protocol are updated.

## Consequence for the paper

A family label or total parameter count cannot tell whether an added mechanism is probed by a dataset. Match each proposed extension comparison to loading controls that activate its intended mechanism and to observations sensitive to that mechanism. Keep constant-ratio compression, reversal-induced contraction and loading-direction dependence as separate questions until the exact formulations and available experiments justify combining them. This note proposes a task; it neither chooses a preferred variant nor supplies an evaluation result.
