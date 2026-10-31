# Independent MC axisymmetric finite paths v1

Source-only high-precision endpoint references for the source-pinned H=0 nonassociated Mohr–Coulomb law. No Atlas imports, candidate evaluations, compiled executions, builds or shared edits. This packet is a finite-path reference; it is not experimental validation, calibration or scientific admission.

The source is Sysala/Cermak arXiv1508.07435v3, exact private PDF SHA bf35ee09d500b8e21aabdddbdfac363c5f68368f150890c60343bc62447c83ca. [Primary source](https://arxiv.org/abs/1508.07435v3). The copied FORMULAS.md supplies equation/page locators and explicit compression-sign conversion. DERIVATION.md gives the independent2scalar reduction, drained stress clamp/plastic strain decomposition, inverse constant-volume q control, and apex subgradient. The reference uses no spectral eigenproblem and no finite-difference/Newton control solver.

## Frozen inputs and interpretation

source-input.json SHA324b94270a22339f5bf262523542e3e649b75a424d4a1e0c2ea1d11b833ad7d2 contains exact binary64 defaults E30MPa,nu.25,c10kPa,phi float(pi/6),psi float(pi/18),p_ref100kPa and initial100kPaI. Its14 paths comprise each of the five protocols monotonic32/cyclic64, drained defaults100/200, zero-hold8, and isotropic expansion32. The source generator consumes the literal stored control_deltas exactly and retains the separately displayed target sequence.

The input sequence is the independently frozen **intended Python binary64** sequence. It is not a claim of exact native/Wasm libm sine bits. The copied parent acceptance-paths.json explicitly bounds backend control discrepancy before backend observations. DERIVATION.md explains the general need to distinguish actual rounded caller increments; for this study those are intended inputs, and the independent backend mismatch is assessed separately by the parent.

Initial source/policy/checker/derivation bytes were pinned in pre-generation-source-freeze.json before numerical source path generation. The supplied input/requests/parent policy were then copied and pinned in prospective-freeze.json before either precision run. Original policies, source code and outputs remain unchanged. The supplemental input-integrity/adequacy check was added afterward without changing their bytes.

## Results and coverage

Both first source runs pass, with no unresolved cases or numerical failures. Outputs reference-p280.json and reference-p360.json contain14 paths,834 points/820 updates. There are577 elastic,147 compression-plastic,48 extension-plastic and48 apex updates. Protocol0 cyclic exercises extension/apex/compression; protocol4 cyclic and expansion exercise the tensile apex. All source regimes reached are reported per path in adequacy-results.json.

check-results.json compares21,711 numerical fields; maximum normalized cross-precision difference and source defect are8.89e-280 against the frozen1e-60 gate. Per-step checks cover equilibrium, source yield/nonnegative multiplier/complementarity, subgradient bounds/trace and applicable control/ordering constraints. check_algebra.py passes12,000 exact rational identities over1,000 independently sampled rational material sets: source edge denominators, flow trace, q/mean-stress inversion and drained radial decomposition.

The supplemental check passes3,883 checks. It verifies all literal request/parameter/initial/protocol/length correspondences, exact binary64 delta subtraction, intended target operation order, all cumulative elastic/plastic volume relations, constant-volume plastic mean-stress nondecrease, drained active plateaux, isotropic apex bound and explicit protocol3 cumulative q. The maximum exact cumulative-delta minus displayed-target discrepancy is

`65461784689723/38685626227668133590597632 = 1.6921474737018587446989465803543449540e-12`,

on protocol3/cyclic step64. This is not an input error: the source consumes stored deltas. Drained100/200 endpoints agree exactly at emitted81-significant-digit stress and strain precision. Their axial plateau is334641.0161513775037933146931Pa; radial stress remains100000Pa. The isotropic expansion plateau is the source tensile apex−17320.5080756887752320030290Pa.

## Files and reproduction

- axisymmetric.py INPUT PRECISION OUTPUT generates a reference with independent Decimal trigonometry and scalar finite updates.
- check.py LOW HIGH reference-policy.json compares precision and endpoint source/control defects.
- check_algebra.py runs exact Fraction identities.
- check_adequacy.py reads the frozen inputs/literal requests and high-precision output, writing adequacy-results.json.
- source/ holds exact model-transcription and solver-convention bytes; sources.json pins them. The manifest excludes itself.

Run with python3 -B. Reference output exposes full6stress/strain, control,q,mean_stress,pore_pressure,gamma,branch,accumulated plastic volume, and per-update source defects. All shear components are identically zero. Source residual/precision gates are separate from the parent's prospective backend path accuracy policy. No production parameter-derivative or instantaneous selected-eigenvalue-resolution claim is made here.

An incidental pre-observation parent assessor review found its parameter count was7 while the literal requests contain6; parent was notified. This packet does not execute that assessor or claim its final revised bytes were reviewed. The next step is the parent's independent packet review, frozen assessor/corruption tests, then serial native/Wasm path collection with all failures retained.
