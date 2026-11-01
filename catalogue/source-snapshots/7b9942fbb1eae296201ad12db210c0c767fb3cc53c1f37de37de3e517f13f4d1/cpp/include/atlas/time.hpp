#pragma once
#include "atlas/solver.hpp"

namespace atlas {
struct TimeSettings {
    double relative_tolerance=1e-6;
    // Absolute tolerance is a dimensionless fraction of each declared state scale.
    double absolute_tolerance=1e-9;
    double minimum_step=1e-12, maximum_step=1e6;
    int maximum_substeps=20000, maximum_depth=40;
};
struct TimedAdvance {
    bool ok=false;
    State state;
    double time=0;
    Diagnostics diagnostics;
    std::string message;
};
inline bool valid_time_settings(const TimeSettings& s) {
    return std::isfinite(s.relative_tolerance)&&s.relative_tolerance>0&&
        std::isfinite(s.absolute_tolerance)&&s.absolute_tolerance>0&&
        std::isfinite(s.minimum_step)&&s.minimum_step>0&&
        std::isfinite(s.maximum_step)&&s.maximum_step>=s.minimum_step&&
        s.maximum_substeps>=2&&s.maximum_substeps<=1000000&&
        s.maximum_depth>=1&&s.maximum_depth<=50;
}
inline bool time_domain(int model,const State& z,const State& p,double time,bool initial=false) {
    State unused;Sym<double> zero;
    return finite(z)&&evaluate_model(model,z,z,zero,p,unused,initial,time,true);
}
// Rate history is a pure function of physical time. The caller splits control
// discontinuities into separate advances; it must not mutate committed history.
template<class RateHistory>
bool time_midpoint(int model,const State& zn,const State& p,double t0,double t1,
                   const RateHistory& rate,State& z) {
    const double h=t1-t0,tm=t0+h*.5;
    if(!(tm>t0&&tm<t1))return false;
    const auto d0=rate(t0),dm=rate(tm);
    if(!std::isfinite(norm(d0))||!std::isfinite(norm(dm)))return false;
    State k1,k2,mid=zn;
    if(!evaluate_model(model,zn,zn,d0,p,k1,false,t0)||!finite(k1))return false;
    for(size_t i=0;i<zn.size();++i)mid[i]+=.5*h*k1[i];
    if(!finite(mid)||!evaluate_model(model,mid,mid,dm,p,k2,false,tm)||!finite(k2))return false;
    z=zn;for(size_t i=0;i<zn.size();++i)z[i]+=h*k2[i];
    return time_domain(model,z,p,t1);
}
template<class RateHistory>
bool time_recursive(int model,const State& zn,const State& p,double t0,double t1,
                    const RateHistory& rate,const TimeSettings& settings,const State& scales,
                    State& z,Diagnostics& diag,int depth) {
    if(depth>settings.maximum_depth||diag.substeps+2>settings.maximum_substeps)return false;
    const double h=t1-t0,tm=t0+h*.5;
    if(h*.5<settings.minimum_step||!(tm>t0&&tm<t1))return false;
    if(h<=settings.maximum_step) {
        State full,half,two;
        if(time_midpoint(model,zn,p,t0,t1,rate,full)&&
           time_midpoint(model,zn,p,t0,tm,rate,half)&&
           time_midpoint(model,half,p,tm,t1,rate,two)) {
            double error=0;
            for(size_t i=0;i<zn.size();++i) {
                const double weight=settings.absolute_tolerance*scales[i]+
                    settings.relative_tolerance*std::max(std::abs(zn[i]),std::abs(two[i]));
                // The two-half-step solution is second order; Richardson's
                // factor is 2^2-1. Accept it without extrapolation.
                const double component=std::abs(two[i]-full[i])/(3*weight);
                if(!std::isfinite(weight)||weight<=0||!std::isfinite(component)){error=std::numeric_limits<double>::infinity();break;}
                error=std::max(error,component);
            }
            if(std::isfinite(error)&&error<=1) {
                z=two;diag.error=error;diag.substeps+=2;return true;
            }
        }
        ++diag.rejected;
    }
    State half;
    if(!time_recursive(model,zn,p,t0,tm,rate,settings,scales,half,diag,depth+1))return false;
    return time_recursive(model,half,p,tm,t1,rate,settings,scales,z,diag,depth+1);
}
template<class RateHistory>
TimedAdvance integrate_time_history(int model,const State& zn,const State& p,
                                  double start_time,double duration,const RateHistory& rate,
                                  const TimeSettings& settings={}) {
    TimedAdvance result;result.state=zn;result.time=start_time;
    if(model<0||model>=int(models().size())||!models()[model].physical_time) {
        result.message="physical-time ODE model required";return result;
    }
    const double end_time=start_time+duration;
    if(!std::isfinite(start_time)||!std::isfinite(duration)||duration<=0||
       !std::isfinite(end_time)||!(end_time>start_time)||!valid_time_settings(settings)) {
        result.message="invalid physical time or solver settings";return result;
    }
    if(zn.size()!=initial_state(model).size()||!valid_parameters(model,p)||
       !time_domain(model,zn,p,start_time,true)) {
        result.message="invalid parameters or inadmissible initial state";return result;
    }
    const auto scales=model_scales(model,p);
    for(double s:scales)if(!std::isfinite(s)||s<=0) {
        result.message="invalid state scales";return result;
    }
    State trial;
    result.ok=time_recursive(model,zn,p,start_time,end_time,rate,settings,scales,
                             trial,result.diagnostics,0);
    if(result.ok){result.state=trial;result.time=end_time;}
    else result.message="physical-time integration failed; state and clock rolled back";
    return result;
}
inline TimedAdvance integrate_time(int model,const State& zn,const Sym<double>& strain_rate,
                                  const State& p,double start_time,double duration,
                                  const TimeSettings& settings={}) {
    return integrate_time_history(model,zn,p,start_time,duration,
                                  [strain_rate](double){return strain_rate;},settings);
}
}
