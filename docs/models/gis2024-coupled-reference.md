# Independent instantaneous14-state HP/extracted-ASBS+GIS reference

Draft mathematical reference only; AI technical reviews are retained; scientific source review remains pending. This is not a complete admitted model, discrete integration algorithm, preparation procedure, calibration, reference-author-code comparison or experimental validation.

Source: Mugele, Stutz & Mašín (2024), *Generalized intergranular strain concept and its application to hypoplastic models*, Computers and Geotechnics173,106480; [DOI](https://doi.org/10.1016/j.compgeo.2024.106480); [primary institutional PDF](https://publikationen.bibliothek.kit.edu/1000171366/153009465). Private PDF SHA256 `39ec8356a26b82ae651be8feb4cdb3e49bb86ded9a850adc4c7eee5e9ec3bdc3`. Relevant visually inspected locators: p3 Eqs8–12, p4 Eqs22,26–32, pp5–7 Eqs33–35,39–43, and p12 AppendicesA/B. No paper text/PDF/render is redistributed in this stage.

## Interface and independence

`tools/reference_gis2024_coupled.py` exports:

```python
coupled_rates(state, de, parameters)
```

`state` has exactly sigma (six Mandel components), e (scalar), h (six Mandel components), Omega (scalar). `de` is a six-component instantaneous strain derivative with respect to dimensionless path coordinate, not a finite integrated update. `parameters` has exactly the18 independent physical parameters: phi,hs,ei0,ec0,ed0,n,alpha,beta,R,m_R,m_T,beta_R,chi_R,gamma_chi,chi_0,chi_max,C_Omega,gamma_Omega. All values are explicit; test fixture parameters are examples rather than implicit universal defaults. phi is radians and hs Pa.

The result contains `sigma_rhs`, `e_rhs`, `h_rhs`, `Omega_rhs`, plus `derivative` ordered as `[sigma6,e,h6,Omega]` and scalar diagnostics. Inputs are not mutated. No state is advanced or committed; no parent or previous-substep history, hidden reset, numerical lag, phase event or physical clock is introduced.

The coupled oracle uses **only stdlib and the independent Cartesian/dense HP oracle** retained as `tools/reference_gis2024_hp_host.py`. That dependency computes the host with original tension-positive auxiliaries, dense pivoted6x6 elimination and expanded Eq31. The installed code uses one shared host-reference module. The coupled GIS implementation is independently written with ordinary3x3 matrices and scalars, including a direct Cartesian B.2 host action. It imports neither Atlas, the supplied-GIS DSL evaluator, the production host evaluator nor any material integrator.

## Equations and conventions

Compression-positive stress, strain direction and full symmetric h are used. AppendixA's source conventions map through sigma_A=-sigma_source, de_A=-de_source, h_A=-h_source and m_A=-m_source; scalar host C,S and GIS scalar factors are unchanged. The independent host's m output already has the mapped compression-positive sign. H=sigma/trace(sigma) and host stiffness action are unchanged by this simultaneous convention change. Mandel shear entries carry sqrt(2). No deviatoric projection is applied to h.

The stress rate uses the selected extracted-ASBS pairing only: E=fs L, m normalized from L inverse action, C=norm(B)fdAstar, S=fd/fdAstar, and f=0. Actual ASBS reference-state preparation is distinct from evaluating the projected fdAstar at supplied sigma,e. No S=Y fallback is used.

GIS Eqs33–35 and39–43 are implemented directly: directional h evolution; direction-dependent k; nested suppression `S**(k**gamma)`; gamma=gamma_chi*chi; chi=chi_0+Omega*(chi_max-chi_0); and Omega rate `C_Omega*(1-rho**gamma_Omega-Omega)*norm(de)`. gamma_Omega remains an independent parameter. The void-ratio equation is Eq22 mapped to compression-positive convention: `e_rhs=-(1+e)*trace(de)`.

The source's general objective stress rate does not establish finite-rotation support: this reference is for zero-spin instantaneous constitutive algebra.

## Zero direction and domain policy

At exact-zero de, valid current state/parameters are still checked and the host evaluated. All14 rates are zero. The direction-dependent q,k and suppression diagnostics are None because k has no unique zero-direction limit. This is an explicit analytic zero-rate continuation, not an inferred author-code branch. Nonzero strain/memory whose squared Cartesian norm underflows is rejected rather than assigned a zero direction. No norm floor is used.

The domain matches the bounded source fragments: finite lossless real scalar inputs excluding bools; positive pressure; positive ordered limiting void ratios and ed<e<ei; positive hs,alpha and0<n<1,0<phi<pi/2,beta>=0; positive R,beta_R,chi_R,gamma_chi,chi_0,gamma_Omega; chi_max>=chi_0; C_Omega>=0;1<=m_T<=m_R;0<=Omega<=1. The full pairing requires computed Mandel norm(h)<=R, without an expanded roundoff shell. Its coordinate norm is sqrt(sum(h_i*h_i)); Cartesian tensor actions remain independently evaluated. The historical supplied-host fragment has a looser tolerance, but the coupled wrapper applies this stronger guard. Finite precision can still make an intended sphere point fall outside: callers must provide an admitted initial state, never rely on silent projection. The directional cosine receives the same64ulp arithmetic check used in the supplied fragment, without clipping. Host root/denominator failures, nonpositive required factors, invalid F denominators/radicands and nonfinite outputs are rejected with ReferenceDomainError. These are bounded audit restrictions, not exhaustive physical admissibility or a near-singular numerical guarantee. No state projection or silent regularization is introduced.

## Retained checks

Seven stdlib-only test groups pass. `catalogue/investigations/gis2024-coupled-rates-v1/reference.json` retains exact states, strain directions, parameters, all14 reference rates and diagnostics for six explicit branch fixtures and32 deterministic non-axisymmetric states (seed20261102). Fixtures include zero memory, zero direction, forward/reverse/tangent full memory, and full isotropic/nondeviatoric h. Random stresses are positive definite; void ratios are explicitly selected inside the audit interval. This sampling is not a physical calibration dataset.

Tests verify rate layout/finiteness/input isolation, exact e-rate sign, k checkpoints, h branch checkpoints, zero-rate continuation, oblique rotational covariance and positive degree-one strain-direction homogeneity. A closed isotropic stress-rate reduction checks the coupled stress action. gamma_Omega changes affect Omega rate without altering instantaneous stress when Omega is fixed, while Omega growth and decay are both exercised.

Two additional analytical checks concern differential identities, not finite-step integration accuracy:

- For beta_R=1, fixed aligned loading magnitude D and initial aligned h0, `h(s)=R-(R-h0)*exp(-D*s/R)` solves the scalar aligned-memory equation. Its analytical derivative is compared against h_rhs at three supplied points.
- With h deliberately frozen for the check, target A=1-rho**gamma_Omega and constant D, `Omega(s)=A+(Omega0-A)*exp(-C_Omega*D*s)` solves the scalar relaxation equation. Its derivative is compared against Omega_rhs. This is explicitly not a fully coupled trajectory because h would evolve under the same loading.

Run with the stage or installed repository on PYTHONPATH:

```sh
python3 -m unittest discover -s tests -p 'test_gis2024_coupled_reference.py' -v
```

The isolated14-state research schema is now compared against all38 cases through Python, native C++ and real-C-ABI Wasm. No finite GIS trajectory verification is claimed. The isotropic-full fixture is explicitly prepared at nextafter(R/sqrt(3),-infinity) to keep its computed norm within R; this changes test input preparation, not evaluated state. Shared source derivation and scientific assumptions still require independent review. The reference itself does not build or execute native code. Separate engine evidence and limits are documented in [research rates](gis2024-research-rates.md).
