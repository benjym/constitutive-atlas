# Nakai–Hinokio subloading clay model (2004)

The model describes how clay compresses and shears under three-dimensional effective stress. The intermediate principal stress affects both deformation and strength. A density index tracks how far the current state is from the reference compression surface. This lets the same law represent normally consolidated and overconsolidated states. The model splits plastic deformation into two parts: flow in a modified stress space and additional compression along some loading paths.

In the laboratory, load **Nakai–Hinokio · Table 2 clay · drained**. Start at an isotropic effective pressure of 98 kPa, with void ratio 0.83 and a zero density index, then apply 1% axial compression at fixed lateral effective stress. Compare the rise in deviator stress with the change in volumetric strain. The preset includes the complete starting state, including the tensor used to transform the effective stress. Changing initial pressure or density independently may create a synthetic state that no longer fits the same reference compression line.

| Input | Symbol | Unit | Interpretation |
| --- | --- | --- | --- |
| `p_ref` | pᵣ | Pa | Reference pressure and stress scale. Keep it consistent with the chosen reference state. |
| `Cc` | Cc | 1 | Normal compression slope divided by one plus the reference void ratio. |
| `Ce` | Ce | 1 | Swelling and recompression slope on the same basis. It controls elastic bulk stiffness at a given pressure. |
| `e_ref` | eᵣ | 1 | Fixed reference void ratio used to scale volume change. It differs from the evolving void ratio. |
| `Rcs` | Rcs | 1 | Principal stress ratio at critical state in triaxial compression. |
| `beta` | β | 1 | Shapes the yield surface in the modified stress space. |
| `a_density` | a | 1 | Controls how the density index affects the clay response. |
| `nu` | ν | 1 | Elastic Poisson ratio, which sets shear stiffness relative to bulk stiffness. |

This is the one-coefficient clay formulation with Appendix V, for small strains in fixed axes. The short demonstration uses source parameters with an illustrative starting state. Sustained post-peak softening and general cyclic accuracy are outside the tested scope. The law has no pore-fluid evolution, finite rotation, or creep. The separate sand formulation is not included.

Related: Matsuoka–Nakai describes the strength framework; Nakai–Hinokio adds the elastic response, plastic flow and history update of a full clay law. Reference: [Nakai and Hinokio (2004), Table 2, equations 40–52 and Appendix V](https://doi.org/10.3208/sandf.44.2_53). Local provenance: [source decisions](working-v1/SOURCE_DECISIONS.md) and [dossier](../../models/nakai-hinokio-2004-clay-appendix-v-be.md).
