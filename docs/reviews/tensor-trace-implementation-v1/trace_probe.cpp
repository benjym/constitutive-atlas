// Standalone generic operator probe. No model definitions or constitutive law.
#include "atlas/tensor.hpp"
#ifndef ATLAS_TRACE_INTEGRATED
#include "trace_accuracy_candidate.hpp"
#endif
#include "trace_fixtures.hpp"
#include <iomanip>
#include <sstream>
#include <string>
#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#define TRACE_EXPORT EMSCRIPTEN_KEEPALIVE
#else
#define TRACE_EXPORT
#endif
namespace {
namespace ta=atlas::trace_accuracy;
std::string hex(std::uint64_t b){std::ostringstream o;o<<std::hex<<std::setw(16)<<std::setfill('0')<<b;return o.str();}
bool equal(const atlas::Jet& a,const atlas::Jet& b){
 if(ta::bits(a.v)!=ta::bits(b.v))return false;
 for(unsigned j=0;j<a.d.size();++j)if(ta::bits(a.d[j])!=ta::bits(b.d[j]))return false;
 return true;
}
std::string run(){
 unsigned checks=0,failures=0;std::ostringstream bad;
 auto expect=[&](bool ok,const std::string& label){++checks;if(!ok){++failures;bad<<'"'<<label<<"\",";}};
 std::ostringstream rows;bool first=true;
 for(const auto& f:trace_fixtures){
  const double old=123.25;double out=old;
  const bool ok=ta::sum3_checked(ta::binary(f.input[0]),ta::binary(f.input[1]),ta::binary(f.input[2]),out);
  expect(ok==f.ok && (!ok?ta::bits(out)==ta::bits(old):ta::bits(out)==f.expected),f.id);
  if(!first)rows<<',';first=false;
  rows<<"{\"id\":\""<<f.id<<"\",\"ok\":"<<(ok?"true":"false")<<",\"result_bits\":\""<<hex(ta::bits(out))<<"\"}";
 }
 atlas::Sym<double> scalar{{500.,1e-130,-500.,0.,0.,0.}};double value=42.;
 expect(ta::trace_checked(scalar,value)&&ta::bits(value)==ta::bits(1e-130),"scalar_witness");
 for(unsigned component=0;component<6;++component){
  for(double invalid:{std::numeric_limits<double>::infinity(),-std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()}){
   auto a=scalar;a.v[component]=invalid;double destination=42.;
   expect(!ta::trace_checked(a,destination)&&ta::bits(destination)==ta::bits(42.),"scalar_full6_nonfinite");
   expect(!std::isfinite(ta::trace_or_nonfinite(a)),"scalar_failure_sentinel");
   expect(ta::trace_checked(scalar,destination)&&ta::bits(destination)==ta::bits(1e-130),"scalar_recovery");
  }
 }
 atlas::Sym<atlas::Jet> jet{};
 jet.v[0].v=500.;jet.v[1].v=1e-130;jet.v[2].v=-500.;
 for(unsigned j=0;j<38;++j){jet.v[0].d[j]=500.;jet.v[1].d[j]=j%2?-1e-130:1e-130;jet.v[2].d[j]=-500.;}
 atlas::Jet result{};
 expect(ta::trace_checked(jet,result)&&ta::bits(result.v)==ta::bits(1e-130),"jet_primal");
 std::ostringstream derivative_bits;
 for(unsigned j=0;j<38;++j){
  const auto expected=ta::bits(j%2?-1e-130:1e-130);
  expect(ta::bits(result.d[j])==expected,"jet_full38_cancellation");
  if(j)derivative_bits<<',';derivative_bits<<'"'<<hex(ta::bits(result.d[j]))<<'"';
 }
 for(unsigned component=0;component<6;++component){
  atlas::Sym<atlas::Jet> basis{};basis.v[component].d[0]=1.;atlas::Jet b{};
  expect(ta::trace_checked(basis,b)&&b.v==0&&b.d[0]==(component<3?1.:0.),"jet_basis6");
 }
 atlas::Jet old(42.);for(unsigned j=0;j<38;++j)old.d[j]=double(j+1);
 for(unsigned component=0;component<6;++component){
  auto a=jet;a.v[component].v=std::numeric_limits<double>::quiet_NaN();auto destination=old;
  expect(!ta::trace_checked(a,destination)&&equal(destination,old),"jet_full6_primal_nonmutation");
  expect(!atlas::finite_value(ta::trace_or_nonfinite(a)),"jet_failure_sentinel");
  for(unsigned j=0;j<38;++j){
   a=jet;a.v[component].d[j]=std::numeric_limits<double>::infinity();destination=old;
   expect(!ta::trace_checked(a,destination)&&equal(destination,old),"jet_full6_full38_nonmutation");
   expect(ta::trace_checked(jet,destination)&&ta::bits(destination.d[j])==ta::bits(j%2?-1e-130:1e-130),"jet_recovery");
  }
 }
 auto overflowing=jet;overflowing.v[0].d[37]=overflowing.v[1].d[37]=std::numeric_limits<double>::max();overflowing.v[2].d[37]=0.;
 auto destination=old;
 expect(!ta::trace_checked(overflowing,destination)&&equal(destination,old),"jet_final_derivative_overflow");
 overflowing=jet;overflowing.v[0].v=overflowing.v[1].v=std::numeric_limits<double>::max();overflowing.v[2].v=0.;destination=old;
 expect(!ta::trace_checked(overflowing,destination)&&equal(destination,old),"jet_final_primal_overflow");
 expect(ta::trace_checked(jet,destination)&&ta::bits(destination.v)==ta::bits(1e-130),"recovery_after_final_overflows");
 auto large=jet;
 large.v[0].v=large.v[1].v=std::numeric_limits<double>::max();large.v[2].v=-std::numeric_limits<double>::max();
 for(unsigned j=0;j<38;++j){large.v[0].d[j]=large.v[1].d[j]=std::numeric_limits<double>::max();large.v[2].d[j]=-std::numeric_limits<double>::max();}
 expect(ta::trace_checked(large,destination)&&ta::bits(destination.v)==ta::bits(std::numeric_limits<double>::max()),"jet_finite_intermediate_overflow_primal");
 for(unsigned j=0;j<38;++j)expect(ta::bits(destination.d[j])==ta::bits(std::numeric_limits<double>::max()),"jet_finite_intermediate_overflow_seed");
 auto sub=jet;sub.v[0].d[37]=1.;sub.v[1].d[37]=std::numeric_limits<double>::denorm_min();sub.v[2].d[37]=-1.;
 expect(ta::trace_checked(sub,destination)&&ta::bits(destination.d[37])==1,"jet_subnormal_seed");
 auto zero=jet;
 for(auto& x:zero.v){x.v=-0.;for(auto& seed:x.d)seed=-0.;}
 expect(ta::trace_checked(zero,destination)&&ta::bits(destination.v)==0,"jet_zero_primal_canonical");
 for(unsigned j=0;j<38;++j)expect(ta::bits(destination.d[j])==0,"jet_zero_seed_canonical");
 double z=-1.;expect(ta::sum3_checked(-0.,-0.,-0.,z)&&ta::bits(z)==0,"zero_canonical");
 const int rounding=std::fegetround();
 bool alternate_supported=false;
 if(rounding!=-1 && std::fesetround(FE_DOWNWARD)==0){
  alternate_supported=true;double x=0.;
  expect(ta::sum3_checked(1.,0x1p-53,0.,x)&&ta::bits(x)==ta::bits(1.),"ambient_rounding_independent");
  expect(std::fesetround(rounding)==0,"restore_rounding_mode");
 }
#ifdef ATLAS_TRACE_INTEGRATED
 expect(ta::bits(atlas::trace(scalar))==ta::bits(1e-130),"integrated_trace");
 auto invalid=scalar;invalid.v[5]=std::numeric_limits<double>::infinity();
 expect(!atlas::finite_value(atlas::dev(invalid)),"integrated_nested_dev_invalid");
 const bool select_guard=false;
 const double lazy=select_guard?atlas::trace(invalid):7.;
 expect(lazy==7.,"integrated_lazy_select");
#endif
 std::string errors=bad.str();if(!errors.empty())errors.pop_back();
 std::ostringstream out;out<<"{\"version\":\""<<ta::version<<"\",\"checks\":"<<checks<<",\"failures\":"<<failures
 <<",\"rounding_mode_test_supported\":"<<(alternate_supported?"true":"false")<<",\"records\":["<<rows.str()<<"],\"jet_derivative_bits\":["<<derivative_bits.str()<<"],\"errors\":["<<errors<<"]}";
 return out.str();
}
std::string answer;
}
extern "C" TRACE_EXPORT const char* atlas_trace_selftest(){answer=run();return answer.c_str();}
#ifndef __EMSCRIPTEN__
#include <iostream>
int main(){const auto result=run();std::cout<<result<<'\n';return result.find("\"failures\":0,")!=std::string::npos?0:1;}
#endif
