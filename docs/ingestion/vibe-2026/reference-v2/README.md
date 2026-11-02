# VIBE independent mechanical histories v2

Task REF-vibe2026-mechanical-histories-v2, owner `/root/vibe_source`, 3 November 2026. Owned output: only this new `reference-v2/` packet. The published explicit Appendix A formulation remains the exact selected identity, with its full hydraulic/thermal/mechanical/viscous terms and the source-v2 disclosed Eq27 discrepancy. This packet is an independent numerical reference study, not scientific admission or production qualification.

[plan.json](plan.json) SHA256 **6dd5a3b20eabcac10ffe82e0385d72cd37364009133a92c596898d0b322e814d** was frozen and sent to the coordinator before any v2 history observations. It prescribes the three requested histories, initial-state generation, method, precisions, partitions and unchanged tolerance gates. No production declarative candidate was read or copied and no backend, vendor, build, browser or remote operation was performed.

The scripts reuse the unchanged independent source-authored [v1 Cartesian oracle](../reference-v1/oracle.py), verified against v1 manifest SHA256 `04dd3a8831e83cada428a38479f72908f8f1ed03ea640df4b4c9826dabf0d079` before importing it. The oracle uses arbitrary precision Decimal, Cartesian tensor invariants and the original fourth-order B composition followed by a direct pivoted 6×6 solve. It does not import production model expressions or use its rank-one inverse. Earlier source and reference packets remain unchanged.

Every history starts from source-BCV parameters, e=.725, scan=.35, suction10 MPa, temperature294 K and isotropic net compression chosen independently from source algebra so OA=1.005. These are constructed illustrative contexts, not experimental specimen preparations. Controls use physical seconds, Pa and K, with compression-positive Mandel rates `[xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz]` and explicit conversion into the source compression-negative tensors.

[run_histories.py](run_histories.py) advances all eight components with classical RK4. The mechanical rate vector is `[2,-1,3,-2,1,-3]×10^-8/s`. The first history holds that vector for100s; the second reverses its sign exactly at50s; the third combines it with suction rate+2000Pa/s and temperature rate+.02K/s. The reversal is split at the event: each interval samples its own side's derivative even at the shared endpoint. Other controls are evaluated at each RK stage. The original source-positive-suction and ASBS/domain guards remain active, with no clipping, projection or numerical branch threshold.

All three histories complete at64,128,256 partitions with70 decimal digits; each256-partition run is independently repeated at50 digits. Complete initial/final stress6/e/scan, changes, endpoint controls/rates and derived quantities are retained for every run. Both128-versus256 partition convergence and50-versus70 precision convergence pass the original gates for every component:

- Stress: `.01 Pa + 1e-7 relative`.
- e and scan: `1e-9 + 1e-7 relative`.
- Dimensionless em/eM/S_M/Sr/OA/re observables: `1e-8 + 1e-7 relative`.

The64-versus128 comparison is retained as additional evidence. Gates were not changed after observation. No failures or rejected trajectories occurred in this study.

| History | Net normal stress changes [xx,yy,zz], Pa | Net shear stress changes [sqrt2xy,sqrt2yz,sqrt2xz], Pa | e change | scan change |
| --- | --- | --- | ---: | ---: |
| Mixed mechanics100s | [−538.044681,−1322.014203,−276.721507] | [−522.646348,+261.323174,−783.969522] | −.0000068999862000184 | zero |
| Mechanical reversal100s | [−1507.603262,−1507.662555,−1507.583497] | [−.039528764,+.019764382,−.059293145] | approximately zero | zero |
| Coupled mechanical/THM100s | [−9034.672296,−9818.686894,−8773.334096] | [−522.676399,+261.338200,−784.014599] | −.0000068999862000184 | +.154392591834381 |

The nonzero residual stress after reversal records constitutive history and viscosity despite zero net prescribed mechanical strain. The tiny numerical e residual on that path is about4.46×10^-47. As an additional analytical check independent of the stress oracle, `verify_results.py` compares e against `(1+e0)*exp(-trace(E_dot)*duration)-1` for the two constant-rate histories and against e0 for the exact reversal. These checks pass the original scalar gate. All six stress components change in all three histories.

Reproduce without overwriting frozen originals:

```sh
python3 -B docs/ingestion/vibe-2026/reference-v2/verify_results.py
python3 -B docs/ingestion/vibe-2026/reference-v2/run_histories.py --output /private/tmp/vibe-reference-v2-reproduction
```

Only standard-library Python is needed. The output is deterministic. The manifest pins this packet and the dependency identity. Production comparison, integration-budget choices, restart/rollback, native/Wasm agreement, scientific review and public protocol qualification belong to the coordinator. This three-history study does not prove arbitrary nonproportional loading, every material parameter range or experimental agreement.

Cleanup: no temporary output directory was created by this worker, and no process, dependency environment, worktree, build, downloaded source or preview resource was created. All files in this packet and pinned v1 dependencies remain necessary for active reference consumers. No disposable resource or uncertain deletion remains.
