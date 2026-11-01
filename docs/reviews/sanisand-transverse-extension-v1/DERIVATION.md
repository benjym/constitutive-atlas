# Transverse stability of the selected fixed-memory law

This is a new analytical diagnosis of the exact project equations already
transcribed from [Dafalias & Manzari (2004)](https://doi.org/10.1061/%28ASCE%290733-9399%282004%29130%3A6%28622%29),
not a new source reading or a scientific signature. Source equation locators and
private PDF identity remain in the [reference derivation](../../references/sanisand-project-monotonic-v1/DERIVATION.md).

Consider a symmetric diagonal extension base state under the existing
constant-volume direction. Use the antisymmetric lateral differences

```
x = (delta sigma_yy - delta sigma_zz)/p0
y = delta alpha_yy - delta alpha_zz
z = delta fabric_yy - delta fabric_zz.
```

The initial pressure p0 scales x only. All base tensors have equal yy/zz values;
all shear components vanish. Scalar invariants p, e, norm(r-alpha), cubic trace,
Lode interpolation, hardening distance and loading multiplier have **zero first
variation** in this antisymmetric mode. The same holds for fabric:n and D.
With N=norm(r-alpha), the normal difference is

```
delta n_yy - delta n_zz = (p0*x/p - y)/N.
```

For Rdev=dev(B*n-C*n²), ordinary matrix multiplication gives

```
delta Rdev_yy - delta Rdev_zz = f*(delta n_yy - delta n_zz)
f = B - 2*C*n_yy.
```

At symmetric extension n=(-2,1,1)/sqrt(6), cos(3 theta)=-1 and g=c.
Consequently B=(3c-1)/2, 2*C*n_yy=3(1-c), and

```
f_extension = (9*c - 7)/2.
```

For the selected c=0.712, f_extension=-0.296 exactly. At symmetric compression,
n=(2,-1,-1)/sqrt(6), g=1, and f_compression=1+4.5*(1-c)/c>0.
A negative f is a statement about this flow derivative; it alone is not a
complete stability analysis or a declaration that the source model is invalid.

Let L be the plastic-multiplier rate, q the regular finite loading quotient,
b0 the hardening factor, and ab the scalar such that alpha_b=ab*n. Define

```
A = -2*G*L*f/N
H = (2/3)*b0*q
J = H*ab/N
F = cz*max(-L*D,0).
```

The full continuous law linearizes in the antisymmetric mode to

```
[x]'   [ A/p           -A/p0            0 ] [x]
[y]' = [ J*p0/p       -J-H              0 ] [y]
[z]'   [-F*zmax*p0/p/N F*zmax/N        -F ] [z].
```

The stress/backstress 2x2 determinant simplifies to **-A*H/p**. On the positive
plastic branch, G,p,N,b0,q,L are positive. When f<0, A>0 and H>0, so this
determinant is negative: one instantaneous real eigenvalue is positive and one
negative. At exact elastic entry L=0, that argument degenerates to a zero mode.
Fabric does not feed back into this antisymmetric stress/backstress subsystem
to first order; this follows from the zero variation of the scalar contractions,
not from deleting fabric from the model.

The sign argument establishes a local saddle in the selected continuous law
after entry. It does not by itself quantify a finite-path amplification, prove
that every perturbation grows, or identify where a discrete Newton solve selects
a branch. The time-varying variational equation and full-tensor signed perturbation
studies measure those effects separately, with no forced symmetry or projection.

## Covariance and the remaining implementation question

The mathematical residual is orthogonally covariant: trace, deviator, contraction,
matrix square, cubic trace and scalar elementary functions commute with a change
of basis. An exchange of y/z combined with x sign reversal is a proper rotation.
For Mandel vectors it maps `[xx,yy,zz,xy,yz,xz]` to
`[xx,zz,yy,-xz,yz,-xy]`, applied to every tensor state/input/residual; scalar
void ratio and gamma remain unchanged. Differentiation gives the corresponding
Jacobian covariance wherever the selected branches are differentiable.

This is a mathematical statement, not a check of the compiled AD implementation.
A frozen follow-up must exercise actual generated residuals/Jets at the saved
parents and endpoints (including the first visible symmetry loss), compare
rotated values/derivatives and audit transverse conditioning. A passing law-level
perturbation study cannot exclude an implementation error on its own. No change
to the shared solver or a symmetry-forcing workaround is justified by this packet.
