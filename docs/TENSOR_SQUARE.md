# Symmetric tensor square

`tensor_square(A)` returns the symmetric second-order tensor whose Cartesian matrix is `A @ A`. This is an additive expression-language operation available to both schema-v0.1 and v0.2 definitions. It supplies the algebra needed for the generalized SANISAND flow direction; it does not implement that model, its reversal memory or any additional state capacity.

For a symmetric input, its matrix square is symmetric. A product of two different symmetric matrices need not be symmetric, so arbitrary tensor multiplication remains rejected. This operation is neither componentwise squaring nor the scalar contraction `dot(A,A)`.

## Representation and dimensions

Inputs and outputs use orthonormal Mandel order `xx, yy, zz, xy, yz, xz`, with physical off-diagonal entries multiplied by √2. If `A` has SI dimension vector `d`, the result has dimension vector `2d`. Scalar inputs, unsupported arity and dimensionally inconsistent expressions are rejected before generation. A pressure-valued input therefore produces pressure-squared output; it cannot be added directly to a pressure-valued tensor.

With Mandel components `(x,y,z,u,v,w)`, output components are:

```text
x*x + (u*u+w*w)/2
y*y + (u*u+v*v)/2
z*z + (v*v+w*w)/2
(x+y)*u + v*w/sqrt(2)
(y+z)*v + u*w/sqrt(2)
(x+z)*w + u*v/sqrt(2)
```

The Python interpreter and templated C++ primitive use this contract. Generated calls use `atlas::tensor_square`, so a local declared identifier cannot shadow the function call. Existing model definitions and their equations are unchanged. Ordinary overflow/nonfinite handling continues to apply; the operation introduces no clipping or regularization.

## Verification

The reference calculations use ordinary 3×3 Cartesian matrix multiplication and a separate Mandel conversion. They do not reuse the primitive's component formulas.

- Python covers zero, diagonal, pure shear, fully sheared and 80 seeded random tensors; trace of the square equals the Frobenius squared norm. Three oblique rotations about distinct axes check covariance. Shape, dimension, arity and generated-name checks exercise the DSL boundary.
- Native C++ checks 80 random tensors and all 2,880 Jacobian entries against centered finite differences of the Cartesian reference. Automatic differentiation is exercised with every input Mandel component.
- A separate synthetic generated fixture, `test-tensor-square`, evaluates `A_dot=tensor_square(A)/tau`. It checks interpretation and actual generated evaluation, with `tau=2 s`; it is not counted as a constitutive model or shipped in the public browser model bundle.
- WebAssembly evaluates 24 tensors through that generated fixture and compares both native and Wasm output with Cartesian results. Existing native model references and native/Wasm protocol, time, schedule and Terracotta checks remain regression gates.

Run:

```sh
cmake --build build --parallel 2
ctest --test-dir build --output-on-failure
cmake --build build-wasm --parallel 2
node tools/test_time_wasm.mjs
```

The [updated capability observations](../catalogue/investigations/sanisand-capabilities-v2.json) record the new function's accepted symmetric type. The original v1 report remains an immutable observation of the earlier engine. These checks establish an engine primitive, not independent scientific review or SANISAND admission. State-capacity expansion and a source-reconciled reversal contract remain open.
