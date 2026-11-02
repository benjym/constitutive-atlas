# Independent source and contract gate: fully rough HvWE interface

Task `REVIEW-interface2016-source-contract-v1`; reviewer run `/root/hill_scientific_review`, separate from source author `/root/hill_source` and implementing/coordinating run `/root`. Owned output: this new directory only. Review date: 2 November 2026. Exact author freeze: source-v2 manifest SHA-256 `9637c8859d36def48aac3cb43785141395f69572e00e54a4689e33020e70123a` (eight listed files, plus manifest). All listed hashes/sizes and twelve retained private resources were independently verified.

**Decision: the complete, explicitly source-reconciled fully rough realization may proceed to transcription and numerical qualification under its own precise identity.** There is no remaining scientific source blocker for that disclosed realization. This does not establish verbatim journal fidelity, executable support, E5 approval or full-delivery completion. The exact original/accepted 2016 article PDF remains unacquired; its visual equation-verification task remains open and must not be retrospectively marked complete.

The required identity is: **Stutz–Mašín–Wuttke (2016) fully rough HvWE interface, inherited original von Wolffersdorff (1996) host, source-reconciled, prescribed local stretching, fixed aligned zero-spin realization**. The candidate/dossier must preserve that distinction. It would be false to name an unqualified literal 2016 transcription or silently substitute an arbitrary bulk host.

## Primary support and reconciliation

Using the PDF skill, the reviewer independently rendered and visually inspected the retained 2016 author thesis, PDF pages 98, 100–103 and 106–108 (printed 66, 68–71, 74–76). The reviewer also rendered/read original VW96 PDF pages 2, 12, 13 and 20 (printed 252, 262, 263, 270). Original PDF identities are respectively `52e1eb5b510844f1d4a230935dffc03f77df149189cd8e166c9039fa3bd977ed` and `70eb1297cd25e67daf8b35b8f8c22f42c3a7fae2c0a62ae9e0079e3b03e64100`. Exact locators and render/cleanup hashes are retained in `visual-and-cleanup-receipt.json`.

The thesis supplies the enhanced four-stress/two-shear reduction, its weighted operators and explicit use of the unchanged continuum constitutive law. Its Section 5.5.1 expressly distinguishes the evolving in-plane stress from normal stress and identifies the inherited parameters; the following section identifies the formulation as fully rough. These are readable primary statements sufficient for a thesis-supported realization, independent of unverifiable journal typography.

| Issue | Independent finding |
| --- | --- |
| Host and density closure | VW96 Eq. 40 supplies the complete constitutive rate, Eqs. 41–46 its factors and Eq. 2 the void-ratio rate. The thesis explicitly inherits this host. Retaining all eight parameters, both pressure/density factors, full stress-shape factor and density evolution is supported. |
| Duplicated dimensional factors | Thesis Eqs. 5.7–5.9 cannot all be substituted literally: the definitions already contain the dimensional stiffness and nonlinear density factors. Exactly one `fs=fb*fe` and one `fd` in the nonlinear contribution reproduce original Eq. 40. This is an explicit reconciliation, not a numerical tuning. |
| Nonlinear stress vector | Original Eq. 40 visibly contains `a*F*(That+Z)`. The earlier worker suggestion `a*(F*That+Z)` is wrong. The frozen correction is right. |
| Combined stiffness factor | Original `fb` contains `(ei0/ec0)^beta` and `fe=(ec/e)^beta`. The common exponential density law gives `ei/ec=ei0/ec0`, so their product equals the thesis `(ei/e)^beta` expression. |
| Pressure sign | VW96 Eq. 43 has `exp[-(-tr(T)/hs)^n]` for compression-negative stress, consistent with Eq. 46. The thesis Eq. 5.13 lacks the inner minus. Its repair is supported by the inherited primary source. |
| In-plane stress | An independently evolving `Tp` is unambiguous in the thesis. Setting its stretching component to zero does not set its stress rate to zero. Earlier article-text wording reported as constant must remain a documented discrepancy, not an instruction to freeze/reinitialize `Tp`. This review does not certify unseen article page images. |
| Isotropic state | Original Appendix C explicitly supplies `F=1` at isotropy while the normalized Lode direction is undefined. Implement that branch without first evaluating `0/0`; do not invent a Lode direction, clamp or epsilon smoothing. |

The original 2016 publisher/accepted article visual receipt is still absent. Public HTML receipts and older text reports may corroborate identity or reported discrepancies; they do not establish visually verified journal equations. This review relies on the readable author thesis and original inherited host for its accepted scope. No later 2017 conversion, intergranular-strain extension or different roughness law fills a gap.

## Independent algebra and full-law representability

`check_algebra.py` is reviewer-authored, uses exact sparse polynomial arithmetic and imports no Atlas compiler/runtime. It proves 23 polynomial identities for arbitrary coefficients and replays the author's 702 rational checks. This is stronger than checking a few admissible stress points, and is still algebra rather than material/backend validation.

