# Multilaminate host contract: Appendix B/D reconciliation

Task SRC-multilaminate-host-contract-v1; coordinating parent, 1 November 2026. This consolidates the static host/preparation/state review. It does not close full-family ingestion or select a smaller executable variant.

Source: Bert Schädlich, *A Multilaminate Constitutive Model for Stiff Soils*, TU Graz dissertation, April 2012. [DOI/institutional source](https://doi.org/10.3217/wmxdh-rg587), [repository record](https://repository.tugraz.at/publications/wmxdh-rg587). Complete private PDF SHA-256: `43d9a82e21523d303a684776580f57943277bc5fa9cb4d77648494e9daa876a9`. Acquisition and earlier coverage remain in the [thesis packet](../thesis-2012-v1/README.md); the [base-law packet](../base-laws-v1/README.md) remains unchanged. This additive packet qualifies its open questions, rather than rewriting earlier evidence.

Twenty-nine complete pages were visually inspected: PDF184–186,188–191,198–199,202–208,210–212,218–220,224–228,232–233 (printed page = PDF page minus 18). The full AppendixD listing was searched as text to locate assignments/calls; that search is not a claim that every remaining page or equation has been visually reconciled. [contract.json](contract.json) contains the 50 property indices, source units/transforms, history block map, reading receipts and source questions. It targets v0.3 as a capability/source inventory, not a schema-valid executable model. PDF, extracted text, renders and author code stay private; no author code was executed.

## Input and preparation findings

Tables B.4–B.7 give angles in degrees and stress quantities in the host's consistent stress units, not an automatic SI convention. AppendixD p184 divides angle inputs by `Rad=180/pi`; it also divides property6 by 1000 to obtain internal Amat. Atlas must distinguish source UI values from equation parameters. For example UI Amat=60 gives equation Amat=0.06. The tables alone do not document that scale. No source UI default becomes an Atlas physical default.

The code applies parameter policies before branch use (p185): Rf=0 becomes0.9; reference pressure=0 becomes100 in host units; m>=1 becomes0.9999; NUMCP=0 becomes33. These are implementation substitutions, not mathematical admissibility bounds. Allocation using raw NUMCP precedes its zero-to-33 default (pp184–185), another reason not to adopt the listing as a complete portable initializer. Many invalid/degenerate cases remain unguarded.

For optional initial stress, the printed code uses `sum(SIG_I)==0` as a sentinel, then starts modified stress from host Sig0. OCR>1 replaces the three normal components with OCR times SIG_I and clears shear. A subsequent nonzero POP replaces them with `(K0nc*v, v, K0nc*v)`, where `v=SIG_I_yy-abs(POP)`, and clears shear (pp186–187). Thus POP wins when both are active. Vertical is the source y direction. A nonzero zero-trace stress can satisfy the sentinel; do not transfer this encoding to the explicit v0.3 initialization API.

Current and preparation stresses are projected to each plane. Initialization chooses the maximum cone mobilization from both states and the minimum initial angle, then clips it to the plane maximum for non-Hvorslev branches. The cap candidates in code are negative roots `-sqrt(sigma_n^2+tau^2/M_CP^2)`; the more negative candidate is used subject to additional minimum-state/cohesion logic (p188). EqB.5 p166 prints the positive root. Equations B.1/B.3 add POP, while the code subtracts abs(POP) under its compression-negative convention. Both differences are retained; no universal initial-state recipe is claimed. `GetAcap` is called to obtain cap shape but its implementation is absent from this listing.

The initialization marker is StVar(3N+2)=123. It prevents repeat preparation in IDTask1 (p185). A restart must preserve prepared state and marker semantics, not rerun OCR/POP. The source also stores project-path/mesh metadata in the state array; it is not all constitutive material memory.

## Saturation and flow findings

The base cone hardening formula can overshoot maximum friction. AppendixD resolves how stress evaluation treats that for the ordinary nonsoftening branch: it reads stored mobilized tangent, caps the local evaluation value at `tan_phi_i` when not Hvorslev (pp193,200), and sets the cone hardening derivative to zero at equality (p202). The Eq40 update at p206 writes its raw result back; no immediate post-write cap is shown there. Therefore clipping the *stored* state would be an extra numerical choice, not a literal transcription of this ordering. Galavi softening and Hvorslev branches have different policies and cannot inherit this rule indiscriminately.

The third dilatancy region is explicit in p202: above phi_cv it uses `(atan(tphim)-phi_cv)*F_psi`. Non-Hvorslev phi_cv is derived from maximum friction and dilation by the printed arcsine expression; Hvorslev uses phi_res and different slope policies. These details resolve the previously missing upper branch and angle units, but do not complete the extension flow/parameter reconciliation. At zero resultant shear, p206–207 explicitly sets the two directional plastic shear components to zero instead of dividing by tau; nonzero tau uses the local shear direction. Near-zero selection and physical apex behavior still need a reviewed policy.

## Nested integration and commit boundary

The flowcharts (pp170–171) and B.7.1–3 (pp172–173) require nested work:

1. Read lagged neighbour damage where needed; determine elastic stiffness from prior local degradation history.
2. Repeat an outer stiffness/recovery solve. Within each pass determine substeps, solve successive subincrements, and iterate local plastic corrections with global stress reconstruction.
3. Use one elastic matrix for all subincrements in that pass. Update the strain contours after the subincrement loop; repeat when recovery changes stiffness.
4. Return stress/history and, for nonlocal options, update host damage files.

Positive StepSize is a stress-distance criterion (typical source values5–10kPa); negative StepSize selects a strain-norm count in code (p193), zero leaves the initial single substep (p192). Positive selection takes the maximum count over candidate surfaces and planes (p194). It is not a physical timestep or a generic local-error estimator. Exact count formulas contain denominators/radicands needing domain guards; the packet does not implement them.

Page208 code defines the convergence measures: absolute accumulated volumetric plastic change and accumulated octahedral plastic shear. It uses crit=0.001 and a 1e-15 activity floor. The activity condition combines the two accumulated measures with OR, then evaluates ratios for both. A purely deviatoric or purely volumetric witness leaves one denominator zero. The B.1 flowchart instead prints0.01; Chapter3 text and code use0.001. These are source conflicts/guard questions, not adopted Atlas tolerances.

The outer stiffness loop has an `iterStiff<11` condition controlling recovery calculations (p208); that is not a demonstrated general convergence/failure policy. StVar is copied from StVar0 once before that outer loop (p189), while substep scratch is reset separately (p194). Rejected outer-pass history restoration has not been proved. Nonlocal file writes introduce effects beyond a material-state array. Atlas needs an all-history trial/commit/rollback boundary, deterministic event ordering and explicit failure reporting; the printed listing does not establish those guarantees. Physical duration remains unused in the mapped base updates despite the host Time0/dTime arguments.

## State layout and recovery events

For N=33, the source advertises history allocations102/231/264/396/1056 for basic, Hvorslev, Galavi, small strain without recovery, and small strain with recovery, respectively, as described in the prior packet. Pages214–215 confirm the block indices. Global stress is separate. The map includes cap/cone fields; branch-specific damage; three local deviatoric strain components; path magnitude; a return point; active contour count; and four centre/radius sets. Some comments incorrectly label the third return component as second; reads/writes at pp209–210 establish three distinct component indices.

These advertised sizes are not safe universal runtime bounds: p186 writes project-path length at3N+13, and p188 writes B_cs at3N+12 without a branch guard. Both exceed basic nStat=3N+3 (112 and111 versus102 for N33). They fit larger allocations, but that does not prove the complete memory map. Extra bookkeeping is not a reason to increase Atlas capacity blindly; no mathematically equivalent compressed state has been established.

The contour creation condition (p210) includes failure=false, `iStep<=1`, decreasing radius, active count<=3 and radius>1e-15. It adds one contour, at most four. Thus no fifth contour is created by that branch; this is not a rolling four-cycle rule. On crossing an outer contour (pp209–210), inner centres/radii are erased and the outer one reactivated. The printed global failure flag suppresses recovery if any plane has mobilization>=0.99*tan_phi_res; prose p172 describes recovery below the critical-state line. Small local increments are rounded at1e-12. These details require Chapter4 reconciliation: notably the host iStep is documented as the global step reset each phase, so the `iStep<=1` gate must not be silently removed or reinterpreted.

One assignment at p210 prints `Star(9*N+i)` where adjacent components use StVar; it is a visible listing ambiguity, not silently repaired author code. Several called helpers are not defined in AppendixD, including DIRCOS3D and GetAcap; mesh-storage routines are explicitly omitted at p180. Thus table33-plane geometry plus a printed top-level routine does not provide a fully specified executable release.

## Material source conflict: cap hardening

Eq36 p20 prints `K=3/[p_ref*(1/E_oed_ref + 3*(1-2*nu)/E_ur_ref)]`. The p192 HARDCAP assignment uses a **minus** in that denominator. This is material: for E_oed=1000, E_ur=3000, p_ref=100 and nu=0.2, the literal values are75/4 versus75. At E_ur=1800 the minus denominator is zero while the plus expression remains finite. The example is an algebraic witness, not a source-admissible calibrated set. No preferred formula or revised model has been adopted. The earlier V–D Eq26/31 inconsistency also remains open.

## Check, stop condition and next milestone

Run `python3 -B check.py` from this directory or by absolute path. Optional `--pdf PATH` verifies the original source hash. The standard-library checker uses independent rational/index witnesses: cap denominator divergence, POP/OCR precedence, basic allocation overflow, four-contour address bounds, clipping/read-versus-write distinction, input scaling and the mixed-activity convergence guard. [checks.json](checks.json) retains source failures as findings; a successful checker exit does not make those source equalities/guards valid. No Atlas evaluator, native/Wasm build, author routine or experimental curve ran.

This closes the bounded host-contract review, not full AppendixB/D or Chapter4/6 transcription. Stop host micro-audits here. The next source milestone is one explicit full-variant reconciliation across Chapters4/6 and the2013/2014 publications, resolving the cap-sign/listing and helper/preparation questions before proposing a generic executable capability. Existing source acquisition, base-law and host facts should be reused. ING-multilaminate remains open; no model count, independent scientific sign-off, data-rights or deployment status changes.
