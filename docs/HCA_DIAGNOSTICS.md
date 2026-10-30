# HCA-2005 bounded arithmetic diagnostics

Status: Python-only research diagnostics, 2026-10-31. No candidate/model status changes, constitutive solver, host adapter, polarization update or executable-admission claim. This packet follows [the source contract](reviews/hca-2005-contract.md); source conflicts and remaining gates there remain open.

Source: Niemunis, Wichtmann & Triantafyllidis (2005), [DOI](https://doi.org/10.1016/j.compgeo.2005.03.002), [author manuscript](https://www.torsten-wichtmann.de/paper/journal/2005-CG-a-high-cycle-model.pdf), SHA-256 `ecf856384f0c77d5440a2aeb28c96420e609ed7cefffab9f19a0b8e141a796ce`. Locators below use author-manuscript PDF pages; journal/manuscript equivalence remains unverified. No source PDF, extracted text or page render is redistributed.

## Sampled-loop interface and project policies

`sampled_amplitude(samples, basis='atlas_mandel', rank_relative_tolerance=1e-12)` accepts 2..128 ordered samples of all six finite symmetric Mandel logarithmic-strain components. The returned amplitude operator is 6×6, not a six-component strain tensor. Input order, repeated points and drift are preserved; the tool does not close, filter, detrend or sort a loop. There is no automatic physical interpretation of the samples' ordering or time. It applies the source p.10 Eqs.(21)–(23) farthest-pair/projection construction to the **supplied finite point set**, not a continuous-extrema solver or PCA.

Each stage finds a globally farthest sampled pair, takes half its distance as the next radius and projects every residual point onto the perpendicular hyperplane. Directions are reorthogonalized twice. The source radii are returned in extraction order `R_6, R_5, ...`; the retained operator is the sum of radius-weighted direction outer products. Its Frobenius norm is the scalar amplitude. The source optional roughly10% truncation is not used.

Project numerical policies, not source equivalence claims:

- Coordinates are translated by the first sample and scaled before distance arithmetic. Translation reduces cancellation in projection but cannot recover differences already lost in the supplied floats. Nonfinite differences, unrepresentable positive radii or overflowing outputs reject.
- Exact floating-point maximum-distance ties are all reported by caller indices; the lexicographically earliest pair is selected. Direction sign uses the largest-magnitude component, with first component index breaking equal magnitudes. Signs do not affect direction outer products.
- Nearly equal distances are not grouped. Floating-point rounding or reordering may select a different nearly tied span; for nonharmonic loops or anisotropic residuals this can change subsequent radii/operator. Permutation invariance is not promised generally. Tests of reversal/repetition/translation use analytically symmetric examples with known operators.
- Extraction stops after six directions or when the next diameter is at most `rank_relative_tolerance` times the first. The default1e-12 and allowed range `(0,1e-3]` are numerical rank choices. This is full **numerically resolved sampled rank**, not proof of exact mathematical rank or full equivalence to continuous Eqs.(21)–(23). The first omitted radius is reported; it does not bound continuous unsampled excursions.
- Rank zero returns no invented directions, a zero operator and `normalized_operator=None`.

Atlas order is `xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz`; manuscript Appendix A p.14 uses `11,22,33,sqrt(2)12,sqrt(2)13,sqrt(2)23`. Conversion swaps the final two slots only. Actual Cartesian symmetric tensor tests verify shear scaling, basis conversion and the Frobenius metric.

Source harmonic examples p.8 Eqs.(19)–(20) provide exact axis-aligned circle/ellipse amplitude oracles only when the supplied sample set contains the relevant extrema. Cardinal samples of an axis-aligned ellipse recover both semiaxes and norm `sqrt(a²+b²)`. The retained noncardinal10/30/90-sample sequence approaches this norm for one prescribed ellipse; it establishes neither a universal sampling error bound nor monotone convergence for arbitrary loops. Rank-one and six-dimensional ±basis point sets give separate analytical outer-product oracles.

An independent covariance test constructs the Mandel map M from Cartesian tensor rotation `Q T Q^T`. A nonharmonic finite point set with three unique, well-separated antipodal farthest pairs verifies `A_rotated = M A M^T`, operator spectrum, scalar/Frobenius norm and rotated source-order conversion. This supports arithmetic covariance for that finite fixture with unambiguous span choices. It does not establish general covariance across floating-point near ties, a frame-evolution algorithm or constitutive objectivity.

## Fixed-amplitude scalar history

`g_a_increment(g_A, a, C_N1, C_N2, delta_N)` implements only Eq.(37), p.12, with `b=a*C_N1`. Here `a` is the already supplied nonnegative amplitude **factor** `f_ampl`, not raw strain amplitude and not a quantity inferred from cycle count. No Eq.(9) amplitude-factor cap is implemented. `C_N1` must be positive; history, factor, `C_N2` and cycle-count increment must be nonnegative and finite. These admission restrictions are explicit diagnostic choices. Inputs are rejected rather than clipped.

The scalar ODE is `dg_A/dN=b*C_N2*exp(-g_A/b)`. For fixed positive b, substituting `y=exp(g_A/b)` gives `dy/dN=C_N2`; this provides an independent transformed-solution oracle and fixed-amplitude composition law. Stable evaluation uses `log1p`, with logarithms of the two positive factors to avoid overflow in `C_N2*delta_N` and a softplus branch for large arguments. Explicit zero amplitude, zero interval or zero C_N2 returns the unchanged history. For nonnegative initial history, the zero-amplitude limit follows from the increment being bounded above by `b*log1p(C_N2*delta_N)`, which tends to zero; it is not evaluation of the printed undefined ratios at b=0.

An underflowing intermediate exponential or unrepresentable product b does not itself imply an unrepresentable final increment. For `log(z)<-37`, where `z=C_N2*delta_N*exp(-g_A/b)`, evaluation combines `log(b)+log(C_N2)+log(delta_N)-g_A/b` before exponentiating. Replacing `log1p(z)` by z there omits a relative correction below4.3e-17, before logarithm/exponential rounding. The sum uses `fsum` to reduce addition cancellation; it cannot remove individual logarithm errors. An unrepresentable or subnormal b is retained through its logarithm and used in the final combined expression instead. Independent1200-digit Decimal calculations from the actual binary64 input values test several extreme representable cases, including one whose intermediate exponential underflows and one whose b overflows/underflows. Their tolerance is5e-13 relative or one output ulp, not a correctly-rounded numerical guarantee.

A positive final increment that underflows to zero, an overflowing result, or an increment lost completely on addition to the parent rejects separately. This is not arbitrary-precision arithmetic or a general rounding-error estimator. Near representability boundaries, logarithm/exponential rounding may affect the outcome. `delta_N=0` is allowed as an identity diagnostic even though an actual accumulation block contract requires positive count advance. Changing only a reporting count origin has no effect; history remains independently supplied. Changing amplitude between calls preserves the previous history and does not reset it.

Exactness refers solely to the fixed-amplitude scalar ODE in real arithmetic. The diagnostic does not add the persistent constant-rate `b*C_N3` contribution to g_A; it does not compute total accumulation strain, stress, density, direction or pi. The 6D/9D back-polarization conflict and recording-filter conflict remain unresolved and untouched.

## Reproduction and retained evidence

From repository root, using an acquired original manuscript at its local path:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_hca_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 tools/hca_diagnostics.py --source paper/results/sources/niemunis-2005-hca.pdf
```

The generator requires and verifies the original hash without copying it. `--source` can instead name a private acquired copy. Default evidence destination is `catalogue/investigations/hca-diagnostics-v1/`; `--output` supports temporary comparisons. Evidence binds the generator, tests, documentation and original hash. The separate manifest binds those files plus evidence with repository-relative logical paths, even with temporary output. No native execution/build is required. The tests supply analytical comparisons; the generated report supplies retained numerical observations, not a self-certification of scientific review.
