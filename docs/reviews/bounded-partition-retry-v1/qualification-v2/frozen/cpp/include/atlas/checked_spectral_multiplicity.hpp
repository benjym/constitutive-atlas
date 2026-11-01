#pragma once
#include "atlas/tensor.hpp"
#include "atlas/numerics/determinant.hpp"

namespace atlas::spectral_multiplicity_accuracy {
inline constexpr const char* version="mandel-spectral-multiplicity-exact-v1";
// Exact characteristic discriminant of 3*A-tr(A)*I in Q(sqrt(2)).
// Numerical eigenvalues are never used to identify a repeated eigenspace.
template<class T> bool checked(const Sym<T>& a,bool maximum,bool& out) {
    static_assert(sizeof(double)==8&&std::numeric_limits<double>::is_iec559&&std::numeric_limits<double>::digits==53);
    if(!finite_value(a))return false;
    using namespace determinant_accuracy;
    const auto three=Dyadic::from(3.);
    const auto four=Dyadic::from(4.);
    const auto twenty_seven=Dyadic::from(27.);
    std::array<Dyadic,6> s;
    for(unsigned i=0;i<6;++i)s[i]=Dyadic::from(value(a.v[i]));
    const auto trace=s[0]+s[1]+s[2];
    for(unsigned i=0;i<6;++i)s[i]=three*s[i]-(i<3?trace:Dyadic{});
    Dyadic j;for(const auto& x:s)j=j+x*x;j=half(j);
    bool candidate=false;
    if(!j.sign)candidate=true;
    else {
        const auto d=polynomial(s);
        auto twice_b2=d.b*d.b;twice_b2=twice_b2+twice_b2;
        const auto rational=four*j*j*j-twenty_seven*(d.a*d.a+twice_b2);
        // Radical coefficient is -54*d.a*d.b; only exact zero is needed.
        const auto radical=d.a*d.b;
        if(!rational.sign&&!radical.sign){
            const int direction=radical_sign(d);
            candidate=maximum?direction<0:direction>0;
        }
    }
    out=candidate;return true;
}
} // namespace atlas::spectral_multiplicity_accuracy

namespace atlas {
template<class T> bool principal_max_repeated_or_mark(const Sym<T>& a,bool& ok) {
    bool result=false;
    if(!spectral_multiplicity_accuracy::checked(a,true,result))ok=false;
    return result;
}
template<class T> bool principal_min_repeated_or_mark(const Sym<T>& a,bool& ok) {
    bool result=false;
    if(!spectral_multiplicity_accuracy::checked(a,false,result))ok=false;
    return result;
}
} // namespace atlas
