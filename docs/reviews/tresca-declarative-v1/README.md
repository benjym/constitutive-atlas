# Tresca declarative research proposal, v1

This is a proposed schema 0.3 research record, not a catalogue addition or admission. `model.json` names **BK2022v1 associated isotropic elastic-perfect plastic total-stress law with a project-derived backward-Euler metric projection**. The underlying continuum closure and the finite integration algorithm have distinct provenance. No Mohr–Coulomb zero-angle specialization, material kernel, smoothing, yield tolerance or domain relaxation is introduced.

## Source and formulation crosswalk

The primary source is Boulmezaoud and Khouider, [arXiv:2207.12719v1](https://arxiv.org/abs/2207.12719v1). Exact private PDF SHA256: `db7fb284eb9bb622883d5daff6361db37cab912b890b8a24ed99a2428abc7805`, 258014 bytes, 25 pages. This task reuses the integrated source review and certificates; it makes no new PDF inspection claim. The source receipt, original crosswalk, derivation, fixtures and coordinator review are pinned in `source-pins.json`; none of their bytes or gates were changed.

| Source or project derivation | Proposed expression/state |
|---|---|
| pp2–3, Eqs1–8: additive strain, Hooke law, normality and maximum work | Persistent full symmetric `sigma` and `ep`; 12 components, no history reduction |
| p7, Eqs34–37: constant positive Lamé moduli, inverse elasticity | `trial=sigma_n+2*mu*de+lame_lambda*trace(de)*I`; ep residual is the full inverse elastic stress correction |
| pp15–16, Eqs77–81: maximum shear criterion with k>0 | `width=2*k`; initial `max(sigma)-min(sigma)<=width` |
| pp18–21, Eqs89–108: normal cones at repeated spectra | Mathematical continuum support includes repeated stresses; project-derived corner projection uses only the isolated opposite eigenspace |
| Integrated packet, project-derived finite BE minimization | `returned` is the unique projection of trial onto K in the inverse-elasticity metric; branch 0 elastic, 1 upper double, 2 lower double, 3 face |
| Source conventional infinitesimal strain sign, project mapping | Host `sigma=-source_sigma`, `de=-source_strain_increment`, `ep=-source_ep`; compression positive for both stress and strain |

The host uses orthonormal Mandel `[xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz]`, fixed spatial axes and zero spin. This restriction does not claim a finite-rotation update. Stress is **total**, with no pore-pressure state or law. The continuum admissibility is the Tresca cylinder, including hydrostatic tension, zero stress and repeated eigenvalues; it is not an SPD-only soil model. Source positivity lambda>0, mu>0, k>0 is retained. p_ref>0 is a numerical scale, not a source material parameter. These mathematical conditions do not assert that every extreme finite binary64 input avoids intermediate overflow.

## Complete initialization and example

Both sigma and ep must be supplied explicitly. Initial compatible total strain is `ep+C_inverse:sigma`; it is not generally zero. The example uses lambda=30MPa, mu=20MPa, k=50kPa, sigma=100kPa I, ep=0, p_ref=100kPa. It is an uncalibrated numerical example. Its compatible initial total strain is I/1300. Plotted strain increments should start from that preparation. No experimental fit, material identity or laboratory preparation is inferred.

## Spectral guards and boundaries

Only eigenvalue **value-only** operations are eager. The branch comparisons consume their restricted qualifiers. Restricted projectors and differentiable principal values stay inside lazy `select` arms:

- elastic: no projector;
- upper double: only projector_min;
- lower double: only projector_max;
- strict face: projector_max and projector_min plus the matching principal values.

Thus inactive repeated eigenspaces are not evaluated. At exact face/corner transitions, equality is routed to the face arm; at exact yield equality it is elastic. These specify a selected branch derivative, not a unique classical derivative across a nonsmooth transition. The existing generic spectral isolation guards still apply to the selected eigenspace. This proposal does not turn source mathematical admissibility into a promise of numerical support below those gaps.

## Checks and retained blocker

Run `python3 -B check.py --root /absolute/path/to/constitutive-atlas`. It reproduces schema structure, dimensions, value-only qualifiers, 12-component persistent layout, lazy expression routes and C++ expression-string emission. It checks pinned repository source hashes and packet manifest. It does not execute tensors, eigenvalues, material residuals, reference fixtures or compiled code. `expression-emission.json` contains expression strings, not a successful generated model library.

A real generic capability gap is retained: `atlas/model.py` requires the incremental stress binding to equal effective Cauchy sigma. The schema permits total Cauchy stress. Full semantic validation and full compiler generation therefore reject this correct total-stress proposal with `incremental profile requires effective Cauchy stress state sigma`. `checks.json` records both expected failures. A changed checker requires a separately reviewed receipt rather than silently treating this check as a pass. No effective-stress surrogate was generated.

The minimum next implementation scope is generic support for declared total Cauchy bindings, with consistent metadata and downstream stress/observable handling, followed by new source-only checks and separately frozen execution. Merely removing the validator restriction is not consumer validation. Before browser admission, synthetic confinement difference must not be presented as physical pore pressure for this law; any total/effective stress labels and experiment overlays must respect the declared scope.

## Evidence limits

The previous exact rational source-ideal certificates are retained unchanged and not recomputed here. They certify analytical projection/KKT identities at their exact source inputs, not the future stored binary64 Mandel tensors, rounded rotations, 38-column AD or actual driver. This packet sets no numerical accuracy tolerance and makes no public admission claim. See `NEXT_REFERENCES.md` for the independent freeze required before execution.
