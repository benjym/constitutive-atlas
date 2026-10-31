# Symmetric Mandel determinant

`determinant(A)` accepts one symmetric tensor and returns a scalar whose SI exponents are three times those of `A`. For example a stress tensor produces pressure cubed. Mandel order is `[xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz]`. There is no SPD restriction on this mathematical operation.

For exact stored binary64 components `x,y,z,u,v,w`, the determinant is

```
xyz - (x*v*v + y*w*w + z*u*u)/2 + (u*v*w/2)*sqrt(2).
```

The core retains the irrational coefficient and all cancellation with exact integer/dyadic arithmetic, then certifies nearest-even rounding against exact midpoints. Approximate floating results only guide the search. Final rounded zero is canonical positive zero. Nonfinite input or final rounded overflow rejects. C++ automatic differentiation computes each of38exact cofactor contractions at the stored primal, then independently rounds each direction; nonfinite seeds and final derivative overflow reject. This differentiates the exact mathematical determinant, not the binary64 rounding map.

The [primitive study](../catalogue/investigations/symmetric-determinant-v1/RESULTS.md) passes124calls per native/Wasm backend with independent exact result bits and full derivative/recovery checks. Python interpretation and unit/shape inference are registered. Generated model expressions mark a sticky evaluation failure; history expressions throw into their transaction failure handler. Eager masking cannot erase a failure. Unselected lazy `select` branches do not execute it. The primitive preserves output on rejection; generated model outputs remain scratch, and history transactions retain their existing rollback contract.

The [separate expression integration plan](../catalogue/investigations/determinant-expressions-v1/README.md) still requires a prospectively frozen compiled study across model/history contexts, trace/AD routing, failures and recovery. No current public model uses the operation yet. Correct determinant arithmetic alone does not prove accurate complete clay rates, finite integration, preparation, experimental validation or scientific admission.
