# PM4Sand3D 1.0: instantaneous flow-direction fragment

Status: **source-linked algebra draft; independent scientific review pending**. This extends the [surface fragment](../../catalogue/source-audits/pm4sand3d-1.0-surfaces.json) with the deviatoric and complete flow directions from Section 2 of the [June 2026 vendor manual](https://itasca-software.s3.amazonaws.com/udm-library/Kippen_et_al_PM4Sand3D_v1_CGM-26-01.pdf), Eqs. 35–37, printed page 29/PDF page 34. The source hash is `6073a97a374d4b947e20a492b5009bbd01e3e5b0b773841b0f3b037c194f7453`, matching the [manual receipt](../../catalogue/source-audits/pm4sand-manuals-2026-10-31.json). That page was rendered and visually inspected for this transcription. Author-linked May 2026 versus vendor June 2026 edition equivalence remains unresolved.

The [typed fragment](../../catalogue/source-audits/pm4sand3d-1.0-flow.json) contains eleven terms. Its first seven are exactly the pinned surface fragment; the dependency hash and copied terms are checked. The four additional terms are:

```text
B = 1+(3/8)*(c^4-1)/c^4*g^4*cos(3theta)
C = (3*sqrt(6)/8)*(c^4-1)/c^4*g^4
Rdev = B*n-C*(n^2-I/3)
R = Rdev+D*I/3
```

Here `n^2` is the Cartesian matrix square represented in Mandel coordinates, not a componentwise square. All terms are dimensionless. These B/C formulas belong to PM4Sand3D's quarter-power Lode interpolation; they are not SANISAND-2004's rational-interpolation formulas. For the tested `c<1` domain, C is negative. For c=1, B=1 and C=0; in axisymmetric compression and extension, Rdev=n for every tested c.

**D is a supplied finite scalar audit input**, including either sign and zero. This work does not extract the complete dilatancy law, choose its fabric/history dependencies or propose physical bounds. The flow tensor obeys `tr(Rdev)=0` and `tr(R)=D`. No normalization is added: Rdev generally has a norm different from one away from axisymmetric loading. Interpretation of the plastic volumetric/deviatoric strain-norm ratio stated in Eq. 38 needs separate reconciliation with the multiplier/direction convention. This fragment uses D strictly as the coefficient of I/3 in Eq. 35.

The inherited surface audit domain remains finite deviatoric r and alpha, a nonzero r-alpha direction, positive m and `0.64<=c<=1`. Trace tolerances and this tested interval are project audit choices, not a complete physical admissibility rule. The evaluator adds no pressure floor, zero-direction regularization, Lode clipping or flow normalization. Very small directions that underflow remain rejected under the existing surface policy.

The [Python research support](../../tools/inspect_pm4sand_flow.py) evaluates the existing surface utility and the new typed terms. [Five test groups](../../tests/test_pm4sand_flow.py) check source/dependency identity and dimensions; circular-surface and compression/extension reductions; independently coded Cartesian matrix-square algebra for 40 general tensors, three c values, three D values and their oblique rotations; trace/translation/positive-scale behavior; supplied-D dependence; and invalid/undefined-domain rejection. The Cartesian oracle substitutes a rearranged expression for g^4 and uses a determinant for the cubic invariant; it does not call the production tensor-square or cubic-invariant functions. This is a separate mathematical implementation, not independent scientific authorship or external-code validation.

```sh
python3 -m unittest discover -s tests -p test_pm4sand_flow.py -v
```

The simplified algorithm's stress correction in Table 3.1 step 7(b)(ii), printed page 76/PDF page 81, differs from the Section 2 Eq. 35 expression. This fragment selects the explicitly located Section 2 flow equation; it neither implements nor resolves the algorithm. Keep that ambiguity alongside the table-label and edition issues in the [manual dossier](pm4sand3d-1.0-manual.md).

This remains an instantaneous algebra investigation. It supplies no complete model, stress update, loading-index history, initialization, reversal policy, lagged coefficients, host averaging, parallel shear resistance, native/Wasm/AD execution, finite-step tangent or experimental calibration. PM4Sand2D 3.3 remains a separate plane-strain candidate. No candidate or review status changes.
