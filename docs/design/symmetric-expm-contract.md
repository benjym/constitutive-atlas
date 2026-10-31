# Dimensionless symmetric matrix exponential: proposed contract

Planning only, against repository b547f44fd02e83f0d983dc7fa94e20ad7de83017. No implementation, model admission, build or source correction is included.

## Requirement and minimal public surface

Barodesy2017 body Eq3 and footnote5, printed366, require R=−exp(alpha D0), with the tensor exponential defined by exponentiating eigenvalues in a diagonalizing basis. The required operation is the mathematical matrix exponential. The [original source packet](../reviews/barodesy-clay-2017-source-packet.md) records the exact [publisher source](https://doi.org/10.1007/s11440-016-0458-4), bytes/hash and visual checks.

Proposed spelling: `expm(A)`, unary, accepting exactly dimensionless `sym` and returning dimensionless `sym`. Keep `exp` scalar-only; reject dimensional tensors, scalars, booleans, extra arguments and keyword arguments. Do not add tensor log, inverse, arbitrary product, eigensolver, or normalized exponential to the public DSL. Cartesian storage of internal work matrices is an implementation detail, not a new schema type. Input/output order stays orthonormal Mandel `(xx,yy,zz,sqrt2 xy,sqrt2 yz,sqrt2 xz)`.

Mathematical domain: every finite real symmetric3×3A. F(A)=sum A^k/k!, symmetric positive definite in exact arithmetic; expm(0)=I; expm(cI)=exp(c)I. F(QAQ^T)=QF(A)Q^T for every orthogonal Q. Matrix exp is not componentwise exp, and expm(A+B)=expm(A)expm(B) must not be asserted for noncommuting A,B.

## Existing integration points

| Locator | Existing behavior | Needed decision |
|---|---|---|
| `atlas/dsl.py:94–107` | Tensor square plus scalar exp/log, trace/dev/dot/norm | Add one callable and interpreter implementation |
| `atlas/dsl.py:181–200` | Function typing; exp requires dimensionless scalar | Add explicit dimensionless symmetric case; leave scalar exp intact |
| `atlas/dsl.py:248` | C++ function-name lowering | Map expm to dedicated tensor helper |
| `atlas/compiler.py:21–24` | Derived finite checks use `atlas::value` only | Ensure derivative failures also reject evaluation, including nested expm |
| `cpp/include/atlas/tensor.hpp:11–27` | Jet has38first-derivative channels; arithmetic product/quotient rule | Kernel can use existing Jet arithmetic; no eigenvector derivatives needed |
| `cpp/include/atlas/tensor.hpp:54–84` | Six-component Sym, Mandel conversion in square, identity/arithmetic | Private3×3work representation needed for polynomial multiplication; do not use Mandel component multiplication |
| `cpp/include/atlas/linearize.hpp:27–70` | Replays accepted partition with Jet, checks endpoint and final tangent | Add operator derivative checks before allowing invalid intermediate derivatives to cancel later |

The failure channel must be resolved before implementation: a checked internal helper can return false plus output; compiler lowering can hoist checked calls and return false from evaluate_model. A raw exception must not escape C/native/Wasm entry points. Do not rely solely on NaN poisoning of values to communicate derivative-only failure. Python should raise the existing validation/evaluation error category; model updates must preserve existing rollback and failure counters.

## Recommended first kernel: bounded polynomial scaling and squaring

Use an eigenvector-free polynomial algorithm, not a spectral formula differentiated through eigenvectors or eigenvalue gaps. Exact repeated/isotropic spectra are regular points of expm; a formula involving division by eigenvalue differences can manufacture singularities.

For a first small, auditable implementation, recommend a fixed-degree Taylor polynomial with scaling/squaring and an explicit implementation envelope. This is a design recommendation, not an attribution of these particular constants to Higham:

1. Check every primal and every active Jet derivative input is finite. Decode Mandel shear by division by sqrt2. Compute Cartesian infinity norm with deterministic row/entry summation and safe preliminary range checks.
2. Initial research envelope: ||A||Frobenius<=64, computed safely from Mandel components. Using a Frobenius support limit preserves rotational invariance of the mathematical support domain; a row-norm support limit would depend on the chosen frame. This is an **algorithmic support limit**, not the mathematical domain or a source-derived barodesy guard. Larger arguments return unsupported-range failure; never clamp. The number64 is provisional and must be retained in operator version metadata, not silently expanded.
3. Choose s=max(0,ceil(log2(||A||infinity/(1/2)))) without unstable log at zero; use integer power-of-two scaling/comparison instead. Then B=A/2^s, ||B||infinity<=1/2 and s<=8 within the proposed envelope, because ||A||infinity<=sqrt3 ||A||Frobenius. Decisions use primal values; differentiate the selected arithmetic graph.
4. Evaluate P18(B)=sum(k=0..18) B^k/k! using Horner or a documented fixed multiplication order in Cartesian3×3Jet arithmetic. Do not prune small terms based on primal size, because an omitted primal term can carry a derivative. No special zero/isotropic branch is necessary. If a shortcut is introduced, it must preserve the full Fréchet derivative for arbitrary perturbations, including off-diagonal ones.
5. Square s times, with private full3×3multiplication; convert the symmetric part to Mandel at documented boundaries. In exact arithmetic F and every directional derivative for symmetric perturbations are symmetric. Any roundoff symmetrization must be applied consistently to values and derivatives; it is not spectral clipping or a constitutive projection.
6. Check finite values and derivatives at **every** polynomial/squaring work stage and final mapping. Report failure before returning any usable result. No entrywise exp, positive-eigenvalue clipping, diagonal replacement, or output normalization.

An independent normwise truncation bound is `||exp(B)−P18(B)|| <= exp(1/2)*(1/2)^19/19!`, approximately2.585e−23. A derivative truncation bound is `||Lexp(B,H)−LP18(B,H)|| <= exp(1/2)*(1/2)^18/18! * ||H||`, approximately9.824e−22||H||. These bound exact polynomial truncation only; they are **not** binary64 rounding/error guarantees after squaring. Squaring propagates value and derivative errors, so measured high-precision error budgets remain an acceptance requirement. Bounds follow the power-series triangle inequality/submultiplicativity, independently of external implementation.

Within this envelope exact eigenvalues lie in[−64,64], so mathematical exp eigenvalues cannot overflow binary64, but derivative seeds can still overflow and floating-point loss of small eigenvalues can occur for ill-conditioned outputs. Do not promise computed SPD in arbitrary ill-conditioned cases or force it via projection. A later wider-range algorithm needs explicit underflow/overflow/range and accuracy policy, not just a larger loop cap. Barodesy alpha becomes singular at K=0; this operator must not turn that into an implicit model branch. Normalizing expm afterwards can still overflow the current naive Frobenius norm; that is a separate model/helper numerical question.

A conventional alternative is diagonal Padé plus scaling/squaring, with a private differentiated3×3linear solve. Primary numerical work establishes this family and warns against excessive scaling; it also develops Fréchet computation by differentiating the rational approximation and squaring recurrence. See [Al-Mohy & Higham2009, scaling/squaring](https://eprints.maths.manchester.ac.uk/1300/) and [Al-Mohy & Higham2009, Fréchet derivative](https://eprints.maths.manchester.ac.uk/1218/). Only the primary repository abstracts were consulted for these algorithm-family claims; no coefficient table or exact published algorithm was imported. That is a sound later performance choice, but do not borrow an unstated threshold/coefficient set or claim this Taylor proposal implements their Padé algorithm. No spectral-gap assumption is required by either polynomial or rational approach.

## AD contract and independent oracle

For symmetric perturbation H, each derivative channel must return the Fréchet derivative

`L(A,H)=integral_0^1 exp((1−t)A) H exp(tA) dt`.

This is not generally exp(A)H. At A=0, L=H; at A=cI, L=exp(c)H for **all** symmetric H. Scaling derivative is H/2^s and squaring derivative is XL+LX. Do not differentiate integer s or norm selection; test both sides of each switching threshold because approximants/roundoff can differ slightly. Strict support-boundary rounding is an admissibility issue to report, not a reason to clip a rotated input. Repeated eigenvalues require no branch or tolerance in the production kernel.

Primary Fréchet paper above supports differentiating the polynomial/rational and squaring construction. For a separate oracle, construct A=Q diag(lambda)Q^T and transform H into that basis. Then L=Q[C o (Q^T H Q)]Q^T, where Cii=exp(lambda_i), Cij=(exp(lambda_i)−exp(lambda_j))/(lambda_i−lambda_j). Evaluate divided differences independently at high precision, using exp(lambda_j)*expm1(delta)/delta and the continuous delta=0value. Oracle eigenspaces are **supplied by fixture construction**, not numerically recovered from production A. Near-repeated actual binary64 A requires high-precision evaluation of that actual rounded matrix, or a precision/rounding error allowance; do not falsely treat rounded QdiagQ^T as exact-spectrum data. A separate high-precision full Cartesian Taylor reference with independent recurrence and convergence supplies this check.

Independent algebra identities: derivative symmetry/self-adjointness `<H,L(A,K)>=<L(A,H),K>`; trace derivative trL=tr(exp(A)H); commuting H gives exp(A)H; derivative of exp(A)exp(−A)=I is zero. Use finite differences only as a secondary h-refinement check. Block6×6exponential identity can serve as an additional oracle only if computed by an independently implemented high-precision method, not the same production kernel.

## Acceptance matrix and retained evidence

- **Typing/wire:** wrong types/dimensions/arity rejected; scalar exp unchanged; schema/load/compiler interpretation agrees; lazy select evaluates only selected branch, including rejected-range expm in unused branch.
- **Exact cases:** zero, cI at c=−64/sqrt3,−1,0,1,64/sqrt3 subject to the computed Frobenius envelope; all six unit Mandel perturbations, multiple simultaneous Jet channels; diagonal and pure off-diagonal matrices expose componentwise-exp errors.
- **Spectra:** equal eigenvalues, double eigenvalue with oblique repeated eigenspace, gaps descending through1e−4,1e−8,1e−12 and exact zero, distinct mixed-sign spectra. Full3Drotations and reflections check primal and Fréchet covariance, including H rotation; no eigenvector ordering admission.
- **Range/boundaries:** nextafter below/at/above each norm scaling boundary and the Frobenius64envelope; finite extreme entries rejected safely, nonfinite primal/seed rejected, derivative-only overflow fails; no host exception escapes. Cancellation-heavy off-diagonals need absolute-plus-relative comparisons, not pure relative error.
- **Independent accuracy:** retain actual binary64inputs, parameters/definitions, oracle precision+refinement evidence, all six output and36Jacobian entries, component and norm errors. Proposed initial moderate-case budgets: normalized primal error<=2e−13 and derivative error<=1e−12 against high-precision oracle, scaled by max(1,oracle Frobenius norm); extreme-range budgets must be established from conditioning and measurements before asserting support. These are proposed gates, not measured guarantees.
- **Parity:** same corpus through Python interpreter, standalone C++double/Jet, compiled DSL model and real Wasm C ABI. Compare every result/status/Jacobian using common gates; bitwise equality is unnecessary. Record compiler/options/library/platform, rounding assumptions, operator implementation/version/input hashes. Include norm-branch edge cases so backend differences cannot be hidden by a parity-only oracle.
- **Solver integration:** a small synthetic expm-containing research model verifies rejection/rollback, caller state unchanged, no partial tangent on derivative failure and accepted-partition replay. Native/Wasm conformance is operator evidence, not barodesy validation.

Implement and validate the operator separately before transcribing barodesy body-law rates. No operator decision resolves the original ec or objective-rate print discrepancies.
