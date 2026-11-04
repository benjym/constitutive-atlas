// Isolated research instantaneous rate transport; no tangent/integration claim.
#include "atlas/solver.hpp"
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#define RATE_EXPORT EMSCRIPTEN_KEEPALIVE
#else
#define RATE_EXPORT
#endif
namespace {
using namespace atlas;
std::string answer;
std::string quoted(const std::string&s){std::string o="\"";for(unsigned char c:s){if(c=='"'||c=='\\')o+='\\';if(c<32)o+=' ';else o+=c;}return o+'"';}
State csv(const char*s){State v;if(!s||!*s)return v;std::istringstream in(s);std::string x;
 while(std::getline(in,x,',')){size_t n=0;double a=std::stod(x,&n);if(n!=x.size()||!std::isfinite(a))throw std::runtime_error("CSV");v.push_back(a);}if(s[std::string(s).size()-1]==',')throw std::runtime_error("CSV");return v;}
void array(std::ostream&o,const State&v){o<<'[';for(size_t i=0;i<v.size();++i){if(i)o<<',';o<<v[i];}o<<']';}
}
extern "C" RATE_EXPORT const char* atlas_describe(){return atlas::describe_models();}
extern "C" RATE_EXPORT const char* atlas_barodesy_rate(const char*id,const char*parameters,const char*state,const char*increment){
 try{
  const std::string model=id?id:"";const auto p=csv(parameters),z=csv(state),de=csv(increment);State out;bool ok=false;
  if(models().size()==1&&model==models()[0].id&&valid_parameters(0,p)&&z.size()==initial_state(0).size()&&de.size()==6){
   ok=evaluate_model(0,z,z,tensor_from(de,0),p,out)&&out.size()==7&&finite(out);
  }
  std::ostringstream o;o<<std::setprecision(17)<<"{\"ok\":"<<(ok?"true":"false")<<",\"model\":"<<quoted(model)<<",\"catalogue_hash\":"<<quoted(catalogue_hash())<<",\"parameters\":";array(o,p);o<<",\"state\":";array(o,z);o<<",\"increment\":";array(o,de);o<<",\"values\":";
  if(ok)array(o,out);else o<<"null";o<<",\"message\":"<<quoted(ok?"":"unsupported research rate request")<<'}';answer=o.str();
 }catch(const std::exception&){answer="{\"ok\":false,\"message\":\"invalid research CSV\"}";}
 return answer.c_str();
}
#ifndef __EMSCRIPTEN__
int main(int argc,char**argv){
 if(argc==2&&std::string(argv[1])=="--describe"){std::cout<<atlas_describe()<<'\n';return 0;}
 if(argc!=5){std::cerr<<"model parameters_csv state_csv increment_csv required\n";return 2;}
 const std::string r=atlas_barodesy_rate(argv[1],argv[2],argv[3],argv[4]);std::cout<<r<<'\n';return r.find("\"ok\":true")!=std::string::npos?0:1;
}
#endif
