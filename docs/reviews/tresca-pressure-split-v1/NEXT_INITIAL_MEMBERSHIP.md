# Separate strict-membership requirement

The unchanged initial check still compares rounded principal values. Pressure/deviator row conditioning does not resolve the retained parent7 discrepancy. Do not add a fitted yield tolerance or silently project the supplied parent.

A generic exact spectral-range predicate is a plausible next capability, rather than another model-specific correction. The existing `atlas::determinant_accuracy` implementation already contains exact dyadic and `a+b√2` arithmetic for mathematical Mandel tensors. Reuse must be designed and tested separately; no such predicate is implemented or certified by this packet.

A useful algebraic route to review: for deviatoric eigenvalues, let `J2=tr(S²)/2`, `J3=det(S)`. The three squared pair gaps are roots of

```
h(s)=s³−6J2 s²+9J2² s−4J2³+27J3².
```

The largest squared gap lies between `3J2` and `4J2`, and `h` is nondecreasing on that interval. For a nonnegative width, compare its square with those bounds, then determine the exact sign of `h` where necessary. Scaling to `S=3σ−tr(σ)I` and width `3Y` avoids division by three. Exact Mandel invariants may contain a `√2` term, so ordinary dyadic-only determinant arithmetic is insufficient; the existing radical representation is relevant. This is a proposed derivation for independent proof, equality/degeneracy checks and source/runtime qualification, not an established predicate here.

Required gates include hydrostatic and repeated spectra, exact yield equality and immediate neighbors, dense stored Mandel inputs, subnormals/mixed scales and extremes, finite/NaN/seed rejection, and the actual parent7 counterexample. Physical units, value-only predicate semantics and Python/native/Wasm consistency need explicit design. Keep the source mathematical inequality and numerical uncertainty distinct throughout. A future implementation must remain generic and must not insert a Tresca-ID branch.
