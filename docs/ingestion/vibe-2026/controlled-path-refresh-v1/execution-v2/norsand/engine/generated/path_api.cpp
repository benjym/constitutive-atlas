// Generated generic path C ABI. All output writes are committed after success.
#include "path_models.hpp"
#include "atlas/path_runtime.hpp"
#include <array>
using atlas::controlled_path::Definition;
static const std::vector<Definition> definitions={{2,{{-1,0},{0,0},{0,1},{1,0},{1,1}},[](const auto& z,const auto& p,const auto& i,auto& r,auto& o,auto& s,bool initial){return atlas::path_generated::evaluate(0,z,p,i,r,o,s,initial);}},{2,{{-1,0},{0,0},{0,1},{1,0}},[](const auto& z,const auto& p,const auto& i,auto& r,auto& o,auto& s,bool initial){return atlas::path_generated::evaluate(1,z,p,i,r,o,s,initial);}},{2,{{-1,0},{0,0},{0,1},{1,0}},[](const auto& z,const auto& p,const auto& i,auto& r,auto& o,auto& s,bool initial){return atlas::path_generated::evaluate(2,z,p,i,r,o,s,initial);}}};
static const std::vector<std::array<int,5>> shapes={{4,6,2,5,13},{7,1,2,4,6},{7,1,2,4,6}};
static bool valid_model(int i){return i>=0&&size_t(i)<definitions.size();}
static bool pointer_ok(const double* p,int n){return n>=0&&(n==0||p!=nullptr);}
static std::vector<double> copy_values(const double* p,int n){return n?std::vector<double>(p,p+n):std::vector<double>();}
extern "C" int path_size(int model,int field){return valid_model(model)&&field>=0&&field<5?shapes[model][field]:-1;}
extern "C" int path_evaluate(int model,const double* state,int ns,const double* params,int np,const double* inputs,int ni,double* rates,double* observed,int no,double* scales,int initial){
 try{
  if(!valid_model(model)||ns!=shapes[model][0]||np!=shapes[model][1]||ni!=shapes[model][3]||no!=shapes[model][4]||!pointer_ok(state,ns)||!pointer_ok(params,np)||!pointer_ok(inputs,ni)||!pointer_ok(rates,ns)||!pointer_ok(observed,no)||!pointer_ok(scales,ns)||(initial!=0&&initial!=1))return 0;
  std::vector<double> r,o,s;
  if(!definitions[model].evaluate(copy_values(state,ns),copy_values(params,np),copy_values(inputs,ni),r,o,s,initial))return 0;
  std::copy(r.begin(),r.end(),rates);std::copy(o.begin(),o.end(),observed);std::copy(s.begin(),s.end(),scales);return 1;
 }catch(...){return 0;}
}
extern "C" int path_advance(int model,const double* state,int ns,double coordinate,const double* params,int np,const double* current,int nc,double progress,const double* start,const double* end,const double* settings,int nsettings,double* output,double* out_coordinate,double* observed,int no){
 try{
  if(!valid_model(model)||ns!=shapes[model][0]||np!=shapes[model][1]||nc!=shapes[model][2]||no!=shapes[model][4]||nsettings!=6||!pointer_ok(state,ns)||!pointer_ok(params,np)||!pointer_ok(current,nc)||!pointer_ok(start,nc)||!pointer_ok(end,nc)||!pointer_ok(settings,nsettings)||!pointer_ok(output,ns)||!out_coordinate||!pointer_ok(observed,no))return 0;
  for(int i=0;i<6;++i)if(!std::isfinite(settings[i]))return 0;
  if(settings[4]!=std::floor(settings[4])||settings[4]<1||settings[4]>60||settings[5]!=std::floor(settings[5])||settings[5]<1||settings[5]>1000000)return 0;
  atlas::controlled_path::Settings execution{settings[0],settings[1],settings[2],settings[3],int(settings[4]),int(settings[5])};
  atlas::controlled_path::Context parent{copy_values(state,ns),coordinate,copy_values(current,nc),copy_values(params,np)},committed;
  std::vector<double> obs;
  if(!atlas::controlled_path::advance(definitions[model],parent,progress,copy_values(start,nc),copy_values(end,nc),execution,committed,obs))return 0;
  std::copy(committed.state.begin(),committed.state.end(),output);std::copy(obs.begin(),obs.end(),observed);*out_coordinate=committed.coordinate;return 1;
 }catch(...){return 0;}
}
