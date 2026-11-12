# Calibration arithmetic v2 — before observation

Candidate v1 and both failed observations are retained unchanged. V2 changes floating-point evaluation order, not the source reconciliation, full thirteen-state law, domain, parameters, initial state or numerical acceptance bounds.

The exact identities are `a1=r*B`, `mR*fs=2*Gtarget*g/a1`, and `mT=mrat*mR`. Evaluate the dimensionless action `L/a1` by its five coefficient ratios, with the identity term applied directly. Set `calibrated_LE=2*Gtarget*g*(L/a1):de` and `calibrated_Lh=2*Gtarget*g*(L/a1):h`. These equal `mR*fs*L:de` and `mR*fs*L:h` respectively. Then the linear blend is `(w*mrat+1-w)*calibrated_LE`; the positive correction is `w*(fs*L:h-mrat*calibrated_Lh)*q`; the nonpositive correction is `w*(1-mrat)*calibrated_Lh*q`. The nonlinear positive correction and the memory/void rates are unchanged. Every tensor action remains declarative, using the common compiler.

This avoids multiplying the independently rounded pressure-calibrated mR and fs back together, and preserves the exact identity coefficient of L/a1. The three original high-stiffness failures are retained rather than accepted under a larger error allowance. All original cases and error bounds remain in the successor qualification.

The six malformed spherical-memory inputs are retained as failures of the original study. Their explicitly prepared, slightly interior full-state replacements were independently frozen before reference results. They supplement the original source-state coverage; exact-axis rho1 boundary cases remain required. No runtime projection, clipping, parameter exclusion or tolerance change is introduced.

New candidate bytes and the exact successor observation protocol must be frozen before observing v2 rates. An independent algebra/source review must assess this evaluation-order change, and all finite-path/backend/app/admission gates remain required.
