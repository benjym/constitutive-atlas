#include "atlas/solver.hpp"
#include "atlas/checked_principal_range.hpp"
#include <iostream>
#include <iomanip>
#include <sstream>
#include <bit>
#include <cstdlib>
#include "corpus.inc"
#include "history.inc"
#include "checks.inc"
using namespace atlas;
#include "requests.hpp"
using namespace atlas;
void array(const State&z){std::cout<<'[';for(size_t i=0;i<z.size();++i){if(i)std::cout<<',';std::cout<<z[i];}std::cout<<']';}
int newton(){
 std::cout<<std::setprecision(17)<<std::boolalpha;
 for(const auto&q:requests()){
  auto settings=IntegrationSettings{};settings.max_depth=0;settings.max_iterations=q.iterations;settings.residual_tolerance=q.tolerance;
  auto z=q.z,p=q.p;const auto r=integrate(q.model,z,tensor_from(q.de,0),p,settings);
  const auto repeat=integrate(q.model,z,tensor_from(q.de,0),p,settings);
  const auto recovery=integrate(2,State{100000,100000,100000,0,0,0,0},Sym<double>{},p,settings);
  State residual;const bool residual_ok=r.ok&&evaluate_model(q.model,r.state,q.z,tensor_from(q.de,0),q.p,residual);
  std::cout<<"{\"id\":\""<<q.id<<"\",\"ok\":"<<r.ok<<",\"state\":";array(r.state);
  std::cout<<",\"input_unchanged\":"<<history_study::same(z,q.z)<<",\"replay\":"<<(r.ok==repeat.ok&&history_study::same(r.state,repeat.state))<<",\"rollback\":"<<history_study::same(r.state,q.z)<<",\"recovery\":"<<recovery.ok<<",\"endpoint_admissible\":"<<solution_admissible(q.model,r.state,p)<<",\"residual_ok\":"<<residual_ok<<",\"residual\":";array(residual);
  std::cout<<",\"iterations\":"<<r.diagnostics.iterations<<",\"substeps\":"<<r.diagnostics.substeps<<",\"rejected\":"<<r.diagnostics.rejected<<",\"restarts\":"<<r.diagnostics.nonmonotone_restarts<<",\"rounding\":"<<r.diagnostics.rounding_corrections<<"}\n";
 }
 return 0;
}
int rounding_checks(){
 auto p=default_parameters(7);State z{100000,100000,100000,0,0,0,100000},delta(7),accepted{9,8};auto scales=model_scales(7,p);delta[6]=1e-12/scales[6];IntegrationSettings settings;
 State outside=z;outside[6]=std::nextafter(z[6],std::numeric_limits<double>::infinity());State out;bool domain_rejected=!evaluate_model(7,outside,z,Sym<double>{},p,out);
 bool domain= !rounding_neighbor(7,z,z,Sym<double>{},p,scales,delta,0.,settings,accepted)&&accepted==State({9,8})&&domain_rejected;
 p=default_parameters(8);p.back()=std::numeric_limits<double>::max();z[6]=p.back();scales=model_scales(8,p);delta[6]=.1/scales[6];
 bool nonfinite=!rounding_neighbor(8,z,z,Sym<double>{},p,scales,delta,0.,settings,accepted)&&accepted==State({9,8});
 std::cout<<std::boolalpha<<"{\"pass\":"<<(domain&&nonfinite)<<",\"domain_rejected\":"<<domain<<",\"nonfinite_rejected\":"<<nonfinite<<"}\n";return 0;
}
int main(int argc,char**argv){if(argc!=2)return 2;std::string mode=argv[1];if(mode=="corpus")return corpus_study::run();if(mode=="history")return history_study::run();if(mode=="checks")return checks_study::run();if(mode=="newton")return newton();if(mode=="roundingchecks")return rounding_checks();return 2;}
