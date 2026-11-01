#pragma once
#include "models.hpp"
#include "atlas/settings.hpp"
#include "atlas/solution_constraints.hpp"
#include <limits>
#include <stdexcept>
#include <sstream>

namespace atlas {
using State=std::vector<double>;
struct Diagnostics { int hierarchical_seed_trials=0, hierarchical_seed_acceptances=0; int path_seed_value_evaluations=0, path_seed_acceptances=0; int reserved_path_trials=0; int iterations=0, substeps=0, rejected=0; double error=0; std::vector<double> increment_fractions; };
struct Advance { bool ok=false; State state; Diagnostics diagnostics; std::string message; IntegrationSettings settings; };
} // namespace atlas
#include "atlas/outer_transaction.hpp"
namespace atlas {
inline State default_parameters(int model) { State p;for(const auto&v:models().at(model).parameters)p.push_back(v.value);return p; }
inline State initial_state(int model){State z;for(const auto&f:models().at(model).fields)for(int i=0;i<f.size;++i)z.push_back(f.initial[i]);return z;}
inline void reset_transients(int model,State&z){for(const auto&f:models().at(model).fields)if(f.transient)for(int j=0;j<f.size;++j)z[f.offset+j]=0;}
inline bool finite(const State&z){for(double v:z)if(!std::isfinite(v))return false;return true;}
inline bool valid_parameters(int model,const State&p){const auto&ps=models().at(model).parameters;if(p.size()!=ps.size())return false;for(size_t i=0;i<p.size();++i)if(!std::isfinite(p[i])||p[i]<ps[i].lower||p[i]>ps[i].upper)return false;return true;}
inline bool solution_admissible(int model,const State& z,const State& p){return model>=0 && model<int(models().size()) && checked_solution_state(models()[model],z,p);}
inline bool domain(int model,const State&z,const State&p,bool initial=false){State out;Sym<double> zero;return finite(z)&&solution_admissible(model,z,p)&&evaluate_model(model,z,z,zero,p,out,initial)&&finite(out);}
inline double scaled_norm(const State&r,const State&scales){double n=0;for(size_t i=0;i<r.size();++i)n=std::max(n,std::abs(r[i]/scales[i]));return n;}
inline bool solve_linear(std::vector<State> a,State b,State&x){
    const int n=int(b.size());
    for(int k=0;k<n;++k){int pivot=k;for(int i=k+1;i<n;++i)if(std::abs(a[i][k])>std::abs(a[pivot][k]))pivot=i;
        if(!std::isfinite(a[pivot][k])||std::abs(a[pivot][k])<1e-14)return false;
        std::swap(a[k],a[pivot]);std::swap(b[k],b[pivot]);
        for(int i=k+1;i<n;++i){double f=a[i][k]/a[k][k];for(int j=k+1;j<n;++j)a[i][j]-=f*a[k][j];b[i]-=f*b[k];}
    }
    x.assign(n,0);for(int i=n-1;i>=0;--i){double s=b[i];for(int j=i+1;j<n;++j)s-=a[i][j]*x[j];x[i]=s/a[i][i];}return finite(x);
}
} // namespace atlas
#include "atlas/implicit_seed.hpp"
namespace atlas {
inline bool implicit_step(int model,const State&zn,const Sym<double>&de,const State&p,State&z,Diagnostics&diag,const IntegrationSettings&settings={},const State*initial_guess=nullptr){
    const auto scales=model_scales(model,p);const int n=int(zn.size());z=zn;reset_transients(model,z);
    if(!solution_admissible(model,z,p))return false;
    bool predictor=false;for(const auto&f:models().at(model).fields)predictor=predictor||f.multiplier;
    if(initial_guess){
        State seeded;
        auto reset=[&](State&candidate){reset_transients(model,candidate);};
        auto admissible=[&](const State&candidate){return solution_admissible(model,candidate,p);};
        auto evaluate=[&](const State&candidate,State&residual){return evaluate_model(model,candidate,zn,de,p,residual);};
        auto override_residual=[&](const State&candidate,State&residual){if(predictor)for(const auto&f:models().at(model).fields)if(f.multiplier)residual[f.offset]=candidate[f.offset];};
        if(choose_implicit_seed(z,initial_guess,scales,reset,admissible,evaluate,override_residual,seeded,diag.path_seed_value_evaluations)){z=std::move(seeded);++diag.path_seed_acceptances;}
    }
    // Input Jets are created here: state columns0..n-1 only, all tail columns equalzero.
    DerivativeTailScope derivative_scope(settings.increment_tolerance>0.?n+1:derivative_work_columns());
    for(int it=0;it<settings.max_iterations;++it){
        ++diag.iterations;std::vector<Jet> x(n),xn(n),r;Sym<Jet>d;
        for(int i=0;i<n;++i){x[i]=Jet(z[i]);x[i].d[i]=scales[i];xn[i]=Jet(zn[i]);}
        for(int i=0;i<6;++i)d.v[i]=Jet(de.v[i]);
        if(!evaluate_model(model,x,xn,d,p,r))return false;
        if(predictor)for(const auto&f:models().at(model).fields)if(f.multiplier)r[f.offset]=x[f.offset];
        State residual(n);std::vector<State> jac(n,State(n));
        for(int i=0;i<n;++i){residual[i]=r[i].v/scales[i];for(int j=0;j<n;++j)jac[i][j]=r[i].d[j]/scales[i];}
        if(!finite(residual))return false;
        double err=0;for(double v:residual)err=std::max(err,std::abs(v));diag.error=err;
        if(err<settings.residual_tolerance){if(predictor){predictor=false;continue;}return solution_admissible(model,z,p);}
        State delta;for(double&v:residual)v=-v;if(!solve_linear(jac,residual,delta))return false;
        bool accepted=false;
        for(int backtrack=0;backtrack<=settings.max_backtracks;++backtrack){double alpha=std::ldexp(1.,-backtrack);State trial=z,rt;for(int i=0;i<n;++i)trial[i]+=alpha*delta[i]*scales[i];
            if(!finite(trial)||!solution_admissible(model,trial,p)||!evaluate_model(model,trial,zn,de,p,rt)||!finite(rt))continue;
            if(predictor)for(const auto&f:models().at(model).fields)if(f.multiplier)rt[f.offset]=trial[f.offset];
            if(scaled_norm(rt,scales)<err){z=trial;accepted=true;break;}
        }
        if(!accepted)return false;
    }
    return false;
}
inline bool midpoint(int model,const State&zn,const Sym<double>&de,const State&p,State&z,State*endpoint_defect=nullptr){
    State k1,k2,mid=zn;if(!evaluate_model(model,zn,zn,de,p,k1)||!finite(k1))return false;
    for(size_t i=0;i<zn.size();++i)mid[i]+=.5*k1[i];
    if(!finite(mid)||!evaluate_model(model,mid,zn,de,p,k2)||!finite(k2))return false;
    z=zn;for(size_t i=0;i<zn.size();++i)z[i]+=k2[i];
    if(!domain(model,z,p))return false;
    // Step doubling alone can miss a branch entered after the final midpoint.
    // Sample the endpoint and compare midpoint with Simpson-type quadrature.
    // The defect is O(increment^3) on smooth paths and detects hidden crossings.
    if(endpoint_defect){
        State k3;if(!evaluate_model(model,z,zn,de,p,k3)||!finite(k3))return false;
        endpoint_defect->resize(zn.size());
        for(size_t i=0;i<zn.size();++i)(*endpoint_defect)[i]=(k1[i]-2*k2[i]+k3[i])/6.;
        if(!finite(*endpoint_defect))return false;
    }
    return true;
}
} // namespace atlas
#include "atlas/path_error_control.hpp"
namespace atlas {
inline bool advance_recursive(int model,const State&zn,const Sym<double>&de,const State&p,State&z,Diagnostics&diag,int depth,const IntegrationSettings&settings={},const State*full_initial_guess=nullptr){
    if(depth>settings.max_depth||diag.substeps>=settings.max_substeps)return false;
    const bool rate=models().at(model).rate;
    State left_seed,right_seed;
    if(!rate){
        if(settings.increment_tolerance==0.){if(implicit_step(model,zn,de,p,z,diag,settings)){++diag.substeps;diag.increment_fractions.push_back(std::ldexp(1.,-depth));return true;}}
        else {
            // Reserve three solves even if short-circuiting executes fewer.
            if(diag.reserved_path_trials>3*settings.max_substeps-3)return false;
            diag.reserved_path_trials+=3;
            State full,half,two;double error=0.;
            const int accepted_before=diag.path_seed_acceptances;
            if(full_initial_guess)++diag.hierarchical_seed_trials;
            bool solved=implicit_step(model,zn,de,p,full,diag,settings,full_initial_guess);
            if(full_initial_guess&&diag.path_seed_acceptances>accepted_before)++diag.hierarchical_seed_acceptances;
            if(solved){State seed=zn;for(size_t i=0;i<seed.size();++i)seed[i]=.5*zn[i]+.5*full[i];solved=implicit_step(model,zn,.5*de,p,half,diag,settings,&seed);}
            if(solved){left_seed=half;solved=implicit_step(model,half,.5*de,p,two,diag,settings,&full);if(solved)right_seed=two;}
            if(solved&&implicit_path_error(model,zn,full,half,two,p,settings,error)){
                diag.error=error;
                if(error<settings.increment_tolerance){
                    if(diag.substeps>settings.max_substeps-2)return false;
                    z=two;diag.substeps+=2;diag.increment_fractions.push_back(std::ldexp(1.,-depth-1));diag.increment_fractions.push_back(std::ldexp(1.,-depth-1));return true;
                }
            }
        }
    }
    else {
        State full,half,two,half_defect,two_defect;const auto halfde=.5*de;
        if(midpoint(model,zn,de,p,full)&&midpoint(model,zn,halfde,p,half,&half_defect)&&midpoint(model,half,halfde,p,two,&two_defect)){
            auto scales=model_scales(model,p);double error=0;
            for(size_t i=0;i<zn.size();++i){
                error=std::max(error,std::abs(full[i]-two[i])/scales[i]);
                error=std::max(error,std::abs(half_defect[i])/scales[i]);
                error=std::max(error,std::abs(two_defect[i])/scales[i]);
            }
            diag.error=error;
            if(error<settings.rate_tolerance){if(diag.substeps>settings.max_substeps-2)return false;z=two;diag.substeps+=2;diag.increment_fractions.push_back(std::ldexp(1.,-depth-1));diag.increment_fractions.push_back(std::ldexp(1.,-depth-1));return true;}
        }
    }
    ++diag.rejected;State half;
    if(!advance_recursive(model,zn,.5*de,p,half,diag,depth+1,settings,left_seed.empty()?nullptr:&left_seed))return false;
    return advance_recursive(model,half,.5*de,p,z,diag,depth+1,settings,right_seed.empty()?nullptr:&right_seed);
}
inline Advance integrate(int model,const State&zn,const Sym<double>&de,const State&p,const IntegrationSettings&settings={}){
    Advance result;result.state=zn;result.settings=settings;
    if(!valid_settings(settings)){result.message="invalid integration settings";return result;}
    if(model<0||model>=int(models().size())){result.message="unknown model";return result;}
    if(models()[model].physical_time){result.message="physical-time model requires the timed update API";return result;}
    if(settings.increment_tolerance>0. && (models()[model].rate||!path_metric_layout(model,settings))){result.message="path error control requires an incremental residual and its declared stress layout";return result;}
    if(zn.size()!=initial_state(model).size()||!valid_parameters(model,p)||!domain(model,zn,p,true)||!std::isfinite(norm(de))){result.message="invalid parameters, inadmissible initial state or strain increment";return result;}
    for(double s:model_scales(model,p))if(!std::isfinite(s)||s<=0){result.message="invalid state scales";return result;}
    State prepared;
    if(!prepare_model_increment(model,zn,de,p,prepared)||!domain(model,prepared,p)){
        result.message="increment reset failed: nonfinite guard/state or domain boundary; state rolled back";return result;
    }
    State trial;
    result.ok=advance_recursive(model,prepared,de,p,trial,result.diagnostics,0,settings);
    if(result.ok && !solution_admissible(model,trial,p))result.ok=false;
    if(result.ok)result.state=trial;else result.message="integration failed: domain boundary, singular system or substep limit; state rolled back";
    return result;
}

// Pore-pressure change is an external effective-stress boundary reconstruction.
// A total/unspecified stress tensor supplies no pore-pressure law.
inline bool laboratory_pore_reconstruction(StressScope scope,int protocol){
    return scope==StressScope::effective&&(protocol==2||protocol==3);
}
struct Point { double control=0; Sym<double> strain; State state; Diagnostics diagnostics; double pore_pressure=0; };
struct Run { bool ok=false; std::string message;std::vector<Point> points; IntegrationSettings settings; };
// Mixed axisymmetric control. Trial constitutive evaluations always start from
// the same committed state. Outer Newton updates never accumulate trial history.
inline bool controlled_step(int model,const State&zn,const State&p,int protocol,double axial,double reference,double current_axial,Sym<double>&de,Advance&result,const IntegrationSettings&settings={},bool allow_outer_reuse=true,OuterReuseCounts*work=nullptr){
    const bool reuse=allow_outer_reuse&&settings.increment_tolerance>0.&&model>=0&&model<int(models().size())&&!models()[model].rate;
    OuterTransaction slot;
    auto execute=[&](const Sym<double>&increment){if(work)++work->executed;return integrate(model,zn,increment,p,settings);};
    auto next_trial=[&](){Advance trial;const bool had=slot.occupied;if(reuse&&slot.take(model,zn,de,p,settings,trial)){if(work)++work->hits;return trial;}if(had&&work)++work->misses;return execute(de);};
    de={};de.v[0]=axial;
    if(protocol==0||protocol==4){de.v[1]=de.v[2]=protocol==4?axial:0.;result=integrate(model,zn,de,p,settings);return result.ok;}
    if(protocol==2){de.v[1]=de.v[2]=-.5*axial;result=integrate(model,zn,de,p,settings);return result.ok;}
    if(protocol==1){
        double lateral=-.2*axial;
        for(int it=0;it<30;++it){de.v[1]=de.v[2]=lateral;auto trial=next_trial();if(!trial.ok)return false;
            double residual=.5*(trial.state[1]+trial.state[2])-reference;
            if(std::abs(residual)<std::max(1.,std::abs(reference))*1e-8){result=trial;return true;}
            double h=std::max(1e-9,std::abs(axial)*1e-3);auto dd=de;dd.v[1]=dd.v[2]=lateral+h;auto pert=execute(dd);
            if(!pert.ok)return false;double derivative=(.5*(pert.state[1]+pert.state[2])-.5*(trial.state[1]+trial.state[2]))/h;
            if(!std::isfinite(derivative)||std::abs(derivative)<1e-6)return false;
            double correction=-residual/derivative;bool accepted=false;
            for(double a=1;a>=1./1024;a*=.5){auto testde=de;testde.v[1]=testde.v[2]=lateral+a*correction;auto test=execute(testde);
                if(test.ok&&std::abs(.5*(test.state[1]+test.state[2])-reference)<std::abs(residual)){if(reuse)slot.retain(model,zn,testde,p,settings,test);lateral+=a*correction;accepted=true;break;}}
            if(!accepted)return false;
        }return false;
    }
    // protocol 3: prescribed deviator stress change and zero volume change.
    if(protocol==3){
        double da=0;double q0=zn[0]-.5*(zn[1]+zn[2]);
        for(int it=0;it<30;++it){de.v[0]=da;de.v[1]=de.v[2]=-.5*da;auto trial=next_trial();if(!trial.ok)return false;
            double q=trial.state[0]-.5*(trial.state[1]+trial.state[2]);double residual=q-q0-axial;
            if(std::abs(residual)<std::max(1.,std::abs(reference))*1e-8){result=trial;return true;}
            auto dd=de;dd.v[0]+=1e-8;dd.v[1]-=5e-9;dd.v[2]-=5e-9;auto pert=execute(dd);if(!pert.ok)return false;
            double tangent=(pert.state[0]-.5*(pert.state[1]+pert.state[2])-q)/1e-8;if(std::abs(tangent)<1e-4)return false;
            double correction=-residual/tangent;bool accepted=false;
            for(double a=1;a>=1./1024;a*=.5){auto testde=de;testde.v[0]=da+a*correction;testde.v[1]=testde.v[2]=-.5*testde.v[0];auto test=execute(testde);
                if(test.ok&&std::abs(test.state[0]-.5*(test.state[1]+test.state[2])-q0-axial)<std::abs(residual)){if(reuse)slot.retain(model,zn,testde,p,settings,test);da+=a*correction;accepted=true;break;}}
            if(!accepted)return false;
        }
    }
    (void)current_axial;return false;
}
// Research range is an explicit caller choice, not a kinematic validity claim.
enum class LaboratoryRange { Interactive, ResearchQuarterStrain };
inline Run run_protocol_impl(int model,const State&initial,const State&p,int protocol,double target,int steps,int cycles,const IntegrationSettings&settings,const State*controls,LaboratoryRange range=LaboratoryRange::Interactive,bool allow_outer_reuse=true){
    Run run;run.settings=settings;if(!valid_settings(settings)||model<0||model>=int(models().size())||protocol<0||protocol>4||steps<1||steps>5000||cycles<0||cycles>100||!std::isfinite(target)||!valid_parameters(model,p)||initial.size()!=initial_state(model).size()||!domain(model,initial,p,true)){
        run.message="invalid run specification";return run;}
    if(std::abs(initial[1]-initial[2])>1e-6||std::abs(initial[3])+std::abs(initial[4])+std::abs(initial[5])>1e-12){run.message="laboratory protocols require axisymmetric initial stress";return run;}
    if(cycles&&steps<16*cycles){run.message="cyclic loading requires at least 16 increments per cycle";return run;}
    const double strain_limit=range==LaboratoryRange::ResearchQuarterStrain?.25:.1;
    if((protocol==3&&std::abs(target)>1e8)||(protocol!=3&&std::abs(target)>strain_limit)){run.message="control amplitude exceeds laboratory limit";return run;}
    Point committed;committed.control=controls?controls->front():0.;committed.state=initial;run.points.push_back(committed);
    double lateral=.5*(initial[1]+initial[2]);
    for(int i=1;i<=steps;++i){
        double control=controls?(*controls)[i]:(cycles?target*std::sin(2*3.141592653589793*cycles*i/steps):target*i/steps);
        auto previous=run.points.back();Sym<double> de;Advance result;
        if(!controlled_step(model,previous.state,p,protocol,control-previous.control,lateral,previous.strain.v[0],de,result,settings,allow_outer_reuse)){
            run.message="control or constitutive solve failed at step "+std::to_string(i)+"; last committed point retained";return run;}
        Point point;point.control=control;point.state=result.state;point.strain=previous.strain+de;point.diagnostics=result.diagnostics;
        if(laboratory_pore_reconstruction(models()[model].stress_scope,protocol))point.pore_pressure=lateral-.5*(point.state[1]+point.state[2]);
        run.points.push_back(point);
    }
    run.ok=true;return run;
}

// Legacy producers retain their original arithmetic and endpoint semantics.
inline Run run_protocol(int model,const State&initial,const State&p,int protocol,double target,int steps,int cycles,const IntegrationSettings&settings={}){
    return run_protocol_impl(model,initial,p,protocol,target,steps,cycles,settings,nullptr);
}
// laboratory-controls-0.1: cumulative change relative to the initial point.
// Protocol 3 specifies deviator stress change (Pa); all others specify strain.
// The original controller consumes differences of consecutive caller values.
// No interpolation, resampling, waveform generation or endpoint snapping.
inline Run run_protocol_controls(int model,const State&initial,const State&p,int protocol,const State&controls,const IntegrationSettings&settings={},LaboratoryRange range=LaboratoryRange::Interactive){
    Run invalid;invalid.settings=settings;
    if(controls.size()<2||controls.size()>5001||controls.front()!=0){
        invalid.message="explicit controls require 2..5001 points beginning at zero";return invalid;
    }
    double amplitude=0;
    for(double control:controls){
        if(!std::isfinite(control)){invalid.message="explicit controls must be finite";return invalid;}
        amplitude=std::max(amplitude,std::abs(control));
    }
    return run_protocol_impl(model,initial,p,protocol,amplitude,int(controls.size())-1,0,settings,&controls,range);
}

}
