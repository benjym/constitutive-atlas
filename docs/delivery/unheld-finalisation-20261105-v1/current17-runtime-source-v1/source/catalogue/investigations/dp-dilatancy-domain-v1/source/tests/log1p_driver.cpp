// Synthetic scalar checked-operation probe, separate from scientific models.
#include "atlas/solver.hpp"
#include "atlas/linearize.hpp"
#include "history_programs.hpp"
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#define EXPORT EMSCRIPTEN_KEEPALIVE
#else
#define EXPORT
#endif
using namespace atlas;
namespace {
int idx(const std::string& suffix){for(size_t i=0;i<models().size();++i)if(models()[i].id=="test-log1p-"+suffix)return int(i);throw std::runtime_error("fixture missing");}
State state(const std::string& name,bool bad){auto s=initial_state(idx(name));if(bad)s[6]=-2.;return s;}
bool eval(const std::string& name,bool bad,bool initial=false,bool check=false,bool obs=false,double t=0.,double load=1.){auto z=state(name,bad);State out;Sym<double>d;d.v[0]=load;return evaluate_model(idx(name),z,z,d,default_parameters(idx(name)),out,initial,t,check,obs);}
bool prepare(const std::string& name,bool bad,double load){auto z=state(name,bad);State out;Sym<double>d;d.v[0]=load;return prepare_model_increment(idx(name),z,d,default_parameters(idx(name)),out);}
bool same(const Jet&a,const Jet&b){return a.v==b.v&&a.d==b.d;}
std::map<std::string,bool> contexts(){
 std::map<std::string,bool> c;
 c["derived_eager_masked_failure"]=!eval("derived-cancel",true);
 c["derived_check_only_failure"]=!eval("derived-cancel",true,false,true);
 c["derived_valid"]=eval("derived-cancel",false);
 c["domain_masked_failure"]=!eval("domain-masked",true);
 c["initial_active_failure"]=!eval("initial-only",true,true);
 c["initial_inactive_skipped"]=eval("initial-only",true);
 c["lazy_bad_arm_skipped"]=eval("lazy-select",true,false,false,false,0.,-1.);
 c["lazy_bad_arm_selected_failure"]=!eval("lazy-select",true);
 c["timed_check_only"]=eval("time-observable",false,false,true,false,2.);
 c["timed_equation_failure"]=!eval("time-observable",false,false,false,false,2.);
 c["observable_only_skips_bad_equation"]=eval("time-observable",false,false,false,true,2.);
 c["observable_failure"]=!eval("time-observable",true,false,false,true);
 c["observable_inactive"]=eval("time-observable",true);
 c["reset_guard_failure"]=!prepare("reset-guard",true,1.);
 c["reset_value_inactive"]=prepare("reset-value",true,1.);
 c["reset_value_failure"]=!prepare("reset-value",true,-1.);
 auto z=state("reset-rollback",true);Sym<double>d;d.v[0]=.001;
 auto r=integrate(idx("reset-rollback"),z,d,default_parameters(idx("reset-rollback")));
 c["reset_rollback"]=!r.ok&&r.state==z;
 double a=.2,y;bool good=scalar_log1p_checked(a,y);c["alias_success"]=good&&scalar_log1p_checked(a,a)&&a==y;
 a=-2.;c["alias_failure_preserves"]=!scalar_log1p_checked(a,a)&&a==-2.;
 Jet sentinel(17.);sentinel.d.fill(19.);Jet out=sentinel,bad(0.);bad.d.back()=std::numeric_limits<double>::quiet_NaN();
 c["last_derivative_nonfinite_rejected"]=!scalar_log1p_checked(bad,out)&&same(out,sentinel);
 bad=Jet(std::nextafter(-1.,0.));bad.d[0]=std::numeric_limits<double>::max();
 c["derivative_overflow_rejected"]=!scalar_log1p_checked(bad,out)&&same(out,sentinel);
 Jet large(std::numeric_limits<double>::max());large.d[0]=large.v;
 c["large_seed_division_stays_finite"]=scalar_log1p_checked(large,out)&&out.d[0]==1.;
 bool flag=true;scalar_log1p_or_mark(-2.,flag);scalar_log1p_or_mark(0.,flag);c["sticky_failure"]=!flag;
 auto& hp=history::programs().at(0);State parent={.1,.2,.3,.4,.5,.6},input={.2,-.1,.3,.1,.05,-.2,1.};
 auto hs=hp.advance(parent,input,7,3);double expected=1.+std::log1p(.2-.1+.3);bool match=hs.ok&&hs.values.size()==6;
 for(int i=0;i<6&&match;++i)match=std::abs(hs.values[i]-(i<3?expected:0.))<1e-14;
 c["history_values_and_counters"]=match&&hs.generation==8&&hs.epoch==3&&hs.events.size()==1;
 input={-2.,0.,0.,0.,0.,0.,0.};auto inactive=hp.advance(parent,input,7,3);
 c["history_lazy"]=inactive.ok&&inactive.values==State({1.,1.,1.,0.,0.,0.});
 input[6]=1.;auto hf=hp.advance(parent,input,7,3);
 c["history_failure_rollback"]=!hf.ok&&hf.values==parent&&hf.generation==7&&hf.epoch==3&&hf.events.empty();
 input={.2,-.1,.3,.1,.05,-.2,1.};auto recovery=hp.advance(parent,input,7,3);
 c["history_recovery"]=recovery.ok&&recovery.values==hs.values&&parent==State({.1,.2,.3,.4,.5,.6});
 return c;
}
}
extern "C" EXPORT const char* atlas_log1p_probe(const char* text){
 static std::string answer;
 try{
  if(!text||!*text)throw std::runtime_error("input");char* end=nullptr;double x=std::strtod(text,&end);
  if(end==text||*end||!std::isfinite(x))throw std::runtime_error("input");
  Jet a(x),out;for(int i=0;i<max_derivatives;++i)a.d[i]=1.;bool primitive=scalar_log1p_checked(a,out);
  int m=idx("direct");auto values=initial_state(m);std::vector<Jet> z;for(auto v:values)z.emplace_back(v);z[6]=a;
  Sym<Jet> d;d.v[0]=Jet(1.);std::vector<Jet> rhs;bool schema=evaluate_model(m,z,z,d,default_parameters(m),rhs);
  auto c=contexts();bool all=primitive&&schema;for(auto& pair:c)all=all&&pair.second;
  std::ostringstream os;os<<std::setprecision(17)<<"{\"ok\":"<<(all?"true":"false")<<",\"input\":"<<x<<",\"operator_version\":\""<<scalar_log1p_version<<"\",\"catalogue_hash\":\""<<catalogue_hash()<<"\",\"primitive_ok\":"<<(primitive?"true":"false")<<",\"schema_ok\":"<<(schema?"true":"false")<<",\"contexts\":{";
  bool first=true;for(auto& pair:c){if(!first)os<<',';first=false;os<<'"'<<pair.first<<"\":"<<(pair.second?"true":"false");}os<<'}';
  os<<",\"value\":";if(primitive)os<<out.v;else os<<"null";
  os<<",\"negative_zero\":"<<((primitive&&out.v==0.&&std::signbit(out.v))?"true":"false");
  os<<",\"derivatives\":";if(primitive){os<<'[';for(int i=0;i<max_derivatives;++i){if(i)os<<',';os<<out.d[i];}os<<']';}else os<<"null";
  os<<",\"schema_values\":";if(schema){os<<'[';for(int i=0;i<6;++i){if(i)os<<',';os<<rhs[i].v;}os<<']';}else os<<"null";
  os<<",\"schema_derivatives\":";if(schema){os<<'[';for(int i=0;i<6;++i){if(i)os<<',';os<<'[';for(int j=0;j<max_derivatives;++j){if(j)os<<',';os<<rhs[i].d[j];}os<<']';}os<<']';}else os<<"null";
  os<<'}';answer=os.str();
 }catch(const std::exception&){answer="{\"ok\":false,\"error\":\"invalid input\"}";}
 return answer.c_str();
}
int main(int argc,char**argv){if(argc==2&&std::string(argv[1])=="--describe"){std::cout<<describe_models()<<'\n';return 0;}std::string r=atlas_log1p_probe(argc>1?argv[1]:"0");std::cout<<r<<'\n';return r.find("\"ok\":true")!=std::string::npos?0:1;}
