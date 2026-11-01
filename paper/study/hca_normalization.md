# Reference normalization in the HCA accumulation kernel

Status: paper-side algebraic derivation and numerical identity checks; independent scientific review pending. This diagnostic covers the scalar accumulation/history factors of the author-hosted 2005 manuscript, not an executable HCA formulation, full constitutive verification or experimental identifiability.

The [source record](source_formulations/hca-sand-2005.json) pins the PDF and its access provenance. Manuscript pages 4, 7 and 12 were visually checked for equations (7), (9), (14), (18) and (37). The [code](../analysis/hca_normalization.py) evaluates only these scalar factors. It does not calculate strain amplitudes, tensor directions, polarization evolution, stress, equilibrium or companion-model response.

## A conditional change of reference void ratio

Write the amplitude factor as \(a=f_{\mathrm{ampl}}\), the cyclic history as \(g=g^A\), and the coefficients as \(C_1=C_{N1}\), \(C_2=C_{N2}\), \(C_3=C_{N3}\). The source history rate separates into

\[
\dot g=aC_1C_2\exp[-g/(aC_1)],\qquad
r=\dot g+aC_1C_3,
\]

where dots mean derivatives with respect to cycle count. Define

\[
B(e_r)=\frac{1+e_r}{(C_e-e_r)^2},\qquad
F(e)=\frac{(C_e-e)^2}{1+e},\qquad f_e=B(e_r)F(e).
\]

Holding the other factors in equation (7) identical, the accumulation magnitude is proportional to \(rB(e_r)F(e)\). Choose a different reference \(e_r^*>-1\), distinct from \(C_e\), and set

\[
s=\frac{B(e_r)}{B(e_r^*)},\qquad
C_1^*=sC_1,\qquad g^*=sg.
\]

The exponent is unchanged, \(\dot g^*=s\dot g\), \(r^*=sr\), and \(f_e^*=f_e/s\). Consequently \(r^*f_e^*=rf_e\). This identity holds in both branches of the published amplitude factor, because the amplitude factor itself is unchanged. Zero initial history stays zero; nonzero initial history must be transformed.

The combinations

\[
A=B(e_r)C_1,\qquad H=B(e_r)g
\]

remove this reference coordinate from the scalar equations:

\[
\dot H=aAC_2\exp[-H/(aA)],\qquad
rf_e=\left(\dot H+aAC_3\right)F(e).
\]

The finite history update in equation (37) is also covariant:

\[
\Delta g=aC_1\log\left[1+C_2\Delta N\exp[-g/(aC_1)]\right],
\qquad \Delta g^*=s\Delta g.
\]

At zero amplitude the diagnostic uses the continuous zero-rate and zero-increment limit for nonnegative history. This avoids evaluating the exponential ratio at zero.

This is a conditional normalization redundancy. It does not allow changing \(e_r\) alone. If a study fixes \(e_r\) using an external measurement or a declared relation to another material quantity, that information constrains the parameterization. The centrifuge table's reference void ratio equals its reported maximum void ratio, but numerical equality alone does not establish a general equation or permit removing a measured input from the information budget.

## A rescaling that fails across the amplitude cap

Within the quadratic amplitude branch, changing \(\varepsilon_r^*=k\varepsilon_r\) and \(C_1^*=k^2C_1\), with \(g\) unchanged, preserves \(aC_1\). It therefore preserves this scalar kernel on paths confined to that branch.

The source's other branch is the literal value \(a=100\) above the stated amplitude threshold. That branch does not acquire \(1/k^2\) when the reference changes. The proposed transformation then changes \(aC_1\) and the rate. It is not a global invariance of the published piecewise formula. Rewriting the cap to depend on the reference would define a different parameterized expression and must not be done silently.

## Evidence and scope of the result

`tests/test_hca_normalization.py` checks fresh and nonzero histories, multiple void ratios and reference choices, amplitudes below, at and above the threshold, and covariance of the finite history update across amplitude changes. Counterexamples check changing the void reference alone, omitting the history transformation, and extending the amplitude rescaling across the cap. These are equation-level identity checks against the paper transcription; they do not constitute independent validation of that transcription or an integrated HCA solver.

The survey should report reference choices and supplied history information separately from fitted material combinations. The source record's independent material dimension remains unknown: this audit neither inventories every coefficient in the full workflow nor establishes which combinations experiments identify.
