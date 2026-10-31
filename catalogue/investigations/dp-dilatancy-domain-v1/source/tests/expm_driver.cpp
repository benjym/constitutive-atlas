// Isolated synthetic checked-expm conformance probe. No scientific model claim.
#include "atlas/expm.hpp"
#include "atlas/solver.hpp"
#include "atlas/linearize.hpp"
#include "history_programs.hpp"
#include <cerrno>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#define ATLAS_PROBE_EXPORT EMSCRIPTEN_KEEPALIVE
#else
#define ATLAS_PROBE_EXPORT
#endif
namespace {
using namespace atlas;
int index_of(const std::string& suffix){
 const std::string id="test-expm-"+suffix;
 for(size_t i=0;i<models().size();++i)if(models()[i].id==id)return int(i);
 throw std::runtime_error("missing isolated fixture: "+id);
}
Sym<double> input(const char* csv){
 Sym<double> a;if(!csv||!*csv)return a;
 const char* s=csv;
 for(int i=0;i<6;++i){char* end=nullptr;errno=0;a.v[i]=std::strtod(s,&end);
  if(end==s||errno==ERANGE||!std::isfinite(a.v[i]))throw std::runtime_error("six finite CSV Mandel components required");
  if(i<5){if(*end!=',')throw std::runtime_error("CSV component count");s=end+1;}
  else if(*end)throw std::runtime_error("CSV trailing input");}
 return a;
}
std::vector<Jet> state_jets(int model,const Sym<double>& a){
 const auto z=initial_state(model);std::vector<Jet> x;for(double v:z)x.emplace_back(v);
 for(int j=0;j<6;++j){x.at(6+j)=Jet(a.v[j]);x.at(6+j).d[j]=1.;}return x;
}
State state_values(int model,bool bad){auto z=initial_state(model);if(bad)z[6]=100.;return z;}
bool eval(const std::string& suffix,bool bad,bool initial=false,bool check=false,bool obs=false,double t=0.,double load=1.){
 int m=index_of(suffix);auto z=state_values(m,bad);State out;Sym<double> d;d.v[0]=load;
 return evaluate_model(m,z,z,d,default_parameters(m),out,initial,t,check,obs);
}
bool prepared(const std::string& suffix,bool bad,double load){
 int m=index_of(suffix);auto z=state_values(m,bad);State out;Sym<double> d;d.v[0]=load;
 return prepare_model_increment(m,z,d,default_parameters(m),out);
}
Sym<Jet> sentinel(){Sym<Jet> y;for(int i=0;i<6;++i){y.v[i]=Jet(-91-i);for(int j=0;j<max_derivatives;++j)y.v[i].d[j]=.125*(i+1);}return y;}
bool same(const Sym<Jet>&a,const Sym<Jet>&b){for(int i=0;i<6;++i){if(a.v[i].v!=b.v[i].v)return false;for(int j=0;j<max_derivatives;++j)if(a.v[i].d[j]!=b.v[i].d[j])return false;}return true;}
void matrix_json(std::ostream& os,const Sym<Jet>& y,bool jac){
 os<<'[';for(int i=0;i<6;++i){if(i)os<<',';if(jac){os<<'[';for(int j=0;j<6;++j){if(j)os<<',';os<<y.v[i].d[j];}os<<']';}else os<<y.v[i].v;}os<<']';
}
std::map<std::string,bool> contexts(){
 std::map<std::string,bool> c;
 c["eager_unused_derived_failure"]=!eval("derived-cancel",true);
 c["eager_derived_check_only_failure"]=!eval("derived-cancel",true,false,true);
 c["derived_good_success"]=eval("derived-cancel",false);
 c["lazy_unsupported_arm_skipped"]=eval("lazy-select",true,false,false,false,0.,-1.);
 c["lazy_unsupported_arm_selected_fails"]=!eval("lazy-select",true);
 c["masked_domain_failure"]=!eval("domain-masked",true);
 c["initial_check_inactive"]=eval("initial-only",true);
 c["initial_check_active_fails"]=!eval("initial-only",true,true);
 c["time_check_only_skips_equation"]=eval("time-observable",false,false,true,false,2.);
 c["time_equation_selected_fails"]=!eval("time-observable",false,false,false,false,2.);
 c["observable_only_skips_bad_equation"]=eval("time-observable",false,false,false,true,2.);
 c["observable_bad_fails"]=!eval("time-observable",true,false,false,true,0.);
 c["observable_inactive_skipped"]=eval("time-observable",true,false,false,false,0.);
 c["reset_guard_masked_failure"]=!prepared("reset-guard",true,1.);
 c["reset_value_inactive_skipped"]=prepared("reset-value",true,1.);
 c["reset_value_active_failure"]=!prepared("reset-value",true,-1.);
 int m=index_of("reset-rollback");auto z=state_values(m,true);Sym<double> de;de.v[0]=.001;
 const auto r=integrate(m,z,de,default_parameters(m));c["reset_full_integration_rollback"]=!r.ok&&r.state==z&&r.message.find("increment reset failed")!=std::string::npos;
 Sym<double> a;a.v[0]=.2;a.v[3]=.3;Sym<double> ref;
 bool ok=tensor_expm_checked(a,ref);auto alias=a;bool ak=tensor_expm_checked(alias,alias);
 bool eq=ok&&ak;for(int j=0;j<6;++j)eq=eq&&alias.v[j]==ref.v[j];c["primitive_alias_success"]=eq;
 Sym<double> bad;bad.v[0]=100.;auto badcopy=bad;
 c["primitive_alias_failure_preserves"]=!tensor_expm_checked(bad,bad)&&bad.v==badcopy.v;
 Sym<Jet> jbad;for(int j=0;j<6;++j)jbad.v[j]=Jet(0.);jbad.v[2].d[max_derivatives-1]=std::numeric_limits<double>::quiet_NaN();
 auto out=sentinel();const auto before=out;
 c["last_derivative_nan_rejected_preserves"]=!tensor_expm_checked(jbad,out)&&same(out,before);
 jbad=Sym<Jet>{};jbad.v[0]=Jet(60.);jbad.v[0].d[0]=std::numeric_limits<double>::max();out=before;
 c["derivative_only_overflow_rejected_preserves"]=!tensor_expm_checked(jbad,out)&&same(out,before);
 bool flag=true;const auto unused=tensor_expm_or_mark(badcopy,flag);(void)unused;
 const auto good=tensor_expm_or_mark(Sym<double>{},flag);(void)good;c["sticky_flag_not_restored"]=!flag;
 m=index_of("direct");auto jets=state_jets(m,Sym<double>{});jets[6].d[max_derivatives-1]=std::numeric_limits<double>::infinity();std::vector<Jet> rhs;Sym<Jet> jd;jd.v[0]=Jet(1.);
 c["compiled_derivative_failure"]=!evaluate_model(m,jets,jets,jd,default_parameters(m),rhs);
 if(history::programs().size()!=1)throw std::runtime_error("one isolated history fixture required");
 const auto& hp=history::programs().at(0);
 if(hp.state_size!=6||hp.input_size!=7)throw std::runtime_error("history fixture layout mismatch");
 const State parent={.1,.2,.3,.4,.5,.6};const auto saved_parent=parent;
 State hi={.2,-.1,.3,.1,.05,-.2,1.};
 Sym<double> hx;for(int i=0;i<6;++i)hx.v[i]=hi[i];Sym<double> expected;
 const bool expected_ok=tensor_expm_checked(hx,expected);
 const auto hs=hp.advance(parent,hi,7,3);bool match=expected_ok&&hs.ok&&hs.values.size()==6;
 if(match)for(int i=0;i<6;++i)match=match&&std::abs(hs.values[i]-expected.v[i])<=1e-13*std::max(1.,std::abs(expected.v[i]));
 c["history_valid_output"]=match&&hs.generation==8&&hs.epoch==3&&hs.events.size()==1&&hs.failed==-1;
 State unsupported={65.,0.,0.,0.,0.,0.,0.};
 const auto inactive=hp.advance(parent,unsupported,7,3);
 c["history_inactive_unsupported_skipped"]=inactive.ok&&inactive.values==State({1.,1.,1.,0.,0.,0.})&&inactive.generation==8&&inactive.epoch==3&&inactive.events.size()==1;
 unsupported[6]=1.;const auto hf=hp.advance(parent,unsupported,7,3);
 c["history_active_failure_rollback"]=!hf.ok&&hf.values==parent&&hf.generation==7&&hf.epoch==3&&hf.events.empty()&&hf.failed==0;
 const auto recovered=hp.advance(parent,hi,7,3);
 c["history_valid_recovery_parent_isolation"]=recovered.ok&&recovered.values==hs.values&&recovered.generation==8&&recovered.epoch==3&&parent==saved_parent;
 // Independent exact midpoint recurrence on the accepted (frozen) partition.
 m=index_of("direct");auto initial=state_values(m,false);const double amplitude=.02;
 Sym<double> total;total.v[0]=amplitude;IntegrationSettings settings;settings.rate_tolerance=1e-8;
 const auto replay=linearize_update(m,initial,total,default_parameters(m),settings);
 double covered=0.,weighted=0.,derivative=0.;bool partition=true;
 for(double fraction:replay.advance.diagnostics.increment_fractions){
  if(!std::isfinite(fraction)||fraction<=0){partition=false;break;}
  const double midpoint_coordinate=covered+.5*fraction;
  const double exponential=std::exp(amplitude*midpoint_coordinate);
  weighted+=fraction*exponential;
  derivative+=fraction*exponential*(1.+amplitude*midpoint_coordinate);
  covered+=fraction;
 }
 const auto near=[](double x,double y){return std::abs(x-y)<=1e-11*std::max(1.,std::abs(y));};
 bool recurrence=replay.advance.ok&&replay.tangent_ok&&partition&&near(covered,1.)&&replay.state_tangent.size()==initial.size();
 if(recurrence){
  recurrence=near(replay.advance.state[0]-initial[0],amplitude*weighted)&&near(replay.state_tangent[0][0],derivative)
    &&near(replay.advance.state[1]-initial[1],amplitude)&&near(replay.advance.state[2]-initial[2],amplitude)
    &&near(replay.state_tangent[1][0],1.)&&near(replay.state_tangent[2][0],1.)
    &&near(replay.advance.state[6],amplitude)&&near(replay.state_tangent[6][0],1.);
 }
 c["common_engine_accepted_partition_recurrence"]=recurrence;
 initial[6]=100.;const auto rejected_replay=linearize_update(m,initial,total,default_parameters(m),settings);
 c["common_engine_failed_replay_rollback"]=!rejected_replay.advance.ok&&rejected_replay.advance.state==initial&&!rejected_replay.tangent_ok&&rejected_replay.state_tangent.empty();
 return c;
}
}
extern "C" ATLAS_PROBE_EXPORT const char* atlas_expm_probe(const char* csv,int mode){
 static std::string answer;
 try{
  if(mode!=0&&mode!=1)throw std::runtime_error("mode must be0or1");
  const auto a=input(csv);const auto c=contexts();bool all=true;for(const auto& v:c)all=all&&v.second;
  std::ostringstream os;os<<std::setprecision(17);Sym<Jet> y;bool primitive=false,schema=false;Sym<Jet> sy;
  if(mode==0){Sym<Jet> x;for(int j=0;j<6;++j){x.v[j]=Jet(a.v[j]);x.v[j].d[j]=1.;}primitive=tensor_expm_checked(x,y);
   int m=index_of("direct");auto z=state_jets(m,a);Sym<Jet>d;d.v[0]=Jet(1.);std::vector<Jet> out;
   schema=evaluate_model(m,z,z,d,default_parameters(m),out);if(schema)sy=tensor_from(out,0);
   all=all&&primitive&&schema;
  }
  os<<"{\"operator_version\":\""<<symmetric_expm_version<<"\",\"catalogue_hash\":\""<<catalogue_hash()<<"\",\"input\":[";
  for(int i=0;i<6;++i){if(i)os<<',';os<<a.v[i];}
  os<<"],\"ok\":"<<(all?"true":"false")<<",\"mode\":"<<mode<<",\"contexts\":{";bool first=true;
  for(const auto& v:c){if(!first)os<<',';first=false;os<<'"'<<v.first<<"\":"<<(v.second?"true":"false");}os<<'}';
  if(mode==0){os<<",\"primitive_ok\":"<<(primitive?"true":"false")<<",\"schema_ok\":"<<(schema?"true":"false");
   os<<",\"values\":";if(primitive)matrix_json(os,y,false);else os<<"null";
   os<<",\"jacobian\":";if(primitive)matrix_json(os,y,true);else os<<"null";
   os<<",\"schema_values\":";if(schema)matrix_json(os,sy,false);else os<<"null";
   os<<",\"schema_jacobian\":";if(schema)matrix_json(os,sy,true);else os<<"null";}
  os<<'}';answer=os.str();
 }catch(const std::exception&){answer="{\"ok\":false,\"error\":\"invalid probe input or missing isolated fixtures\"}";}
 return answer.c_str();
}
int main(int argc,char**argv){
 if(argc==2&&std::string(argv[1])=="--describe"){std::cout<<atlas::describe_models()<<'\n';return 0;}
 int mode=0;if(argc>2){if(std::string(argv[2])=="1")mode=1;else if(std::string(argv[2])!="0")return 2;}
 const std::string result=atlas_expm_probe(argc>1?argv[1]:"0,0,0,0,0,0",mode);
 std::cout<<result<<'\n';return result.find("\"ok\":true")!=std::string::npos?0:1;
}
