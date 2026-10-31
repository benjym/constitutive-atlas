# Equivalent pressure/deviator update and residual rows

Write `C:A=2μA+λtr(A)I`, `C⁻¹:A=[A−λtr(A)I/(3λ+2μ)]/(2μ)`, and let `R(T)` be the selected project BE metric projection onto the BK2022v1 Tresca cylinder. The [source crosswalk](../../ingestion/tresca/README.md) records the positive constant moduli, normal cone, pressure invariance and separately derived BE algorithm. This is a change in algebraic representation, not a new continuum closure.

The cylinder is invariant under adding any `cI`. Normality therefore gives `tr(Δep)=0`. The projection preserves `tr(T)`, acts on deviatoric stress with the Euclidean metric scaled by `1/(2μ)`, and satisfies `R(T+cI)=R(T)+cI`.

For `T=σ_n+C:de`, define

```
D = dev(σ_n) + 2μ dev(de)
m = tr(σ_n)/3 + (λ+2μ/3)tr(de)
T = mI + D
R(T) = mI + R(D)
Δep = (D−R(D))/(2μ)
```

Compute `D` before adding the potentially large `mI`. The candidate keeps the existing lazy elastic/face/upper/lower spectral routes, applied to `D`; it does not introduce a material kernel or numerical regularization. It retains `tr(D)` in the corner expressions rather than assuming a floating computed trace is identically zero. The absolute returned stress is recombined for the stress residual; the plastic increment is computed directly in the deviatoric space so its information is not lost in that recombination.

The original residuals are `rσ=σ−R(T)` and `rp=ep−ep_n−C⁻¹:(T−σ)`. The new residual is

```
rσ_new = rσ
rp_new = rp − C⁻¹:rσ
       = ep−ep_n−C⁻¹:(T−R(T))
       = ep−ep_n−(D−R(D))/(2μ)
```

For fixed parameters this is multiplication by the invertible block-triangular matrix `L=[[I,0],[-C⁻¹,I]]`, whose determinant is one. It preserves the complete solution set and all12persistent components. Current-state, committed-state and loading-direction residual derivatives transform by the same `L`; these are the38frozen columns. Parameter sensitivities away from a root would additionally differentiate `L` and are not claimed here.

The independent check compares two routes: (a) compliance row operation on the full-working-precision old independent residuals/derivatives, and (b) supplied current state/seed minus the independent returned state/direction. A separate high-precision projection of the split tensor checks the pressure identity on every frozen case at both precisions. No candidate interpreter or compiled material is evaluated.

Floating Newton residual norms, backtracking and rounding need not be identical after row conditioning even though exact Newton equations are equivalent. The new variant therefore needs a new frozen compiled study. Absolute stress may still have no representable small deviatoric component at a huge offset; this change is intended to preserve plastic history before recombination. It does not certify initial yield membership, spectral branch rounding, finite-range behavior or mixed-control convergence.
