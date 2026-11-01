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
#include "requests.hpp"
using namespace atlas;
void array(const State&z){std::cout<<'[';for(size_t i=0;i<z.size();++i){if(i)std::cout<<',';std::cout<<z[i];}std::cout<<']';}
int newton(){
 std::cout<<std::setprecision(17)<<std::boolalpha;
 for(const auto&q:requests()){
  auto settings=IntegrationSettings{};settings.max_depth=0;settings.max_iterations=q.iterations;
  auto z=q.z,p=q.p;const auto r=integrate(q.model,z,tensor_from(q.de,0),p,settings);
  const auto repeat=integrate(q.model,z,tensor_from(q.de,0),p,settings);
  const auto recovery=integrate(2,State{100000,100000,100000,0,0,0,0},Sym<double>{},p,settings);
  State residual;const bool residual_ok=r.ok&&evaluate_model(q.model,r.state,q.z,tensor_from(q.de,0),q.p,residual);
  std::cout<<"{\"id\":\""<<q.id<<"\",\"ok\":"<<r.ok<<",\"state\":";array(r.state);
  std::cout<<",\"input_unchanged\":"<<history_study::same(z,q.z)<<",\"replay\":"<<(r.ok==repeat.ok&&history_study::same(r.state,repeat.state))<<",\"rollback\":"<<history_study::same(r.state,q.z)<<",\"recovery\":"<<recovery.ok<<",\"endpoint_admissible\":"<<solution_admissible(q.model,r.state,p)<<",\"residual_ok\":"<<residual_ok<<",\"residual\":";array(residual);
  std::cout<<",\"iterations\":"<<r.diagnostics.iterations<<",\"substeps\":"<<r.diagnostics.substeps<<",\"rejected\":"<<r.diagnostics.rejected<<"}\n";
 }
 return 0;
}
int main(int argc,char**argv){if(argc!=2)return 2;std::string mode=argv[1];if(mode=="corpus")return corpus_study::run();if(mode=="history")return history_study::run();if(mode=="checks")return checks_study::run();if(mode=="newton")return newton();return 2;}
