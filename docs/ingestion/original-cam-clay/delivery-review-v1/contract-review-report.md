# Independent OCC full-contract gate review

Task `REVIEW-occ-full-contract-v1`, reviewer run `/root/occ_contract_review`, 2026-11-01. This separate agent run did not author the historical packet/reference and was dispatched by `/root` to challenge their source/contract blockers. Exclusive new output uses `contract-review-*` under this directory; concurrent reviewers' files are preserved. This is E1/E2 technical review, **not E5 approval**, and no candidate model hash, backend qualification or accepted checklist is invented.

**Decision: blocked for the complete ordinary strain-driven atlas interface as currently proposed.** The principal obstruction is real source-level nonuniqueness under strain control. The source supports useful stress/mixed-control and smooth plastic trajectories; this review does not establish that Original Cam Clay is impossible to implement or that a new DSL primitive is necessarily required. Source-edition authentication also remains unresolved for a delivery explicitly claiming exact 1968 bytes/fidelity.

## Source actually inspected

Private retained PDF `.local/private-sources/original-cam-clay/schofield-wroth-electronic-transcription.pdf`, SHA-256 `638e0ee7dc238ae8922b79983433be7d12ad30450098efe395968f7eeed13cb2`, 7,886,630 bytes, 229 PDF pages. It identifies Schofield/Wroth's book but has 2005 Word/PDFWriter metadata and is the same electronic transcription already disclosed by the packet. PDF skill applied: extracted and read complete printed pp93-104,114,216-218; rendered and visually inspected complete pp95,99,101,216,217 at 1400-pixel scale. Body mapping is one-based PDF page = printed page + 11. Private text/render scratch is in `/private/tmp/occ-review-*`; no copyrighted source assets enter the public report.

Visual reading confirms the absolute-value signs in Eqs6.9,6.10,6.17,6.19. Eq6.7 gives identically zero recoverable distortion; p98 says interior stress probes cause rigid shear response. Printed p101 expressly admits the directions between the two limiting plastic directions, including zero distortion. Printed p216 explicitly begins with Granta-gravel and its `pu=exp((Gamma-v)/lambda)`. p217 C10 extrapolates a limiting distortion magnitude to the corner. These observations support the packet's main warnings.

The university URL in the retained receipt is a source locator, not a verified redistribution license or edition authentication. The parent supplied a ResearchGate author-associated lead; this reviewer has not independently retrieved/bound its exact PDF bytes and makes no finding that it authenticates the edition. Lack of a facsimile is not itself a claim that the read equations are wrong. Delivering the explicitly identified electronic-text formulation could be a separate, honestly declared source identity; it would not resolve the contract issue below.

## Independent continuous interior witness

Take the packet's illustrative M=1.2, lambda=.2, kappa=.04, Gamma=2.5 and p_ref=1000 Pa. Let pc=100000 Pa, p0=50000 Pa, q0=0, and choose packing `w=Gamma+(lambda-kappa)*(1-ln(pc/p_ref))`, `v0=w-kappa*ln(p0/p_ref)`.

For path order t in [0,1], prescribe the same strain history for both responses:

```
p(t) = p0 * exp(t*ln(1.1))
v(t) = v0 - kappa*ln(p(t)/p0)
Ev(t) = ln(v0/v(t)); eps_s(t) = 0
q_A(t) = 0; q_B(t) = 10000*t Pa
pc(t) = 100000 Pa; w(t) = w(0)
```

The recovery relation gives `Ev'=kappa*p'/(v*p)` and zero plastic volume. Eq6.7 and the interior branch allow zero shear strain for both continuous shear-stress histories. Both have the **same incoming complete state**, then different outgoing stresses under identical nonzero volumetric strain history. Both remain strictly inside yield: throughout this interval `M*p*ln(pc/p) >= M*50000*ln(100000/55000) > 35870 Pa`, while |q_B|<=10000 Pa. This is a continuous proof, supplemented by 101 retained samples; it does not depend on a sampled grid finding no violation.

