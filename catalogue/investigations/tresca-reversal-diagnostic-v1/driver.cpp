#include "atlas/solver.hpp"
#include "trace/solver.hpp"
#include <iostream>
#include <iomanip>
#include <bit>
#include "inputs.hpp"
void array(const std::vector<double>& v){std::cout<<'[';for(size_t i=0;i<v.size();++i){if(i)std::cout<<',';if(std::isfinite(v[i]))std::cout<<v[i];else std::cout<<"null";}std::cout<<']';}
void matrix(const std::vector<std::vector<double>>& v){std::cout<<'[';for(size_t i=0;i<v.size();++i){if(i)std::cout<<',';array(v[i]);}std::cout<<']';}
bool bits_equal(const std::vector<double>&a,const std::vector<double>&b){if(a.size()!=b.size())return false;for(size_t i=0;i<a.size();++i)if(std::bit_cast<uint64_t>(a[i])!=std::bit_cast<uint64_t>(b[i]))return false;return true;}
template<class Advance> void result(const Advance& a){std::cout<<"{\"ok\":"<<(a.ok?"true":"false")<<",\"state\":";array(a.state);std::cout<<",\"iterations\":"<<a.diagnostics.iterations<<",\"substeps\":"<<a.diagnostics.substeps<<",\"rejected\":"<<a.diagnostics.rejected<<",\"error\":"<<a.diagnostics.error<<'}';}
int main(){
 std::cout<<std::setprecision(17);const auto before=parent;atlas::IntegrationSettings s;s.max_depth=0;atlas_trace::IntegrationSettings ts;ts.max_depth=0;
 auto de=atlas::tensor_from(loading,0);auto tde=atlas_trace::tensor_from(loading,0);auto original=atlas::integrate(0,parent,de,parameters,s);
 atlas_trace::trace_enabled=true;auto traced=atlas_trace::integrate(0,parent,tde,parameters,ts);atlas_trace::trace_enabled=false;
 bool equivalent=original.ok==traced.ok&&bits_equal(original.state,traced.state)&&original.diagnostics.iterations==traced.diagnostics.iterations&&original.diagnostics.substeps==traced.diagnostics.substeps&&original.diagnostics.rejected==traced.diagnostics.rejected&&std::bit_cast<uint64_t>(original.diagnostics.error)==std::bit_cast<uint64_t>(traced.diagnostics.error);
 std::cout<<"{\"equivalent\":"<<(equivalent?"true":"false")<<",\"input_unchanged\":"<<(bits_equal(before,parent)?"true":"false")<<",\"baseline\":";result(original);std::cout<<",\"traced\":";result(traced);
 std::cout<<",\"full_rollback\":"<<(!original.ok&&bits_equal(original.state,parent)&&!traced.ok&&bits_equal(traced.state,parent)?"true":"false");
 std::vector<double> good{64.,64.,64.,0.,0.,0.,0.,0.,0.,0.,0.,0.};atlas::Sym<double> zero;atlas_trace::Sym<double> tzero;auto recovery=atlas::integrate(0,good,zero,parameters,s);auto trecovery=atlas_trace::integrate(0,good,tzero,parameters,ts);
 std::cout<<",\"recovery\":"<<(recovery.ok&&trecovery.ok&&bits_equal(recovery.state,good)&&bits_equal(trecovery.state,good)?"true":"false");
 const auto scales=atlas::model_scales(0,parameters);std::cout<<",\"scales\":";array(scales);
 std::cout<<",\"nearest_probe\":{\"physical\":"<<(atlas::solution_admissible(0,nearest,parameters)?"true":"false");atlas::State raw;bool raw_ok=atlas::evaluate_model(0,nearest,parent,de,parameters,raw);std::cout<<",\"raw_ok\":"<<(raw_ok?"true":"false")<<",\"raw_values\":";array(raw_ok?raw:std::vector<double>{});std::cout<<'}';
 std::cout<<",\"events\":[";bool first=true;for(auto&e:atlas_trace::trace_events){if(!first)std::cout<<',';first=false;std::cout<<"{\"kind\":\""<<e.kind<<"\",\"iteration\":"<<e.iteration<<",\"backtrack\":"<<e.backtrack<<",\"physical\":"<<e.physical<<",\"raw\":"<<e.raw<<",\"descent\":"<<e.descent<<",\"error\":"<<e.error<<",\"alpha\":"<<e.alpha<<",\"norm\":"<<e.norm<<",\"state\":";array(e.state);std::cout<<",\"residual\":";array(e.residual);std::cout<<",\"delta\":";array(e.delta);std::cout<<",\"raw_values\":";array(e.raw_values);std::cout<<",\"jacobian\":";matrix(e.jacobian);
 if(e.kind=="trial"){atlas::State out;bool ok=atlas::evaluate_model(0,e.state,parent,de,parameters,out);std::cout<<",\"post_raw_ok\":"<<(ok?"true":"false")<<",\"post_physical\":"<<(atlas::solution_admissible(0,e.state,parameters)?"true":"false")<<",\"post_raw_values\":";array(ok?out:std::vector<double>{});}std::cout<<'}';}std::cout<<']';
 std::cout<<",\"derived\":[";first=true;for(auto&r:atlas_trace::derived_observations){if(!first)std::cout<<',';first=false;std::cout<<"{\"branch\":"<<r.branch<<",\"vmax\":"<<r.vmax<<",\"vmid\":"<<r.vmid<<",\"vmin\":"<<r.vmin<<",\"trace_trial\":"<<r.trace_trial<<",\"width\":"<<r.width<<",\"jets\":"<<(r.jets?"true":"false")<<",\"check_initial\":"<<(r.check_initial?"true":"false")<<",\"trial\":";array(r.trial);std::cout<<",\"loading\":";array(r.loading);std::cout<<'}';}std::cout<<"]}\n";
 return equivalent?0:3;
}
