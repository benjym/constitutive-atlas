#include "atlas/solver.hpp"
#include <iomanip>
#include <iostream>
#include <stdexcept>
using namespace atlas;
void require(bool value,const char* message){if(!value)throw std::runtime_error(message);}
void array(const State& s){std::cout<<"[";for(size_t i=0;i<s.size();++i){if(i)std::cout<<",";std::cout<<s[i];}std::cout<<"]";}
int main(){try{
  std::cout<<std::setprecision(17)<<"[";bool comma=false;
  const auto parameters=default_parameters(0);const auto initial=initial_state(0);
  auto emit=[&](const char* name,const State& before,const Advance& result){
    if(comma)std::cout<<",";comma=true;
    std::cout<<"{\"case\":\""<<name<<"\",\"ok\":"<<(result.ok?"true":"false")
      <<",\"substeps\":"<<result.diagnostics.substeps<<",\"rejected\":"<<result.diagnostics.rejected
      <<",\"iterations\":"<<result.diagnostics.iterations<<",\"before\":";array(before);
    std::cout<<",\"state\":";array(result.state);std::cout<<"}";
  };
  // All history tensors must be deviatoric, including dormant fabric/memory.
  for(const auto& field:models().at(0).fields)if(field.name=="alpha"||field.name=="fabric"||field.name=="alpha_in"){
    auto parent=initial;parent[field.offset]+=.001;
    auto failed=integrate(0,parent,make_sym(0.,0.,0.,0.,0.,0.),parameters);
    require(!failed.ok&&failed.state==parent,"invalid history was accepted or mutated");
    require(failed.diagnostics.iterations==0,"invalid history entered the solver");
    emit(field.name.c_str(),parent,failed);
  }
  auto parent=initial;
  const auto load=make_sym(.000125,-.0000625,-.0000625,0.,0.,0.);
  for(int i=0;i<16;++i){auto r=integrate(0,parent,load,parameters);require(r.ok,"preload failed");parent=r.state;}
  // Give the otherwise frozen memory a nonzero admissible value so rollback
  // checks restoration of persistent memory as well as the transient multiplier.
  for(int i=0;i<6;++i)parent[19+i]=.25*parent[7+i];
  require(domain(0,parent,parameters,true),"prepared parent inadmissible");
  const auto saved=parent;
  auto first=integrate(0,parent,load,parameters);require(first.ok,"first trial failed");emit("first-trial",parent,first);
  auto zero=integrate(0,parent,make_sym(0.,0.,0.,0.,0.,0.),parameters);require(zero.ok,"zero trial failed");emit("zero-trial",parent,zero);
  // Exact volume closure forces 1-ch*e<0 under full expansion; internal accepted
  // substeps must not leak into the returned failed transaction.
  auto failed=integrate(0,parent,make_sym(-.25,-.25,-.25,0.,0.,0.),parameters);
  require(!failed.ok,"inadmissible full endpoint accepted");
  require(failed.diagnostics.substeps>0&&failed.diagnostics.rejected>0,"late failure was not exercised");
  require(failed.state==saved&&parent==saved,"late failure leaked trial state");emit("late-failure",parent,failed);
  auto repeated=integrate(0,parent,load,parameters);
  require(repeated.ok&&repeated.state==first.state,"repeated trial depends on rejected work");emit("repeat-trial",parent,repeated);
  require(parent==saved,"caller parent mutated");
  std::cout<<"]\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}}
