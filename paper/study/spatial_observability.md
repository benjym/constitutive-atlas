# Conditional observability of a spatial averaging operator

Status: paper-side mathematical derivation, pending independent review. This is not a rock-model implementation, verified source transcription, parameter count for an admitted formulation, or experimental identification result.

The [partial source note](source_notes/gradient-rock-2018.json) motivates the following assumed operator. Its original PDF equations still require visual verification. The results below concern the explicitly stated mathematical problem; agreement with a complete constitutive law remains a separate question.

## Assumed problem and observable

On a bounded domain with homogeneous Neumann boundary conditions, assume

\[
\bar a-\ell^2\Delta\bar a=a,\qquad
\nabla\bar a\cdot n=0,\qquad
\hat a=m\bar a+(1-m)a,
\]

where \(\ell>0\) is constant and \(m>0\). Treat \(a\) as a prescribed field. The diagnostic assumes that both the input field \(a\) and output field \(\hat a\) are available. It does not assume either can be directly measured in an experiment. Nonlinear evolution, irreversibility constraints and the mapping from internal fields to measured loads or displacements are outside this operator calculation.

## Homogeneous loading removes both spatial parameters

For \(a=A\), the constant solution \(\bar a=A\) satisfies the equation and boundary conditions. To establish uniqueness, let \(w\) be the difference of two solutions. Multiplication by \(w\), integration and the zero normal derivative give

\[
\int_\Omega w^2\,d\Omega+
\ell^2\int_\Omega |\nabla w|^2\,d\Omega=0.
\]

Hence \(w=0\), and \(\hat a=A\) for every allowed \(m,\ell\). Observing this homogeneous operator response cannot constrain either parameter. This says nothing about other parameters or about experiments whose internal fields become heterogeneous despite nominally uniform external loading.

## A single spatial mode still leaves a trade-off

On \([0,L]\), with position and length expressed in a common declared unit, prescribe

\[
a(x)=A+B\cos(kx),\qquad k=n\pi/L,\quad n\geq1,\quad B\ne0.
\]

The cosine has zero normal derivative at both ends. Direct substitution gives

\[
\bar a(x)=A+\frac{B}{1+\ell^2k^2}\cos(kx),
\qquad
\hat a(x)=A+BR(k)\cos(kx),
\]

with normalized amplitude response

\[
R(k)=1-\frac{m\ell^2k^2}{1+\ell^2k^2}.
\]

At one fixed nonzero \(k\), observing \(d=1-R(k)>0\) determines the curve

\[
m=d\frac{1+\ell^2k^2}{\ell^2k^2},
\]

rather than a unique pair. There can be a continuum of admissible pairs even if one further restricts \(m>1\). For a numerical example in dimensionless coordinates on \([0,\pi]\), at \(k=1\), \((m,\ell^2)=(3/2,1)\) and \((9/4,1/2)\) both give \(R=1/4\). At \(k=2\), they give \(-1/5\) and \(-1/2\), respectively. A sufficiently large positive mean and small perturbation can keep these example fields positive; negative contrast alone need not mean a negative field. This remains an operator example, not a proposed softening history.

## Two ideal mode responses can separate the pair

For two distinct nonzero wavenumbers, write \(q=\ell^2\), \(x_j=k_j^2\), and \(d_j=1-R(k_j)\). Then

\[
\frac{x_j}{d_j}=\frac{1}{mq}+\frac{x_j}{m}.
\]

With exact, compatible responses, the line through \((x_j,x_j/d_j)\) has slope \(s=1/m\) and intercept \(b=1/(mq)\). Thus \(m=1/s\) and \(q=s/b\), provided \(s,b>0\). This is a conditional algebraic inversion, not a two-experiment sufficiency claim. Degenerate cases such as zero contrast, missing input amplitude or an unknown field-to-observation mapping do not satisfy its premises.

Sensitivity can remain poor even when the exact inverse exists. If both \(\ell^2k_j^2\) are small, contrasts mainly depend on the product \(m\ell^2\). If both are large, they mainly depend on \(m\). Noise, uncertain geometry and evolving localization can therefore defeat a practically useful separation. Choosing two distinct modes does not itself establish a well-conditioned experiment.

## Consequences for the paper

Use this diagnostic to specify what evidence a mechanism comparison would need, before computing a performance ranking:

- State the response scale, domain, boundary conditions and available spatial observations.
- Separate constitutive length selection, mesh resolution and calibration evidence.
- Assess the sensitivity of actually measured channels, including nuisance parameters and initialization, rather than substituting an internal-field amplitude for an observation.
- Prespecify a spatial task only after source review and data feasibility establish its validity. A homogeneous material-point panel can still assess the local response but cannot establish the benefit of this assumed spatial operator.

The broader survey can describe a spatial formulation while leaving its computational comparison outside the current sand panel. These derivations neither admit the source candidate nor supply its missing experimental information.
