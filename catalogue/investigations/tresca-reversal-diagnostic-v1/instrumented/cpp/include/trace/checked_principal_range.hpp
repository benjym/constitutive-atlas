#pragma once
#include "trace/tensor.hpp"
#include "trace/numerics/determinant.hpp"

namespace atlas_trace::principal_range_accuracy {
inline constexpr const char* version="mandel-principal-range-exact-v1";
// Exact invariant computation starts before scaling, trace or subtraction.
// Primal and every seed are validated; Boolean output is untouched on failure.
template<class T> bool checked(const Sym<T>& a,const T& width,bool& out) {
    if(!finite_value(width)||value(width)<0.)return false;
    for(const auto& x:a.v)if(!finite_value(x))return false;
    using namespace determinant_accuracy;
    const auto two=Dyadic::from(2.),three=Dyadic::from(3.),four=Dyadic::from(4.);
    const auto six=Dyadic::from(6.),nine=Dyadic::from(9.),twenty_seven=Dyadic::from(27.),fifty_four=Dyadic::from(54.);
    std::array<Dyadic,6> s;
    for(unsigned i=0;i<6;++i)s[i]=Dyadic::from(value(a.v[i]));
    const auto trace=s[0]+s[1]+s[2];
    for(unsigned i=0;i<6;++i)s[i]=three*s[i]-(i<3?trace:Dyadic{});
    Dyadic j;for(const auto& x:s)j=j+x*x;j=half(j);
    const auto w=three*Dyadic::from(value(width)),q=w*w;
    bool candidate;
    if(compare_positive(q,three*j)<0)candidate=false;
    else if(compare_positive(q,four*j)>=0)candidate=true;
    else {
        const auto d=polynomial(s);
        const auto h=((q-six*j)*q+nine*j*j)*q-four*j*j*j+twenty_seven*(d.a*d.a+two*d.b*d.b);
        candidate=radical_sign({h,fifty_four*d.a*d.b})>=0;
    }
    out=candidate;return true;
}
} // namespace atlas_trace::principal_range_accuracy
namespace atlas_trace {
template<class T> bool principal_range_le_or_mark(const Sym<T>& a,const T& width,bool& ok) {
    bool result=false;
    if(!principal_range_accuracy::checked(a,width,result))ok=false;
    return result;
}
} // namespace atlas_trace
