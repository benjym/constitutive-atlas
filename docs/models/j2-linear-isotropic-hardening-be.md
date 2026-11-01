# J2 plasticity with linear isotropic hardening

The [exact v0.3 research definition](../../models/research/j2/j2-linear-isotropic-hardening-be.json)
implements the rate-independent, three-dimensional linear-isotropic-hardening
specialization of OpenSees J2Plasticity. It uses constant bulk/shear elasticity,
associated von Mises flow, persistent equivalent plastic strain and a
mathematical backward-Euler radial return. It runs through the unchanged common
Atlas compiler and solver, with native and Wasm interfaces and
[runnable reversal/nonproportional examples](../../examples/j2/README.md).

The first independent review found a reversed-stress algebraic root despite
passing numerical cases. That candidate remains [rejected historical evidence](../reviews/j2-scientific-v1/README.md).
The [corrected equation](../ingestion/j2-linear-hardening/CORRECTION-v2.md)
uses signed trial consistency; the [independent v2 review](../reviews/j2-scientific-v2/README.md)
proves uniqueness and verifies the source and saved numerical evidence. The
[current approval record](../admission/j2-approved-v2/README.md) binds exact
tested bytes under the independent-agent checklist policy. Embedded draft
metadata is retained to preserve that identity.

Qualification covers115main cases,16default-parameter cases and27actual
propagated history increments, each repeated on both native and Wasm. It
includes elastic/plastic response, hydrostatic behavior, pressure independence,
shears, H=0, unloading/reversal, hardening, holds, complete strict-branch8x6
update tangents, explicit initialization, failure rollback and recovery. The
[execution record](../ingestion/j2-linear-hardening/execution-v2/README.md)
gives exact numerical settings, references, errors, archives and commands.

Use is bounded to dry total-stress material points, infinitesimal strain,
fixed spatial components and zero spin. The model has no pore-pressure law,
viscosity, kinematic hardening, saturation or softening. Arbitrary-path accuracy,
whole-parameter-envelope robustness, switch-point tangents, finite rotations,
stress-control protocols and browser packaging remain outside qualification.
Parameters are illustrative, without experimental calibration or validation.
The exact mathematical update intentionally omits the vendor multiplier shrink;
vendor binary parity is not claimed. Copyrighted source originals stay private.
