# Manzari–Dafalias sand (1997): constant yield width

Manzari, M. T. and Dafalias, Y. F. (1997), *A critical state two-surface plasticity model for sands*, Géotechnique 47(2), 255–272. [Original publication](https://doi.org/10.1680/geot.1997.47.2.255).

The exact Atlas variant is `manzari-dafalias-1997-constant-m-be-v1`, definition SHA-256 `28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064`. It uses the original constant-m law and the first published reference-distance option. It excludes the optional evolving-m appendix and the later 2004 fabric model. Atlas supplies backward Euler integration at infinitesimal strain in a fixed frame, with compression-positive effective stress. Physical time does not change the rate-independent response.

## Behaviour and preparation

The state parameter compares current void ratio with the critical void ratio at the current mean effective stress. It controls contraction, dilation and the bounding surface. A translating yield cone records directional plastic loading; pressure-dependent bulk and shear stiffness govern elastic response. Current stress, void ratio and the deviatoric back-stress-ratio tensor determine the persistent state. No reversal-point or accumulated-plastic-strain memory is added.

Prepare all six effective-stress components, void ratio e and all six alpha components. Tensor storage is Mandel order xx, yy, zz, √2xy, √2yz, √2xz. Alpha must be deviatoric. The example begins at isotropic 160 kPa, e = e0 = 0.65 and alpha = 0. This is an illustrative elastic-interior preparation, not an inferred specimen history. The reference parameter e0 stays fixed while current e evolves and must survive a restart.

The supported illustrative comparison uses monotonic drained or undrained triaxial compression, 1% axial strain and 100 steps, at the published example parameters and stated Atlas reference choices. The undrained laboratory imposes zero volume change and reconstructs pore-pressure change; the constitutive law supplies no fluid-transport equation. Oedometer loading, axial stress control and full plastic cycles are outside the exposed qualification scope. Hydrostatic checks are bounded by their retained test inputs.

## Governing law

The following normalized notation follows the visually inspected original equations (1), (6)–(29). A colon denotes tensor contraction, I the identity, and pos(x) = max(x, 0). Define p = tr(sigma)/3, s = dev(sigma), r = s/p, rho = r − alpha and k = √(2/3).

- Critical state: ec = ec_ref − lambda_c ln(p/p_ref); psi = e − ec.
- Elasticity: G = G0 (p/p_at)^a and K = K0 (p/p_at)^a. No optional bulk-pressure floor is selected.
- Yield: f = ‖s − p alpha‖ − k m p ≤ 0. On yield, n = rho/(k m), N = alpha:n + k m.
- Lode interpolation: Jbar = √(rho:rho/2), cos(3 theta) = (√3/2) tr(rho³)/Jbar³, and g(theta,c) = 2c/[(1+c) − (1−c) cos(3 theta)]. The invariant uses translated rho.
- With c = Me/Mc, cb = kbe/kbc and cd = kde/kdc, scalar image radii are ab = g(theta,c) Mc + g(theta,cb) kbc pos(−psi) − m; ad = g(theta,c) Mc + g(theta,cd) kdc psi − m; ac = g(theta,c) Mc − m. Tensor images are alpha_a = k scalar_a n.
- Distances: b = alpha_b − alpha and d = alpha_d − alpha. The selected reference distance is bref = 2 k ab_compression. Hardening h = h0 |b:n|/[bref − |b:n|], requiring the strict positive denominator.
- Dilatancy: D = A d:n, except D = 0 when psi > 0 and d:n < 0. Negative b:n is permitted; no bounding-surface clamp removes softening.
- For constant m, Kp = p h b:n. The loading index is L = [2G n:dev(strain_rate) − K N tr(strain_rate)]/[Kp + 2G − K D N]. Plastic strain rate is pos(L)[n + (D/3)I], stress rate is 2G dev(strain_rate) + K tr(strain_rate) I − pos(L)[2G n + K D I], and alpha_rate = pos(L) h b.

The source gives continuous rate equations. Atlas solves coupled backward-Euler stress and alpha residuals with a temporary plastic multiplier gamma and Fischer–Burmeister complementarity. Its total volume completion is e − e_n + (1+e0) tr(delta strain) = 0. This fixed-e0 infinitesimal mass balance is an explicit project choice consistent with the printed plastic-volume relation. Off yield Atlas uses the unit relative direction; at exactly zero relative direction it uses zero. These discrete and origin conventions require numerical checks and are not attributed to the original authors.

Each trial reads immutable committed state. Success commits stress, e and alpha together; failure restores the full parent state. Temporary gamma is not persistent material memory. Mixed-control trials also restart from the accepted parent. Restart requires the full persistent state, parameters, controls and fixed e0. A single finite step does not promise exact first-yield event location.

## Parameters and limits

The 17 parameters are p_at, p_ref, G0, K0, a, Mc, Me, lambda_c, ec_ref, kbc, kbe, kdc, kde, h0, m, A and e0. Pressure and modulus parameters use Pa; the others are dimensionless. The published 31400 kPa moduli become 31400000 Pa. The critical-state reference is 160 kPa, distinct from Atlas's illustrative atmospheric reference of 100 kPa. Table 1 and the extension-calibration prose supply the remaining example constants. UI parameter bounds do not establish a scientific calibration envelope.

The literal domain requires positive mean effective pressure and void ratio, admissible yield state, deviatoric alpha and bref > |b:n|. No tension extension, denominator clipping, finite rotation law or general fluid transport is supplied. No general finite-element tangent or arbitrary noncoaxial loading claim follows from sampled tensor checks. Experimental validation is separately unassessed; original experimental arrays are not redistributed.

## Evidence and delivery status

[Source receipts and visual equation reconciliation](../ingestion/manzari-dafalias-1997/source-v1/visual-verification.md), [full integration crosswalk](../ingestion/manzari-dafalias-1997/delivery-v1/MODEL.md), [public control scope](../ingestion/manzari-dafalias-1997/delivery-v1/public-control-scope-v2.md) and [delivery ledger](../ingestion/manzari-dafalias-1997/DELIVERY.md) identify the exact source and retained limitations. Original pages were inspected through a normal public viewer and privately captured; this is not a publisher-PDF receipt. Copyrighted source captures remain private.

The retained independent ODE reference, fine-resolution native/Wasm studies, complete-state replay and backend parity support the bounded numerical cases. Earlier coarse-grid accuracy and binary64 finite-difference failures remain retained. The corrected precision fixture has separate actual evidence and review. The [independent agent review](../../catalogue/agent-reviews/manzari-dafalias-1997-constant-m-be-v1-agent-review-v2.json) accepts all nine scientific checklist items for the exact bounded native/Wasm formulation. The approval registry and catalogue include that scope. Normal current-build CI, packaged browser qualification and live delivery remain open gates in the ledger.
