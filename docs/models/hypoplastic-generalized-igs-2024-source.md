# Generalized intergranular strain 2024 — source and capability packet

Candidate: `hypoplastic-generalized-igs-2024`. This is a bounded source inventory, not an executable transcription, admission, validation, or independent review of an implementation. Inspection date: 2026-10-31. No source PDF, extracted text, screenshots, or author code is included in this packet.

The exact worked pairing is **von Wolffersdorff (1996) HP, reformulated with the extracted ASBS, plus GIS (2024)**. The existing IGS97 model is not this pairing. The paper also permits a different `S=Y` pairing and discusses other hosts; those require separate identities and evidence.

## Pinned source and access

Mugele, L.; Stutz, H.H.; Mašín, D. (2024), *Generalized intergranular strain concept and its application to hypoplastic models*, Computers and Geotechnics 173, article 106480. [Publisher DOI](https://doi.org/10.1016/j.compgeo.2024.106480); [KIT institutional record](https://publikationen.bibliothek.kit.edu/1000171366); [institutional published PDF](https://publikationen.bibliothek.kit.edu/1000171366/153009465).

Private file: `/private/tmp/atlas-generalized-igs-source/mugele-stutz-masin-2024-gis.pdf`; SHA256 `39ec8356a26b82ae651be8feb4cdb3e49bb86ded9a850adc4c7eee5e9ec3bdc3`; 2,381,423 bytes; 13 PDF pages. Printed page numbers equal one-based PDF pages. Visually inspected pages 1, 3–8 and 12 after Poppler rendering. Page 1 confirms title/authors/DOI, online date 5 June 2024 and CC BY-NC-ND 4.0 paper license. The KIT landing page's separate 2023 advance-publication field conflicts with its 2024 publication record and the PDF; retain this metadata conflict rather than copying that date.

No matching named original was identified in Downloads at task start. Existing triage already records that the three generic `1-s2.0-*.pdf` files concern other topics (`docs/reviews/parallel-candidate-triage.md:58–68`). This acquisition resolves that original-paper gap; no supplementary file or author implementation was inspected.

[Author implementation landing page](https://soilmodels.com/download/generalised-intergranular-strain-concept/) explicitly identifies HP reformulated using the ASBS, coupled with GIS. It lists Abaqus `umat.for`, `vumat.for` and a Plaxis `udsm.dll` (posted 16 July 2024; last update 29 October 2024). The page exposes login text and a free-download placeholder. No package or reuse license has been acquired/verified. Do not infer a code license from the paper license or public download listing. The smallest next acquisition is that exact release, its license/readme, parameter/state ordering and integration routine; no execution is necessary to inspect them.

## Host / overlay dependency table

| Identity / dependency | Source locator | Required contract and scope |
|---|---|---|
| Extended generalized hypoplastic host | p3 Eq7 | Expose elastic action `E:X`, normalized hypoplastic flow `m`, scalar `C`, state mobilization `S`, and homogeneous degree-one correction `f(strain_rate, host_state)`. A black-box final stress-rate expression alone is insufficient for generic overlay composition. |
| Selected HP host with extracted ASBS | p3 Eqs8–12; p4 Eqs17–32; p7 Section6; p12 AppendixB | `E=fs*L`; `m=-normalize(L^-1:N)`; `C=norm(L^-1:N)*fdAstar`; `S=fd/fdAstar`; `f=0`. `fdAstar` is obtained by evaluating Eq31 with current stress and void ratio as the presumed asymptotic state. |
| Actual ASBS reference state | p4 following Eqs31–32; p9 Section6.1.2 (text inspection only) | Actual ASBS states generally require a numerical search because the asymptotic barotropy factor depends on asymptotic void ratio. This is distinct from evaluating the projected `fdAstar` at a supplied current state; do not insert a new root solve at every rate evaluation without derivation. |
| Alternative HP+GIS using `S=Y` | p3 Eqs13–14; p7 Section6 | `C=1`, `S=Y=fd*norm(L^-1:N)`. Preserves the specified limit state, not the full extracted-ASBS identity. This is a distinct optional pairing, not a silent fallback. |
| Other rate-independent hypoplastic hosts | p2 Section2; p3 Eq7 and surrounding text | General formal scope, not a verified list of executable pairings. Nonzero `f` may depend on additional host state. Host-specific ASBS/projection and evolution laws must be pinned independently. |
| Elasto-plastic extension | p7 Eqs44–45 | Elastic-stiffness scaling is discussed, including the need to modify elasto-plastic stiffness; expressly outside the paper's worked scope. It is not a complete admitted elastic-plastic overlay algorithm. |
| GIS memory and stress-rate modification | p5 Eq33; p6 Eqs34–35,39; p7 Eqs40–43 | Add full symmetric strain-memory `h` and scalar cyclic-preloading memory `Omega`; retain the host evolution of void ratio. |

Equation 40 contains the **nested exponent `S**(k**gamma)`**, not a multiplier `S*k**gamma`. The multiplier `k` acts on the entire elastic action, including any nonzero `f`. The selected HP has `f=0`. At `S=1`, exponentiation leaves the specified boundary state unchanged, but this is not proof that every transient stress curve is free of overshoot; p8 discusses a small remaining transient overshoot relative to the continued virgin monotonic path.

## Independent parameters and retained physical state

Table1, p8 supplies 18 independent material parameters for the worked HP+GIS example: 8 HP; 5 IS/GIS; 5 additional GIS historiotropy parameters. The paired JSON enumerates all with the published values. `p_ref` in the existing Atlas HP implementation is an additional numerical scaling parameter, not one of these 18 physical parameters. Angles are printed in degrees and hardness in kPa; the Atlas boundary must explicitly convert to radians and Pa.

| Field | Shape / unit | Responsibility / source |
|---|---|---|
| effective Cauchy stress `sigma` | symmetric tensor / Pa; 6 scalars | HP physical state, p4 Section3; objective Zaremba–Jaumann rate convention p1 introduction |
| void ratio `e` | scalar / 1 | HP physical state, p4 Eq22: void-ratio evolution from volumetric strain rate |
| intergranular strain `h` | symmetric tensor / 1; 6 scalars | GIS physical strain-history memory, p5 Eq33 adopted in p6 Section5. **Not deviatoric:** p8 isotropic initial memory has nonzero trace. |
| cyclic-preloading `Omega` | scalar / 1 | GIS physical history, p7 Eq43; continuous-rate state, not a cycle counter or a maximum. |

Total: **14 raw scalar state components**. Tensor symmetry is used; no minimal independent count across arbitrary loading is asserted. `rho`, `h_direction`, `k`, `chi`, `gamma`, `fd`, `fdAstar`, `m`, `C`, `S`, and host stiffness actions are derived quantities, not additional independent physical memories. No lagged numerical memory, reversal anchor, plastic multiplier, parent-increment reset, host zone reduction or FirstCall flag is specified by these equations. Author code may have numerical workspace, which must be inventoried separately rather than relabeled as physical state.

## Evolution, branches and initialization

The source adopts Eq33 for `h`: on positive `h_direction:strain_rate`, remove the `rho**beta_R` projection along `h_direction`; otherwise use the full strain rate. Eq34 explicitly sets the direction to zero at `h=0`; Eq35 defines `rho=norm(h)/R`. These are directional continuous evolution branches, not a discrete reversal-reset event.

Equation39 determines `k` using `rho`, loading direction and `m_R,m_T,chi_R`. Its source checkpoints are: fully mobilized monotonic `k→1`; fully mobilized 180° reversal `k=m_R`; 90° reversal `k=m_T`; zero memory `k=m_R`. Loading-direction normalization is undefined at zero strain rate in the displayed notation. Before transcription specify and independently test a zero-increment continuation giving zero rates; do not substitute an arbitrary epsilon norm.

Equations41–43 make `gamma=gamma_chi*chi`, `chi=chi_0+Omega*(chi_max-chi_0)`, and evolve `Omega` with `C_Omega*(1-rho**gamma_Omega-Omega)*norm(strain_rate)`. `gamma_Omega` is independent in Table1; a textual option equates it to `gamma` for the HP coupling following earlier work, but this is not the published example's setting. `Omega` may decrease during long monotonic loading. Source interval statements `rho∈[0,1]`, `Omega∈[0,1]` concern the continuous laws; they do not authorize endpoint clamping in a discrete solver.

For p8 Section6.1.1 / Figs7–9, the source supplies isotropic compressive pressure magnitude 100 kPa, `e0=0.595`, `h_a0=h_r0=-R/sqrt(3)` in the source's extension-positive convention, and `Omega0=0`. The axial unloading is 70 kPa after 10% compressive axial strain, followed by reloading. These are explicit prepared inputs, not defaults to impose on every material instance. Equation43 permits `Omega0=0` when cyclic preloading is absent or unknown; known preparation remains caller data. A second regression can use the p9 Section6.2 cyclic example after visually checking that page: p0=200 kPa, e0=0.6915, h0=0, Omega0=0, five cycles and axial/radial amplitudes stated there. This packet has not visually verified p9, so that second fixture remains pending.

AppendixA p12 uses **tensile stress and extension-positive strain**, `p=-trace(sigma)/3`, and Euclidean tensor norms. Convert stress, strain and `h` consistently to Atlas compression-positive Mandel components, including sqrt(2) shear scaling. The source's general objective rate is not permission to claim a full finite-rotation implementation: the current zero-spin material path is the immediate admissible scope. Dot notation and `Omega` do not introduce a physical clock; the selected laws are degree-one, rate-independent.

## Smallest capability and evidence work

1. **Source fragment, no new DSL primitive initially:** encode Eqs33–35 and39–43 with typed supplied host `E` action / `m,C,S`; test `h=0`, zero increment, both branches, reversal angles, `S=1`, covariance and `Omega` increase/decrease limits. Pin the nested exponent and independent `gamma_Omega`. Existing scalar/symmetric operations and lazy `select` are present (`atlas/dsl.py:103–107,224–228`). Retained state fits the existing capacity (`atlas/model.py:97–102`).
2. **Selected HP host reduction:** transcribe Eq31 and the required actions of `L^-1` into independent Cartesian algebra. AppendixB EqB.2 gives an identity-plus-dyadic structure; a structured inverse/action may be derived and verified without storing a general fourth-order tensor. The paper does **not** print an inverse in B.10 (B.10 is `fd`). Generic fourth-order operator storage/inversion is a compositional interface gap, not yet a proven necessary new primitive for this selected pair. Verify denominators, square-root domains, isotropic/Lode limits and units before joining the overlay.
3. **Typed dependency/provenance contract:** either flatten the selected pairing explicitly or add a declared host-action contract; preserve variant IDs and hashes. Do not mark every existing HP host compatible merely because its state contains sigma/e. Existing `models/hypoplastic-sand-vw96.json` and `hypoplastic-sand-igs97.json` provide algebra/testing infrastructure only.
4. **Integration policy and preparation:** paper rate laws do not establish an author-code-equivalent discrete method, error norm, substep controller, endpoint admissibility, overshoot handling or rollback policy. Inspect the listed implementation before claiming equivalence. Current immutable candidate/rollback infrastructure may integrate these continuous states; no new ordered-history phase is demanded by this paper inventory. Initial memory and preparation must be explicit; no hidden ASBS preparation or fabricated reset event.
5. **Admission gates:** independently review each source fragment and sign mapping; compare structured and Cartesian host actions; require rate-zero/no-op, rotational covariance, state-bound convergence with refinement, reversal/cyclic regression, transaction rollback and reference-code reproduction when licensed. Keep implementation/source-algorithm/reference-validation flags pending until those distinct checks pass.

No native build/run, author-code run, shared repo edit or candidate promotion occurred in producing this packet.
