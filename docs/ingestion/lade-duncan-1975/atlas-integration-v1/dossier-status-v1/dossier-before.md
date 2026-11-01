# Lade–Duncan 1975: midpoint-elastic local Eq. 19 realization

Exact definition: `models/research/implicit-path/lade-duncan-1975-midpoint-elastic-eq19-gap-v4.json`, SHA-256 `120b93f319543518b2b87221ab7457afaca2a1fb5de78af901276e8e89a22e63`.
This is the original full elastoplastic cohesionless-soil formulation, with
Atlas numerical choices. The 1977 curved-surface extension is a distinct law.
Current status is unapproved integration candidate; the
[delivery ledger](../ingestion/lade-duncan-1975/DELIVERY.md) records actual gates,
retained failures and eventual approval/browser status.

P. V. Lade and J. M. Duncan, *Elastoplastic Stress-Strain Theory for Cohesionless
Soil*, JGED 101(10), 1037–1053 (1975),
[DOI](https://doi.org/10.1061/AJGEB6.0000204). The supplied seventeen-page original
was read visually. Its private receipt, page/equation inventory, Table 1,
convention decisions and rights are in the
[readable-source packet](../ingestion/lade-duncan-1975/delivery-v1/supplied-original-v2/README.md).
The copyrighted PDF is retained privately and is not a website asset.

For normalized stress s=σ/pₐ, f=I₁³/I₃; hydrostatic f=27. Source equations use
k₂=A f+27(1−A), ḡ=I₁³−k₂I₃ and the fixed-k₂ flow derivative
N̄=3I₁²I−k₂ cof(s). The elastic modulus is E=K_ur pₐ s_minⁿ;
a=M pₐ s_minˡ and dWᵖ=a df/[1−r_f(f−fₜ)/(k₁−fₜ)]² on new loading.
The numerical plastic multiplier is (dWᵖ/pₐ)/(3ḡ); its inactive branch is zero.
Unloading/reloading below the prior loading maximum is elastic.
The exact declarative definition and source crosswalk retain all branches,
initial checks and restrictions; these summaries do not replace them.

Compression-positive Mandel order is xx, yy, zz, √2xy, √2yz, √2xz.
Stress is small-strain, fixed spatial Cauchy stress, mechanically interpreted
as total stress under a zero-pore embedding. There is no pore-pressure law,
finite-rotation objectivity or physical-time dependence. Laboratory constant
volume is a kinematic control and does not imply a predicted pore pressure.

Persistent state is six stress components (Pa), a dimensionless signed history
gap and plastic work (Pa). Decode H=max(fₜ,f+max(gap,0)). Increments update H
monotonically; exact zero increments preserve the raw carrier. The carrier is
not deviator stress q. Changing parameters or initial state starts a new
history; a complete saved request/result is required for reproducible replay.

This realization samples E at the tensor arithmetic midpoint, and plastic
flow/loading history at the endpoint. It uses generic residual Newton solves,
implicit step doubling and a positive-pressure-relative stress error metric.
Successful two-half endpoints are committed; failed caller increments retain
all of the parent state. Warm initial guesses are always validated against the
actual parent; reused outer transactions require complete bitwise-identical
inputs. These are Atlas numerical choices, not a source-prescribed algorithm.
Generic explicit-fused linear arithmetic is under a distinct prospective
repair study; it does not alter the declarative law or relax numerical gates.

Positive-definite stress and the closed numerical checks f≤k₁ and H≤k₁
bound this realization. A boundary endpoint permits no post-failure continuation. Source-derived
hydrostatic/proportional unloading reaches zero pressure in finite strain;
those paths require rejection at the boundary. Convex midpoint-quadrature
arguments are bounded to that family, not a general 3D event theorem. No
post-failure continuation, broad parameter envelope, finite-strain material
claim, calibration or experimental validation is inferred.

The two named source presets use Table 1 dense/loose parameters at 60 kPa
isotropic initial stress, H=fₜ and Wᵖ=0. pₐ=101325 Pa and νᵢ=0 are explicit
conventions of this realization. Other parameter combinations are exploratory;
rectangular schema limits are not an experimentally qualified material range.
The schema example initial state is 100 kPa isotropic, signed gap13 and Wᵖ=0;
its examples_only initialization policy is separate from the explicitly
prepared 60 kPa named source studies. Those studies do not automatically
qualify every schema-default request.
Named browser examples request a fixed-lateral-stress path to .005 axial
strain with 400 caller increments and explicit eight-setting numerical data.

The maintained versioned generic profile is under
`cpp/profiles/implicit-path-v1/`, with normal compiler generation through
`tools/generate_implicit_path.py` and `cmake/implicit-path-v1/`. Its complete
four-model compiled catalogue includes historical regression witnesses;
public routing exposes this Lade definition alone. Profile packaging requires
exact model, source, generated catalogue, qualified artifact and independent
review identities. The current implementation and UI remain prospective until
the outstanding aggregate backend gate, independent approval and actual
packaged-browser tests pass.
