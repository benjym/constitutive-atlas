#include "atlas/solver.hpp"
#include <iomanip>
#include <iostream>
#include <stdexcept>
using namespace atlas;
void array(const State& s){std::cout<<"[";for(size_t i=0;i<s.size();++i){if(i)std::cout<<",";std::cout<<s[i];}std::cout<<"]";}
int main(){try{
 int model=-1;for(size_t i=0;i<models().size();++i)if(models()[i].id=="research-sanisand-2004-parent-reset-be")model=i;
 if(model<0)throw std::runtime_error("research model absent");
 auto parameters=default_parameters(model);std::cout<<std::setprecision(17)<<"[";bool comma=false;
 for(int protocol:{1,3})for(int steps:{0,16,32,64}){
   auto parent=initial_state(model);double accumulated=0.;const double factors[]={1.,-2.,2.,-1.};
   for(int leg=0;leg<(steps?4:1);++leg)for(int step=0;step<(steps?steps:1);++step){
     const double requested=steps?factors[leg]*(protocol==1?.001:10000.)/steps:(protocol==1?1e-6:100.);
     Sym<double> de;Advance result;const auto saved=parent;
     bool ok=controlled_step(model,parent,parameters,protocol,requested,1e5,accumulated,de,result);
     if(comma)std::cout<<",";comma=true;
     std::cout<<"{\"protocol\":"<<protocol<<",\"steps\":"<<steps<<",\"leg\":"<<leg<<",\"step\":"<<step
       <<",\"request\":"<<requested<<",\"ok\":"<<(ok?"true":"false")<<",\"before\":";array(parent);
     std::cout<<",\"increment\":";array(State(de.v.begin(),de.v.end()));
     if(!ok){std::cout<<"}]\n";return 1;}
     State prepared;if(!prepare_model_increment(model,parent,de,parameters,prepared))throw std::runtime_error("preparation failed");
     auto replay=integrate(model,parent,de,parameters);
     if(!replay.ok||replay.state!=result.state||parent!=saved)throw std::runtime_error("outer trials leaked memory or changed replay");
     double control=protocol==1?.5*(result.state[1]+result.state[2])-1e5:
        result.state[0]-.5*(result.state[1]+result.state[2])-parent[0]+.5*(parent[1]+parent[2])-requested;
     std::cout<<",\"prepared\":";array(prepared);std::cout<<",\"state\":";array(result.state);
     std::cout<<",\"substeps\":"<<result.diagnostics.substeps<<",\"rejected\":"<<result.diagnostics.rejected
       <<",\"fractions\":";array(result.diagnostics.increment_fractions);
     std::cout<<",\"control_residual\":"<<control<<",\"replay_equal\":true}";
     parent=result.state;accumulated+=de.v[0];
   }
 }
 std::cout<<"]\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}}
