# Requirements crosswalk to schema v0.3

This is a non-executable requirements crosswalk, not a model-v0.3 instance. No complete general Original Cam Clay profile has been selected. The [current schema](../../../../schemas/model-v0.3.schema.json) and [formulation contract](../../../FORMULATION_CONTRACT.md) are the target; no historical record is migrated.

| Requirement established for this fixture | v0.3 representation or unresolved decision |
| --- | --- |
| Quasi-static rate independence; derivatives per distortion increment | `formulation.time_dependence = strain_path`; this RK4 independent variable is dimensionless path order, not seconds. A physical-time rate profile would misrepresent the fixture. |
| Smooth positive-q wet-side differential constraints | `strain_path_rate` describes the local mathematical fragment. Its general executable profile currently specifies `small_strain_3d`; a full3D source closure is not established by this axisymmetric reference. No executable profile is selected here. |
| Fixed-principal-axis infinitesimal specimen, zero spin | Restricted small-strain axisymmetric scope. `fixed_spatial` and `objective_rate = none` describe this zero-spin fixture only; neither grants finite-rotation support. |
| Compression-positive effective p and signed axial q | Explicit stress/strain sign and effective-stress scope are required. The specimen reconstruction is sigma_axial=p+2q/3 and sigma_radial=p-q/3. It does not establish general changing-principal-direction behavior. |
| Undrained volume and epsilon_s=2/3(epsilon_axial-epsilon_radial) | For a future restricted Mandel adapter, an increment d epsilon_s maps to `[d epsilon_s, -d epsilon_s/2, -d epsilon_s/2, 0, 0, 0]`. This is infinitesimal volume control, not finite-volume kinematics. |
| State `(p, q, c)` with c=ln(pc/p_ref); constant specific volume supplied | These are scalar reference coordinates, not a complete six-component runtime stress binding. A candidate implementation must declare stress binding, persistent history, constraints and state redundancy explicitly. |
| Analytically prepared positive-offset seed | Full state and parameter/reference-pressure identity are required. `initialization` must not silently set pc=p, treat a missing history as zero, or label these illustrative inputs as a matched specimen. |
| Zero recoverable shear strain | This is constrained shear compliance, not G=0. Finite-G elasticity would define an augmented variant. A mixed-control constraint and corner/active-set design are still required before production integration. |
| q=0 vertex, critical mechanism, unloading and extension | Deliberately excluded from this smooth reference. General branch selection, loading-control rank, finite update/tangent and transaction behavior remain separate tasks. |

The source supports this selected trajectory; the existing scalar/log operations can express much of its algebra. That is not a finding that every necessary generic engine capability exists, or that a new primitive is necessary. Establish the exact full closure and residual/control requirements before changing the schema or solver. Do not use the existing physical-time axisymmetric profile merely to evade the missing strain-path/general-closure decision.
