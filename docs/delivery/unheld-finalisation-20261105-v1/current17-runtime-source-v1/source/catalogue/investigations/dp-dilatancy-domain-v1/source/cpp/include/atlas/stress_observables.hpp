#pragma once
#include "atlas/tensor.hpp"

namespace atlas {
// Nonnegative q of an already-stored orthonormal Mandel tensor. Double-only:
// constitutive dev/DSL/AD semantics are intentionally independent of this observable.
// Pairwise differences keep exactly isotropic stored tensors at exact positive zero.
// The independently specified reference-study domain is |component| <= 1e300.
inline double deviatoric_stress_magnitude(const Sym<double>& a) {
    const double d01=a.v[0]-a.v[1], d12=a.v[1]-a.v[2], d20=a.v[2]-a.v[0];
    if(d01==0 && d12==0 && d20==0 && a.v[3]==0 && a.v[4]==0 && a.v[5]==0) return 0.;
    const double normal=std::hypot(d01,d12,d20)/std::sqrt(2.);
    const double shear=std::hypot(a.v[3],a.v[4],a.v[5])*std::sqrt(1.5);
    return std::hypot(normal,shear);
}
}
