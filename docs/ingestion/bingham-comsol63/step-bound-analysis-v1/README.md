# Bingham source-only maximum-step analysis v1

This is a post-observation diagnostic, authored after v1 direct-midpoint failures and after the coordinator reported reversal failures in the ongoing v2 BE campaign. It is not a frozen qualification study, a revised acceptance gate, or permission to execute new requests. No candidate, source packet, v1/v2 policy, runtime or prior evidence is changed. A separate agent must review any later prospective study. The arithmetic below uses source equations and the fixed original inputs, without fitting a cap to saved numerical errors. `analyze.py` runs Python arithmetic only; `results.json` binds its source inputs. No compiled artifact was executed.

## Source and host

The source packet's readable COMSOL6.3 Bingham equation-image locators are theory039 images016,022,057,059,060,076–078 and the interface's viscosity entry. See [the source crosswalk](../source-v1/README.md). They give q=√(3s:s/2), εvp′=3s(q−Y)+/(2ηq), α′=(q−Y)+/η. Positive K,G,Y,η and fixed-frame small strain are essential. These are project-selected nominal parameters, not vendor calibration.

For radial s=zN, N:N=2/3, prescribed deviatoric strain rate dN, q=|z| and

    z′ = c − a S(z),  c=2Gd, a=3G/η=1/τ,
    S(z)=sign(z)(|z|−Y)+, α′=(|z|−Y)+/η.

Thus τ=η/(3G)=2/3s at G=10MPa,η=20MPa·s. The elastic signed loading rate is c in Pa/s; d is the scalar coefficient in the normalized radial direction, not an arbitrary single tensor component. Original108 cases have d∈{0,.003,−.012}/s, z0∈{0,99900,100000,100100,200000,−200000}Pa, T=2s, with six fixed direction seeds. Therefore max|c|=240000Pa/s and max|z′(0)|=390000Pa/s. K has no effect on these zero-volume scalar trajectories.

`cpp/include/atlas/schedule.hpp` controlled_residual/controlled_backward_euler/advance_controlled shows that accepted output is the **two half-step** BE solution, and the candidate parent interval must be ≤ `maximum_step=M`. Consequently every accepted actual BE step H≤M/2. The rejected full-step solution is not committed. These bounds concern accepted steps, not the saved-output interval or the source's vendor FE solver. Steps also must satisfy Newton, minimum-step, depth and accepted-substep budgets; a cap cannot guarantee their success.

## A conservative global exact-BE bound

For a constant radial loading segment f(z)=c−aS(z) is continuous, Lipschitz and nonincreasing. Its implicit resolvent is nonexpansive. The exact scalar trajectory is monotone toward equilibrium (or stationary), and |z′| is nonincreasing. It follows that TV(z′)≤|f(z0)|, including continuous yield crossings; there is no derivative impulse at yield.

The local exact-solution BE residual on [tprev,t] is ∫z′(u)du−h z′(t), whose magnitude is ≤h∫|z″(u)|du. Nonexpansiveness and summation give, at every endpoint,

    Ez ≤ H·TV(z′) ≤ H F0,  F0=|f(z0)|.

All six stress errors are |Ni|Ez, with |Ni|≤√(2/3). Prescribed total strain is exact in this ideal arithmetic. The viscoplastic component error is |Ni|Ez/(2G). For L(z)=(|z|−Y)+/η, its Lipschitz constant is1/η, and TV(L(z(t)))≤TF0/η. Comparing BE's right-endpoint α sum to the exact integral, and separating trajectory error from quadrature error, gives

    Eα ≤ (T/η)Ez + H TV(L) ≤ 2HTF0/η.

These are deliberately conservative complete-segment bounds for exact implicit solves. Using only the unchanged absolute α floor3e−7 gives H≤3.846153846e−6s, or M≤7.692307692e−6s. This is **not an adopted policy**. It leaves no allowance for finite nonlinear solves/roundoff, and is costly: dyadic division of2s at this cap alone yields524288 accepted halfsteps, before any tighter adaptive rejection. It is insufficient to promise success under the1,000,000 accepted-step budget.

Newton residuals cannot simply be assumed zero. Here state scales are1 and the source's stopping residual bounds each real state balance defect by nonlinear_tolerance·min(h,1), conditional on interpreting the computed residual as its exact real counterpart. Summed state forcing then scales with elapsed time rather than accepted-step count. For example, for all-strain control its induced deviatoric stress perturbation is at most4G√6·tolerance·T in Euclidean Mandel norm, by contraction, and its additional α effect at most6G·tolerance·T²/η + tolerance·T. Binary64 residual evaluation/cancellation and serialization need their own allowance; this packet does not certify them. The ideal global cap above therefore is not a certified compiled-host guarantee.

## The missed active-exit contribution

