# Prospective full-formulation source decision — review requested

This is a proposal for independent assessment, not model approval or an assertion of author intent. No new model has been selected or implemented. Source: Mašín author manuscript dated 26 November 2013, DOI 10.1680/geot.13.P.065, SHA-256 `2eb8598297e3ac9cf245161f56674d6cef622b35fc612adc89dc129568b55202`. PDF pages 3, 4, 9, 10 and 11 were visually inspected in this source follow-up. Publisher-version equivalence remains unverified.

## Full intended target

Retain anisotropic base stiffness, the proposed Eq49 exponent in both density factors, and the complete Appendix B IGS law, including both loading branches and six memory components. Stress6 + void ratio1 + IGS6 gives thirteen retained scalars. An explicitly supplied fixed material plane and zero-spin/small-strain laboratory are platform restrictions; no fabric transport is invented. The historical printed-Am seven-state realization stays unchanged and does not qualify this target.

## Two source contradictions and a possible explicit reconciliation

Use `r=alpha_E`, `v=alpha_nu`, `g=alpha_G`, `nu=nu_pp`, `B=1-nu-2*r*nu^2/v^2`. For the source symmetric fourth-order action, contraction gives

```
T = trace(L:I) = 3*a1+9*a2+6*a3+2*a4+a5
  = 2*r+1 + nu*(2*r+4*r/v) + nu^2*(4*r/v-1)
T-Am_printed = 2*r^2*nu^2*(1-1/v^2).
```

The existing independent coefficient review already confirms this discrepancy. A possible new **source-reconciled** identity would use `Acal=T` in the barotropy factor so that the source isotropic-unloading calibration is internally consistent. It would not claim literal Eq14 fidelity or equivalence to the final publisher or vendor implementation. Reviewer must check that the isotropic-unloading derivation actually requires this contraction; algebraic inequality alone does not establish which source quantity should change.

With compression-positive mean effective stress `p`, Eq15 is `fs=9*p/(2*Acal)*(1/lambda_star+1/kappa_star)`. At zero IGS, Eq16 gives `M0=mR*fs*L`, and Eq17 gives `Gtp0=mR*fs*r*B/(2*g)`. The target Eq18 is `Gtarget=pr*Ag*(p/pr)^ng`. Therefore solving this calibration yields

```
mRcal = Gtarget * 4*Acal*g/(9*p*r)
        * lambda_star*kappa_star/(lambda_star+kappa_star) / B.
```

Printed Eqs19 and56 instead contain `2*p*r` in that denominator, yielding `Gtp0/Gtarget=9/2` on substitution. A new reconciled identity could use the calibration-derived expression above, while explicitly disclosing both printed discrepancies. This is not permission to silently fix historical bytes.

## Appendix B branch transcription to assess

In the source's own stress/strain signs, set `h=delta/||delta||` for nonzero delta and `h=0` at delta=0; `rho=||delta||/R`, `q=h:D`, `c=rho^chi*mT+(1-rho^chi)*mR`, `mT=mrat*mR`.

```
q>0:  sigma_dot = c*fs*L:D
                    + rho^chi*(1-mT)*fs*(L:h)*q
                    + rho^chi*fs*fd*N*q
       delta_dot = D - h*rho^beta_r*q
q<=0: sigma_dot = c*fs*L:D
                    + rho^chi*(mR-mT)*fs*(L:h)*q
       delta_dot = D
```

Here `N` must be identified explicitly from the base Eq34, rather than borrowed from an unrelated IGS implementation: its product with `fs*fd` must reproduce `-fd/fdA*A:d`. Confirm tensor-product order against image Eq52. For a compression-positive Atlas representation, both source stress/strain and memory signs must be mapped consistently; no signed-memory convention is selected in this proposal.

At delta=0, rho=0 and q=0, so the limit is Eq16 and memory starts with D. At rho=1 and q>0, radial memory growth is zero in the continuous law. This does not justify clipping discrete overshoot, projecting state, or replacing the branch. The integration contract must state domain handling and transactional rejection. Source table1 provides R and other IGS example parameters, but its image still needs inspection before transcription. Full scalar state/parameter domains, initialization/preparation and isotropic continuation still require an explicit crosswalk.

## Independent decision requested

1. Independently verify the two calibration derivations and Appendix B branch transcription against the private original page images, not just this proposal.
2. Decide whether an explicitly named full thirteen-state source-reconciled formulation is a defensible candidate for implementation, or whether a primary-source ambiguity still blocks it. Identify a smaller bounded next source action if blocked. Do not infer author intent or final-version equivalence.
3. Check whether the proposal preserves the requested model's mechanisms and useful scope. A base-only shortcut is outside this assignment.
4. Identify missing source definitions, sign mapping, boundary/initialization requirements and independent prospective numerical gates needed before implementation.

Any source-scope acceptance here is not E5 admission: there is no candidate definition, frozen numerical protocol, compiled evidence, app integration or live delivery. Original 37-rate/16-recovery observations and the finite-path FAIL4/144 per backend remain historical evidence; the separate passing hydro study does not erase that failure. No build/material slot is claimed, no copyrighted PDF is published, and no archives are created.
