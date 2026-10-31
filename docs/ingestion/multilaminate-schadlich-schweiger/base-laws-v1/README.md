# Multilaminate base laws and integration requirements

Task SRC-multilaminate-base-laws-v1; coordinating parent, 1 November 2026. Bounded source extraction, not complete family ingestion or executable admission.

Bert Schädlich, *A Multilaminate Constitutive Model for Stiff Soils*, TU Graz doctoral thesis, April 2012. [Persistent source](https://doi.org/10.3217/wmxdh-rg587), [institutional record](https://repository.tugraz.at/publications/wmxdh-rg587). The private PDF has SHA-256 `43d9a82e21523d303a684776580f57943277bc5fa9cb4d77648494e9daa876a9`. Acquisition, identity, quadrature and source history allocations are preserved in the [prior packet](../thesis-2012-v1/README.md).

This pass visually inspected PDF31–34,37–44,47,192 (printed pp13–16,19–26,29,174): fourteen complete pages. Other Chapter3 pages were searched as text but are not claimed visually reconciled. [source-ledger.json](source-ledger.json) records page/equation locators, private render hashes, literal equations and open questions. Copyrighted pages/text remain private. The ledger targets v0.3 as a source inventory; it is deliberately not a schema-valid model or a complete formulation declaration.

## What the source fixes

Local normal stress is effective stress; tangential stress is the resultant of two local shear components (p19). Compression is plotted on the negative normal-stress axis (Fig5), and the cap intercept is negative in Eq35. Source equations below retain that convention. Atlas compression-positive conversion, effective Cauchy binding, infinitesimal kinematics and fixed-frame assumptions still require one explicit reconciled declaration; no defaults are inferred from the existing engine.

The three local yield functions are an elliptical cap, a hardening cone and a fixed tension cut-off (Eqs32–34). Cap and tension flow are associated; cone flow uses mobilized dilatancy (Eqs38,41–48 and p22). Cap and cone hardening are independent (AppendixB p174); the later Hvorslev extension is explicitly different. These are dependencies of the full requested model, not a newly selected reduced Atlas variant.

For cap hardening, writing `q=-sigma_nc > 0` gives Eq35 as

```
q_new^(1-m) = q_old^(1-m) + K*(m-1)*p_ref^(1-m)*delta_epsilon_n_cap_p
K = 3 / [p_ref*(1/E_oed_ref + 3*(1-2*nu)/E_ur_ref)]
```

The plus sign in Eq36 is retained. Eq37 scales the two moduli with `(p'/p_ref)^m`; pressure/reference signs and the permitted power domain need AppendixB/parameter reconciliation. Eq35 is undefined as printed at `m=1` and requires a positive real-power base for a general noninteger exponent. A possible limiting law is not silently substituted.

For cone hardening let `t=tan(phi_m)`, `t0=tan(phi_0)`, `u=tan(phi_mod)`, `h=A_mat/3`. Then Eq39 is `t=t0+(u-t0)*gamma/(h+gamma)`. Eq40 is the corresponding exact incremental rewrite while its denominators exist. Since `Rf=tan(phi_max)/u`, `Rf<1` puts the asymptote above the stated maximum friction. Algebra gives finite `gamma_at_max=h*(tan(phi_max)-t0)/(u-tan(phi_max))`; continuing Eq39 beyond it exceeds the maximum. The clipping/branch rule must be reconciled with AppendixB/D before implementation. This packet does not introduce one.

Dilatancy Eqs42–48 specify two cubic intervals and a slope parameter. Their literal coefficients satisfy the lower endpoint, shared minimum, zero slope at that minimum, zero at `phi_cv` and slope `k_II` there, for nonsingular inputs. The printed figure has a third region: full upper-interval selection, angle units and degenerate cases remain to be reconciled. Checking these polynomials does not establish a complete flow law over every state.

## Coupled return and temporal contract

Eqs49–53 start with an elastic global trial, project stresses to each plane, calculate local plastic contributions, reconstruct `delta_epsilon_p = 3*sum(T_i*delta_epsilon_i_p*w_i)`, and update global trial stress from total minus plastic strain. Page24 explicitly rejects finishing all planes independently without intermediate global updates because that breaks the intended constraints. A generic plane loop must preserve this coupling; multiplying independent point solvers is insufficient.

At a corner, Eqs54–60 combine two potential gradients and solve a coupled 2x2 multiplier system. Diagonal terms include same-surface hardening; off-diagonal terms contain the elastic coupling. Page26 uses positive trial yield values to select candidates, positive multipliers for the corner, and removes a surface when its multiplier is negative. It warns about convexity. Exact ties, singular/near-singular determinant policy, zero-resultant shear/apex derivatives and nonconvex extensions need explicit handling. The independent check verifies the algebraic solve, not an implemented return algorithm.

The reported stopping rule is current iteration plastic-strain contribution below 0.1% of the step total (p23). Its norm, absolute fallback at zero plastic strain, iteration ceiling, failure/rollback and substep ordering need the AppendixB/D reconciliation. This source criterion is not an adopted Atlas acceptance tolerance. The previous packet records the host's time-independent classification and stress/history increment interface: elapsed seconds are not supplied by these Chapter3 laws. Hold/zero-load behavior is not yet proven for the complete branch.

Atlas trials must copy all plane histories, hardening variables and active sets from the committed parent and roll back all of them on failure/rejected host trials. That is a required implementation contract, not a source-verified transaction implementation. Restart must retain prepared cap/cone positions rather than rerunning initialization. Per-plane reversal memory and nonlocal host dependencies remain as recorded in the prior packet.

## Elasticity and preparation questions

Eqs17–24 give the N–T local compliance `Cn=(1-2*nu)/E`, `Ct=(1+3*nu)/E`. Substituting in Eq23 recovers all normal and engineering-shear coefficients of Eq17. AppendixB EqB.14 explicitly uses that N–T compliance for the local return calculation. This resolves the local-return split without selecting the entire small-strain extension or proving its history handling.

The separate V–D discussion prints `K'=E'/[2*(1-2*nu')]` (Eq26) and `Cv=1/K'=(1-2*nu')/E` (Eq31). Their equality is inconsistent by a factor of two for the same E and nu. Eq17 under the usual volumetric trace gives another normalization, `K=E/[3*(1-2*nu)]`. The checker retains the Eq26/31 equality failure as a source question. It does not correct the thesis or block the separately explicit N–T return relation on an invented choice of K.

Section3.4 p29 determines cap shape numerically by an oedometer strain increment matched to desired K0nc. It distinguishes that procedure from the earlier fixed `M_CP=(1-sin(2*phi/3))*tan(phi)` approximation. Preparation needs its iteration, loading, tolerances and restart semantics reconciled, not a guessed universal M_CP. Full parameter bounds, source units, NUMCP/state indices, substeps, small-strain/Hvorslev/Galavi branches and 2013/2014 version differences remain open.

## Checks and next decision

Run `python3 -B check.py` in this directory (or use its absolute path); `--pdf /private/path/to/thesis.pdf` additionally checks source bytes. The standard-library checker uses exact rational arithmetic, imports no Atlas/author code and needs no build. [checks.json](checks.json) records the reproducible outcome, including the retained V–D equality failure. It checks N–T reconstruction, transformed cap composition for m=0 and m=1/2, cone total/incremental equivalence and finite maximum crossing, cubic endpoints/slopes, and the two-surface linear solve. These are bounded equation checks, not material-path, convergence, numerical stability or experimental validation.

Stop this extraction here. The next implementation decision requires one consolidated static AppendixB/D pass for parameter domains, saturation, preparation, substeps and state/event indexing, then an explicit full-variant choice including Chapters4/6 and later-publication reconciliation. Do not open a solver feature task from this packet alone. Full ING-multilaminate stays open; executable counts, scientific review, experimental rights and deployment are unchanged.
