#pragma once
#include "atlas/tensor.hpp"
#include "atlas/numerics/determinant.hpp"
namespace atlas::centered_middle_accuracy {
inline constexpr const char* version="mandel-centered-middle-exact-v1";
// Every finite primal and seed is checked before exact conversion.
// All centering and polynomial arithmetic uses dyadics, not binary64 intermediates.
template<class T> bool checked(const Sym<T>& a,const T& width,bool& out) {
    if(!finite_value(width)||value(width)<0.)return false;
    for(const auto& x:a.v)if(!finite_value(x))return false;
    using namespace determinant_accuracy;
    const auto three=Dyadic::from(3.);
    std::array<Dyadic,6> s;
    for(unsigned i=0;i<6;++i)s[i]=Dyadic::from(value(a.v[i]));
    const auto trace=s[0]+s[1]+s[2];
    for(unsigned i=0;i<6;++i)s[i]=three*s[i]-(i<3?trace:Dyadic{});
    Dyadic j;for(const auto& x:s)j=j+x*x;j=half(j);
    const auto w=Dyadic::from(value(width));
    bool candidate=false;
    if(compare_positive(j,three*w*w)>0){
        const auto d=polynomial(s);
        candidate=radical_sign({d.a+j*w-w*w*w,d.b})<0;
    }
    out=candidate;return true;
}
} // namespace atlas::centered_middle_accuracy
namespace atlas {
template<class T> bool principal_centered_mid_gt_or_mark(const Sym<T>& a,const T& width,bool& ok) {
    bool result=false;
    if(!centered_middle_accuracy::checked(a,width,result))ok=false;
    return result;
}
} // namespace atlas
