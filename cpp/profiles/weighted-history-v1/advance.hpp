#pragma once
#include "reversal.hpp"
#include "atlas/solver.hpp"

namespace atlas::weighted_history_v1 {
// Layout is supplied by the profile; the numerical code does not select a
// material, evaluate a constitutive equation or infer any field convention.
struct Binding {
    size_t stress=0,void_ratio=0,memory=0;
    double R=0.,beta=0.,stress_margin=0.;
};
inline Tensor block(const State& a,size_t i) {
    Tensor b{};std::copy_n(a.begin()+i,b.size(),b.begin());return b;
}
inline bool physical(const State& z,const Binding& b) {
    if(!finite(z)||z[b.void_ratio]<0||!in_ball(block(z,b.memory),b.R))return false;
    auto s=block(z,b.stress);
    const double n=magnitude(s);
    if(!std::isfinite(n)||n<=0)return false;
    for(double& x:s)x/=n;
    const auto [x,y,w,u,v,t]=s;
    const double minor=x*y-u*u/2;
    const double det=x*y*w-(x*v*v+y*t*t+w*u*u)/2+u*v*t/std::sqrt(2.);
    double h2=0.;for(double xh:block(z,b.memory))h2+=xh*xh;
    return x>0&&y>0&&w>0&&minor>b.stress_margin&&det>b.stress_margin&&std::sqrt(h2)<=b.R;
}

inline bool radial(const Tensor& total,const Wide& fraction,double R,double beta,Tensor& out) {
    // Same positive-series inversion as the reviewed onset preflight.
    WideTensor d{};Wide squared=0;
    for(size_t i=0;i<d.size();++i){d[i]=total[i];squared+=d[i]*d[i];}
    const Wide length=sqrt(squared);
    if(length==0){out={};return true;}
    const double distance=(length/Wide(R)*fraction).convert_to<double>();
    if(distance<0||distance>.5)return false;
    double lo=0.,hi=distance;
    for(int j=0;j<56;++j){
        const double mid=(lo+hi)*.5;
        if(mid==lo||mid==hi)break;
        const double q=std::pow(mid,beta);
        if(!std::isfinite(q)||q>=1)return false;
        double term=1.,sum=0.;
        bool enclosed=false;
        for(int k=0;k<4096;++k){
            sum+=term/(1+k*beta);
            term*=q;
            if(term/((1-q)*(1+(k+1)*beta))<=2e-17*sum){enclosed=true;break;}
        }
        if(!enclosed)return false;
        if(mid*sum<distance)lo=mid;else hi=mid;
    }
    for(Wide& x:d)x/=length;
    out=convert(Wide((lo+hi)*.5),Wide(R),d);
    return in_ball(out,R);
}

inline Wide point(int j,int k,bool graded) {
    const Wide t=ldexp(Wide(j),-k);
    if(!graded)return t;
    if(t<Wide(1)/64)return t/4096;
    return t*t*t;
}

inline Advance advance(int model,const State& parent,const Sym<double>& total,const State& params,
                       const IntegrationSettings& settings,const Binding& b) {
    constexpr double memory_budget=2e-12;
    constexpr double stress_budget=0.00034707403038589053;
    constexpr int probes_max=1000000,onset_depth=5;
    Advance out;out.state=parent;out.settings=settings;
    const auto fail=[&](const char* why){out.message=why;return out;};
    if(!valid_settings(settings)||settings.max_depth>20||settings.max_iterations>45||
       settings.max_backtracks>11||settings.max_substeps>20000||
       model<0||model>=int(models().size())||!models()[model].rate||models()[model].physical_time)
        return fail("weighted history requires qualified rate-model settings");
    if(parent.size()!=13||b.stress+6>13||b.void_ratio>=13||b.memory+6>13||
       b.stress!=0||b.void_ratio!=6||b.memory!=7||
       !std::isfinite(b.stress_margin)||b.stress_margin<0||
       !std::isfinite(b.beta)||b.beta<=0||b.beta>1||
       !valid_parameters(model,params)||!domain(model,parent,params,true)||
       !physical(parent,b)||!std::all_of(total.v.begin(),total.v.end(),[](double x){return std::isfinite(x);}))
        return fail("invalid weighted history layout, parameters or state");
    State prepared;
    if(!prepare_model_increment(model,parent,total,params,prepared)||prepared!=parent)
        return fail("weighted history profile requires no increment reset");
    const auto scales=model_scales(model,params);
    for(double x:scales)if(!std::isfinite(x)||x<=0)return fail("invalid weighted history scales");
    const auto scaled=[&](const State& a,const State& z){
        double err=0.;for(size_t i=0;i<a.size();++i)err=std::max(err,std::abs(a[i]-z[i])/scales[i]);
        return err;
    };
    auto dist=[&](const State& a,const State& z,size_t offset){
        Tensor d{};for(size_t i=0;i<d.size();++i)d[i]=a[offset+i]-z[offset+i];return magnitude(d);
    };
    const auto H=block(parent,b.memory);
    const bool loaded=std::any_of(total.v.begin(),total.v.end(),[](double x){return x!=0;});
    const bool graded=loaded&&std::all_of(H.begin(),H.end(),[](double x){return x==0;});
    const auto rr=Dyadic::from(b.R)*Dyadic::from(b.R)*Dyadic::power(-2);
    const bool use_radial=graded&&(exact_dot(total.v,total.v)-rr).sign<0&&magnitude(total.v)/b.R<.5;
    const bool reversal=loaded&&!graded&&reversal_region(H,total.v,b.R);
    auto& diag=out.diagnostics;
    int probes=0;
    auto rate=[&](const State& z,const State& zn,const Sym<double>& de,State& v){
        if(probes>=probes_max)return false;
        ++probes;
        if(!physical(z,b)||!physical(zn,b)||!domain(model,zn,params,true)
           ||!solution_admissible(model,z,params))return false;
        State gate;
        return evaluate_model(model,z,zn,de,params,gate,false,std::numeric_limits<double>::quiet_NaN(),true)
            &&evaluate_model(model,z,zn,de,params,v)&&v.size()==z.size()&&finite(v);
    };
    const auto norm=[&](const State& x){
        double n=0.;for(size_t i=0;i<x.size();++i)n=std::max(n,std::abs(x[i])/scales[i]);return n;
    };
    auto step=[&](const State& zn,const Sym<double>& de,const Wide& end,const Wide& fraction,State& x){
        History hist;
        Tensor resolved{};
        if(reversal&&!reversal_history(block(zn,b.memory),de.v,b.R,b.beta,resolved,
                                       memory_budget*fraction.convert_to<double>(),probes,probes_max))return false;
        if(!endpoint(zn[b.void_ratio],block(zn,b.memory),de.v,b.R,b.beta,hist,reversal?&resolved:nullptr)||
           (use_radial&&!radial(total.v,end,b.R,b.beta,hist.h)))return false;
        State r0;
        if(!rate(zn,zn,de,r0))return false;
        const double initial=norm(r0);
        x=zn;
        x[b.void_ratio]=hist.e;
        std::copy(hist.h.begin(),hist.h.end(),x.begin()+b.memory);
        if(initial==0.){
            if(x!=zn)return false;
            x=zn;return true;
        }
        auto residual=[&](const State& candidate,State& res){
            State r;
            if(!rate(candidate,zn,de,r))return false;
            res.resize(zn.size());
            for(size_t i=0;i<res.size();++i){
                const double delta=candidate[i]-zn[i];
                const double blend=(use_radial||reversal)&&i>=b.memory?delta:r0[i]+hist.theta*(r[i]-r0[i]);
                res[i]=delta-blend;
            }
            return finite(res);
        };
        State res;
        if(!residual(x,res))return false;
        for(int it=0;it<settings.max_iterations;++it){
            ++diag.iterations;
            const double error=norm(res);
            if(error<std::min(1e-12,initial*1e-6))return true;
            bool decreased=false;
            for(int j=0;j<=settings.max_backtracks;++j){
                State trial=x,rt;const double alpha=std::ldexp(1.,-j);
                for(size_t i=b.stress;i<b.stress+6;++i)trial[i]-=alpha*res[i];
                if(residual(trial,rt)&&norm(rt)<error){x=std::move(trial);res=std::move(rt);decreased=true;break;}
            }
            if(!decreased)return false;
        }
        return false;
    };
    const Wide floor=ldexp(Wide(1),-settings.max_depth);
    const char* terminal=nullptr;
    auto walk=[&](auto&& self,const State& zn,int j,int k,State& z)->bool{
        if(probes>=probes_max){terminal="probe cap";return false;}
        if(k>settings.max_depth){terminal="depth cap";return false;}
        if(diag.substeps+2>settings.max_substeps){terminal="substep cap";return false;}
        const Wide lo=point(j,k,graded),hi=point(j+1,k,graded),mid=point(2*j+1,k+1,graded);
        if(hi-lo<floor||mid-lo<floor/2||hi-mid<floor/2){terminal="physical depth cap";return false;}
        if(!graded||k>=onset_depth){
            const auto full_load=(hi-lo).convert_to<double>()*total;
            const auto first_load=(mid-lo).convert_to<double>()*total;
            const auto second_load=(hi-mid).convert_to<double>()*total;
            State full,half,two;
            if(step(zn,full_load,hi,hi-lo,full)&&step(zn,first_load,mid,mid-lo,half)&&step(half,second_load,hi,hi-mid,two)){
                const double defect=scaled(full,two),span=(hi-lo).convert_to<double>();
                diag.error=defect;
                if(defect<std::min(1e-8,settings.rate_tolerance)
                   &&(graded||dist(full,two,b.memory)<=memory_budget*std::ldexp(1.,-k))
                   &&dist(full,two,b.stress)<=stress_budget*span){
                    diag.substeps+=2;
                    diag.increment_fractions.push_back((mid-lo).convert_to<double>());
                    diag.increment_fractions.push_back((hi-mid).convert_to<double>());
                    diag.accepted_increments.emplace_back(first_load.v.begin(),first_load.v.end());
                    diag.accepted_increments.emplace_back(second_load.v.begin(),second_load.v.end());
                    z=std::move(two);return true;
                }
            }
            ++diag.rejected;
        }
        State half;
        return self(self,zn,2*j,k+1,half)&&self(self,half,2*j+1,k+1,z);
    };
    State z;
    out.ok=walk(walk,parent,0,0,z);
    diag.attempted_substeps=diag.first_attempt_substeps=diag.substeps;
    if(out.ok)out.state=std::move(z);
    else{
        out.message=std::string(terminal?terminal:"weighted material advance refused")+"; state rolled back";
        diag.discarded_substeps=diag.substeps;
        diag.discarded_increment_fractions=std::move(diag.increment_fractions);
        diag.discarded_increments=std::move(diag.accepted_increments);
    }
    return out;
}
}
