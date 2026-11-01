# Information requirements for an interface comparison

This is a development task design, not an admitted benchmark panel. The [2016 interface source review](source_formulations/hypoplastic-interface-2016.json) exposes requirements that a bulk stress–strain inventory does not cover. Keep them as source-located descriptions while the atlas interface representation evolves.

## Define the experimental task before choosing models

| Input or observation | Required declaration |
| --- | --- |
| Tangential loading | Slip components, units, ordering, reversals, coordinate frame and control mode |
| Normal constraint | Prescribed load/traction, prescribed normal displacement, or a declared stiffness relation |
| Normal stiffness | Whether the derivative uses force or traction, and displacement or strain; area and thickness conversions where used |
| Local strain mapping | The thickness, geometry and finite/incremental convention used to convert displacement to constitutive input |
| Preparation and initialization | Initial density, tractions, any in-plane stresses, history and how each was measured, inferred, assumed or fitted |
| Surface description | Structural material, measured roughness and its conversion to any model coefficient |
| Evaluation channels | Tangential traction versus slip and normal displacement or traction, according to the imposed controls |

Do not treat a prescribed channel as an independent prediction. Under a prescribed normal load, for example, normal displacement can be an outcome; under prescribed normal displacement, normal traction can be an outcome. A stiffness-controlled task requires its apparatus relation to be part of the replay and provenance.

## Keep stiffness and thickness conventions explicit

As an illustrative conversion, suppose a study explicitly adopts signed engineering normal strain \(\varepsilon_n=u_n/d\), with constant thickness \(d\) and matching compression signs. Then

\[
K_\varepsilon=\frac{d\sigma_n}{d\varepsilon_n}
=d\frac{d\sigma_n}{du_n}=dK_u.
\]

Here \(K_\varepsilon\) has pressure units and \(K_u\) has pressure-per-length units. If stiffness is force per displacement, specimen area also enters. This conditional example is not an initialization or kinematic rule inferred for the reviewed formulation. Variable thickness, other strain measures or opposite displacement signs require their own derivation.

A thickness obtained by matching a response consumes calibration information. Report it separately from independently measured geometry and propagate its role into subsequent predictions. Do not compare two stiffness numbers merely because both are labelled CNS or K.

## Separate mechanisms from variants and evidence

Pin the interface formulation, its host law, roughness scheme and initialization before defining a parent–extension comparison. Preserve any unresolved source statements; the present source review cannot establish a complete equation set. Extra model inputs can be scientifically necessary without being independently measured or identifiable.

Any eventual comparison should use the same material–surface pair and declared loading tasks, with separate whole-test calibration and evaluation. Review the original experimental methods and data access before admitting the literature curves. A source's reported comparison remains source evidence until independently reproduced; it does not establish a result for the atlas implementation.
