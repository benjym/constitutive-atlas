#include "atlas/solver.hpp"
#include <iomanip>
#include <iostream>
#include <stdexcept>
using namespace atlas;
void require(bool v,const char* why){if(!v)throw std::runtime_error(why);}
void array(const State& v){std::cout<<"[";for(size_t i=0;i<v.size();++i){if(i)std::cout<<",";std::cout<<v[i];}std::cout<<"]";}
int main(){try{
 int fixed=-1,reset=-1;for(size_t i=0;i<models().size();++i){
   if(models()[i].id=="research-sanisand-2004-fixed-memory-be")fixed=i;
   if(models()[i].id=="research-sanisand-2004-parent-reset-be")reset=i;
 }
 require(fixed>=0&&reset>=0,"missing research definitions");
 const auto parameters=default_parameters(reset);std::cout<<std::setprecision(17)<<"[";bool comma=false;
 auto emit=[&](int path,int steps,int leg,int step,const State& before,const Sym<double>& de,const State& prepared,const Advance& result){
   if(comma)std::cout<<",";comma=true;
   std::cout<<"{\"path\":"<<path<<",\"steps\":"<<steps<<",\"leg\":"<<leg<<",\"step\":"<<step
     <<",\"ok\":"<<(result.ok?"true":"false")<<",\"substeps\":"<<result.diagnostics.substeps
     <<",\"rejected\":"<<result.diagnostics.rejected<<",\"before\":";array(before);
   std::cout<<",\"increment\":";array(State(de.v.begin(),de.v.end()));
   std::cout<<",\"prepared\":";array(prepared);std::cout<<",\"state\":";array(result.state);
   std::cout<<",\"fractions\":";array(result.diagnostics.increment_fractions);std::cout<<"}";
 };
 for(int path=0;path<2;++path)for(int steps:{16,32,64}){
   State current=initial_state(reset),reference=initial_state(fixed),first_peak;
   const auto direction=path==0?make_sym(.002,-.001,-.001,0.,0.,0.):make_sym(.001,-.0003,-.0007,.001,-.0004,.0002);
   const double factors[]={1.,-2.,2.,-1.};
   for(int leg=0;leg<4;++leg)for(int step=0;step<steps;++step){
     const auto de=(factors[leg]/steps)*direction;const auto saved=current;State prepared;
     require(prepare_model_increment(reset,current,de,parameters,prepared),"preparation failed");
     const auto result=integrate(reset,current,de,parameters);emit(path,steps,leg,step,current,de,prepared,result);
     require(result.ok,"cyclic increment failed");require(current==saved,"parent mutated");
     if(leg==0){auto matching=integrate(fixed,reference,de,parameters);require(matching.ok&&matching.state==result.state,"monotonic parity changed");reference=matching.state;}
     current=result.state;if(leg==0&&step==steps-1)first_peak=current;
   }
   // Select nonzero memory, then force an inadmissible requested endpoint.
   const auto bad=make_sym(-.2501,-.24995,-.24995,0.,0.,0.);State prepared;
   require(prepare_model_increment(reset,first_peak,bad,parameters,prepared),"reset-failure preparation failed");
   require(prepared!=first_peak,"failure case did not trigger reset");
   const auto failed=integrate(reset,first_peak,bad,parameters);emit(path,steps,4,0,first_peak,bad,prepared,failed);
   require(!failed.ok&&failed.state==first_peak,"failed increment did not restore pre-reset parent");
   // This zero trial must retain parent memory without rerunning a prior reset.
   auto zero=make_sym(0.,0.,0.,0.,0.,0.);State zero_prepared;
   require(prepare_model_increment(reset,first_peak,zero,parameters,zero_prepared)&&zero_prepared==first_peak,"zero increment reset memory");
   auto z=integrate(reset,first_peak,zero,parameters);emit(path,steps,5,0,first_peak,zero,zero_prepared,z);
   require(z.ok,"zero trial failed");
 }
 std::cout<<"]\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}}
