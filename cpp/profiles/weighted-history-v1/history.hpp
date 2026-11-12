#pragma once
#include "atlas/numerics/determinant.hpp"
#include <boost/multiprecision/cpp_bin_float.hpp>

namespace atlas::weighted_history_v1 {
using Wide=boost::multiprecision::number<boost::multiprecision::cpp_bin_float<224,
          boost::multiprecision::digit_base_2>>;
using Tensor=std::array<double,6>;
using WideTensor=std::array<Wide,6>;
using determinant_accuracy::Dyadic;

inline Dyadic exact_dot(const Tensor& a,const Tensor& b) {
    Dyadic out;
    for(size_t i=0;i<a.size();++i)out=out+Dyadic::from(a[i])*Dyadic::from(b[i]);
    return out;
}
inline bool in_ball(const Tensor& h,double radius) {
    if(!std::isfinite(radius)||radius<=0||
       !std::all_of(h.begin(),h.end(),[](double x){return std::isfinite(x);}))return false;
    const auto r=Dyadic::from(radius);
    return (exact_dot(h,h)-r*r).sign<=0;
}
inline double magnitude(const Tensor& a) {
    // Evaluate one norm from the exact binary inputs, then round once.
    Wide v=0;
    for(const double x:a)v+=Wide(x)*x;
    return sqrt(v).convert_to<double>();
}
inline double toward_zero(const Wide& v) {
    const double rounded=v.convert_to<double>();
    return abs(Wide(rounded))>abs(v)?std::nextafter(rounded,0.):rounded;
}
inline Tensor convert(const Wide& r,const Wide& R,const WideTensor& u) {
    Tensor h{};
    for(size_t i=0;i<h.size();++i)h[i]=toward_zero(R*r*u[i]);
    return h;
}
inline Tensor radius(const Wide& L,const Wide& a,const Wide& beta,const Wide& R,
                     const WideTensor& u,int& powers) {
    powers=0;
    Wide lo=0,hi=L,x=L;
    if(a==0){
        for(int i=0;i<192;++i)lo=(lo+hi)/2;
        return convert((lo+hi)/2,R,u);
    }
    while(powers<192){
        const Wide power=pow(x,beta);
        ++powers;
        const Wide g=x+a*power-L;
        (g>0?hi:lo)=x;
        if(powers<=12){
            const Wide pad=abs(g)+L*Wide("1e-52");
            const Wide lower=std::max(lo,Wide(x-pad)),upper=std::min(hi,Wide(x+pad));
            if(lower<upper){
                const auto left=convert(lower,R,u),right=convert(upper,R,u);
                if(left==right){
                    const Wide gl=lower+a*pow(lower,beta)-L,gu=upper+a*pow(upper,beta)-L;
                    powers+=2;
                    if(gl<0&&gu>0)return left;
                }
            }
            if(x!=0){
                const Wide next=x-g/(1+a*beta*power/x);
                if(lo<next&&next<hi){x=next;continue;}
            }
        }
        x=(lo+hi)/2;
    }
    return convert((lo+hi)/2,R,u);
}

struct History {double e=0.,theta=0.;Tensor h{};int powers=0;};
inline bool endpoint(double e,const Tensor& parent,const Tensor& increment,double R,double beta,History& out,const Tensor* resolved=nullptr) {
    out={};
    if(!std::isfinite(e)||e<0||!std::isfinite(beta)||beta<=0||beta>1||!in_ball(parent,R)
       ||!std::all_of(increment.begin(),increment.end(),[](double x){return std::isfinite(x);}))return false;
    const double length=magnitude(increment);
    const double relative=length/R;
    if(relative>.5)return false;
    out.theta=(1+relative)*.5;
    if(length==0){out.e=e;out.h=parent;return true;}
    if(resolved)out.h=*resolved;
    else {
        const Wide wide_R=R,t=out.theta,b=beta;
        WideTensor h{},load{},u{};
        Wide h2=0,dot=0;
        for(size_t i=0;i<h.size();++i){
            h[i]=Wide(parent[i])/wide_R;load[i]=Wide(increment[i])/wide_R;
            h2+=h[i]*h[i];dot+=h[i]*load[i];
        }
        Wide red=0;
        if(exact_dot(parent,increment).sign>0)red=(1-t)*pow(sqrt(h2),b)*dot/h2;
        Wide p2=0;
        for(size_t i=0;i<u.size();++i){u[i]=(1-red)*h[i]+load[i];p2+=u[i]*u[i];}
        if(p2>0){
            const Wide L=sqrt(p2);
            Wide q=0;
            for(size_t i=0;i<u.size();++i){u[i]/=L;q+=u[i]*load[i];}
            out.h=radius(L,t*std::max(Wide(0),q),b,wide_R,u,out.powers);
        }
    }
    const Wide t=out.theta;
    const Wide trace=Wide(increment[0])+Wide(increment[1])+Wide(increment[2]);
    const Wide den=1+t*trace;
    if(den<=0)return false;
    const Wide ev=(1+Wide(e))*(1-(1-t)*trace)/den-1;
    if(ev<0||!in_ball(out.h,R))return false;
    out.e=ev.convert_to<double>();
    return std::isfinite(out.e);
}
}
