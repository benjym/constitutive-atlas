#include "models.hpp"
#include "history.hpp"
#include "cases.hpp"
#include <bit>
#include <iomanip>
#include <sstream>
#include <iostream>
#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#define EXPORT EMSCRIPTEN_KEEPALIVE
#else
#define EXPORT
#endif
using namespace atlas;
std::string bits(double value){if(std::isnan(value))return "nan";std::ostringstream s;s<<std::hex<<std::setw(16)<<std::setfill('0')<<std::bit_cast<std::uint64_t>(value);return s.str();}
void values(std::ostream& out,const std::vector<double>& a){out<<'[';for(size_t i=0;i<a.size();++i){if(i)out<<',';out<<'"'<<bits(a[i])<<'"';}out<<']';}
bool same(const std::vector<Jet>& a,const std::vector<Jet>& b){if(a.size()!=b.size())return false;for(size_t i=0;i<a.size();++i){if(bits(a[i].v)!=bits(b[i].v))return false;for(int j=0;j<38;++j)if(bits(a[i].d[j])!=bits(b[i].d[j]))return false;}return true;}
std::string run(){std::ostringstream out;out<<"{\"version\":\"expression-generated-context-observations-v1\",\"material\":[";bool first=true;
for(const auto& f:trace_cases){
 if(!first)out<<',';first=false;
 std::vector<Jet> z(12),result;for(int i=0;i<6;++i)z[6+i]=Jet(f.a[i]);
 if(f.seed>=1&&f.seed<=3)z[6+f.component].d[f.column]=f.seed==1?std::numeric_limits<double>::infinity():f.seed==2?-std::numeric_limits<double>::infinity():std::numeric_limits<double>::quiet_NaN();
 if(f.seed==4)for(int j=0;j<38;++j){z[6].d[j]=500.;z[7].d[j]=j%2?-1e-130:1e-130;z[8].d[j]=-500.;}
 if(f.seed==5)for(int j=0;j<38;++j){z[6].d[j]=z[7].d[j]=std::numeric_limits<double>::max();z[8].d[j]=-std::numeric_limits<double>::max();}
 if(f.seed==6){z[6].d[f.column]=z[7].d[f.column]=std::numeric_limits<double>::max();}
 if(f.seed==7){z[6].d[f.column]=std::numeric_limits<double>::max();z[7].d[f.column]=z[8].d[f.column]=-std::numeric_limits<double>::max();}
 auto before=z;std::vector<double> p;for(const auto& param:models()[f.model].parameters)p.push_back(param.name=="r"?f.param:param.value);
 Sym<Jet> loading{};std::string kind=f.kind;bool ok=true;std::vector<double> v;
 if(kind=="state-scale"||kind=="observable-scale")v=kind=="state-scale"?model_scales(f.model,p):model_observable_scales(f.model,p);
 else{
  ok=kind.rfind("reset",0)==0?prepare_model_increment(f.model,z,loading,p,result):evaluate_model(f.model,z,z,loading,p,result,f.initial,0.,f.check,f.observe);
  if(ok)for(const auto& x:result)v.push_back(x.v);
 }
 out<<"{\"id\":\""<<f.id<<"\",\"ok\":"<<(ok?"true":"false")<<",\"input_unchanged\":"<<(same(z,before)?"true":"false")<<",\"values_bits\":";values(out,v);out<<",\"derivative_bits\":[";
 if(ok&&(f.seed==4||f.seed==5))for(int j=0;j<38;++j){if(j)out<<',';std::vector<double> d;for(const auto& x:result)d.push_back(x.d[j]);values(out,d);}out<<"]}";
}
out<<"],\"history\":[";first=true;
for(const auto& p:history::programs())for(int mode=0;mode<3;++mode){
 if(!first)out<<',';first=false;
 std::vector<double> parent{.1,.2,.3,.4,.5,.6},input{3.,0.,0.,0.,0.,0.};auto before=parent;
 if(mode==1){double m=std::numeric_limits<double>::max();input={m,m,m,0.,0.,0.};if(std::string(p.id)=="trace-history-dev")input={m,-m,-m,0.,0.,0.};}
 const auto result=p.advance(parent,input,7,3);
 out<<"{\"id\":\""<<p.id<<'/'<<(mode==0?"good":mode==1?"bad":"recover")<<"\",\"ok\":"<<(result.ok?"true":"false")<<",\"values_bits\":";values(out,result.values);
 out<<",\"generation\":"<<result.generation<<",\"epoch\":"<<result.epoch<<",\"events\":[";for(size_t i=0;i<result.events.size();++i){if(i)out<<',';out<<result.events[i];}
 bool unchanged=true;for(size_t i=0;i<parent.size();++i)unchanged=unchanged&&bits(parent[i])==bits(before[i]);
 out<<"],\"failed\":"<<result.failed<<",\"parent_unchanged\":"<<(unchanged?"true":"false")<<'}';
}out<<"]}";return out.str();}
extern "C" EXPORT const char* atlas_expression_context(){static std::string s;s=run();return s.c_str();}
#ifndef __EMSCRIPTEN__
int main(){std::cout<<atlas_expression_context()<<'\n';}
#endif
