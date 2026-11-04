// Isolated instantaneous material AD; exact nonzero hydrostatic loading only.
#include "atlas/solver.hpp"
#include <iomanip>
#include <iostream>
#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#define AD_EXPORT EMSCRIPTEN_KEEPALIVE
#else
#define AD_EXPORT
#endif
namespace {
using namespace atlas;
std::string reply;
std::string quote(const std::string&s){std::string o="\"";for(unsigned char c:s){if(c=='"'||c=='\\')o+='\\';if(c<32)o+=' ';else o+=c;}return o+'"';}
State csv(const char*s){State v;if(!s||!*s)return v;std::istringstream in(s);std::string x;while(std::getline(in,x,',')){size_t n;double a=std::stod(x,&n);if(n!=x.size()||!std::isfinite(a))throw std::runtime_error("CSV");v.push_back(a);}if(s[std::string(s).size()-1]==',')throw std::runtime_error("CSV");return v;}
void array(std::ostream&o,const State&a){o<<'[';for(size_t i=0;i<a.size();++i){if(i)o<<',';o<<a[i];}o<<']';}
}
extern "C" AD_EXPORT const char* atlas_describe(){return atlas::describe_models();}
extern "C" AD_EXPORT const char* atlas_barodesy_hydro_ad(const char*id,const char*parameters,const char*state,const char*increment){
 try{
  const std::string model=id?id:"";const auto p=csv(parameters),z=csv(state),de=csv(increment);std::vector<Jet> out;bool ok=false;
  if(models().size()==1&&model==models()[0].id&&valid_parameters(0,p)&&z.size()==7&&de.size()==6){
   const auto loading=tensor_from(de,0);
   const bool hydro=de[0]==de[1]&&de[1]==de[2]&&de[3]==0&&de[4]==0&&de[5]==0;
   if(norm(loading)>0&&hydro&&de[0]!=0){
    std::vector<Jet> current(7),previous(7);Sym<Jet> d;
    for(int i=0;i<7;++i){current[i]=Jet(z[i]);current[i].d[i]=1;previous[i]=Jet(z[i]);}
    for(int i=0;i<6;++i){d.v[i]=Jet(de[i]);d.v[i].d[7+i]=1;}
    ok=evaluate_model(0,current,previous,d,p,out)&&out.size()==7;
    for(const auto&x:out){ok=ok&&finite_value(x);for(int j=13;j<max_derivatives;++j)ok=ok&&x.d[j]==0;}
   }
  }
  std::ostringstream o;o<<std::setprecision(17)<<"{\"ok\":"<<(ok?"true":"false")<<",\"model\":"<<quote(model)<<",\"catalogue_hash\":"<<quote(catalogue_hash())<<",\"parameters\":";array(o,p);o<<",\"state\":";array(o,z);o<<",\"increment\":";array(o,de);o<<",\"values\":";
  if(ok){State v;for(const auto&x:out)v.push_back(x.v);array(o,v);}else o<<"null";
  o<<",\"jacobian\":";if(ok){o<<'[';for(size_t i=0;i<out.size();++i){if(i)o<<',';State row;for(int j=0;j<13;++j)row.push_back(out[i].d[j]);array(o,row);}o<<']';}else o<<"null";
  o<<",\"columns\":[\"sigma_xx\",\"sigma_yy\",\"sigma_zz\",\"sigma_xy_mandel\",\"sigma_yz_mandel\",\"sigma_xz_mandel\",\"e\",\"de_xx\",\"de_yy\",\"de_zz\",\"de_xy_mandel\",\"de_yz_mandel\",\"de_xz_mandel\"],\"message\":"<<quote(ok?"":"unsupported exact hydro material AD request")<<'}';reply=o.str();
 }catch(const std::exception&){reply="{\"ok\":false,\"message\":\"invalid research CSV\"}";}
 return reply.c_str();
}
#ifndef __EMSCRIPTEN__
int main(int argc,char**argv){
 if(argc==2&&std::string(argv[1])=="--stream"){
  std::string line;while(std::getline(std::cin,line)){
   if(line=="--describe"){std::cout<<atlas_describe()<<std::endl;continue;}
   std::vector<std::string> fields;std::istringstream input(line);std::string field;while(std::getline(input,field,'\t'))fields.push_back(field);
   if(fields.size()!=4){std::cout<<"{\"ok\":false,\"message\":\"invalid stream request\"}"<<std::endl;continue;}
   std::cout<<atlas_barodesy_hydro_ad(fields[0].c_str(),fields[1].c_str(),fields[2].c_str(),fields[3].c_str())<<std::endl;
  }
  return std::cin.bad()?2:0;
 }
 if(argc==2&&std::string(argv[1])=="--describe"){std::cout<<atlas_describe()<<'\n';return 0;}if(argc!=5)return 2;const std::string s=atlas_barodesy_hydro_ad(argv[1],argv[2],argv[3],argv[4]);std::cout<<s<<'\n';return s.find("\"ok\":true")!=std::string::npos?0:1;}
#endif
