#include "atlas/schedule.hpp"
#include <iostream>
#include <stdexcept>
using namespace atlas;
void require(bool b,const char* s){if(!b)throw std::runtime_error(s);}
void close(double a,double b,double tol,const char* s){require(std::isfinite(a)&&std::abs(a-b)<tol,s);}
int main(){try{
    int m=-1;for(size_t i=0;i<models().size();++i)if(models()[i].id=="test-capacity-32")m=int(i);
    require(m>=0,"capacity fixture missing");
    auto p=default_parameters(m),z=initial_state(m),scales=model_scales(m,p),os=model_observable_scales(m,p);
    require(z.size()==32&&max_derivatives>=38,"32 states and six controls must fit");
    z[31]=2; // Non-equilibrium highest component must actually move in Newton.
    ControlPath path;path.stress.fill(true);path.stress_start=tensor_from(z,0);
    State u=z;u.insert(u.end(),6,.002);
    std::vector<Jet> x;for(size_t i=0;i<u.size();++i){x.emplace_back(u[i]);x.back().d[i]=1;}
    std::vector<Jet> ad;
    require(controlled_residual(m,x,z,p,0,.5,path,scales,os,ad),"AD residual failed");
    // All 38 columns against independently perturbed residual evaluations,
    // including the off-diagonal highest-state coupling and six controls.
    for(size_t j=0;j<u.size();++j){
        auto plus=u,minus=u;double h=1e-5*std::max(1.,std::abs(u[j]));plus[j]+=h;minus[j]-=h;
        State rp,rm;
        require(controlled_residual(m,plus,z,p,0,.5,path,scales,os,rp)&&
                controlled_residual(m,minus,z,p,0,.5,path,scales,os,rm),"finite-difference residual failed");
        for(size_t i=0;i<u.size();++i)close(ad[i].d[j],(rp[i]-rm[i])/(2*h),1e-8,"38-column AD/finite-difference mismatch");
    }
    require(std::abs(ad[0].d[31])>0,"highest state derivative coupling was not exercised");
    for(int j=0;j<6;++j)require(std::abs(ad[j].d[32+j])>0,"mixed-control derivative missing");
    ControlledState before,after;before.state=z;ScheduleSettings settings;Diagnostics diagnostics;
    require(controlled_backward_euler(m,before,p,0,.5,path,settings,after,diagnostics),"38-unknown joint Newton solve failed");
    // Independent backward-Euler solution: memory=(2+h/tau)/(1+h/tau).
    const double memory=1.8;
    close(after.state[31],memory,1e-12,"last state did not solve analytically");
    for(int j=0;j<6;++j){
        close(after.state[j],z[j],1e-10,"stress hold failed");
        close(after.strain.v[j],-.5*p[1]/(p[0]*p[2])*memory*(j+1),1e-12,"stress-control strain incorrect");
    }
    for(int i=1;i<=25;++i)close(after.state[5+i],.25*i,1e-12,"intermediate state was lost");
    std::cout<<"32-state, 38-column finite differences and analytical mixed-control Newton solve passed\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
