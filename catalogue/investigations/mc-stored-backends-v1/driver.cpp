#include "atlas/solver.hpp"
#include <iostream>
#include <iomanip>
#include <sstream>
#include <bit>
#include <cstdlib>
using namespace atlas;
double number(const std::string&s){char*end=nullptr;double v=std::strtod(s.c_str(),&end);if(end!=s.c_str()+s.size())throw std::runtime_error("bad numeric token");return v;}
bool same(double a,double b){return std::bit_cast<std::uint64_t>(a)==std::bit_cast<std::uint64_t>(b);}
bool same(const State&a,const State&b){if(a.size()!=b.size())return false;for(size_t i=0;i<a.size();++i)if(!same(a[i],b[i]))return false;return true;}
bool same(const std::vector<Jet>&a,const std::vector<Jet>&b){if(a.size()!=b.size())return false;for(size_t i=0;i<a.size();++i){if(!same(a[i].v,b[i].v))return false;for(int j=0;j<max_derivatives;++j)if(!same(a[i].d[j],b[i].d[j]))return false;}return true;}
void vector_json(const State&v){std::cout<<'[';for(size_t k=0;k<v.size();++k){if(k)std::cout<<',';if(!std::isfinite(v[k]))throw std::runtime_error("nonfinite output");std::cout<<v[k];}std::cout<<']';}
template<class T>void output_json(const std::vector<T>&v){std::cout<<"\"output\":[";for(size_t k=0;k<v.size();++k){if(k)std::cout<<',';if(!finite_value(v[k]))throw std::runtime_error("nonfinite output");std::cout<<"{\"value\":"<<value(v[k]);if constexpr(std::is_same_v<T,Jet>){std::cout<<",\"derivatives\":[";for(int j=0;j<max_derivatives;++j){if(j)std::cout<<',';std::cout<<v[k].d[j];}std::cout<<']';}std::cout<<'}';}std::cout<<']';}
int main(){std::cout<<std::setprecision(17);std::string line;while(std::getline(std::cin,line))try{
 std::istringstream in(line);std::string id,mode,kind,token;int initial,iterations,depth;
 if(!(in>>id>>mode>>kind>>initial>>iterations>>depth))throw std::runtime_error("bad header");
 auto read=[&](){if(!(in>>token))throw std::runtime_error("missing input");return number(token);};
 State p(6);for(auto&v:p)v=read();std::vector<Jet>z(6),zn(6);Sym<Jet>d;
 for(auto&v:z)v.v=read();for(auto&v:zn)v.v=read();for(auto&v:d.v)v.v=read();
 for(int j=0;j<max_derivatives;++j){for(auto&v:z)v.d[j]=read();for(auto&v:zn)v.d[j]=read();for(auto&v:d.v)v.d[j]=read();}
 if(in>>token)throw std::runtime_error("extra input");
 auto oldz=z,oldzn=zn,oldloading=std::vector<Jet>(d.v.begin(),d.v.end());auto oldp=p;
 bool ok=false,unchanged=true;study_selected_branch=-1;study_failure_line=-1;study_values.fill(std::numeric_limits<double>::quiet_NaN());
 std::cout<<"{\"id\":\""<<id<<"\",\"mode\":\""<<mode<<"\",\"kind\":\""<<kind<<"\",";
 if(mode=="eval"){
  if(kind=="jet"){std::vector<Jet>out;ok=valid_parameters(0,p)&&evaluate_model(0,z,zn,d,p,out,initial);if(!ok)out.clear();output_json(out);}
  else if(kind=="double"){State a,b,out;Sym<double>dd;for(int k=0;k<6;++k){a.push_back(z[k].v);b.push_back(zn[k].v);dd.v[k]=d.v[k].v;}ok=valid_parameters(0,p)&&evaluate_model(0,a,b,dd,p,out,initial);if(!ok)out.clear();output_json(out);}
  else throw std::runtime_error("unknown kind");
 }else{
  State parent;Sym<double>dd;for(int k=0;k<6;++k){parent.push_back(zn[k].v);dd.v[k]=d.v[k].v;}
  IntegrationSettings settings;settings.max_iterations=iterations;settings.max_depth=depth;
  if(mode=="solve"){
   auto a=integrate(0,parent,dd,p,settings);ok=a.ok;output_json(a.state);
   std::cout<<",\"iterations\":"<<a.diagnostics.iterations<<",\"substeps\":"<<a.diagnostics.substeps<<",\"rejected\":"<<a.diagnostics.rejected;
  }else if(mode=="transaction"){
   auto normal=settings;normal.max_iterations=45;auto goodp=default_parameters(0);Sym<double>zero;
   // Establish an actual accepted result before inducing a later failed call.
   auto accepted=integrate(0,parent,zero,goodp,normal);if(!accepted.ok)throw std::runtime_error("transaction baseline failed");
   State committed=accepted.state;const auto snapshot=committed;
   // The iteration-budget case exercises tentative Newton updates, rather than early validation alone.
   State tentative;Diagnostics trialdiag;bool trialok=implicit_step(0,committed,dd,p,tentative,trialdiag,settings);
   bool tentative_changed=!same(tentative,committed);
   auto a=integrate(0,committed,dd,p,settings);const auto failed_trace=study_values;const int failed_branch=study_selected_branch,failed_line=study_failure_line;ok=a.ok;if(a.ok)committed=a.state;
   bool returned_parent=same(a.state,snapshot),committed_unchanged=same(committed,snapshot);
   auto recovery=integrate(0,committed,zero,goodp,normal);auto fresh=integrate(0,snapshot,zero,goodp,normal);
   study_values=failed_trace;study_selected_branch=failed_branch;study_failure_line=failed_line;
   output_json(a.state);
   std::cout<<",\"message\":\""<<a.message<<"\"";
   std::cout<<",\"transaction\":{\"tentative_ok\":"<<(trialok?"true":"false")<<",\"tentative_changed\":"<<(tentative_changed?"true":"false")<<",\"trial_iterations\":"<<trialdiag.iterations<<",\"iterations\":"<<a.diagnostics.iterations<<",\"rejected\":"<<a.diagnostics.rejected<<",\"returned_parent\":"<<(returned_parent?"true":"false")<<",\"committed_unchanged\":"<<(committed_unchanged?"true":"false")<<",\"recovery_ok\":"<<(recovery.ok?"true":"false")<<",\"recovery_matches_fresh\":"<<((recovery.ok&&fresh.ok&&same(recovery.state,fresh.state))?"true":"false")<<",\"committed_state\":";vector_json(committed);std::cout<<",\"recovery_state\":";vector_json(recovery.state);std::cout<<",\"fresh_state\":";vector_json(fresh.state);std::cout<<'}';
  }else throw std::runtime_error("unknown mode");
 }
 unchanged=same(z,oldz)&&same(zn,oldzn)&&same(std::vector<Jet>(d.v.begin(),d.v.end()),oldloading)&&same(p,oldp);
 std::cout<<",\"trace\":[";for(size_t i=0;i<study_values.size();++i){if(i)std::cout<<',';if(std::isfinite(study_values[i]))std::cout<<study_values[i];else std::cout<<"null";}std::cout<<']';
 std::cout<<",\"branch\":"<<study_selected_branch<<",\"failure_line\":"<<study_failure_line<<",\"ok\":"<<(ok?"true":"false")<<",\"input_unchanged\":"<<(unchanged?"true":"false")<<"}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}return 0;}
