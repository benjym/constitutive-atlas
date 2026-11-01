# Barodesy sand 2015: approved material-point scope

The atlas exposes the complete Kolymbas2015 Eq31 interior sand law in fixed
spatial components with zero spin, small strain, compression-positive effective
Cauchy stress and orthonormal Mandel tensors. Initial stress and void ratio
are explicit. The seven illustrative parameters come from the separately
attributed Kolymbas/Bathaeian2019 manuscript Table1, not an exact2015
experimental reproduction. Original2015 DOI: https://doi.org/10.1680/geot.14.P.151;
separate2019 fixture DOI: https://doi.org/10.1002/nag.2984.

[Original source packet](../ingestion/barodesy-sand/README.md) and
[current numerical qualification](../ingestion/barodesy-sand/delivery-v1/README.md)
retain equations, locators, privately retained original-source hashes,
initialization, numerical restrictions and historical failures.
[Independent nine-item review](../../catalogue/agent-reviews/barodesy-sand-agent-v1.json)
accepts the exact unchanged definition
`3a61b5373404d6973a2957bd0fa21692e10b49e974cdf87eff047d5531851239`.
The model JSON's draft transcription metadata remains historical; current
project approval is separately bound to these exact bytes in the registry.

Native and Wasm each pass672 calls: unchanged independent source-rate cases,
all five laboratory controls with monotonic and cyclic histories, default and
tighter settings, full-tensor oblique updates, midpoint restarts, exact zero,
partial-progress rollback and recovery. All45817 compared physical channels
agree exactly. Independent RK4 references give a maximum default stress error
of1.07118Pa against a frozen5Pa budget; tighter settings reduce it to0.090165Pa.
The ordinary1%/100increment drained default is part of this bounded corpus.

The laboratory uses straight strain increments and endpoint stress control.
This differs from continuously imposing the lateral stress rate at every
constitutive stage; source p59's continuously drained closure is not claimed.
A strain hold has no physical-clock evolution. Zero-loading continuation and
positive-definite nonzero-stress/density/exponential numerical support are
explicit project choices; ill-conditioned states may reject. Parameters are
illustrative; the declared input bounds are not a blanket accuracy guarantee.
There is no artificial stress seed or clipping.

Finite rotations/spin, zero-stress evolution, FE consistent tangents, arbitrary
parameter envelopes, source-matched physical specimen preparation and
experimental validation are not qualified. Measurement overlays do not
establish calibration or experimental applicability. Native CLI recovery uses
fresh processes; Wasm recovery uses the same persistent instance. Exact build,
source, approval, package and live identities are tracked in the
[delivery ledger](../ingestion/barodesy-sand/DELIVERY.md).
