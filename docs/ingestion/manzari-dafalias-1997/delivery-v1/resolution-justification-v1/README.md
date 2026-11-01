# Independent cross-path source BE resolution justification

NUM-md1997-resolution-justification-v1 owns this new directory only. This is independent source-derived numerical justification for a separately identified2048/4096backend study, not backend execution, scientific approval or replacement of failed128/512evidence. No production model residual/evaluator/compiler/interpreter or compiled artifact was imported or called. Earlier references, policies and failures remain unchanged.

## Frozen inputs and scope

POLICY.md was written before this study ran. The exact active v4 requests are SHA256dc02829df6c1e1b3500781bb5c3c7dc6728897a64b2cd50bd56ef60d99a89d10. All14source paths were evaluated at both requested resolutions: dense/loose, compression/extension, undrained/drained axisymmetry (8), and dense/loose at interior cos3theta0,+.5,-.5 (6). The exact checkpoint/control coordinate arrays are read from the frozen request file. Interior increments were separately audited to equal delta-coordinate times the saved Mandel direction exactly in binary64; maximum discrepancy is zero. Only the prescribed grids and source reference values are read from that file, not production equations or compiled outputs.

Source equations are the original1997constant-m law, as independently derived in ../reference-v1/ and its interior-lode-v1/. Table1plus p266extension coefficients are fixed; pat100kPa is the explicit project choice, distinct from pref160kPa. This script is not a general parameter-family verifier. Original first b_ref choice, fixed-initial-e0 small-strain volume relation, and source loose-state zero-dilation restriction are retained.

## Independent BE equations

For a fixed trace-free unit direction n, let alpha=beta*n and s=dev(sigma):n. Active source yield gives s=p*(beta+S*m), S=sqrt(2/3). Source image projections beta_b,beta_d follow original Eqs17–21 at the direction's translated Lode angle. Put b=beta_b-beta, h=h0*abs(b)/(b_ref-abs(b)), D=A*(beta_d-beta), with the original override. For an isochoric total increment delta_t*n, backward Euler applied directly to original stress/backstress rates yields:

- `p-p_n + gamma*K(p)*D(p,beta) = 0`.
- `p*(beta+S*m)-s_n - 2*G(p)*(delta_t-gamma) = 0`.
- `beta-beta_n-gamma*h(p,beta)*(beta_b(p)-beta) = 0`.

The three unknowns p,beta,gamma are solved together. No division by h*b occurs, so the peak/softening limit does not introduce the singular parameterization encountered and retained in the previous bounded diagnostic. Axisymmetric undrained increments map delta_t=z*delta_axial/S and n=z*(2,-1,-1)/sqrt(6); interior increments use their full shear-bearing direction. Elastic interior/wedge response is evaluated before activating yield, with exact source first-yield coordinates included by the frozen grids.

For drained axisymmetry at constant radial stress160kPa, let signed q=3*(p-160), a=scalar alpha_ax-alpha_rad=q/p-z*m, and n=z*(2,-1,-1)/sqrt(6). The source backstress rate is a'=L*h*(z*B-a). With endpoint pressure modulus G=K for this calibration, pressure and deviatoric elastic strain plus source plastic flow give

`v=(p-p_n)/K + gamma*D`,

`delta_axial=(p-p_n)/(3K)+(q-q_n)/(3G)+gamma*(z*S+D/3)`,

`e-e_n+(1+e0)*v=0`,

`a-a_n-gamma*h*(z*B-a)=0`.

Solve p,e,gamma together and reconstruct radial increment(v-delta_axial)/2. The same infinitesimal fixed-e0 relation holds in elastic preparation. Final stress/backstress tensors are reconstructed from the independent scalar endpoint and fixed direction. The implementation does not assume the continuous source ODE and finite BE solution are identical.

A small standard-library3x3finite-difference Newton solver with bounded backtracking solves each local source BE system. Every completed root must satisfy max normalized mechanical/kinematic residual<=1e-11, positive pressure and hardening-distance denominator, and nonnegative plastic multiplier. The actual maximum local normalized residual was9.9986e-14. No root failed or required a tolerance change.

## Results under unchanged source gates

All28case/resolution combinations complete. All200full-state checkpoint comparisons satisfy the original stress100Pa+1%*max(1000Pa,abs(component)), alpha.002, e.0002 and axis radialstrain.0002limits. All86fine/coarse refinement checks satisfy the original rule (fine error strictly less than coarse, or both normalized errors below1e-5).

The largest normalized error is.5117032at2048and.2569232at4096, both for loose undrained compression. Every path's worst normalized error decreases with refinement, approximately by the expected factor2for first-order BE. Detailed per-path values are in summary.json; complete checkpoint tensors, all normalized component-group errors, root statistics and refinement decisions are in results.json. There are no omitted, failed or downgraded path cases in this source-only justification.

These results support carrying out the separately frozen2048/4096actual qualification with unchanged gates. They do not guarantee an adaptive runtime chooses the same material partition or that mixed control succeeds. The separately traced protocol1partition-derivative issue remains a generic runtime task. Native/Wasm agreement, source accuracy, derivatives, restart, covariance, rollback, ordinary regressions and scientific review still require their actual evidence. No original128/512failure is excused by these results.

## Reproduce and handoff

Run `python3 docs/ingestion/manzari-dafalias-1997/delivery-v1/resolution-justification-v1/source_be.py` from repository root. It overwrites only this directory's reproducible results.json. No compiled code runs. inputs.json binds frozen requests/manifest and independent source references; manifest.json binds this new packet. Exact files are POLICY.md, README.md, source_be.py, results.json, summary.json, inputs.json and manifest.json. Parent's next action is independent prospective review and actual serial backend qualification under its separately assigned runtime/build scope.