For `E(X)=[[a,c,d],[c,b,0],[d,0,b]]`, both associations of the printed reduced cubic differ from `tr(E(X)^3)` by `(a+2b)*(c^2-d^2)`. Thus the Lode numerator, evaluated on the trace-free normalized deviator, is exactly the Cartesian cubic. Its norm/contraction also agrees with Cartesian contraction. The historical intermediate-product nonclosure remains true; unrestricted matrix-product replacement is unjustified.

More importantly, the complete host action is a linear combination of `D`, `That*(That:D)`, `That` and `Z`, with scalar coefficients containing every original host factor. The proof establishes equality of reduced and embedded actions for arbitrary such coefficients, while preserving equal in-plane diagonals and zero in-plane shear. Both tangential shear modes remain present. This proves closure of the actual constitutive rate, not closure of arbitrary intermediate matrix products or arbitrary full-three-dimensional loading.

No material mechanism of the selected fully rough HvWE law is omitted: independent normal/in-plane stresses, both shear tractions, void ratio, eight host parameters, density effects, pressure dependence and the full Lode-dependent stress factor remain. Restricting supplied kinematics to zero spin is an explicit host restriction; it is not permission to claim simple-shear FE transport, finite-slip contact or general bulk-soil equivalence.

Compression-positive conversion must negate both source stress and stretching. Normalized stress is unchanged; the Atlas stress rate has positive linear contributions and a negative nonlinear norm contribution, while `eDot=-(1+e)*tr(D_A)`. The reviewer checked the stress-rate sign identity symbolically. Negating stress alone would be a material error.

## Requirements for E2/E3 and subsequent gates

These are concrete transcription/qualification obligations, not unresolved source equations:

- Use a distinct v0.3 `strain_path/path_ode` identity with five complete state components, a six-component symmetric effective-stress observable through the stated embedding, fixed-component semantics, explicit local axes and compression-positive Mandel conversion. `fixed_spatial/objective_rate:none` means zero spin only. The current contract supports this mathematics; actual candidate validation/generation and exposed interface support must still be demonstrated.
- Name controls as prescribed normal and two engineering-shear stretching paths, with the shear halves and units explicit. The dimensionless path coordinate is not a physical clock. A finite-slip/angle/thickness adapter is a separately identified map: differentiating `tan(gamma)=u/ds` does not establish a universal FE velocity-gradient algorithm. Do not advertise displacement, arbitrary thickness evolution or finite rotation unless that adapter is supplied and qualified.
- Supply an admissible complete initial stress/density/control context. Do not infer a unique specimen from Jaky, set `Tp=Tn`, or reset density/in-plane stress at reversal. Freeze a useful illustrative preparation independently of any calibration claim.
- Freeze the precise material/domain branch before observations: positive pressure/hardness, finite parameter powers, ordered limiting densities, permissible void ratio, nonsingular positive stiffness branch, real stress-shape factor, and the source isotropic continuation. In particular a merely nonzero stiffness denominator is insufficient to justify negative stiffness as a physical branch. Source parameter names are not universal parameter bounds; choose/disclose numerical guard margins rather than silently clipping states.
- Evaluate factors at the same trial state; validate holds before applying zero rate. Keep all stress, density, coordinate, parameters and start/end control context transactional. Failures roll back the complete parent. Preserve stage/restart consistency and qualify reversals, both shear directions, coupled normal response, isotropic and boundary cases, refinement, full-state rollback/recovery and replay.
- Prescribed normal stretching (including zero normal stretching) retains the complete material law. CNL/CNS mixed-control solvers, normal displacement/stiffness conversion, contact opening/recontact and FE tangents are additional interface/numerical contracts. Do not imply that these exist from source closure or omit them silently from a named public example.

The profile draft is appropriately reading-only. It explains granular confinement and dilation, identifies independent initial in-plane stress and supplies no runnable defaults. An executable profile must later describe the exact controls, parameters and preparation actually implemented; generic preset language must not manufacture availability.

## Handoff, limitations and cleanup

Source gate accepted for the named reconciled realization; exact-journal acquisition/visual fidelity remains separately incomplete. Candidate, frozen numerical reference policy, native/Wasm delivery, independent nine-item review, atlas/profile integration, actual browser qualification and live release remain outstanding. No scientific registry/admission record is created here.

Reproduce `python3 -B .../source-review-v1/check_bindings.py` and `python3 -B .../source-review-v1/check_algebra.py`. `source-bindings.json` binds the exact source freeze, originals, inherited historical evidence and relevant contracts. `algebra-results.json` records 23 symbolic and 702 replayed checks; no compiled call, build, browser, vendor execution, shared edit, commit or remote action occurred.

The only reviewer-created scratch directory was `/private/tmp/atlas-interface2016-source-review-v1`. After visual reading and retaining hashes/locators, its 1,828,504 bytes of extracted text/renders were removed and absence verified. Original private PDFs and author evidence remain untouched and durable. No running process or disposable reviewer resource remains. Author resources and subsequent builds remain coordinator-owned.