At the common final strain Ev=.002160267272412729, eps_s=0, p=55000 Pa and v=1.7628794428326064, the two admissible stresses have q=0 and q=10000 Pa. Yield residuals are -39457.24205 and -29457.24205 Pa. Therefore neither a unique stress update nor a differentiable finite strain-to-stress rate follows from the source interior law. A zero-increment identity or freezing q from its previous value can be an explicit selection convention, but it is extra interface/numerical policy and does not remove the broader continuous counterexample. Supplying an external stress/equilibrium constraint can determine q.

Nonzero imposed shear starting from a strict interior state also cannot be represented by an ordinary finite local strain-path stress derivative that stays interior: recoverable and plastic distortion both vanish there. A finite update may jump to an active yield branch; its event/jump selection needs an explicit contract. This observation does not refute a suitably formulated finite residual/mixed-control solver.

## Independent vertex witness

For `f=|q|+M*p*ln(p/pc)`, at q=0,p=pc the two plastic normals in `(Ev^p,eps_s)` coordinates are `(M,+1)` and `(M,-1)`. The cone generated by them has `Ev^p>=M*|eps_s|`. With a prescribed positive hydrostatic pressure rate, p101 gives `Ev=lambda*p'/(v*p)` and `Ev^p=(lambda-kappa)*p'/(v*p)`. It allows all distortions in `[-Ev^p/M,+Ev^p/M]`, including zero. This proves nonuniqueness of distortion for that stress-controlled probe; it does **not** prove that every fully strain-controlled vertex problem is nonunique.

At p=pc=100000 Pa, v=1.7389659628023817 and p'=1000 Pa per path unit, the retained witness gives Ev=.0011501087673832075 and Ev^p=.000920087013906566. Permissible eps_s ranges from -.0007667391782554717 to +.0007667391782554717. Five explicit directions, including isotropic strain and two interior cone directions, are retained.

There is an important source interpretation boundary: at the interior cone directions the smooth formula `p*Ev^p=M*p*abs(eps_s)` does not hold as an equality. For the zero-distortion direction its sides are 92.00870139 Pa per path unit and zero. Source6.10bis labels the distortion form for nonzero distortion, while p101 introduces the corner convention. Treating the endpoint dissipation formula or Appendix C10 as a mandatory equality at every corner direction would delete directions p101 expressly permits. This warrants an explicit corner/dissipation interpretation and independent acceptance, not a claim that this diagnostic discovers an error in the original book. A normal-cone/active-set rule can represent the p101 cone; a single derivative of abs(q) at zero cannot span it.

## Findings ranked by severity

1. **Blocking: claimed full strain-driven execution is not a source-determined map.** The continuous interior witness applies before any q=0 yield vertex. Decide whether the exposed formulation is a constrained/set-valued stress relation with appropriate mixed controls, or a separately declared deterministic selection/extension with its own source/numerical identity. Adding finite G silently would change the model.
2. **Blocking: complete vertex algorithm and dissipation scope are not selected.** Preserve the p101 cone, distinguish its interior from one-sided smooth limits, and specify reversal/entry/critical mechanisms, domain/failure and transaction behavior. C10 is insufficient as a replacement.
3. **Blocking for an exact-original-edition claim: artifact identity/fidelity remains unverified.** The existing hash verifies retained bytes only. A newly authenticated author/publisher source or an explicitly changed artifact identity would resolve this source gate, subject to equation crosscheck.
4. **High, conditional on a general 3D claim: extension mapping requires explicit review.** p114 points toward Appendix C; Appendix C actually derives Granta-gravel geometry under general principal stresses. The invariant geometric construction can inform a declared OCC continuation using the OCC packing coordinate, so this is not evidence of an impossible or wholly absent mathematical route. Its complete recovery/history mapping, arbitrary principal-direction scope and corner behavior are not independently established by the current axisymmetric reference. An exact Chapter6 axisymmetric identity need not claim arbitrary 3D behavior.
5. **High: present generic engine semantics are insufficient evidence of capability.** `solver.hpp` exposes `integrate(old_state,de,parameters)` and explicit midpoint rates or square Newton residuals. The default plastic-multiplier predictor replaces multiplier residuals by zero-increment multiplier equations. In a shear-rigid interior formulation, the shear equation contains no q response compliance; without an added q constraint that system is rank-deficient when a nonzero correction must be solved. Initial residual acceptance may select a previous q without resolving mathematical nonuniqueness. Adaptive substepping cannot create a missing constitutive relation. This predictor issue is role-specific: v0.3 `increment_unknown` variables need not invoke that predictor. Two signed branch multipliers can be represented as such temporary unknowns, retaining actual complementarity residuals. That route deserves a bounded existing-residual experiment before any schema/runtime change. Its convergence, nonsmooth treatment, 3D extension and complete control selection are unqualified; no new primitive is proved necessary by this source inspection alone.
6. **Informational: retained smooth reference is valid within its frozen scope.** It integrates differentiated yield/packing/volume constraints after positive shear offset and passes the unchanged policy. It does not exercise the interior, vertex, reversal, transactions, native/Wasm or a browser.

