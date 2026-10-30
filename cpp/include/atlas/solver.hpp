#pragma once
#include "models.hpp"
#include <limits>
#include <stdexcept>
#include <sstream>

namespace atlas {
using State=std::vector<double>;
struct Diagnostics { int iterations=0, substeps=0, rejected=0; double error=0; std::vector<double> increment_fractions; };
struct Advance { bool ok=false; State state; Diagnostics diagnostics; std::string message; };
inline State default_parameters(int model) { State p;for(const auto&v:models().at(model).parameters)p.push_back(v.value);return p; }
inline State initial_state(int model){State z;for(const auto&f:models().at(model).fields)for(int i=0;i<f.size;++i)z.push_back(f.initial[i]);return z;}
inline void reset_transients(int model,State&z){for(const auto&f:models().at(model).fields)if(f.transient)for(int j=0;j<f.size;++j)z[f.offset+j]=0;}
inline bool finite(const State&z){for(double v:z)if(!std::isfinite(v))return false;return true;}
inline bool valid_parameters(int model,const State&p){const auto&ps=models().at(model).parameters;if(p.size()!=ps.size())return false;for(size_t i=0;i<p.size();++i)if(!std::isfinite(p[i])||p[i]<ps[i].lower||p[i]>ps[i].upper)return false;return true;}
inline bool domain(int model,const State&z,const State&p,bool initial=false){State out;Sym<double> zero;return finite(z)&&evaluate_model(model,z,z,zero,p,out,initial)&&finite(out);}
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
inline bool implicit_step(int model,const State&zn,const Sym<double>&de,const State&p,State&z,Diagnostics&diag){
    const auto scales=model_scales(model,p);const int n=int(zn.size());z=zn;reset_transients(model,z);
    bool predictor=false;for(const auto&f:models().at(model).fields)predictor=predictor||f.multiplier;
    for(int it=0;it<45;++it){
        ++diag.iterations;std::vector<Jet> x(n),xn(n),r;Sym<Jet>d;
        for(int i=0;i<n;++i){x[i]=Jet(z[i]);x[i].d[i]=scales[i];xn[i]=Jet(zn[i]);}
        for(int i=0;i<6;++i)d.v[i]=Jet(de.v[i]);
        if(!evaluate_model(model,x,xn,d,p,r))return false;
        if(predictor)for(const auto&f:models().at(model).fields)if(f.multiplier)r[f.offset]=x[f.offset];
        State residual(n);std::vector<State> jac(n,State(n));
        for(int i=0;i<n;++i){residual[i]=r[i].v/scales[i];for(int j=0;j<n;++j)jac[i][j]=r[i].d[j]/scales[i];}
        if(!finite(residual))return false;
        double err=0;for(double v:residual)err=std::max(err,std::abs(v));diag.error=err;
        if(err<2e-10){if(predictor){predictor=false;continue;}return true;}
        State delta;for(double&v:residual)v=-v;if(!solve_linear(jac,residual,delta))return false;
        bool accepted=false;
        for(double alpha=1.;alpha>=1./2048;alpha*=.5){State trial=z,rt;for(int i=0;i<n;++i)trial[i]+=alpha*delta[i]*scales[i];
            if(!finite(trial)||!evaluate_model(model,trial,zn,de,p,rt)||!finite(rt))continue;
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
inline bool advance_recursive(int model,const State&zn,const Sym<double>&de,const State&p,State&z,Diagnostics&diag,int depth){
    if(depth>14||diag.substeps>20000)return false;
    const bool rate=models().at(model).rate;
    if(!rate){if(implicit_step(model,zn,de,p,z,diag)){++diag.substeps;diag.increment_fractions.push_back(std::ldexp(1.,-depth));return true;}}
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
            if(error<1e-6){z=two;diag.substeps+=2;diag.increment_fractions.push_back(std::ldexp(1.,-depth-1));diag.increment_fractions.push_back(std::ldexp(1.,-depth-1));return true;}
        }
    }
    ++diag.rejected;State half;
    if(!advance_recursive(model,zn,.5*de,p,half,diag,depth+1))return false;
    return advance_recursive(model,half,.5*de,p,z,diag,depth+1);
}
inline Advance integrate(int model,const State&zn,const Sym<double>&de,const State&p){
    Advance result;result.state=zn;
    if(model<0||model>=int(models().size())){result.message="unknown model";return result;}
    if(models()[model].physical_time){result.message="physical-time model requires the timed update API";return result;}
    if(zn.size()!=initial_state(model).size()||!valid_parameters(model,p)||!domain(model,zn,p,true)||!std::isfinite(norm(de))){result.message="invalid parameters, inadmissible initial state or strain increment";return result;}
    for(double s:model_scales(model,p))if(!std::isfinite(s)||s<=0){result.message="invalid state scales";return result;}
    State trial;
    result.ok=advance_recursive(model,zn,de,p,trial,result.diagnostics,0);
    if(result.ok)result.state=trial;else result.message="integration failed: domain boundary, singular system or substep limit; state rolled back";
    return result;
}

struct Point { double control=0; Sym<double> strain; State state; Diagnostics diagnostics; double pore_pressure=0; };
struct Run { bool ok=false; std::string message;std::vector<Point> points; };
// Mixed axisymmetric control. Trial constitutive evaluations always start from
// the same committed state. Outer Newton updates never accumulate trial history.
inline bool controlled_step(int model,const State&zn,const State&p,int protocol,double axial,double reference,double current_axial,Sym<double>&de,Advance&result){
    de={};de.v[0]=axial;
    if(protocol==0||protocol==4){de.v[1]=de.v[2]=protocol==4?axial:0.;result=integrate(model,zn,de,p);return result.ok;}
    if(protocol==2){de.v[1]=de.v[2]=-.5*axial;result=integrate(model,zn,de,p);return result.ok;}
    if(protocol==1){
        double lateral=-.2*axial;
        for(int it=0;it<30;++it){de.v[1]=de.v[2]=lateral;auto trial=integrate(model,zn,de,p);if(!trial.ok)return false;
            double residual=.5*(trial.state[1]+trial.state[2])-reference;
            if(std::abs(residual)<std::max(1.,std::abs(reference))*1e-8){result=trial;return true;}
            double h=std::max(1e-9,std::abs(axial)*1e-3);auto dd=de;dd.v[1]=dd.v[2]=lateral+h;auto pert=integrate(model,zn,dd,p);
            if(!pert.ok)return false;double derivative=(.5*(pert.state[1]+pert.state[2])-.5*(trial.state[1]+trial.state[2]))/h;
            if(!std::isfinite(derivative)||std::abs(derivative)<1e-6)return false;
            double correction=-residual/derivative;bool accepted=false;
            for(double a=1;a>=1./1024;a*=.5){auto testde=de;testde.v[1]=testde.v[2]=lateral+a*correction;auto test=integrate(model,zn,testde,p);
                if(test.ok&&std::abs(.5*(test.state[1]+test.state[2])-reference)<std::abs(residual)){lateral+=a*correction;accepted=true;break;}}
            if(!accepted)return false;
        }return false;
    }
    // protocol 3: prescribed deviator stress change and zero volume change.
    if(protocol==3){
        double da=0;double q0=zn[0]-.5*(zn[1]+zn[2]);
        for(int it=0;it<30;++it){de.v[0]=da;de.v[1]=de.v[2]=-.5*da;auto trial=integrate(model,zn,de,p);if(!trial.ok)return false;
            double q=trial.state[0]-.5*(trial.state[1]+trial.state[2]);double residual=q-q0-axial;
            if(std::abs(residual)<std::max(1.,std::abs(reference))*1e-8){result=trial;return true;}
            auto dd=de;dd.v[0]+=1e-8;dd.v[1]-=5e-9;dd.v[2]-=5e-9;auto pert=integrate(model,zn,dd,p);if(!pert.ok)return false;
            double tangent=(pert.state[0]-.5*(pert.state[1]+pert.state[2])-q)/1e-8;if(std::abs(tangent)<1e-4)return false;
            double correction=-residual/tangent;bool accepted=false;
            for(double a=1;a>=1./1024;a*=.5){auto testde=de;testde.v[0]=da+a*correction;testde.v[1]=testde.v[2]=-.5*testde.v[0];auto test=integrate(model,zn,testde,p);
                if(test.ok&&std::abs(test.state[0]-.5*(test.state[1]+test.state[2])-q0-axial)<std::abs(residual)){da+=a*correction;accepted=true;break;}}
            if(!accepted)return false;
        }
    }
    (void)current_axial;return false;
}
inline Run run_protocol(int model,const State&initial,const State&p,int protocol,double target,int steps,int cycles){
    Run run;if(model<0||model>=int(models().size())||protocol<0||protocol>4||steps<1||steps>5000||cycles<0||cycles>100||!std::isfinite(target)||!valid_parameters(model,p)||initial.size()!=initial_state(model).size()||!domain(model,initial,p)){
        run.message="invalid run specification";return run;}
    if(std::abs(initial[1]-initial[2])>1e-6||std::abs(initial[3])+std::abs(initial[4])+std::abs(initial[5])>1e-12){run.message="laboratory protocols require axisymmetric initial stress";return run;}
    if(cycles&&steps<16*cycles){run.message="cyclic loading requires at least 16 increments per cycle";return run;}
    if((protocol==3&&std::abs(target)>1e8)||(protocol!=3&&std::abs(target)>.1)){run.message="control amplitude exceeds laboratory limit";return run;}
    Point committed;committed.state=initial;run.points.push_back(committed);
    double lateral=.5*(initial[1]+initial[2]);
    for(int i=1;i<=steps;++i){
        double control=cycles?target*std::sin(2*3.141592653589793*cycles*i/steps):target*i/steps;
        auto previous=run.points.back();Sym<double> de;Advance result;
        if(!controlled_step(model,previous.state,p,protocol,control-previous.control,lateral,previous.strain.v[0],de,result)){
            run.message="control or constitutive solve failed at step "+std::to_string(i)+"; last committed point retained";return run;}
        Point point;point.control=control;point.state=result.state;point.strain=previous.strain+de;point.diagnostics=result.diagnostics;
        if(protocol==2||protocol==3)point.pore_pressure=lateral-.5*(point.state[1]+point.state[2]);
        run.points.push_back(point);
    }
    run.ok=true;return run;
}
}
