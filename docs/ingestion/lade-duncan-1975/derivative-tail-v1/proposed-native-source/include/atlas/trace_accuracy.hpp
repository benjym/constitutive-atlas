#pragma once
// Source-only generic candidate. IEEE binary64, no fast-math/reassociation.
#include <algorithm>
#include <array>
#include <bit>
#include <cfloat>
#include <cfenv>
#include <cmath>
#include <cstdint>
#include <limits>
#include <type_traits>
#include "atlas/derivative_tail.hpp"

#if defined(__FAST_MATH__) || (defined(__FINITE_MATH_ONLY__) && __FINITE_MATH_ONLY__)
#error "Accurate trace requires ordinary IEEE arithmetic, not fast-math"
#endif
static_assert(sizeof(double)==8 && std::numeric_limits<double>::is_iec559 &&
              std::numeric_limits<double>::radix==2 && std::numeric_limits<double>::digits==53 &&
              std::numeric_limits<double>::max_exponent==1024 &&
              std::numeric_limits<double>::min_exponent==-1021);
static_assert(FLT_EVAL_METHOD==0,"TwoSum requires binary64 expression evaluation");

namespace atlas::trace_accuracy {
inline constexpr const char* version="trace-three-binary64-certified-eft-fixed34-v1-candidate";
using Words=std::array<std::uint64_t,34>;
inline constexpr std::uint64_t fraction_mask=(std::uint64_t(1)<<52)-1;
inline constexpr std::uint64_t sign_mask=std::uint64_t(1)<<63;
inline std::uint64_t bits(double x){return std::bit_cast<std::uint64_t>(x);}
inline double binary(std::uint64_t x){return std::bit_cast<double>(x);}

inline void add_word(Words& a,unsigned i,std::uint64_t value){
    while(value!=0 && i<a.size()){
        const auto old=a[i];a[i]=old+value;value=a[i]<old?1:0;++i;
    }
    // Three finite binary64 inputs need <=2100bits; 34words provide2176.
}
inline void accumulate(Words& positive,Words& negative,double x){
    const auto b=bits(x);const unsigned exponent=unsigned((b>>52)&2047);
    const auto sig=(b&fraction_mask)|(exponent?std::uint64_t(1)<<52:0);
    const unsigned shift=exponent?exponent-1:0,word=shift/64,offset=shift%64;
    auto& a=(b&sign_mask)?negative:positive;
    add_word(a,word,sig<<offset);
    if(offset!=0)add_word(a,word+1,sig>>(64-offset));
}
inline int compare(const Words& a,const Words& b){
    for(unsigned i=unsigned(a.size());i-->0;){if(a[i]!=b[i])return a[i]>b[i]?1:-1;}
    return 0;
}
inline Words subtract(const Words& a,const Words& b){
    Words out{};std::uint64_t borrow=0;
    for(unsigned i=0;i<a.size();++i){
        const auto x=a[i]-b[i];const bool first=a[i]<b[i];
        out[i]=x-borrow;const bool second=x<borrow;borrow=(first||second)?1:0;
    }
    return out; // caller establishes a>=b
}
inline int top_bit(const Words& a){
    for(unsigned i=unsigned(a.size());i-->0;)if(a[i])return int(i*64+63-std::countl_zero(a[i]));
    return -1;
}
inline bool bit_at(const Words& a,unsigned n){return((a[n/64]>>(n%64))&1)!=0;}
inline bool any_below(const Words& a,unsigned count){
    const unsigned full=count/64,rest=count%64;
    for(unsigned i=0;i<full;++i)if(a[i])return true;
    return rest!=0 && (a[full]&((std::uint64_t(1)<<rest)-1))!=0;
}
inline std::uint64_t shifted53(const Words& a,unsigned shift){
    const unsigned word=shift/64,offset=shift%64;
    auto q=a[word]>>offset;
    if(offset && word+1<a.size())q|=a[word+1]<<(64-offset);
    return q&((std::uint64_t(1)<<53)-1);
}
inline bool exact_fallback(double a,double b,double c,double& out){
    Words positive{},negative{};
    accumulate(positive,negative,a);accumulate(positive,negative,b);accumulate(positive,negative,c);
    const int order=compare(positive,negative);
    if(order==0){out=0.;return true;}
    const auto magnitude=order>0?subtract(positive,negative):subtract(negative,positive);
    const auto sign=order<0?sign_mask:0;const int top=top_bit(magnitude);
    if(top<52){out=binary(sign|magnitude[0]);return true;}
    unsigned shift=unsigned(top-52);auto q=shifted53(magnitude,shift);
    if(shift && bit_at(magnitude,shift-1) && (any_below(magnitude,shift-1)||(q&1)))++q;
    if(q==(std::uint64_t(1)<<53)){q>>=1;++shift;}
    const unsigned exponent=shift+1;
    if(exponent>=2047)return false;
    const double candidate=binary(sign|(std::uint64_t(exponent)<<52)|(q&fraction_mask));
    out=candidate;return true;
}
struct Pair{double high,low;};
inline bool two_sum(double a,double b,Pair& out){
    const double high=a+b;
    if(!std::isfinite(high))return false;
    const double z=high-a,u=high-z,v=a-u,w=b-z,low=v+w;
    if(!std::isfinite(z)||!std::isfinite(u)||!std::isfinite(v)||!std::isfinite(w)||!std::isfinite(low))return false;
    out={high,low};return true;
}
inline bool sum3_impl(double a,double b,double c,double& out,bool nearest){
    if(!std::isfinite(a)||!std::isfinite(b)||!std::isfinite(c))return false;
    if(nearest){
        Pair first{},second{};
        if(two_sum(a,b,first)&&two_sum(first.high,c,second)){
            if(first.low==0 && second.low==0){out=second.high==0?0.:second.high;return true;}
            Pair residual{},finish{};
            if(two_sum(first.low,second.low,residual)&&two_sum(second.high,residual.high,finish)){
                if(finish.low==0 && residual.low==0){out=finish.high==0?0.:finish.high;return true;}
                const double below=std::nextafter(finish.high,-std::numeric_limits<double>::infinity());
                const double above=std::nextafter(finish.high,std::numeric_limits<double>::infinity());
                if(finish.high!=0 && std::isfinite(below)&&std::isfinite(above)){
                    const double gap=std::min(std::abs(finish.high-below),std::abs(above-finish.high));
                    if(std::max(std::abs(finish.low),std::abs(residual.low)) < gap*.25){out=finish.high;return true;}
                }
            }
        }
    }
    return exact_fallback(a,b,c,out);
}
inline bool sum3_checked(double a,double b,double c,double& out){
    return sum3_impl(a,b,c,out,std::fegetround()==FE_TONEAREST);
}
// Structural templates avoid circular inclusion with Atlas tensor.hpp. Only
// Sym<double>/Sym<Jet> with6components and38Jet directions are supported.
template<class Tensor,class Result>bool trace_checked(const Tensor& a,Result& out){
    static_assert(std::tuple_size_v<std::remove_cvref_t<decltype(a.v)>> ==6);
    Result candidate{};const bool nearest=std::fegetround()==FE_TONEAREST;
    if constexpr(std::is_same_v<Result,double>){
        for(const auto& x:a.v)if(!std::isfinite(x))return false;
        if(!sum3_impl(a.v[0],a.v[1],a.v[2],candidate,nearest))return false;
    }else{
        static_assert(std::tuple_size_v<std::remove_cvref_t<decltype(candidate.d)>> ==38);
        for(const auto& x:a.v){
            if(!std::isfinite(x.v))return false;
            for(double seed:x.d)if(!std::isfinite(seed))return false;
        }
        if(!sum3_impl(a.v[0].v,a.v[1].v,a.v[2].v,candidate.v,nearest))return false;
        for(unsigned j=0;j<unsigned(atlas::derivative_work_columns());++j)
            if(!sum3_impl(a.v[0].d[j],a.v[1].d[j],a.v[2].d[j],candidate.d[j],nearest))return false;
        atlas::fill_derivative_tail(candidate);
    }
    out=candidate;return true;
}
template<class Tensor>auto trace_or_nonfinite(const Tensor& a){
    using Result=std::remove_cvref_t<decltype(a.v[0])>;Result out{};
    if(!atlas::trace_accuracy::trace_checked(a,out)){
        if constexpr(std::is_same_v<Result,double>)out=std::numeric_limits<double>::quiet_NaN();
        else out.v=std::numeric_limits<double>::quiet_NaN();
    }
    return out;
}
} // namespace atlas::trace_accuracy