## Checklist-v1 relevance, without an E5 decision

| Item | Gate assessment for a future complete candidate |
| --- | --- |
| source_provenance | Bounded artifact binding is verified; exact1968 fidelity unresolved. |
| equation_fidelity | Packet's selected smooth equations agree with inspected source; no complete candidate/branch implementation supplied. |
| conventions_dimensions | Compression-positive signed q, work pairing and kappa/log-pressure mapping are coherent for the named axisymmetric scope. General3D scope unresolved. |
| initialization_domain | Existing explicit preparation and packing checks are sensible; complete interface must retain them and define admitted branches. |
| integration_transactions | Blocking missing controls/selection/corner/jump contract; proposed rollback prose has no backend qualification. |
| independent_numerical_evidence | Existing algebra/smooth reference reproduced; this independent continuous witness identifies missing full-scope contract. |
| backend_delivery | Not assessed; no compiled interface claimed by this report, no builds or compiled calls performed. |
| applicability_claims | Current packet/reference limitations are appropriately bounded. Full interactive original-OCC delivery is not established. |
| reproducibility_rights | Exact reviewed input/output hashes retained separately. Private sources stay private; no distribution rights inferred. |

## Reproduction and retained results

Run from repository root:

```
python3 -B docs/ingestion/original-cam-clay/delivery-review-v1/contract-review-witness.py
python3 -B docs/ingestion/original-cam-clay/check_packet.py --source .local/private-sources/original-cam-clay/schofield-wroth-electronic-transcription.pdf --output /private/tmp/occ-packet-independent.json
python3 -B docs/ingestion/original-cam-clay/smooth-reference-v1/reference.py --output /private/tmp/occ-smooth-independent.json
python3 -B docs/ingestion/original-cam-clay/test_packet.py
python3 -B -m unittest tests.test_occ_smooth_reference -v
```

All five commands passed in this run; the two existing suites have six tests each. Retained `contract-review-packet-replay.json` includes a matching private-source hash. Smooth replay passes all three resolutions; finest scaled state error 1.0864287978620268e-8 and adjacent improvements 17.291934293284434 / 16.638893321088386. No original policy was edited. Evidence hashes and test transcripts are in the accompanying bindings/log files. No compiled observations or failures exist in this review; the blocking findings above are retained analytical/contract failures, not waived numerical tests.

## Smallest resumption path

The parent should complete source identity acquisition alongside a separately owned **contract and current-residual capability experiment**, before assuming a generic engine extension is necessary. Freeze: axisymmetric signed-q controls and equations; interior stress selection/rank behavior; two-sided vertex cone and corner dissipation interpretation; strain-induced yield entry; critical/softening support; invalid-input, hold, reversal and exact rollback outcomes. First test a minimal two-signed-mechanism residual with `increment_unknown` variables and the declared selection policy, using the witnesses here as required capability cases before production implementation. This task can use existing residual algebra; shared runtime changes require a demonstrated missing capability. Decide whether the result preserves an exact stress-controlled source relation or introduces an explicitly named selection variant. Do not count a post-vertex fixture as the full law or start backend qualification before these decisions.

Then transcribe a v0.3 candidate only if the exact interface is supported, with a predeclared independent acceptance plan. Generic implementation can be explored under its own whitelist; coordinator serial native/Wasm execution and separate E5 review follow. This review returns a real resumption condition rather than requesting human scientific approval.
