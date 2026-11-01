# Exact centered-middle comparison

For a real symmetric 3x3 tensor A and real w>=0, define the strict predicate

`3*lambda_middle(A) - trace(A) > w`.

Set `S=3A-trace(A)I`, `B=S-wI`, `J=trace(S*S)/2`, `D=det(S)`.
All eigenvalues are real, `trace(S)=0`, and `trace(B)=-3w<=0`.
Shifting and positive scaling preserve eigenvalue order, so the desired answer
is whether B has at least two strictly positive eigenvalues, counted with
multiplicity.

Suppose two eigenvalues are a,b>0. The third c obeys c<=-(a+b)<0. Consequently
`det(B)=abc<0` and `e2(B)=ab+(a+b)c<=ab-(a+b)^2<0`.
Conversely, if det(B)<0, no eigenvalue is zero. The possible sign patterns are
three negative eigenvalues or two positive and one negative. Three negative
eigenvalues have e2(B)>0, so e2(B)<0 excludes that possibility. This proves the
necessary and sufficient test, including repeated spectra:

`e2(B)<0 and det(B)<0`.

A zero determinant or e2=0 does not satisfy the strict test. In particular, a
zero middle eigenvalue with nonpositive trace cannot have two strictly positive
eigenvalues. At w=0 the trace is zero and the same argument applies; hydrostatic
A gives S=B=0 and false. No division by an eigenvalue gap occurs.

Because S has trace zero, its characteristic polynomial is
`x^3-J*x-D`. Shifting all three eigenvalues by -w gives

`e2(B)=3*w^2-J`, `det(B)=D+J*w-w^3`.

Thus the exact decision is

`J>3*w^2 and D+J*w-w^3<0`.

For the lower comparison `3*lambda_middle(A)-trace(A)<-w`, apply the same strict
predicate to -A. Negation reverses the ordered eigenvalues and trace. This
preserves the original strict corner inequalities; it does not turn a rounded
equality into a non-strict comparison.

## Exact stored Mandel input

Treat each finite binary64 operand as its exact dyadic value. For input
`(x0,x1,x2,x3,x4,x5)`, put `t=x0+x1+x2`, `a=3x0-t`, `b=3x1-t`, `c=3x2-t`,
`u=3x3`, `v=3x4`, `z=3x5`. These operations take place in exact arithmetic.
The physical off-diagonal components of S are `(u,v,z)/sqrt(2)`, hence

```
J = (a*a+b*b+c*c+u*u+v*v+z*z)/2
D = a*b*c - (a*v*v+b*z*z+c*u*u)/2 + (u*v*z/2)*sqrt(2)
```

J is rational dyadic and D lies in Q(sqrt(2)). Its determinant-shift sign is the
sign of an element of that ordered field. Exact rational sign comparisons
against squared radical coefficients avoid a floating square root. The algebra
is the same Mandel determinant convention as the existing exact range design,
but this predicate has different invariants and a strict inequality.

Pressure shifts leave S unchanged. Orthogonal transformations preserve the
middle eigenvalue and trace. Positive scaling of both A and w preserves the
answer; negative scaling is handled through the explicit lower comparison.
Runtime tests must distinguish mathematical invariance from a rounded rotation
or pressure shift that changes the represented tensor.

## Independent oracle and limits

`exact.py` contains two decision routes. The invariant route implements the
formula above. The independent oracle constructs the exact Cartesian matrix
in Q(sqrt(2)), builds B directly and expands `det(xI-B)` by all six matrix
permutations. It uses signed Euclidean polynomial remainders and Sturm root
counting strictly above zero. It does not use the J/D coefficient formula or
its determinant-sign decision.

Ordinary Sturm variation counts distinct roots. The oracle recursively counts
positive roots of the polynomial gcd with its derivative to restore
multiplicities. Thus a repeated positive eigenvalue counts twice, while roots
at zero remain excluded by right-hand coefficient signs. This is essential at
the repeated-minimum Tresca corner. The two routes share only ordered-field
arithmetic, not the target characteristic coefficients or branch decision.

The literal agreement and known-spectrum tests support this proof. They do not
prove a future C++ implementation, validate a constitutive equation against
experiments or admit Tresca to the atlas. Upstream expression overflow and
representability of a returned stress remain separate questions.
