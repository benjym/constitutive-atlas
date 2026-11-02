// Prospective engine fixture tests; install/build/run only through coordinator.
#include "atlas/schedule.hpp"
#include <cmath>
#include <iostream>
#include <stdexcept>
using namespace atlas;
void require(bool b,const char* m){if(!b)throw std::runtime_error(m);}
void close(double x,double y,double e,const char* m){require(std::isfinite(x)&&std::abs(x-y)<=e,m);}
int find(const char* id){for(size_t i=0;i<models().size();++i)if(models()[i].id==id)return int(i);throw std::runtime_error("fixture missing");}
State unknowns(int m,const ControlledState& s,const ControlPath& path,double h){
    State u=s.state;for(int j:control_components(m))if(path.stress[j])u.push_back(s.rate.v[j]*h);return u;
}
bool predict(int m,const ControlledState& s,const State& p,double t,double h,const ControlPath& path,State& u){
    return controlled_forward_euler_guess(m,s,p,t,t+h,path,model_scales(m,p),model_observable_scales(m,p),u);
}
int main(){try{
    ScheduleSettings settings;
    const int boundary=find("test-predictor-boundary");auto bp=default_parameters(boundary);
    // Independent unilateral-memory law: x'=trace(D), alpha'=max(x,0)/tau.
    // Active old-state Newton gives delta_alpha=h*x0+h*h*D<0, blocked by alpha>=0.
    // FE guess reaches the inactive endpoint while keeping positive memory admissible.
    for(double x0:{0.,std::nextafter(0.,1.),std::ldexp(1.,-50),.125}){
        ControlledState s;s.state={x0,0};s.rate.v[0]=3; // stale strain rate must not be used
        ControlPath path;path.rates.v[0]=-1;State u=unknowns(boundary,s,path,.25);
        require(predict(boundary,s,bp,3,.25,path,u),"boundary predictor rejected");
        close(u[0],x0-.25,1e-15,"predictor used stale prescribed strain rate");
        close(u[1],.25*x0,1e-15,"predictor lost admissible incoming memory rate");
        ControlledState result;Diagnostics diagnostics;
        require(controlled_backward_euler(boundary,s,bp,3,3.25,path,settings,result,diagnostics),"boundary BE solve failed");
        close(result.state[0],x0-.25,1e-12,"boundary BE x wrong");
        close(result.state[1],0,1e-12,"inactive endpoint BE alpha wrong");require(result.state[1]>=0,"negative accepted alpha");
    }
    {
        ControlledState s;s.state={.125,0};ControlPath path;path.rates.v[0]=1;
        ControlledState r;Diagnostics d;require(controlled_backward_euler(boundary,s,bp,0,.25,path,settings,r,d),"outward BE failed");
        close(r.state[0],.375,1e-12,"outward x wrong");close(r.state[1],.09375,1e-12,"outward alpha wrong");
    }
    const int fallback=find("test-predictor-fallback");auto fp=default_parameters(fallback);
    {
        ControlledState s;s.state={1};ControlPath path;State u=unknowns(fallback,s,path,2),before=u;
        require(!predict(fallback,s,fp,0,2,path,u)&&u==before,"inadmissible FE guess did not preserve original unknowns");
        ControlledState r;Diagnostics d;require(controlled_backward_euler(fallback,s,fp,0,2,path,settings,r,d),"fallback BE failed");
        close(r.state[0],1./3,1e-12,"fallback changed BE solution");require(r.state[0]>=0,"fallback accepted inadmissible state");
    }
    const int clock=find("test-predictor-clock");auto cp=default_parameters(clock);cp[0]=2;
    {
        ControlledState s;s.state={0};ControlPath path;State u=unknowns(clock,s,path,.125);
        require(predict(clock,s,cp,3,.125,path,u),"nonautonomous predictor rejected");
        close(u[0],.09375,1e-15,"predictor RHS not evaluated at t0");
        ControlledState r;Diagnostics d;require(controlled_backward_euler(clock,s,cp,3,3.125,path,settings,r,d),"clock BE failed");
        close(r.state[0],.09765625,1e-12,"BE residual not evaluated at t1");
        cp[2]=3.1;u=unknowns(clock,s,path,.125);auto before=u;
        require(!predict(clock,s,cp,3,.125,path,u)&&u==before,"endpoint domain rejection changed fallback");
        require(!controlled_backward_euler(clock,s,cp,3,3.125,path,settings,r,d),"invalid endpoint time accepted");
        cp[2]=1000;u=before;
        require(!controlled_forward_euler_guess(clock,s,cp,3,3,path,model_scales(clock,cp),model_observable_scales(clock,cp),u)&&u==before,"zero-time predictor changed fallback");
    }
    // Current prescribed strain rates, but previous solved strain rates for stress controls.
    const int kelvin=find("test-kelvin");auto kp=default_parameters(kelvin);
    {
        ControlledState s;s.state=initial_state(kelvin);s.rate.v={-.01,-.0003,.0004,0,0,0};
        ControlPath path;path.stress[1]=path.stress[2]=true;path.rates.v={.001,9999,-999,.0002,0,0};
        path.stress_start=tensor_from(s.state,0);State u=unknowns(kelvin,s,path,.125),before=u;
        require(predict(kelvin,s,kp,0,.125,path,u),"mixed predictor rejected");
        Sym<double> D;D.v={.001,-.0003,.0004,.0002,0,0};auto f=identity<double>()*(kp[0]*trace(D))+dev(D)*(2*kp[1]);
        for(int j=0;j<6;++j)close(u[j],s.state[j]+.125*f.v[j],1e-8,"mixed control predictor used stress rate as strain rate");
        require(u[6]==before[6]&&u[7]==before[7],"predictor changed stress-controlled increment guesses");
    }
    const int axis=find("test-maxwell-axisymmetric");auto ap=default_parameters(axis);
    {
        ControlledState s;s.state=initial_state(axis);s.rate.v={-.01,-.0002,-.0002,0,0,0};
        ControlPath path;path.stress[1]=path.stress[2]=true;path.rates.v={.001,9999,-999,0,0,0};
        path.stress_start=tensor_from(s.state,0);State u=unknowns(axis,s,path,.125);
        require(u.size()==s.state.size()+1,"axisymmetric radial unknown duplicated");
        require(predict(axis,s,ap,0,.125,path,u),"axisymmetric predictor rejected");
        Sym<double> D;D.v={.001,-.0002,-.0002,0,0,0};
        auto f=identity<double>()*(ap[0]*trace(D))+dev(D)*(2*ap[1])-dev(tensor_from(s.state,0))*(1/ap[2]);
        for(int j=0;j<6;++j)close(u[j],s.state[j]+.125*f.v[j],1e-8,"axisymmetric rate symmetry not respected");
        require(u[1]==u[2],"axisymmetric state prediction lost radial equality");
    }
    std::cout<<"Prospective generic predictor boundary, fallback, mixed-rate and clock checks passed\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
