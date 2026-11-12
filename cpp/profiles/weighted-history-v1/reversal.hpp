#pragma once
#include "history.hpp"
namespace atlas::weighted_history_v1 {
inline bool reversal_region(const Tensor& h,const Tensor& d,double R) {
    const double l=magnitude(d);
    if(!(l>0&&l<R/8&&magnitude(h)<=2*l))return false;
    Wide dd=0,hd=0;
    for(size_t i=0;i<6;++i){dd+=Wide(d[i])*d[i];hd+=Wide(h[i])*d[i];}
    const Wide t=std::max(Wide(0),std::min(Wide(1),Wide(-hd/dd)));
    Wide r2=0;
    for(size_t i=0;i<6;++i){const Wide x=Wide(h[i])+t*d[i];r2+=x*x;}
    return r2<=dd/256;
}
// Fixed quadrature stages inside one leaf; no new material subdivision.
// Integrate only the nonlinear correction to the affine memory path.
inline bool reversal_history(const Tensor& parent,const Tensor& d,double R,double beta,Tensor& result,
                            double memory_limit,int& probes,int probes_max) {
    Wide dd=0,hd=0;
    for(size_t i=0;i<6;++i){dd+=Wide(d[i])*d[i];hd+=Wide(parent[i])*d[i];}
    // For H:d <= 0 the source rate is exactly d; the affine path locates
    // the first positive branch without snapping a transverse component to zero.
    if((exact_dot(parent,d)+exact_dot(d,d)).sign<=0){
        for(size_t i=0;i<6;++i)result[i]=toward_zero(Wide(parent[i])+d[i]);
        return in_ball(result,R);
    }
    Wide start=0;
    if(dd>0)start=std::max(Wide(0),std::min(Wide(1),Wide(-hd/dd)));
    Tensor base{},load{};
    const Wide wide_span=1-start;
    if(wide_span<=0)return false;
    const double span=wide_span.convert_to<double>();
    for(size_t i=0;i<6;++i){base[i]=(Wide(parent[i])+start*d[i]).convert_to<double>();load[i]=span*d[i];}
    auto rate=[&](double u,const Tensor& c,Tensor& r){
        if(probes>=probes_max)return false;
        ++probes;
        const double u2=u*u,u3=u2*u,u4=u2*u2;
        double n2=0;Tensor h{};
        for(size_t i=0;i<6;++i){h[i]=base[i]+u4*load[i]+c[i];n2+=h[i]*h[i];}
        if(!std::isfinite(n2)||!in_ball(h,R))return false;
        r={};
        if(u==0)return true;
        const auto sign=exact_dot(h,d).sign;
        if(sign<=0)return true;
        Wide dot=0;
        for(size_t i=0;i<6;++i)dot+=Wide(h[i])*d[i];
        const double dir=(dot*wide_span).convert_to<double>();
        if(!(n2>0&&dir>0))return false;
        const double a=-4*u3*(dir/n2)*std::pow(std::sqrt(n2)/R,beta);
        for(size_t i=0;i<6;++i)r[i]=a*h[i];
        return std::isfinite(a);
    };
    auto integrate=[&](int panels,Tensor& endpoint){
        Tensor correction{};
        const double step=1./panels;
        for(int j=0;j<panels;++j){
            const double u=j*step;Tensor a{},b{},c{},e{},x{};
            if(!rate(u,correction,a))return false;
            for(size_t i=0;i<6;++i)x[i]=correction[i]+step/2*a[i];
            if(!rate(u+step/2,x,b))return false;
            for(size_t i=0;i<6;++i)x[i]=correction[i]+step/2*b[i];
            if(!rate(u+step/2,x,c))return false;
            for(size_t i=0;i<6;++i)x[i]=correction[i]+step*c[i];
            if(!rate(u+step,x,e))return false;
            for(size_t i=0;i<6;++i)correction[i]+=step/6*(a[i]+2*b[i]+2*c[i]+e[i]);
        }
        for(size_t i=0;i<6;++i)endpoint[i]=toward_zero(Wide(parent[i])+d[i]+correction[i]);
        return in_ball(endpoint,R);
    };
    // The outer full/half check can share a positive-branch quadrature at
    // a midpoint reversal. Also compare two quadratures inside each stage,
    // keeping their total at 192 rate stages under the shared probe cap.
    Tensor coarse{},difference{};
    if(!integrate(16,coarse)||!integrate(32,result))return false;
    for(size_t i=0;i<6;++i)difference[i]=coarse[i]-result[i];
    return magnitude(difference)<=memory_limit;
}
}
