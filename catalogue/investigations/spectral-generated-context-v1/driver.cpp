#include "contexts.hpp"
#include <iostream>
#include <iomanip>
#include <sstream>
#include <bit>
#include <cstdlib>
using namespace atlas;
double number(const std::string&s){char*end=nullptr;double v=std::strtod(s.c_str(),&end);if(end!=s.c_str()+s.size())throw std::runtime_error("bad numeric token");return v;}
bool same(double a,double b){return std::bit_cast<std::uint64_t>(a)==std::bit_cast<std::uint64_t>(b);}
bool same(const State&a,const State&b){if(a.size()!=b.size())return false;for(size_t i=0;i<a.size();++i)if(!same(a[i],b[i]))return false;return true;}
bool same(const Sym<Jet>&a,const Sym<Jet>&b){for(int k=0;k<6;++k){if(!same(a.v[k].v,b.v[k].v))return false;for(int j=0;j<max_derivatives;++j)if(!same(a.v[k].d[j],b.v[k].d[j]))return false;}return true;}
void vector_json(const State&v){std::cout<<'[';for(size_t i=0;i<v.size();++i){if(i)std::cout<<',';if(!std::isfinite(v[i]))throw std::runtime_error("nonfinite wire output");std::cout<<v[i];}std::cout<<']';}
template<class T>void output_json(const std::vector<T>&v){std::cout<<"\"output\":[";for(size_t k=0;k<v.size();++k){if(k)std::cout<<',';if(!finite_value(v[k]))throw std::runtime_error("nonfinite checked output");std::cout<<"{\"value\":"<<value(v[k]);if constexpr(std::is_same_v<T,Jet>){std::cout<<",\"derivatives\":[";for(int j=0;j<max_derivatives;++j){if(j)std::cout<<',';std::cout<<v[k].d[j];}std::cout<<']';}std::cout<<'}';}std::cout<<']';}
int main(){std::cout<<std::setprecision(17);std::string line;while(std::getline(std::cin,line)){
 try{
  std::istringstream in(line);std::string id,kind,token;int slot,initial,check,reset,scale,observe_scale,solver_fail;double threshold;
  if(!(in>>id>>slot>>kind>>threshold>>initial>>check>>reset>>scale>>observe_scale>>solver_fail))throw std::runtime_error("bad wire header");
  Sym<Jet>A;for(int k=0;k<6;++k){if(!(in>>token))throw std::runtime_error("missing primal");A.v[k].v=number(token);}
  for(int j=0;j<max_derivatives;++j)for(int k=0;k<6;++k){if(!(in>>token))throw std::runtime_error("missing seed");A.v[k].d[j]=number(token);}if(in>>token)throw std::runtime_error("extra input");
  const auto before=A;bool ok=false;bool input_unchanged=true;
  std::cout<<"{\"id\":\""<<id<<"\",\"slot\":"<<slot<<",\"kind\":\""<<kind<<"\",";
  if(slot==33){
   if(kind!="double")throw std::runtime_error("history has no Jet ABI");State parent{17,11,12,13,0,0,0},inputs;for(int k=0;k<6;++k)inputs.push_back(A.v[k].v);const auto original=parent,oldinputs=inputs;
   const auto r=history::programs()[0].advance(parent,inputs,7,3);ok=r.ok;std::vector<double>out;if(ok)out.assign(r.values.begin()+1,r.values.end());output_json(out);
   input_unchanged=same(parent,original)&&same(inputs,oldinputs);
   std::cout<<",\"history\":{\"values\":";vector_json(r.values);std::cout<<",\"generation\":"<<r.generation<<",\"epoch\":"<<r.epoch<<",\"failed\":"<<r.failed<<",\"executed\":"<<r.executed<<",\"events\":[";for(size_t k=0;k<r.events.size();++k){if(k)std::cout<<',';std::cout<<r.events[k];}std::cout<<"]}";
  }else if(slot==32){
   if(kind!="double")throw std::runtime_error("solver is double API");const int model=19;const State parent{7,2,-3,0,0,0,.7,0};const auto original=parent;const auto p=default_parameters(model);Sym<double>de;if(solver_fail){de.v[0]=-4;de.v[1]=1;de.v[2]=6;}const auto oldde=de;State tentative;
   bool prepared=prepare_model_increment(model,parent,de,p,tentative);bool changed=prepared&&tentative.size()==8&&tentative[7]==1&&parent[7]==0;
   IntegrationSettings settings;settings.max_depth=0;
   const auto result=integrate(model,parent,de,p,settings);ok=result.ok;output_json(result.state);
   const auto recovery=integrate(model,parent,Sym<double>{},p,settings);const auto fresh=integrate(model,original,Sym<double>{},p,settings);
   bool recovered=recovery.ok&&fresh.ok&&same(recovery.state,fresh.state);input_unchanged=same(parent,original);for(int k=0;k<6;++k)input_unchanged=input_unchanged&&same(de.v[k],oldde.v[k]);
   std::cout<<",\"solver\":{\"tentative_reset_observed\":"<<(changed?"true":"false")<<",\"rejected\":"<<result.diagnostics.rejected<<",\"message\":\""<<result.message<<"\",\"recovery_matches_fresh\":"<<(recovered?"true":"false")<<",\"recovery_ok\":"<<(recovery.ok?"true":"false")<<",\"recovery_state\":";vector_json(recovery.state);std::cout<<",\"fresh_state\":";vector_json(fresh.state);std::cout<<'}';
  }else if(kind=="jet"){
   std::vector<Jet>out;ok=context_study::call(slot,A,threshold,initial,check,reset,scale,observe_scale,out);if(!ok)out.clear();output_json(out);
  }else if(kind=="double"){
   Sym<double>a;for(int k=0;k<6;++k)a.v[k]=A.v[k].v;std::vector<double>out;ok=context_study::call(slot,a,threshold,initial,check,reset,scale,observe_scale,out);if(!ok)out.clear();output_json(out);
  }else throw std::runtime_error("bad wire kind");
  input_unchanged=input_unchanged&&same(A,before);std::cout<<",\"ok\":"<<(ok?"true":"false")<<",\"input_unchanged\":"<<(input_unchanged?"true":"false")<<"}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}
}return 0;}
