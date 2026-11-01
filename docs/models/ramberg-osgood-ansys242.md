# Ramberg–Osgood nonlinear elasticity — ANSYS2024R2

Source-linked three-dimensional reversible isotropic nonlinear elasticity. Unloading retraces loading; there is no yield surface, irreversible plastic strain or cyclic hysteresis. This is the constant-parameter small-strain mechanical law from ANSYS2024R2 Material Reference §4.17, not an original1943 or cyclic extension claim.

The compliance is E epsilon = [(1+nu)+1.5 alpha(q/sigma0)^(n−1)] dev(sigma) + (1−2nu) tr(sigma)I/3, with q=sqrt(1.5 dev(sigma):dev(sigma)). Positive compression for both stress and strain is obtained by reversing both source tensors. alpha is dimensionless and the uniaxial nonlinear strain at sigma0 is alpha sigma0/E.

The shared engine solves this compliance at each endpoint together with epsilon=epsilon_n+de. Both six-component Mandel stress and accumulated total strain are persistent and must be explicitly initialized consistently. Project residuals/transactions are numerical choices, not the vendor algorithm. Fixed spatial axes and zero spin; dry total Cauchy stress. No pore-pressure/drainage inference or finite-deformation host qualification.

Require finite E>0, −1<nu<0.5, sigma0>0, alpha>0, n>1. At zero deviatoric stress the nonlinear term is exactly zero and the tangent is the linear elastic limit. Source fractional exponents are supported mathematically; numerical qualification covers the named cases only. Finite input bounds are software limits, not empirical parameter ranges.

Illustrative defaults E30MPa,nu0.25,sigma0=100kPa,alpha0.5,n5 are not calibration. Initial isotropic compression100kPa corresponds to epsilon_ii=(1−2nu)100kPa/E. Changing parameters requires rechecking this consistency. Temperature-dependent parameters, pseudo-plastic postprocessing, energy output, permanent plasticity and experimental validation are excluded. The source optional energy formula repeats q² in its volumetric term and is inconsistent in hydrostatic loading; original bytes/finding are retained without silently correcting it.

[Primary versioned source](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/ans_mat/ramberg-osgood.html). [Source receipts and equation crosswalk](../ingestion/ramberg-osgood-ansys242/source-v1/README.md). [Prospective qualification](../ingestion/ramberg-osgood-ansys242/PLAN.md). [Delivery ledger](../ingestion/ramberg-osgood-ansys242/DELIVERY.md).
