#include "atlas/schedule.hpp"
#include <cstring>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <sstream>
#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#endif
namespace {
std::string bits(double x){std::uint64_t u;std::memcpy(&u,&x,8);std::ostringstream s;s<<std::hex<<std::setfill('0')<<std::setw(16)<<u;return s.str();}
bool same(const atlas::State&a,const atlas::State&b){if(a.size()!=b.size())return false;for(size_t i=0;i<a.size();++i)if(bits(a[i])!=bits(b[i]))return false;return true;}
int model(const std::string&id){for(size_t i=0;i<atlas::models().size();++i)if(atlas::models()[i].id==id)return int(i);throw std::runtime_error("missing fixture "+id);}
struct Writer{std::ostringstream out;bool first=true;Writer(){out<<"{\"version\":\"solver-rollback-observations-v1\",\"rows\":[";}
void row(const std::string&id,bool ok,const atlas::State*state,const double*time,const int*substeps,const bool*scale,const int*points,bool unchanged){if(!first)out<<',';first=false;out<<"{\"id\":\""<<id<<"\",\"ok\":"<<(ok?"true":"false")<<",\"state_bits\":";if(state){out<<'[';for(size_t i=0;i<state->size();++i){if(i)out<<',';out<<'\"'<<bits((*state)[i])<<'\"';}out<<']';}else out<<"null";out<<",\"time_bits\":";if(time)out<<'\"'<<bits(*time)<<'\"';else out<<"null";out<<",\"substeps\":";if(substeps)out<<*substeps;else out<<"null";out<<",\"scales_all_nonfinite\":";if(scale)out<<(*scale?"true":"false");else out<<"null";out<<",\"points\":";if(points)out<<*points;else out<<"null";out<<",\"inputs_bitwise_unchanged\":"<<(unchanged?"true":"false")<<'}';}
std::string finish(const std::string& preparation){out<<"],\"preparation\":["<<preparation<<"]}";return out.str();}};
atlas::IntegrationSettings legacy_settings(){atlas::IntegrationSettings s;s.max_depth=0;s.max_substeps=2;s.max_iterations=3;s.max_backtracks=0;return s;}
atlas::TimeSettings timed_settings(){atlas::TimeSettings s;s.minimum_step=.03125;s.maximum_step=.25;s.maximum_depth=4;s.maximum_substeps=32;return s;}
bool allbad(const atlas::State&s){return !s.empty()&&std::all_of(s.begin(),s.end(),[](double x){return !std::isfinite(x);});}
std::string run(){Writer w;std::ostringstream preparation;bool firstprep=true;const double M=std::numeric_limits<double>::max();
for(const std::string id:{"reset-late-guard","reset-late-value","reset-parent-success","legacy-state-scale"}){
 const int index=model(id);for(int bad=1;bad>=0;--bad){if(id!="legacy-state-scale"&&bad==0)continue;auto p=atlas::default_parameters(index);if(bad)p[1]=M;const auto p0=p;auto z=atlas::initial_state(index);const auto z0=z;atlas::Sym<double>d;const auto d0=d;if(id.rfind("reset-",0)==0){atlas::State scratch;bool ok=atlas::prepare_model_increment(index,z,d,p,scratch);if(!firstprep)preparation<<',';firstprep=false;preparation<<"{\"id\":\""<<id<<"\",\"ok\":"<<(ok?"true":"false")<<",\"scratch_bits\":[";for(size_t k=0;k<scratch.size();++k){if(k)preparation<<',';preparation<<'\"'<<bits(scratch[k])<<'\"';}preparation<<"],\"inputs_bitwise_unchanged\":"<<((same(z,z0)&&same(p,p0))?"true":"false")<<'}';}auto a=atlas::integrate(index,z,d,p,legacy_settings());bool invalid=allbad(atlas::model_scales(index,p));w.row(id=="legacy-state-scale"?id+(bad?"-reject":"-control"):id,a.ok,&a.state,nullptr,&a.diagnostics.substeps,id=="legacy-state-scale"?&invalid:nullptr,nullptr,same(z,z0)&&same(p,p0)&&std::memcmp(&d,&d0,sizeof d)==0);}}
for(const std::string id:{"timed-late-domain","timed-state-scale"}){const int index=model(id);for(int bad=1;bad>=0;--bad){auto p=atlas::default_parameters(index);if(bad)p[1]=M;const auto p0=p;auto z=atlas::initial_state(index);const auto z0=z;atlas::Sym<double>d;const auto d0=d;auto a=atlas::integrate_time(index,z,d,p,2.,1.,timed_settings());bool invalid=allbad(atlas::model_scales(index,p));w.row(id+(bad?"-reject":"-control"),a.ok,&a.state,&a.time,&a.diagnostics.substeps,id=="timed-state-scale"?&invalid:nullptr,nullptr,same(z,z0)&&same(p,p0)&&std::memcmp(&d,&d0,sizeof d)==0);}}
const int index=model("timed-observable-scale");for(int bad=1;bad>=0;--bad){auto p=atlas::default_parameters(index);if(bad)p[1]=M;const auto p0=p;auto z=atlas::initial_state(index);const auto z0=z;atlas::Sym<double>d;const auto d0=d;atlas::Segment segment;segment.id="one";segment.duration=1;segment.samples=1;atlas::ScheduleSettings s;s.time=timed_settings();s.maximum_iterations=3;auto a=atlas::run_schedule(index,z,p,d,d,2.,{segment},s);bool invalid=allbad(atlas::model_observable_scales(index,p));int n=int(a.points.size());const atlas::State*state=n?&a.points.back().state:nullptr;const double*time=n?&a.points.back().time:nullptr;w.row("timed-observable-scale"+std::string(bad?"-reject":"-control"),a.ok,state,time,nullptr,&invalid,&n,same(z,z0)&&same(p,p0)&&std::memcmp(&d,&d0,sizeof d)==0);}
return w.finish(preparation.str());}
}
#ifdef __EMSCRIPTEN__
extern "C" EMSCRIPTEN_KEEPALIVE const char* atlas_solver_rollback(){static std::string result;result=run();return result.c_str();}
#else
int main(){std::cout<<run()<<'\n';}
#endif
