# Exact principal-value multiplicity controls

`principal_max_repeated(A)` and `principal_min_repeated(A)` are Boolean DSL predicates for a finite symmetric tensor in Atlas Mandel coordinates. They test exact multiplicity of the represented matrix, with Cartesian shear equal to stored Mandel shear divided by exact sqrt(2). Both are true at a hydrostat. They use exact dyadic/radical characteristic arithmetic rather than rounded eigenvalue comparisons or tolerance clustering.

They support ordinary lazy controls, domain/initial checks and generated model/history expressions. Every C++ primal and Jet seed must be finite; checked failure leaves direct Boolean output unchanged and marks the caller's normal sticky failure. Located history/reset event guards reject these predicates, including aliases, under the existing spectral-control policy. A Boolean cannot be used as a numerical coefficient.

To evaluate a numerical maximum with a declared selected row at exact repeats, use this lazy composition (A has the same units as p_ref):

```
select(principal_range_le(A,0*p_ref),trace(A/3),
       select(principal_max_repeated(A),principal_upper_sum(A)/2,
              principal_max(A)))
```

For a minimum substitute min_repeated, lower_sum and principal_min. Put restricted primitives inside the lazy arms; eager derived aliases still evaluate eagerly. Dividing before the hydrostatic trace avoids the retained trace-overflow case, with ordinary rounding/subnormal error. Existing simple-eigenvalue/pair-sum isolation and range diagnostics are unchanged. A true but unresolved nonzero gap fails numerically rather than being declared a repeated physical state. A rounded rotated tensor need not retain the exact multiplicity of its unrounded precursor.

At a repeated selected extreme the branch row is contraction with the cluster projector divided by its rank; at a hydrostat it is tr(H)/3. This is a rotation-covariant scalar Clarke subgradient, not a unique classical derivative or the nonlinear directional derivative at a tie. Independently selected scalar rows are not automatically a Clarke Jacobian of an arbitrary composed model. Qualify the actual finite residual and solver separately.

[The independent final review](reviews/spectral-multiplicity-v1/independent-review/FINAL_REVIEW_V4.md) accepts the bounded generic capability. [Results](reviews/spectral-multiplicity-v1/RESULTS.md) retain the exact native/Wasm scope and failed revisions. This API does not approve Duncan–Chang or establish its material-point integration, calibration, browser delivery or finite-rotation behavior.
