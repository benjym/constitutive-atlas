# Prospective SLS executable qualification v1

Frozen before any compiled SLS observations. Source closure and full v0.3 validation precede serial single-target builds. No model-specific C++ kernel. New direct and scheduled observations are retained with exact source/model/driver receipts and partial failures. No changing limits after observing failure.

## Reference and cases

Use independent closed-form exponential evolution for a single Maxwell shear branch in parallel with an equilibrium shear spring and elastic bulk. Complete state and stress are checked separately. Constant-rate arbitrary six-component paths cover relaxation times .2,2,20s and durations .01,.5,4 times tau. Pure hydro, pure shear, zero-rate prestressed hold and exact zero hold are included. Prescribed schedules cover held strain relaxation, held stress creep, load/hold/reversal and a nonzero-time full-state restart. Initial internal branch stress must be traceless and compatible with explicit strain; no arbitrary isotropic branch stress is admissible.

For a constant rate D and overstress q, q(t)=exp(-t/tau)q0+2G1*tau*(1-exp(-t/tau))*dev(D); strain=eps0+D*t. Stress=K tr(eps)I+2Ginf dev(eps)+q. Under held total stress, mean strain is constant and deviator strain tends to dev(stress)/(2Ginf) with creep time tau*(Ginf+G1)/Ginf; branch stress follows from stress decomposition. Piecewise paths compose these exact solutions without fitting.

## Gates

Positive direct cases: every component finite, state strains absolute error <=2e-8, branch stress and observed stress absolute error <=1Pa, returned endpoint time within1e-12*max(1,abs(t)); all six components checked, not only invariants. Schedule cases: state strains <=2e-7, branch stress and observed stress <=15Pa; imposed strain/control quantities checked to same bounds. Coarse/fine settings1e-4/1e-8 must reduce nonzero relaxation error, fine bound15Pa; no general order claim. Independent dissipation identity and rotation/Mandel checks run before build.

Negative/recovery: nonpositive modulus/relaxation time, omitted state, nontraceless branch history, zero/negative duration, deliberately exhausted substep budget. Failures must reject; integration failures with represented parent return full unchanged state/time; budget failure must show accepted internal work before rollback. Same-process Wasm valid call after every failure recovers and repeated identical trials have exact responses. Returned failure inputs must remain unchanged. Restart resumes complete persistent state at a nonzero clock with equivalent continued reference.

Native then Wasm at the same frozen case/settings; Wasm built only after native passes. Each positive/negative call repeated twice. State and observable parity absolute bound2e-7 for strain,1e-6Pa for stress (separate from reference accuracy); metadata/messages/rollback semantics checked, timings excluded. Retained saved-evidence check is read-only. Browser UI and experimental claims are excluded. Scientific review is a fresh separate agent after qualification and all findings must be retained.
