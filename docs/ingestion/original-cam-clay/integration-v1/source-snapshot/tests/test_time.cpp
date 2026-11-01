#include "atlas/time.hpp"
#include <iostream>
#include <stdexcept>
using namespace atlas;
void require(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
void close(double a,double b,double tol,const char* message){require(std::isfinite(a)&&std::abs(a-b)<tol,message);}
int find(const char* name){for(size_t i=0;i<models().size();++i)if(models()[i].id==name)return int(i);throw std::runtime_error("fixture missing");}
int main(){try{
    const int m=find("test-maxwell"),c=find("test-clock");
    auto p=default_parameters(m),z=initial_state(m);Sym<double> zero;
    TimeSettings settings;settings.relative_tolerance=1e-10;settings.absolute_tolerance=1e-13;
    auto relaxed=integrate_time(m,z,zero,p,7,4,settings);
    require(relaxed.ok&&relaxed.time==11,"relaxation must advance physical clock");
    close(relaxed.state[0],100000+40000*std::exp(-2.),.01,"Maxwell relaxation analytical error");
    close(trace(tensor_from(relaxed.state,0))/3,100000,1e-7,"relaxation changed pressure");
    auto first=integrate_time(m,z,zero,p,7,1,settings);
    auto second=integrate_time(m,first.state,zero,p,first.time,3,settings);
    require(first.ok&&second.ok,"partition integration failed");
    close(second.state[0],relaxed.state[0],.01,"partition changed trajectory");
    auto shifted=integrate_time(m,z,zero,p,0,4,settings);
    close(shifted.state[0],relaxed.state[0],1e-7,"autonomous trajectory depends on time origin");
    TimeSettings loose=settings;loose.relative_tolerance=1e-3;
    auto coarse=integrate_time(m,z,zero,p,0,4,loose);
    const double exact=100000+40000*std::exp(-2.);
    require(coarse.ok&&std::abs(relaxed.state[0]-exact)<std::abs(coarse.state[0]-exact),"refinement did not reduce temporal error");
    require(relaxed.diagnostics.rejected>0,"analytical test did not exercise rejection");
    // Under constant deviatoric stress the Maxwell law predicts constant creep rate.
    auto creep_rate=dev(tensor_from(z,0))*(1./(2*p[1]*p[2]));
    auto creep=integrate_time(m,z,creep_rate,p,0,4,settings);
    require(creep.ok,"creep integration failed");
    for(size_t i=0;i<z.size();++i)close(creep.state[i],z[i],1e-7,"analytical stress-controlled creep relation failed");
    // Nonautonomous scalar ODE; this detects wrong stage/half-step start times.
    auto cp=default_parameters(c),cz=initial_state(c);
    auto clock=integrate_time(c,cz,zero,cp,3,2,settings);
    require(clock.ok&&clock.time==5,"clock integration failed");
    close(clock.state[0],2.,1e-12,"nonautonomous analytical increment incorrect");
    // Stage rate changes continuously with time. Elastic volume response is exact.
    auto varying=integrate_time_history(m,z,p,3,2,[](double t){Sym<double>d;d.v={t*1e-5,t*1e-5,t*1e-5,0,0,0};return d;},settings);
    require(varying.ok,"time-varying history failed");
    close(trace(tensor_from(varying.state,0))/3,100000+3*p[0]*8e-5,1e-6,"stage strain rate was not sampled at stage time");
    // First half succeeds, later domain failure must roll back the whole update.
    cp[1]=.75;
    auto failed=integrate_time(c,cz,zero,cp,0,1,settings);
    require(!failed.ok&&failed.time==0&&failed.state==cz&&failed.diagnostics.substeps>0,"partial advance leaked after failure");
    TimeSettings budget=settings;budget.maximum_substeps=2;
    auto exhausted=integrate_time(m,z,zero,p,0,4,budget);
    require(!exhausted.ok&&exhausted.state==z&&exhausted.time==0,"budget failure did not roll back");
    for(double duration:{0.,-1.,std::numeric_limits<double>::infinity()})
        require(!integrate_time(m,z,zero,p,0,duration).ok,"invalid duration accepted");
    require(!integrate_time(m,z,zero,p,1e100,1).ok,"unrepresentable endpoint accepted");
    TimeSettings invalid=settings;invalid.relative_tolerance=0;
    require(!integrate_time(m,z,zero,p,0,1,invalid).ok,"invalid tolerance accepted");
    // An untimed entry point cannot execute physical-time equations accidentally.
    require(!integrate(m,z,zero,p).ok,"untimed API accepted physical-time model");
    std::cout<<"Physical-time analytical solutions, stage histories, refinement, partitioning and rollback passed\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
