# SANISAND research variant: mixed-control verification

Status: **research software evidence; independent scientific review pending**. This tests the existing generic axisymmetric controls with the [parent-reset research variant](sanisand-2004-parent-reset-be.md). Neither the material equations nor the compiler, solver, reset contract or control tolerances changed. Original SANISAND event reconciliation and full admission remain open.

## Controls and replay

The [native harness](../../tests/native/sanisand_mixed_controls.cpp) calls the common `controlled_step` function for two protocols, starting from `sigma=100000 I Pa`, `e=0.7`, and zero histories:

- Protocol 1: prescribe the axial strain increment, solve equal radial strain increments to maintain radial stress `100000 Pa`.
- Protocol 3: prescribe the change in signed triaxial `q=sigma_xx-(sigma_yy+sigma_zz)/2`, solve an axial strain increment with radial increments equal to minus half the axial increment, giving zero total volume change.

Both use four caller legs with factors `1,-2,2,-1`. The base leg is axial strain `0.001` for protocol 1, and deviator stress `10000 Pa` for protocol 3. Each leg uses 16, 32 or 64 increments. These are project verification paths, not experimental calibration or published benchmark reproduction. Protocol 3 has a prescribed stress increment at each caller boundary; accumulated stress differs slightly from the ideal waveform because of the existing per-increment control tolerance.

The common outer solver evaluates all candidate strains from the same parent. The parent-reset guard can therefore select different branches in different trial calls without accumulating trial memory. For every successful control increment, the harness independently calls `integrate` from the original parent with the final selected strain increment and requires exact numeric state equality with the controlled result. It also checks that the caller's parent remains unchanged. These replay assertions test isolation, not an independent constitutive implementation.

All **896 cyclic mixed-control increments** succeed. They include 18 memory resets, three per protocol/partitioned path. Every accepted material increment uses one internal substep. No new successful-cutback or failed-outer-control evidence is claimed here; the [earlier reset rollback investigation](sanisand-2004-parent-reset-be.md) remains separate.

The existing outer tolerance for these records is `max(1,abs(reference))*1e-8=0.001 Pa`, with `reference=100000 Pa`. The largest radial-stress residual is about `0.000995212 Pa`; the largest prescribed-q-increment residual is about `0.000967252 Pa`. The largest scaled material residual is `6.7583e-12`, below the common constitutive tolerance `2e-10`. Constitutive Newton residual and outer control residual measure different equations and retain separate units/scales in the record. The verifier also tracks cumulative q error and bounds it by the number of accepted stress increments times the per-increment tolerance; it does not silently identify incremental control with exact cumulative control.

Successive endpoint changes under step halving have ratios about `0.502` (fixed radial stress) and `0.515` (prescribed q at zero volume). These support first-order convergence on the selected parent-partitioned paths. They provide no absolute error bound, complete update tangent, event-location accuracy or independent reference trajectory.

## Independent elastic cases

Two additional small cases stay inside the yield cone and permit scalar analytical solutions. They test absolute responses alongside replay/refinement. The source elasticity is Eq. (3), p. 623, of [Dafalias and Manzari (2004)](https://doi.org/10.1061/%28ASCE%290733-9399%282004%29130%3A6%28622%29); project finite discretization and constant-solid-volume closure remain those documented for the [research material](sanisand-2004-fixed-memory-be.md).

For the fixed-radial-stress case, prescribe `Delta_epsilon_xx=1e-6`. The exact endpoint backward-Euler elastic solution has radial strains `-nu*Delta_epsilon_xx`, because the ratio `K/G` is constant. Define

```text
e_f = (1+e_initial)*exp(-(1-2*nu)*Delta_epsilon_xx)-1
u_initial = sqrt(p_initial/p_at)
b = 2*G0*(1+nu)/3 * (2.97-e_f)^2/(1+e_f) * Delta_epsilon_xx
u_f = (b+sqrt(b^2+4*u_initial^2))/2
p_f = p_at*u_f^2
Delta_sigma_xx = 3*(p_f-p_initial)
Delta_sigma_yy = Delta_sigma_zz = 0
```

This is an analytical solution of the selected finite residuals, not the exact continuous elastic path. The reference checks final stress to `0.002 Pa`, radial strains to `1e-11`, and void ratio to `5e-11`. These comparison tolerances account for the existing `0.001 Pa` outer stopping tolerance; that stopping tolerance was not changed.

For the zero-volume elastic stress case, prescribe `Delta_q=100 Pa`. Pressure, void ratio and `G` stay constant, and the analytical strains are `Delta_epsilon_xx=Delta_q/(3G)`, with radial increments `-Delta_epsilon_xx/2`. The stress increments are `(2*Delta_q/3,-Delta_q/3,-Delta_q/3,0,0,0)`. Compare strains to `1e-11`, stress to `0.001 Pa`, and void ratio to `1e-12`. Both elastic cases check that persistent histories and the transient multiplier remain at their elastic values within the declared solver comparison tolerance.

## Retained evidence and reproduction

The [manifest](../../catalogue/investigations/sanisand-mixed-controls-v1/manifest.json) pins the unchanged model, compiler/engine/harness/verifier sources, generated header, binary and compressed full 898-record matrix. The [Python verifier](../../tools/verify_sanisand_mixed_controls.py) checks protocol requests, path continuity, strain constraints, radial symmetry, independent memory preparation, all successful finite residuals, analytical references, control residuals and refinement. Four [test groups](../../tests/test_sanisand_mixed_controls.py) additionally reject corrupted controls, memory, response, replay flags, ordering and unrecorded partitions. The combined SANISAND Python suite passes 30 groups.

```sh
python3 tools/verify_sanisand_mixed_controls.py prepare /private/tmp/atlas-sanisand-mixed-small
c++ -std=c++20 -O0 -Icpp/include -I/private/tmp/atlas-sanisand-mixed-small/generated /private/tmp/atlas-sanisand-mixed-small/probe.cpp -o /private/tmp/atlas-sanisand-mixed-small/probe
/private/tmp/atlas-sanisand-mixed-small/probe > /private/tmp/atlas-sanisand-mixed-small/output.json
python3 tools/verify_sanisand_mixed_controls.py verify /private/tmp/atlas-sanisand-mixed-small/output.json --output /private/tmp/atlas-sanisand-mixed-small/verification.json
```

Preparation and verification never compile/run native code. Two small compilations and separate bounded runs completed normally: the first tested cyclic controls, and the second added the two analytical cases. No full external build was attempted. Native/Wasm parity, general six-component mixed controls, failed outer solves, nonsmooth derivatives, full original-model identification, independent matching references and browser execution remain open. This is progress toward SAN-03/05/06 and NUM-01/02/04; those milestones are not closed.
