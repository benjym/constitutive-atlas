#pragma once
#include "trace/time.hpp"
#include <set>

namespace atlas_trace {
struct ScheduleSettings {
    TimeSettings time;
    double nonlinear_tolerance=1e-10;
    int maximum_iterations=40;
};
struct Control { bool stress=false; int kind=0; double value=0; }; // 0 hold, 1 rate, 2 absolute target
struct Segment { std::string id; double duration=0; int samples=1; std::array<Control,6> controls; };
struct ControlPath {
    std::array<bool,6> stress{};
    Sym<double> rates, stress_start;
    double start=0;
};
inline std::vector<int> control_components(int model){return models()[model].axisymmetric?std::vector<int>{0,1}:std::vector<int>{0,1,2,3,4,5};}
struct ControlledState { State state,observables; Sym<double> strain,rate; double nonlinear_error=0; };
struct SchedulePoint : ControlledState {
    double time=0; int segment=-1; bool transition=false;
    std::array<bool,6> stress_controls{};
    Diagnostics diagnostics;
};
struct ScheduleResult { bool ok=false; std::string message; std::vector<SchedulePoint> points; };
inline bool observables(int model,const State& state,const Sym<double>& rate,const State& p,double time,State& out) {
    return evaluate_model(model,state,state,rate,p,out,false,time,false,true)&&finite(out);
}
inline bool valid_schedule_settings(const ScheduleSettings& s) {
    return valid_time_settings(s.time)&&std::isfinite(s.nonlinear_tolerance)&&s.nonlinear_tolerance>0&&
        s.nonlinear_tolerance<=1e-3&&s.maximum_iterations>=1&&s.maximum_iterations<=100;
}
// Simultaneously solve backward-Euler state balance and endpoint mixed controls.
// Unknown strain increments exist only for stress-controlled Mandel components.
template<class T>
bool controlled_residual(int model,const std::vector<T>& u,const State& zn,const State& p,
                         double t0,double t1,const ControlPath& path,const State& scales,
                         const State& output_scales,std::vector<T>& r) {
    const int n=int(zn.size()),so=models()[model].stress_offset;
    const double h=t1-t0;std::vector<T> z(u.begin(),u.begin()+n),f,output;
    Sym<T> rate;int k=n;
    for(int j=0;j<6;++j)rate.v[j]=T(path.rates.v[j]);
    for(int j:control_components(model))if(path.stress[j])rate.v[j]=u[k++]/T(h);
    if(models()[model].axisymmetric)rate.v[2]=rate.v[1];
    if(!evaluate_model(model,z,z,rate,p,f,false,t1)||
       !evaluate_model(model,z,z,rate,p,output,false,t1,false,true))return false;
    r.resize(u.size());
    for(int i=0;i<n;++i)r[i]=(z[i]-T(zn[i])-T(h)*f[i])/T(scales[i]*std::min(h,1.));
    k=n;
    for(int j:control_components(model))if(path.stress[j]){
        const double target=path.stress_start.v[j]+path.rates.v[j]*(t1-path.start);
        r[k++]=(output[so+j]-T(target))/T(output_scales[so+j]);
    }
    return true;
}
inline bool controlled_backward_euler(int model,const ControlledState& previous,const State& p,
                                      double t0,double t1,const ControlPath& path,const ScheduleSettings& settings,
                                      ControlledState& result,Diagnostics& diagnostics) {
    const int n=int(previous.state.size());const double h=t1-t0;
    const auto scales=model_scales(model,p),os=model_observable_scales(model,p);
    State u=previous.state,unknown_scales=scales;
    for(int j:control_components(model))if(path.stress[j]){u.push_back(previous.rate.v[j]*h);unknown_scales.push_back(1.);}
    const int count=int(u.size());
    if(count>max_derivatives)return false;
    for(int iteration=0;iteration<settings.maximum_iterations;++iteration){
        ++diagnostics.iterations;std::vector<Jet> x(count),r;
        for(int i=0;i<count;++i){x[i]=Jet(u[i]);x[i].d[i]=unknown_scales[i];}
        if(!controlled_residual(model,x,previous.state,p,t0,t1,path,scales,os,r))return false;
        State residual(count);std::vector<State> jac(count,State(count));
        for(int i=0;i<count;++i){residual[i]=r[i].v;for(int j=0;j<count;++j)jac[i][j]=r[i].d[j];}
        if(!finite(residual))return false;
        double error=0;for(double v:residual)error=std::max(error,std::abs(v));
        if(error<=settings.nonlinear_tolerance){
            result.nonlinear_error=error;result.state.assign(u.begin(),u.begin()+n);result.strain=previous.strain;
            int k=n;
            Sym<double> increments;for(int j=0;j<6;++j)increments.v[j]=path.rates.v[j]*h;
            for(int j:control_components(model))if(path.stress[j])increments.v[j]=u[k++];
            if(models()[model].axisymmetric)increments.v[2]=increments.v[1];
            for(int j=0;j<6;++j){result.strain.v[j]+=increments.v[j];result.rate.v[j]=increments.v[j]/h;}
            return finite(result.state)&&std::isfinite(norm(result.strain))&&
                observables(model,result.state,result.rate,p,t1,result.observables);
        }
        State delta;for(double& v:residual)v=-v;
        if(!solve_linear(jac,residual,delta))return false;
        bool accepted=false;
        for(double alpha=1;alpha>=1./2048;alpha*=.5){
            auto trial=u;State rt;
            for(int i=0;i<count;++i)trial[i]+=alpha*delta[i]*unknown_scales[i];
            if(!finite(trial)||!controlled_residual(model,trial,previous.state,p,t0,t1,path,scales,os,rt)||!finite(rt))continue;
            double trial_error=0;for(double v:rt)trial_error=std::max(trial_error,std::abs(v));
            if(trial_error<error){u=trial;accepted=true;break;}
        }
        if(!accepted)return false;
    }
    return false;
}
inline bool advance_controlled(int model,const ControlledState& previous,const State& p,double t0,double t1,
                               const ControlPath& path,const ScheduleSettings& settings,ControlledState& out,
                               Diagnostics& diagnostics,int depth=0){
    const double h=t1-t0,tm=t0+h*.5;
    if(depth>settings.time.maximum_depth||diagnostics.substeps+2>settings.time.maximum_substeps||
       h*.5<settings.time.minimum_step||!(tm>t0&&tm<t1))return false;
    if(h<=settings.time.maximum_step){
        ControlledState full,half,two;
        if(controlled_backward_euler(model,previous,p,t0,t1,path,settings,full,diagnostics)&&
           controlled_backward_euler(model,previous,p,t0,tm,path,settings,half,diagnostics)&&
           controlled_backward_euler(model,half,p,tm,t1,path,settings,two,diagnostics)){
            auto scales=model_scales(model,p);double error=0;
            auto accumulate=[&](double a,double b,double initial,double scale){
                const double weight=settings.time.absolute_tolerance*scale+settings.time.relative_tolerance*std::max(std::abs(initial),std::abs(b));
                const double component=std::abs(a-b)/weight; // Richardson factor for BE is 2^1-1.
                if(!std::isfinite(weight)||weight<=0||!std::isfinite(component))error=std::numeric_limits<double>::infinity();
                else error=std::max(error,component);
            };
            for(size_t i=0;i<previous.state.size();++i)accumulate(full.state[i],two.state[i],previous.state[i],scales[i]);
            for(int i=0;i<6;++i)accumulate(full.strain.v[i],two.strain.v[i],previous.strain.v[i],1.);
            if(error<=1){out=two;diagnostics.error=error;diagnostics.substeps+=2;return true;}
        }
        ++diagnostics.rejected;
    }
    ControlledState half;
    if(!advance_controlled(model,previous,p,t0,tm,path,settings,half,diagnostics,depth+1))return false;
    return advance_controlled(model,half,p,tm,t1,path,settings,out,diagnostics,depth+1);
}
// At a segment boundary enforce the algebraic stress controls without changing
// persistent state. A state-only stress may leave its instantaneous rate
// undetermined; transition samples mask those stress-controlled rates as null.
inline bool transition_controls(int model,const State& z,const State& p,double time,const ControlPath& path,
                                Sym<double>& rate,State& output,double& nonlinear_error,const ScheduleSettings& settings){
    std::vector<int> indices;for(int j=0;j<6;++j)if(!path.stress[j])rate.v[j]=path.rates.v[j];
    for(int j:control_components(model))if(path.stress[j])indices.push_back(j);
    const int n=int(indices.size()),so=models()[model].stress_offset;const auto scales=model_observable_scales(model,p);
    for(int iteration=0;iteration<settings.maximum_iterations;++iteration){
        if(models()[model].axisymmetric)rate.v[2]=rate.v[1];
        if(!observables(model,z,rate,p,time,output))return false;
        double error=0;State residual(n);
        for(int i=0;i<n;++i){residual[i]=(output[so+indices[i]]-path.stress_start.v[indices[i]])/scales[so+indices[i]];error=std::max(error,std::abs(residual[i]));}
        nonlinear_error=error;if(error<=settings.nonlinear_tolerance)return true;
        std::vector<Jet> zj;for(double v:z)zj.emplace_back(v);Sym<Jet> d;for(int j=0;j<6;++j)d.v[j]=Jet(rate.v[j]);
        for(int i=0;i<n;++i)d.v[indices[i]].d[i]=1.;
        if(models()[model].axisymmetric)d.v[2]=d.v[1];std::vector<Jet> obs;
        if(!evaluate_model(model,zj,zj,d,p,obs,false,time,false,true))return false;
        std::vector<State> jac(n,State(n));
        for(int i=0;i<n;++i)for(int j=0;j<n;++j)jac[i][j]=obs[so+indices[i]].d[j]/scales[so+indices[i]];
        State correction;for(double& v:residual)v=-v;if(!solve_linear(jac,residual,correction))return false;
        bool accepted=false;
        for(double alpha=1;alpha>=1./2048;alpha*=.5){auto trial=rate;for(int j=0;j<n;++j)trial.v[indices[j]]+=alpha*correction[j];
            if(models()[model].axisymmetric)trial.v[2]=trial.v[1];State values;
            if(!observables(model,z,trial,p,time,values))continue;
            double next=0;for(int j=0;j<n;++j)next=std::max(next,std::abs(values[so+indices[j]]-path.stress_start.v[indices[j]])/scales[so+indices[j]]);
            if(next<error){rate=trial;accepted=true;break;}}
        if(!accepted)return false;
    }
    return false;
}
inline ScheduleResult run_schedule(int model,const State& initial,const State& p,const Sym<double>& initial_strain,
                                   const Sym<double>& initial_rate,double start,const std::vector<Segment>& segments,
                                   const ScheduleSettings& settings={}){
    ScheduleResult run;
    if(model<0||model>=int(models().size())||!models()[model].physical_time||models()[model].stress_offset<0||
       initial.size()!=initial_state(model).size()||!valid_parameters(model,p)||!valid_schedule_settings(settings)||
       !std::isfinite(start)||!std::isfinite(norm(initial_strain))||!std::isfinite(norm(initial_rate))||segments.empty()||segments.size()>100){run.message="invalid schedule or missing symmetric stress observable";return run;}
    if(models()[model].axisymmetric){
        if(!axisymmetric_x(initial_strain)||!axisymmetric_x(initial_rate)){run.message="axisymmetric_x requires compatible initial strain and rate";return run;}
        for(const auto& seg:segments){const auto& a=seg.controls[1];const auto& b=seg.controls[2];
            if(a.stress!=b.stress||a.kind!=b.kind||a.value!=b.value){run.message="axisymmetric_x requires identical radial controls";return run;}
            for(int j=3;j<6;++j){const auto& c=seg.controls[j];if(c.stress||c.value!=0){run.message="axisymmetric_x requires zero prescribed shear strain";return run;}}
        }
    }
    const auto scales=model_scales(model,p),os=model_observable_scales(model,p);
    for(double s:scales)if(!std::isfinite(s)||s<=0){run.message="invalid state scale";return run;}
    for(double s:os)if(!std::isfinite(s)||s<=0){run.message="invalid observable scale";return run;}
    std::set<std::string> ids;double end=start;int total=0;
    for(const auto& seg:segments){
        const double next=end+seg.duration;
        if(seg.id.empty()||!ids.insert(seg.id).second||!std::isfinite(seg.duration)||seg.duration<=0||!std::isfinite(next)||!(next>end)||seg.samples<1||seg.samples>5000||(total+=seg.samples)>10000){run.message="invalid segment duration, identity or sample budget";return run;}
        for(const auto& control:seg.controls)if(control.kind<0||control.kind>2||!std::isfinite(control.value)||(control.kind==0&&control.value!=0)){run.message="invalid component control";return run;}
        end=next;
    }
    SchedulePoint point;point.time=start;point.state=initial;point.strain=initial_strain;point.rate=initial_rate;
    if(!time_domain(model,initial,p,start,true)||!observables(model,initial,initial_rate,p,start,point.observables)){run.message="inadmissible initial state or outputs";return run;}
    run.points.push_back(point);int accepted=0;
    for(size_t index=0;index<segments.size();++index){const auto& seg=segments[index];
        const auto entry=run.points.back();const double endpoint=entry.time+seg.duration;ControlPath path;path.start=entry.time;
        path.stress_start=tensor_from(entry.observables,models()[model].stress_offset);
        for(int j=0;j<6;++j){const auto& control=seg.controls[j];path.stress[j]=control.stress;
            const double initial_value=control.stress?path.stress_start.v[j]:entry.strain.v[j];
            path.rates.v[j]=control.kind==0?0:control.kind==1?control.value:(control.value-initial_value)/seg.duration;
            if(!std::isfinite(path.rates.v[j])){run.message="unrepresentable control rate";return run;}}
        point=entry;point.segment=int(index);point.transition=true;point.stress_controls=path.stress;point.diagnostics={};
        if(!transition_controls(model,entry.state,p,entry.time,path,point.rate,point.observables,point.nonlinear_error,settings)){run.message="inconsistent segment-entry controls; last committed point retained";return run;}
        run.points.push_back(point);
        for(int sample=1;sample<=seg.samples;++sample){
            const double target=sample==seg.samples?endpoint:entry.time+seg.duration*(double(sample)/seg.samples);
            const auto previous=run.points.back();ControlledState candidate;Diagnostics diagnostics;auto remaining=settings;
            remaining.time.maximum_substeps=settings.time.maximum_substeps-accepted;
            if(!(target>previous.time)||!advance_controlled(model,previous,p,previous.time,target,path,remaining,candidate,diagnostics)){
                run.message="schedule solve failed in segment "+seg.id+"; last committed sample retained";return run;}
            point={};static_cast<ControlledState&>(point)=candidate;point.time=target;point.segment=int(index);point.diagnostics=diagnostics;point.stress_controls=path.stress;
            run.points.push_back(point);accepted+=diagnostics.substeps;
        }
    }
    run.ok=true;return run;
}
}