A sharper bound addresses the specific loss of initial active flow when an inward step starts outside yield but its BE endpoint is inactive. It does not bound all integration error.

Take the positive branch without loss of generality, v=|c|>0, initial overstress δ=zstart−Y>0. Before exit, w=z−Y obeys w′=−v−w/τ. Its exact exit time is tc=τ log(1+δ/(vτ)). If an exact BE endpoint is inactive, BE assigns no viscoplastic increment and zBE=zstart−vH, hence δ≤vH. The positive exact accumulated increment omitted by that step is

    I = ∫₀ᵗᶜ w/η dt
      = (δ−v tc)/(3G)
      ≤ vτ²/η · [H/τ − log(1+H/τ)]
      ≤ vH²/(2η).

The first bound increases with δ, and the last uses x−log(1+x)≤x²/2 for x≥0. This captures the lost **accumulated** history even if the stress later recovers. At the step endpoint, its scalar stress contribution is3GI; its vp component contribution is(3/2)|Ni|I. Relative to the exact state at that endpoint, later exact radial evolution is contractive in z. Over remaining time≤T, the additional α difference is ≤(3GT/η)I; therefore this isolated defect's eventual α effect is bounded by(1+T/τ)I. This is a decomposition, not a sum-free proof of the actual numerical trajectory: other discretization and nonlinear errors still accumulate.

For the proposed source-scaled formula

    M = min(τ/1024, Y/(2G max|d|·1024)), H≤M/2,

nominal max|d|=.012/s gives M=0.0004069010416667s and H≤0.0002034505208333s. The arithmetic yields:

- omitted exit α≤2.483526866e−10;
- immediate scalar stress contribution≤0.007450581Pa, hence every stress component≤0.006083374Pa;
- every vp component contribution≤3.041686792e−10;
- eventual isolated α contribution over2s≤9.934107463e−10.

These are below the original absolute physical floors3e−7state/3Pa. Even conservatively substituting M itself for H gives omitted α≤9.934107463e−10. The formula's1024 is an explicit proposed resolution factor, not a value uniquely dictated by COMSOL; the inequalities make its physical consequence inspectable without an observed-error search. The cap alone yields16384 dyadic accepted halfsteps per2s request. Adaptive refinement may require more, and this count excludes discarded full-step work and Newton iterations.

For any of the original constant radial histories there is at most one active exit. A reversal can subsequently enter the opposite branch, but the elastic transit spans2Y/v≥2048M under this formula; a capped step cannot hide exit and opposite entry together. A truly inactive-start, inactive-end BE step under constant radial forcing has no missed intermediate active excursion. Holds have no finite active exit and d=0 uses only the τ restriction. These observations do not bound partially active endpoint quadrature error, accumulated smooth-branch BE error, or the adaptive estimator's global accuracy. The existing full-vs-two-halves local estimator is not a proof that those remaining errors meet the unchanged physical gates.

## Scope limits and smallest next action

The event bound applies to each constant **radial strain-rate** segment with known direction and rate, including the original108 source cases. At loading changes a state need not be coaxial with the new rate. The scalar proof then does not apply; no guarantee for the noncoaxial history, mixed controls or every public mode follows from these108 bounds.

A possible vector extension for prescribed constant six-component strain rate uses s′=b−a(1−Y/q)+s, b=2G dev(D). The radial soft-threshold operator is monotone in Mandel norm; exact BE remains contractive. A weaker bound follows from ∫||s″||dt≤aT||s′(0)||, leading to Es≤HaT||s′(0)|| and Eα≤H√(3/2)||s′(0)||(aT²+T)/η. This is an analytical starting point, not a checked host policy. Stress control changes the coupled algebraic problem and requires a separate derivation. Constant all-stress creep is linear in time in the ideal exact law; that observation does not qualify the actual coupled solver.

The finite model parameter envelope1e−12..1e30 supplies no practical global step, duration or rate bound. τ and elastic transit time can be arbitrarily small relative to the public clock/minimum step or budgets; max|d| is not defined by those parameter bounds. A fixed nominal cap cannot support all public values. Any future policy must explicitly cover its parameter/rate/history range and fail honestly when min-step/depth/substep budgets prevent it. This analysis proposes no model clamp or clipping.

The smallest next action is independent review of these inequalities and an explicit error decomposition, then a separately identified prospective study/policy if the coordinator chooses one. Keep v1/v2 failures and gates unchanged. In particular, the inexpensive event cap offers an a priori bound on a diagnosed missing-flow contribution; it is **not an overall accuracy guarantee** and is not yet a public-interface qualification.

Reproduce source-only arithmetic from the isolated worktree root:

`python3 -B docs/ingestion/bingham-comsol63/step-bound-analysis-v1/analyze.py`
