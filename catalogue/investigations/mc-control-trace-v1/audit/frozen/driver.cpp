#include "atlas/solver.hpp"
#include <iostream>
#include <iomanip>
#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#define TRACE_EXPORT EMSCRIPTEN_KEEPALIVE
#else
#define TRACE_EXPORT
#endif
namespace atlas {
struct TraceCall {int step,iteration;std::string role;Sym<double> de;State parent;Advance result;};
inline std::vector<TraceCall> trace_calls;
inline int active_step=0;
inline bool literal_controls=false;
inline const double common_controls[64]={0x1.324db656e9146p+14,0x1.30d420f975a7ep+15,0x1.c591def36b5c5p+15,0x1.2af8afbcb219bp+16,0x1.704758ececfbcp+16,0x1.b20a0bee3c0a2p+16,0x1.ef9ea82630927p+16,0x1.1436ad992f24fp+17,0x1.2df50b9b2874ep+17,0x1.44caf6132f9b2p+17,0x1.5880205e088b8p+17,0x1.68e3f40844168p+17,0x1.75ce0898412dbp+17,0x1.7f1e872da68e7p+17,0x1.84be7900b80a7p+17,0x1.86a0000000000p+17,0x1.84be7900b80a8p+17,0x1.7f1e872da68e7p+17,0x1.75ce0898412dcp+17,0x1.68e3f40844168p+17,0x1.5880205e088b9p+17,0x1.44caf6132f9b2p+17,0x1.2df50b9b2874fp+17,0x1.1436ad992f250p+17,0x1.ef9ea82630927p+16,0x1.b20a0bee3c0a2p+16,0x1.704758ececfbfp+16,0x1.2af8afbcb219dp+16,0x1.c591def36b5c7p+15,0x1.30d420f975a87p+15,0x1.324db656e9152p+14,0x1.aee2609b0f0ecp-36,-0x1.324db656e9145p+14,-0x1.30d420f975a81p+15,-0x1.c591def36b5bfp+15,-0x1.2af8afbcb219ap+16,-0x1.704758ececfbcp+16,-0x1.b20a0bee3c09fp+16,-0x1.ef9ea82630924p+16,-0x1.1436ad992f24fp+17,-0x1.2df50b9b2874bp+17,-0x1.44caf6132f9b2p+17,-0x1.5880205e088b8p+17,-0x1.68e3f40844167p+17,-0x1.75ce0898412dbp+17,-0x1.7f1e872da68e6p+17,-0x1.84be7900b80a8p+17,-0x1.86a0000000000p+17,-0x1.84be7900b80a8p+17,-0x1.7f1e872da68e7p+17,-0x1.75ce0898412dcp+17,-0x1.68e3f40844168p+17,-0x1.5880205e088b9p+17,-0x1.44caf6132f9b3p+17,-0x1.2df50b9b2874dp+17,-0x1.1436ad992f251p+17,-0x1.ef9ea8263092dp+16,-0x1.b20a0bee3c0a2p+16,-0x1.704758ececfc0p+16,-0x1.2af8afbcb21a4p+16,-0x1.c591def36b5cap+15,-0x1.30d420f975a8ap+15,-0x1.324db656e9140p+14,-0x1.aee2609b0f0ecp-35};
inline Advance trace_integrate(const char*role,int iteration,int model,const State&zn,const Sym<double>&de,const State&p,const IntegrationSettings&settings){
 auto result=integrate(model,zn,de,p,settings);trace_calls.push_back({active_step,iteration,role,de,zn,result});return result;
}
inline bool traced_controlled_step(int model,const State&zn,const State&p,int protocol,double axial,double reference,double current_axial,Sym<double>&de,Advance&result,const IntegrationSettings&settings={}){
    de={};de.v[0]=axial;
    if(protocol==0||protocol==4){de.v[1]=de.v[2]=protocol==4?axial:0.;result=trace_integrate("direct",-1,model,zn,de,p,settings);return result.ok;}
    if(protocol==2){de.v[1]=de.v[2]=-.5*axial;result=trace_integrate("direct",-1,model,zn,de,p,settings);return result.ok;}
    if(protocol==1){
        double lateral=-.2*axial;
        for(int it=0;it<30;++it){de.v[1]=de.v[2]=lateral;auto trial=trace_integrate("trial",it,model,zn,de,p,settings);if(!trial.ok)return false;
            double residual=.5*(trial.state[1]+trial.state[2])-reference;
            if(std::abs(residual)<std::max(1.,std::abs(reference))*1e-8){result=trial;return true;}
            double h=std::max(1e-9,std::abs(axial)*1e-3);auto dd=de;dd.v[1]=dd.v[2]=lateral+h;auto pert=trace_integrate("pert",it,model,zn,dd,p,settings);
            if(!pert.ok)return false;double derivative=(.5*(pert.state[1]+pert.state[2])-.5*(trial.state[1]+trial.state[2]))/h;
            if(!std::isfinite(derivative)||std::abs(derivative)<1e-6)return false;
            double correction=-residual/derivative;bool accepted=false;
            for(double a=1;a>=1./1024;a*=.5){auto testde=de;testde.v[1]=testde.v[2]=lateral+a*correction;auto test=trace_integrate("test",it,model,zn,testde,p,settings);
                if(test.ok&&std::abs(.5*(test.state[1]+test.state[2])-reference)<std::abs(residual)){lateral+=a*correction;accepted=true;break;}}
            if(!accepted)return false;
        }return false;
    }
    // protocol 3: prescribed deviator stress change and zero volume change.
    if(protocol==3){
        double da=0;double q0=zn[0]-.5*(zn[1]+zn[2]);
        for(int it=0;it<30;++it){de.v[0]=da;de.v[1]=de.v[2]=-.5*da;auto trial=trace_integrate("trial",it,model,zn,de,p,settings);if(!trial.ok)return false;
            double q=trial.state[0]-.5*(trial.state[1]+trial.state[2]);double residual=q-q0-axial;
            if(std::abs(residual)<std::max(1.,std::abs(reference))*1e-8){result=trial;return true;}
            auto dd=de;dd.v[0]+=1e-8;dd.v[1]-=5e-9;dd.v[2]-=5e-9;auto pert=trace_integrate("pert",it,model,zn,dd,p,settings);if(!pert.ok)return false;
            double tangent=(pert.state[0]-.5*(pert.state[1]+pert.state[2])-q)/1e-8;if(std::abs(tangent)<1e-4)return false;
            double correction=-residual/tangent;bool accepted=false;
            for(double a=1;a>=1./1024;a*=.5){auto testde=de;testde.v[0]=da+a*correction;testde.v[1]=testde.v[2]=-.5*testde.v[0];auto test=trace_integrate("test",it,model,zn,testde,p,settings);
                if(test.ok&&std::abs(test.state[0]-.5*(test.state[1]+test.state[2])-q0-axial)<std::abs(residual)){da+=a*correction;accepted=true;break;}}
            if(!accepted)return false;
        }
    }
    (void)current_axial;return false;
}
inline Run traced_run_protocol(int model,const State&initial,const State&p,int protocol,double target,int steps,int cycles,const IntegrationSettings&settings={}){
    Run run;run.settings=settings;if(!valid_settings(settings)||model<0||model>=int(models().size())||protocol<0||protocol>4||steps<1||steps>5000||cycles<0||cycles>100||!std::isfinite(target)||!valid_parameters(model,p)||initial.size()!=initial_state(model).size()||!domain(model,initial,p)){
        run.message="invalid run specification";return run;}
    if(std::abs(initial[1]-initial[2])>1e-6||std::abs(initial[3])+std::abs(initial[4])+std::abs(initial[5])>1e-12){run.message="laboratory protocols require axisymmetric initial stress";return run;}
    if(cycles&&steps<16*cycles){run.message="cyclic loading requires at least 16 increments per cycle";return run;}
    if((protocol==3&&std::abs(target)>1e8)||(protocol!=3&&std::abs(target)>.1)){run.message="control amplitude exceeds laboratory limit";return run;}
    Point committed;committed.state=initial;run.points.push_back(committed);
    double lateral=.5*(initial[1]+initial[2]);
    for(int i=1;i<=steps;++i){
        double control=literal_controls?common_controls[i-1]:(cycles?target*std::sin(2*3.141592653589793*cycles*i/steps):target*i/steps);
        auto previous=run.points.back();Sym<double> de;State parent;Advance result;
        active_step=i;
        if(!traced_controlled_step(model,previous.state,p,protocol,control-previous.control,lateral,previous.strain.v[0],de,result,settings)){
            run.message="control or constitutive solve failed at step "+std::to_string(i)+"; last committed point retained";return run;}
        Point point;point.control=control;point.state=result.state;point.strain=previous.strain+de;point.diagnostics=result.diagnostics;
        if(protocol==2||protocol==3)point.pore_pressure=lateral-.5*(point.state[1]+point.state[2]);
        run.points.push_back(point);
    }
    run.ok=true;return run;
}inline Run literal_run_protocol(int model,const State&initial,const State&p,int protocol,double target,int steps,int cycles,const IntegrationSettings&settings={}){
    Run run;run.settings=settings;if(!valid_settings(settings)||model<0||model>=int(models().size())||protocol<0||protocol>4||steps<1||steps>5000||cycles<0||cycles>100||!std::isfinite(target)||!valid_parameters(model,p)||initial.size()!=initial_state(model).size()||!domain(model,initial,p)){
        run.message="invalid run specification";return run;}
    if(std::abs(initial[1]-initial[2])>1e-6||std::abs(initial[3])+std::abs(initial[4])+std::abs(initial[5])>1e-12){run.message="laboratory protocols require axisymmetric initial stress";return run;}
    if(cycles&&steps<16*cycles){run.message="cyclic loading requires at least 16 increments per cycle";return run;}
    if((protocol==3&&std::abs(target)>1e8)||(protocol!=3&&std::abs(target)>.1)){run.message="control amplitude exceeds laboratory limit";return run;}
    Point committed;committed.state=initial;run.points.push_back(committed);
    double lateral=.5*(initial[1]+initial[2]);
    for(int i=1;i<=steps;++i){
        double control=common_controls[i-1];
        auto previous=run.points.back();Sym<double> de;State parent;Advance result;
        if(!controlled_step(model,previous.state,p,protocol,control-previous.control,lateral,previous.strain.v[0],de,result,settings)){
            run.message="control or constitutive solve failed at step "+std::to_string(i)+"; last committed point retained";return run;}
        Point point;point.control=control;point.state=result.state;point.strain=previous.strain+de;point.diagnostics=result.diagnostics;
        if(protocol==2||protocol==3)point.pore_pressure=lateral-.5*(point.state[1]+point.state[2]);
        run.points.push_back(point);
    }
    run.ok=true;return run;
}
void values(std::ostream&o,const State&v){o<<'[';for(size_t i=0;i<v.size();++i){if(i)o<<',';o<<v[i];}o<<']';}
void tensor(std::ostream&o,const Sym<double>&v){values(o,State(v.v.begin(),v.v.end()));}
void diagnostic(std::ostream&o,const Diagnostics&d){o<<"{\"iterations\":"<<d.iterations<<",\"substeps\":"<<d.substeps<<",\"rejected\":"<<d.rejected<<",\"error\":"<<d.error<<'}';}
void run_json(std::ostream&o,const Run&r){o<<"{\"ok\":"<<(r.ok?"true":"false")<<",\"points\":[";for(size_t i=0;i<r.points.size();++i){if(i)o<<',';auto&p=r.points[i];o<<"{\"control\":"<<p.control<<",\"state\":";values(o,p.state);o<<",\"strain\":";tensor(o,p.strain);o<<",\"u\":"<<p.pore_pressure<<",\"diagnostics\":";diagnostic(o,p.diagnostics);o<<'}';}o<<"]}";}
}
extern "C" TRACE_EXPORT const char* atlas_trace(){
 using namespace atlas;static std::string output;std::ostringstream o;o<<std::setprecision(17);int model=-1;for(size_t i=0;i<models().size();++i)if(models()[i].id=="mohr-coulomb")model=int(i);
 if(model<0)return "{\"error\":\"model absent\"}";
 const State p={100000.,30000000.,.25,10000.,.5235987755982988,.17453292519943295};const State initial={100000.,100000.,100000.,0.,0.,0.};IntegrationSettings settings;
 o<<"{\"schema\":\"control-trace-diagnostic-v1\",\"catalogue_hash\":\""<<catalogue_hash()<<"\",\"streams\":[";
 for(int mode=0;mode<2;++mode){if(mode)o<<',';literal_controls=bool(mode);auto baseline=mode?literal_run_protocol(model,initial,p,3,200000.,64,1,settings):run_protocol(model,initial,p,3,200000.,64,1,settings);trace_calls.clear();auto traced=traced_run_protocol(model,initial,p,3,200000.,64,1,settings);
  o<<"{\"id\":\""<<(mode?"common-literal":"backend-sine")<<"\",\"baseline\":";run_json(o,baseline);o<<",\"traced\":";run_json(o,traced);o<<",\"calls\":[";
  for(size_t j=0;j<trace_calls.size();++j){if(j)o<<',';auto&c=trace_calls[j];o<<"{\"step\":"<<c.step<<",\"iteration\":"<<c.iteration<<",\"role\":\""<<c.role<<"\",\"de\":";tensor(o,c.de);o<<",\"parent\":";values(o,c.parent);o<<",\"ok\":"<<(c.result.ok?"true":"false")<<",\"state\":";values(o,c.result.state);o<<",\"diagnostics\":";diagnostic(o,c.result.diagnostics);o<<'}';}o<<"]}";
 }o<<"]}";output=o.str();return output.c_str();
}
#ifndef __EMSCRIPTEN__
int main(){std::cout<<atlas_trace()<<'\n';}
#endif
