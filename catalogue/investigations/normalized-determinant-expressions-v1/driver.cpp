#include "models.hpp"
#include "history.hpp"
#include "cases.hpp"
#include <bit>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <sstream>
#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#define EXPORT EMSCRIPTEN_KEEPALIVE
#else
#define EXPORT
#endif
using namespace atlas;
namespace {
std::string answer;
std::string bits(double x){std::ostringstream out;out<<std::hex<<std::setw(16)<<std::setfill('0')<<std::bit_cast<std::uint64_t>(x);return out.str();}
std::vector<double> csv(const char* text){std::istringstream in(text);std::string token;std::vector<double> a;while(std::getline(in,token,',')){char* end=nullptr;double x=std::strtod(token.c_str(),&end);if(token.empty()||end!=token.c_str()+token.size())throw std::runtime_error("fixture CSV");a.push_back(x);}return a;}
bool same(const std::vector<Jet>&a,const std::vector<Jet>&b){if(a.size()!=b.size())return false;for(size_t i=0;i<a.size();++i){if(bits(a[i].v)!=bits(b[i].v))return false;for(unsigned j=0;j<38;++j)if(bits(a[i].d[j])!=bits(b[i].d[j]))return false;}return true;}
bool same(const std::vector<double>&a,const std::vector<double>&b){if(a.size()!=b.size())return false;for(size_t i=0;i<a.size();++i)if(bits(a[i])!=bits(b[i]))return false;return true;}
}
extern "C" EXPORT const char* determinant_context(const char* text){
 try{
  std::istringstream request(text?text:"");char kind;unsigned index;request>>kind>>index;if(!request||!(request>>std::ws).eof())throw std::runtime_error("request shape");
  std::ostringstream out;
  if(kind=='M'){
   if(index>=std::size(context_cases))throw std::runtime_error("case index");const auto& f=context_cases[index];auto a=csv(f.values),s=csv(f.seeds);if(a.size()!=6||s.size()!=228)throw std::runtime_error("fixture shape");
   std::vector<Jet> z(13),result;for(unsigned i=0;i<6;++i){z[6+i].v=a[i];for(unsigned j=0;j<38;++j)z[6+i].d[j]=s[i*38+j];}const auto before=z;
   std::vector<double> params;for(const auto&p:models()[f.model].parameters)params.push_back(p.name=="r"?f.param:p.value);
   Sym<Jet> loading{};const std::string context=f.context;bool scale=context=="state-scale"||context=="observable-scale";bool ok;
   if(scale){const auto v=context=="state-scale"?model_scales(f.model,params):model_observable_scales(f.model,params);ok=std::all_of(v.begin(),v.end(),[](double x){return std::isfinite(x);});if(ok)for(double x:v)result.push_back(Jet(x));}
   else if(context.rfind("reset",0)==0)ok=prepare_model_increment(f.model,z,loading,params,result);
   else ok=evaluate_model(f.model,z,z,loading,params,result,f.initial,0.,f.check,f.observe);
   out<<"{\"id\":\""<<f.id<<"\",\"model_id\":\""<<models()[f.model].id<<"\",\"catalogue_hash\":\""<<catalogue_hash()<<"\",\"ok\":"<<(ok?"true":"false")<<",\"input_unchanged\":"<<(same(z,before)?"true":"false")<<",\"output_count\":"<<(ok?result.size():0)<<",\"scalar_bits\":";
   if(ok&&!result.empty())out<<'"'<<bits(result.back().v)<<'"';else out<<"null";
   out<<",\"derivative_bits\":[";if(ok&&!scale&&!result.empty())for(unsigned j=0;j<38;++j){if(j)out<<',';out<<'"'<<bits(result.back().d[j])<<'"';}out<<"],\"all_outputs_finite\":";
   if(ok)out<<(std::all_of(result.begin(),result.end(),[](const Jet& x){return finite_value(x);})?"true":"false");else out<<"null";out<<'}';
  }else if(kind=='H'){
   if(index>=std::size(history_cases))throw std::runtime_error("history index");const auto& f=history_cases[index];const auto& p=history::programs()[f.program];std::vector<double> parent{17.25},input=csv(f.values);const auto before=parent,inputs_before=input;const auto result=p.advance(parent,input,7,3);
   out<<"{\"id\":\""<<f.id<<"\",\"model_id\":\""<<p.id<<"\",\"catalogue_hash\":\""<<p.sha256<<"\",\"ok\":"<<(result.ok?"true":"false")<<",\"input_unchanged\":"<<(same(parent,before)&&same(input,inputs_before)?"true":"false")<<",\"output_count\":"<<result.values.size()<<",\"scalar_bits\":\""<<bits(result.values.at(0))<<"\",\"derivative_bits\":[],\"all_outputs_finite\":"<<(std::all_of(result.values.begin(),result.values.end(),[](double x){return std::isfinite(x);})?"true":"false")<<",\"generation\":"<<result.generation<<",\"epoch\":"<<result.epoch<<",\"failed\":"<<result.failed<<",\"events\":[";
   for(size_t i=0;i<result.events.size();++i){if(i)out<<',';out<<result.events[i];}out<<"]}";
  }else throw std::runtime_error("request kind");answer=out.str();
 }catch(const std::exception&){answer="{\"harness_error\":true}";}
 return answer.c_str();
}
#ifndef __EMSCRIPTEN__
int main(){std::string line;while(std::getline(std::cin,line))std::cout<<determinant_context(line.c_str())<<std::endl;}
#endif
