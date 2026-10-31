# Actual v0.3 research record and bounded numerical-policy review

Reviewed staged parent `model.json`, `policy.json`, generated `models.hpp`, source `FORMULAS.md`, original certificates and source-only hold diagnostics. Exact source identities are pinned separately. No Atlas implementation was imported or run by this auditor.

## Correct source specialization

The six-state stress-only fixed-frame small-strain record defines E,nu,c,phi,psi with strict interior domain checks and numerical p_ref scaling. E>0 and −1<nu<1/2 imply K,G>0. Its explicitly positive K/G denominator forms agree with source H0 even at negative Lamé modulus. Cohesion is constant; there is no cap, cutoff, void ratio, extra history, zero-dilation extrapolation or unproven restriction psi<=phi.

`trial=−(sigma_n+K trace(de)I+2G dev(de))` converts the compression-positive elastic trial to tension-positive source notation. Source descending eigenvalues v1/v2/v3 are taken from that negated tensor. Gamma numerators/denominators and all four reconstructed return branches match the source. Equation `sigma+returned_source` has correct units/sign. State initialization separately checks the compression-form yield. Effective stress is an explicit host specialization and is not inferred as a source pore-pressure law.

Value-only eigenvalues feed only classifier predicates through derived aliases. Ordinary eigenvalues, group sums and projectors are inside the selected gamma/whole-tensor conditional. Generated C++ line ordering declares classifier values eagerly, then selected ordinary gamma expressions, then the lazy returned tensor. Ordinary spectral calls in unselected gamma/tensor branches are not evaluated. Elastic does not demand differentiable eigenspaces; face requires all-simple trial spectrum; left/right use the isolated complementary extreme and grouped pair; apex is constant in trial stress. This is enough mathematically, not proof against every floating intermediate failure.

## R1: middle reconstruction, fixed

The first record used `trace(trial)−principal_max(trial)−principal_min(trial)` three times for the face's middle value. This avoids an individual middle projector but loses legitimate mixed-scale middle values; direct ordinary `principal_mid` is available. Coordinator replaced all three occurrences and regenerated before numerical certificate observations. Initial generator source is retained by the parent. Final reviewed model and generated headers use the corrected expression.

The witness diag(10^300,1,−10^300) loses middle1 under ordinary binary64 trace-minus-extrema. It can be a genuine open face input: K=2/3,G=1,s=3/5,d=1/3,c=(5/8)10^300,cos(phi)=4/5 gives h=10^300 and gamma_s=(5/24)10^300<min(g_sl,g_sr), with aa0. Returned middle remains1, so subtraction loses meaningful preserved data. No floating Atlas calculation was used to establish that algebraic witness.

## V1 blocker observed independently by parent, retained

Parent's policy-v1 keeps raw Ftrial<=0 and raw source equality tests. Its frozen source-only certificate/hold diagnostic reports25 initial values within its prospective bounded gate, but four zero-increment holds fail `selected_eigenvalue_unresolved`: left/right-to-apex boundaries in diagonal and rotated form. Rounded returned states have tiny positive yield and split repeated eigenvalues; the strict classifier can select a differentiable face at a numerically unresolved selected gap. `retained/parent-v1-check.stderr` and `retained/parent-v1-diagnostic-results.json` preserve the parent's evidence. This audit did not rerun Atlas or alter v1. The proof of exact classifier equivalence remains valid; the v1 floating hold requirement remains failed.

The current v1 postreturn and initial yield allowance is256eps*max(h,|extrema|); this is an explicitly numerical admissibility allowance, not source exact F<=0. It does not itself change raw classifier selection. Strict sine checks and positive selected multipliers diagnose numerical representability; they should not be described as narrowing the mathematical source domain. A yield residual gate alone does not verify the full subgradient or bound trial-to-return tensor/tangent error.

## Unadopted elastic-zone alternative

An alternative numerical policy could deliberately choose elastic when `Ftrial<=delta`, `delta=256eps*max(h,|trial extrema|)`, consistent with its already accepted-state yield allowance. This can prevent the reported hold failure without treating every spectral failure as elastic. This alternative was not adopted. Any future adoption would require its own model/policy identity; preserve failed v1 unchanged.

This zone **changes finite-precision branch semantics**. On0<Ftrial<=delta the exact source is plastic, while the zone returns the full trial and its identity trial-stress tangent. At Ftrial=delta the resulting approximation generally has a nonzero jump when crossing to the plastic return. `check_zone_policy.py` and `zone-policy-witness.json` show this exactly at a well-resolved smooth face, with no candidate floating execution. The stress jump is small when the source return is well-conditioned, but its tangent difference is not generally small. Tiny friction/dilation or moduli ratios can amplify residual-scale errors, so the allowance is not a universal tensor-accuracy bound.

Required distinctions: source-exact classifier/AD references versus hypothetical zone-policy classifier/AD references; equality to the new delta boundary versus source F0; admissibility residual versus stress/derivative accuracy; numerical rejection versus model physical domain. Do not retry/reclassify an unresolved spectral failure deeper outside the zone. No unique classical tangent is claimed at either nonsmooth source boundaries or the artificial zone boundary.

Smallest next checks: retain the four v1 failing holds verbatim; for any future zone policy, freeze it and test exact stored-input states just below/at/above delta and zero, repeated and rotated holds, accumulated tiny increments, stress error and all38 selected derivatives, and rollback after rejected out-of-zone gaps. A passing alternative-zone hold test cannot retroactively pass v1 or establish the full source domain.


## Adopted candidate: gap-based classifier v2

The adopted distinct v2 is **not** the elastic-zone alternative. It retains strict Ftrial<=0, all classifier inequalities, stress/gamma branches, spectral policy and acceptance bounds. Actual JSON diff from pinned final v1 is only two raw gap aliases, three classifier expressions and record id:

```
x=v1−v2, y=v2−v3
L=(x+2y)/[2G(3−d)], R=(2x+y)/[2G(3+d)]
gamma_a=[Ftrial−(1+s/3)x−(1−s/3)y]/D_a.
```

Because `t1=mean+(2x+y)/3`, `t3=mean−(x+2y)/3`, the source trial yield is `Ftrial=2s*mean−h+(1+s/3)x+(1−s/3)y`. Thus every rearrangement is an exact source identity and the exhaustive proof is unchanged. At exactly hydrostatic raw spectrum x=y0, the same computed Ftrial feeds gamma_a=Ftrial/D_a and M0; a positive Ftrial selects apex instead of invoking an inconsistent independently summed mean. This specifically addresses the observed v1 hydrostatic-hold mechanism without a tolerance elastic zone or catching arbitrary spectral failures.

`check_gap_identities.py` independently verifies all five identities on1,440 exact rational cases, including hydrostatic and huge-mean/small-gap inputs. The parent's preserved source-only v2 check report passes25 initial diagonal/rotated values,25 holds and9 invalid-parameter rejections under the unchanged4096eps gate. This auditor read and pinned that report; it did not execute Atlas. V1's four failed holds remain failed and preserved.

The v2 rearrangement improves coherence at hydrostatic input but does not establish full floating-domain robustness. Tiny nonzero gaps, cancellation near apex, overflowing gap products/denominators or different rounding between classifier and ordinary branch gammas may still reject or select adjacent branches. Full independent stored-input tensor/38-column directional/parameter/rollback references remain the next gate. No new source-domain restriction or generalized-tangent admission follows from the bounded25-case check.
